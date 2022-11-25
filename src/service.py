import json
import os
from typing import Optional, Union

import googleapiclient
import googleapiclient.discovery
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

PandasGoogleDriveException = Exception

MIME_TYPE_CSV = "text/csv"
MIME_TYPE_EXCEL_SPREADSHEET = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
MIME_TYPE_FOLDER = "application/vnd.google-apps.folder"

GOOGLE_DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive",
]


def get_credentials() -> dict:
    if credentials := os.getenv("GOOGLE_DRIVE_CREDENTIALS"):
        return json.loads(credentials)
    else:
        raise ValueError("Missing environment variable GOOGLE_DRIVE_CREDENTIALS")


def get_service():
    credentials = service_account.Credentials.from_service_account_info(
        get_credentials(),
        scopes=GOOGLE_DRIVE_SCOPES,
    )

    return googleapiclient.discovery.build("drive", "v3", credentials=credentials)


def create(
    name: str,
    parent_folder_id: Optional[str],
    drive_id: str,
    mime_type: Optional[str] = None,
    media: Optional[Union[MediaFileUpload, MediaIoBaseUpload]] = None,
) -> dict:
    """
    Executes Google Drive HttpRequest to create/upload resources (files,
    folders).

    Args:
        name (str): Resource name.
        parent_folder_id (str): Google Drive folder ID where to place resource. The ID
            can be found in the folder URL. If None, creates resource in Drive root.
        drive_id (str, optional): The Google Drive ID to upload to.
        mime_type (Optional[str], optional): Type of resource to create.
        media (Optional[Union[MediaFileUpload, MediaIoBaseUpload]], optional):
            When uploading files, the file content.

    Returns:
        dict: Request response.
    """

    metadata = {
        "name": name,
        "driveId": drive_id,
        "parents": [parent_folder_id] if parent_folder_id else None,
        "mimeType": mime_type,
    }

    service = get_service().files()
    return service.create(
        body=metadata, media_body=media, fields="id,webViewLink", supportsAllDrives=True
    ).execute()


def update(
    file_id: str,
    media: Union[MediaFileUpload, MediaIoBaseUpload],
) -> dict:
    """
    Executes Google Drive HttpRequest to update files.

    Args:
        file_id (str): File ID.
        media (Union[MediaFileUpload, MediaIoBaseUpload]]): File content.

    Returns:
        dict: Request response.
    """

    service = get_service().files()
    return service.update(
        fileId=file_id,
        media_body=media,
        fields="id,webViewLink",
        supportsAllDrives=True,
    ).execute()
