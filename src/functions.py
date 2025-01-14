from logging import Logger
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from werkzeug.utils import secure_filename

from src.database.schemas.base import ErrorResponseSchema


def exception_handler(logger: Logger, error_type: str, error_message: str):
    """
    Handles exceptions by logging them and returning a standardized error response.

    Args:
        logger (Logger): The logger instance to log the error.
        error_type (str): A short description of the type of error.
        error_message (str): Detailed information about the error.

    Returns:
        ErrorResponseSchema: A schema representing the error details.
    """
    logger.exception("error_type: %s, error_message: %s", error_type, error_message)

    return ErrorResponseSchema(
        result=False, error_type=error_type, error_message=error_message
    )


def allowed_file(filename):
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

    if not allowed_file(upload_file.filename):
        raise ValueError("File format is not allowed. Please upload a valid file.")

    filename = upload_file.filename if upload_file.filename else ""
    filename = secure_filename(filename)
    output_file = (upload_folder / filename).resolve()

    if not str(output_file).startswith(str(upload_folder)):
        raise ValueError("Attempt to write outside the media directory.")

    try:
        async with aiofiles.open(output_file, "wb") as opened_file:
            await opened_file.write(await upload_file.read())
    except Exception as exc:
        raise ValueError(f"Failed to save file: {str(exc)}")

    return str(output_file)
