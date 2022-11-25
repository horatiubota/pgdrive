from pathlib import Path
from typing import Union

from googleapiclient.http import MediaFileUpload

from .find import find_drive_id
from .service import PandasGoogleDriveException, create
from .write import create_folders


def upload_file(local_path: Union[str, Path], drive_path: str) -> str:
    """
    Uploads file to Google Drive.

    Args:
        local_path (Union[str, Path]): Local path of file to upload.
        drive_path (str): Google Drive path to uploaded to. First part of path is the drive name.
            Must include file name: "drive_name/folder1/folder2/file_name.zip".

    Returns:
        str: Google Drive URL of uploaded file.
    """

    local_path = Path(local_path) if isinstance(local_path, str) else local_path
    if not local_path.exists():
        raise FileNotFoundError(f"File {local_path} does not exist.")

    drive, *folders, file_name = drive_path.split("/")
    if not drive or not file_name:
        raise PandasGoogleDriveException(f"Invalid path: {drive_path}.")

    drive_id = find_drive_id(drive)
    parent_folder_id = create_folders(folders, drive_id=drive_id)

    response = create(
        name=file_name,
        parent_folder_id=parent_folder_id,
        drive_id=drive_id,
        media=MediaFileUpload(local_path, resumable=False),
    )

    if not response:
        raise PandasGoogleDriveException(f"Unable to write to {drive_path}.")

    file_url = response.get("webViewLink")
    if not file_url or not isinstance(file_url, str):
        raise PandasGoogleDriveException(
            f"Unable to get uploaded file URL for {drive_path}."
        )

    return file_url
