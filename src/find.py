from functools import lru_cache
from typing import Optional

from googleapiclient.errors import HttpError

from .service import MIME_TYPE_FOLDER, PandasGoogleDriveException, get_service


@lru_cache
def find_drive_id(name: str) -> str:
    """
    Finds the ID of a shared Google Drive by name.
    """

    service = get_service()

    try:
        drives = (
            service.drives().list(fields="drives(id, name)").execute().get("drives")
        )
    except HttpError as e:
        raise PandasGoogleDriveException("Unable to list Google Drives.") from e

    if drives is None:
        raise PandasGoogleDriveException("No Google Drives accessible.")

    if drive := next(filter(lambda drive: drive.get("name") == name, drives)):
        return drive.get("id")

    raise PandasGoogleDriveException(
        f"No Google Drive with name {name} found for account."
    )


def find_resource(
    name: str,
    parent_folder_id: Optional[str],
    drive_id: str,
    mime_type: Optional[str] = None,
    trashed: bool = False,
) -> Optional[dict]:
    """
    Finds resource (file, folder) on Google Drive.

    Args:
        name (str): Resource name.
        drive_id (str): Drive ID to search in.
        parent_folder_id (Optional[str]): What folder to search for resource. Optional.
        mime_type (Optional[str]): Type of resource to look for. Defaults to None.
        trashed (bool): Search trash. Defaults to False.

    Raises:
        PandasGoogleDriveException: Raised when more than one resource matches the provided
        query parameters.

    Returns:
        dict: Dictionary containing resource `name` and `id`.
    """

    service = get_service().files()
    query = (
        f"name = '{name}' "
        + (f"and parents in '{parent_folder_id}' " if parent_folder_id else "")
        + (f"and trashed = {str(trashed or False).lower()} ")
        + (f"and mimeType = '{mime_type}'" if mime_type else "")
    )

    response = service.list(
        q=query,
        fields="files(id, name)",
        corpora="drive",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        driveId=drive_id,
    ).execute()

    if files := response.get("files"):
        if len(files) == 1:
            return files.pop()

        else:
            raise PandasGoogleDriveException(
                f"{len(response.get('files'))} resources found with name: {name} "
                f"in parent: {parent_folder_id}."
            )

    else:
        return None


def find_folder_id(
    name: str, parent_folder_id: Optional[str], drive_id: str, trashed: bool = False
) -> Optional[str]:
    """
    Find the Google Drive ID of an existing folder in given parent.

    Args:
        name (str): Folder name.
        parent_folder_id (Optional[str]): Optional. Where to look for the folder. Parent folder
            ID can be found in the parent folder URL or by using this method and searching for
            the parent folder name.

    Returns:
        Optional[str]: Folder ID. Returns `None` if no folder is found.
    """

    if resource := find_resource(
        name=name,
        parent_folder_id=parent_folder_id,
        drive_id=drive_id,
        mime_type=MIME_TYPE_FOLDER,
        trashed=trashed,
    ):
        return resource.get("id")

    return None


def find_file_id(path: str, trashed: bool = False) -> Optional[str]:
    """
    Finds the ID of a file by Google Drive path.

    Args:
        path (str): Google Drive path. First part of the path must be the name of a shared
            Google Drive.
        trashed (bool, optional): Search Trash. Defaults to False.

    Returns:
        str: Google Drive ID of file described by path.
    """

    drive, *folders, file_name = path.split("/")
    if not drive or not file_name:
        raise PandasGoogleDriveException(f"Invalid path: {path}.")

    drive_id = find_drive_id(drive)
    parent_folder_id = None

    for folder in folders:
        parent_folder_id = find_folder_id(
            name=folder, parent_folder_id=parent_folder_id, drive_id=drive_id
        )

    if resource := find_resource(
        name=file_name,
        parent_folder_id=parent_folder_id,
        drive_id=drive_id,
        trashed=trashed,
    ):
        return resource.get("id")

    return None
