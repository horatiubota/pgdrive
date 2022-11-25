import io
import re
from typing import Optional, Tuple

import pandas as pd
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from .find import find_file_id
from .service import (
    MIME_TYPE_EXCEL_SPREADSHEET,
    PandasGoogleDriveException,
    get_service,
)


def _parse_url(url: str) -> Tuple[str, str]:
    """
    Parses a Google Drive spreadsheets or file URL to extract file ID.
    """
    GOOGLE_DRIVE_URL_PATTERN = r"/(spreadsheets|file)/d/([^&#/]*)"

    if search := re.search(GOOGLE_DRIVE_URL_PATTERN, url, flags=re.IGNORECASE):
        file_type, file_id = search.groups()
        return file_type, file_id

    raise PandasGoogleDriveException(f"Unable to parse Drive URL: {url}.")


def _download_file(file_url: str) -> io.BytesIO:
    """
    Downloads file stored on Google Drive.

    NOTE: The file you want to download needs to be shared with the service account
    you are using to make the request.
    """
    service = get_service().files()
    file_type, file_id = _parse_url(file_url)

    # Google spreadsheets need to be downloaded using the export method
    if file_type == "spreadsheets":
        return service.export(
            fileId=file_id,
            mimeType=MIME_TYPE_EXCEL_SPREADSHEET,
        ).execute()

    # all other binary media needs to use get_media, including Excel files
    file_request = service.get_media(fileId=file_id, supportsAllDrives=True)
    file_handle = io.BytesIO()

    downloader = MediaIoBaseDownload(file_handle, file_request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    file_handle.seek(0)
    return file_handle


def read_drive(
    url: Optional[str] = None, path: Optional[str] = None, **kwargs
) -> pd.DataFrame:
    """
    Reads a file from Google Drive into a Pandas DataFrame.
    """
    if path is None and url is None:
        raise PandasGoogleDriveException("Must provide either path or url.")

    if path is not None and url is not None:
        raise PandasGoogleDriveException("Must provide either path or url, not both.")

    if path is not None:
        if (file_id := find_file_id(path)) is not None:
            url = f"https://docs.google.com/file/d/{file_id}"
        else:
            raise PandasGoogleDriveException(f"Unable to find file on Drive: {path}.")

    try:
        assert isinstance(url, str)
        file_content = _download_file(url)
    except HttpError as e:
        raise PandasGoogleDriveException(
            f"Unable to download file: {path or url}"
        ) from e

    try:
        return pd.read_excel(file_content, **kwargs)
    except ValueError:
        return pd.read_csv(file_content, **kwargs)
    except Exception as e:
        raise ValueError(f"Unable to read {path or url} from Google Drive.") from e
