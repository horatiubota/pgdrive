import io
from typing import List, Optional

import pandas as pd
from googleapiclient.http import MediaIoBaseUpload

from .find import find_drive_id, find_folder_id, find_resource
from .service import (
    MIME_TYPE_CSV,
    MIME_TYPE_EXCEL_SPREADSHEET,
    MIME_TYPE_FOLDER,
    PandasGoogleDriveException,
    create,
    update,
)


def _setup_media(df: pd.DataFrame, path: str, **kwargs) -> MediaIoBaseUpload:
    """
    Creates MediaIoBaseUpload object with appropriate mime type.
    """

    buffer_: Optional[io.IOBase] = None

    if path.endswith(".csv"):
        mime_type = MIME_TYPE_CSV
        buffer_ = io.StringIO()
        df.to_csv(buffer_, **kwargs)

    elif path.endswith(".xlsx"):
        mime_type = MIME_TYPE_EXCEL_SPREADSHEET
        buffer_ = io.BytesIO()
        df.to_excel(buffer_, **kwargs)

    else:
        raise PandasGoogleDriveException(f"Unsupported file type: {path}.")

    return MediaIoBaseUpload(buffer_, resumable=False, mimetype=mime_type)


def create_folder(
    name: str, parent_folder_id: Optional[str], drive_id: str, exist_ok: bool = True
) -> Optional[str]:
    """
    If `exist_ok`, tries to find existing folder ID given name and
    parent_folder_id. If no such folder exists or not `exist_ok`, creates the
    folder in the given parent (note that Google Drive allows multiple folders
    with same name in same parent).

    Args:
        name (str): Folder name.
        parent_folder_id (Optional[str]): Where to put the folder. Parent folder ID can be found
            in the parent folder URL. If None, creates folder in Drive root.
        exist_ok (bool): Return existing folder ID, if available. Defaults to True.

    Returns:
        str: Google Drive ID of created folder.
    """

    if exist_ok and (
        folder_id := find_folder_id(
            name, parent_folder_id=parent_folder_id, drive_id=drive_id
        )
    ):
        return folder_id

    if response := create(
        name=name,
        parent_folder_id=parent_folder_id,
        drive_id=drive_id,
        mime_type=MIME_TYPE_FOLDER,
    ):
        return response.get("id")
    else:
        raise PandasGoogleDriveException(f"Unable to create folder {name}.")


def create_folders(
    folders: List[str],
    drive_id: str,
    parent_folder_id: Optional[str] = None,
    exist_ok: bool = True,
) -> Optional[str]:
    """
    Creates folder tree from list of folder names in given parent folder. If no
    parent folder provided, creates folder tree in root folder.

    Args:
        folders (List[str]): List of folder names.
        drive_id (str): Google Drive ID.
        parent_folder_id (str): Folder ID of parent folder. Defaults to None.
        exist_ok (bool, optional): Existing folders can be re-used. Defaults to True.

    Returns:
        str: Google Drive ID of last folder in list.
    """

    for folder in folders:
        parent_folder_id = create_folder(
            name=folder,
            parent_folder_id=parent_folder_id,
            drive_id=drive_id,
            exist_ok=exist_ok,
        )

    return parent_folder_id


def to_drive(df: pd.DataFrame, path: str, overwrite: bool = False, **kwargs) -> str:
    """
    Write a DataFrame to a file on Google Drive, in the specified parent folder.
    Example:
    >>> df.pipe(gdrive.to_drive, "drive_name/folder1/folder2/file_name.csv")
    >>> df.pipe(gdrive.to_drive, "drive_name/folder1/folder2/file_name.xlsx")

    Args:
        df (pd.DataFrame): DataFrame to write.
        path (str): Path to write to. First part of path is the drive name.
        overwrite (bool, optional): Overwrite existing file. Defaults to False.

    Raises:
        PandasGoogleDriveException: Raised if `overwrite` is False and file exists.
        PandasGoogleDriveException: Raised if path is invalid.
        PandasGoogleDriveException: Raised if write response does not contain file ID.

    Returns:
        str: Google Drive file URL.
    """

    drive, *folders, file_name = path.split("/")
    if not drive or not file_name:
        raise PandasGoogleDriveException(f"Invalid path: {path}.")

    drive_id = find_drive_id(drive)
    parent_folder_id = create_folders(folders, drive_id=drive_id)

    media = _setup_media(df, path, **kwargs)
    if resource := find_resource(file_name, parent_folder_id, drive_id):
        if not overwrite:
            raise PandasGoogleDriveException(f"File {path} already exists.")

        if file_id := resource.get("id"):
            response = update(file_id=file_id, media=media)
        else:
            raise PandasGoogleDriveException(
                f"File ID for {path} not found when attempting update."
            )

    else:
        response = create(
            name=file_name,
            parent_folder_id=parent_folder_id,
            drive_id=drive_id,
            media=media,
        )

    if not response:
        raise PandasGoogleDriveException(f"Unable to write to {path}.")

    file_url = response.get("webViewLink")
    if not file_url or not isinstance(file_url, str):
        raise PandasGoogleDriveException(f"Unable to get uploaded file URL for {path}.")

    return file_url
