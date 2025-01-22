from pathlib import Path

import aiofiles
from fastapi import UploadFile
from werkzeug.utils import secure_filename

from src.handlers.exceptions import FileException


async def allowed_file(filename: str) -> bool:
    """
    Checks if a file has an allowed extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    allowed_extensions = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}

    return "." in filename and filename.rsplit(".", 1)[1] in allowed_extensions


async def save_uploaded_file(api_key: str, upload_file: UploadFile) -> str:
    """
    Asynchronously saves an uploaded file to disk.

    Args:
        api_key (str): A unique identifier to determine the upload folder.
        upload_file (UploadFile): The uploaded file object to save.

    Raises:
        ValueError: If the file format is not allowed or an error occurs during saving.

    Returns:
        str: The absolute path to the saved file.
    """
    upload_folder = Path(__file__).parent.parent / "media" / secure_filename(api_key)
    upload_folder.mkdir(parents=True, exist_ok=True)

    if upload_file.filename is None or not await allowed_file(upload_file.filename):
        raise FileException("File format is not allowed. Please upload a valid file.")

    filename = upload_file.filename
    filename = secure_filename(filename)
    output_file = (upload_folder / filename).resolve()

    if not str(output_file).startswith(str(upload_folder)):
        raise FileException("Attempt to write outside the media directory.")

    async with aiofiles.open(output_file, "wb") as opened_file:
        await opened_file.write(await upload_file.read())

    return str(output_file)
