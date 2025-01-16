from logging import Logger
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from werkzeug.utils import secure_filename

from src.schemas.base_schemas import ErrorResponseSchema


async def exception_handler(logger: Logger, exception: Exception):
    """
    Handles exceptions by logging them and returning a standardized error response.

    Args:
        logger (Logger): The logger instance to log the error.
        exception (Exception): The type of error.

    Returns:
        ErrorResponseSchema: A schema representing the error details.
    """

    error_type = exception.__class__.__name__
    error_message = str(exception)

    logger.exception(f"{error_type=}, {error_message=}")
    # logger.exception(f"error_type: %s, error_message: %s" % (error_type, error_message))

    return ErrorResponseSchema(
        result=False, error_type=error_type, error_message=error_message
    )


async def allowed_file(filename):
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

    if not await allowed_file(upload_file.filename):
        raise ValueError("File format is not allowed. Please upload a valid file.")

    filename = upload_file.filename if upload_file.filename else ""
    filename = secure_filename(filename)
    output_file = (upload_folder / filename).resolve()

    if not str(output_file).startswith(str(upload_folder)):
        raise ValueError("Attempt to write outside the media directory.")

    async with aiofiles.open(output_file, "wb") as opened_file:
        await opened_file.write(await upload_file.read())

    return str(output_file)


async def json_response_serialized(
    response: BaseModel, status_code: int
) -> JSONResponse:
    """
    Return a JSON response with the given status code.

    This function serializes the provided Pydantic model (`BaseModel`) into a JSON response
    and returns it with the specified HTTP status code.

    Args:
        response (BaseModel): The Pydantic model to be serialized into JSON.
        status_code (int): The HTTP status code to be returned with the response.

    Returns:
        JSONResponse: A JSON response containing the serialized data and status code.
    """
    return JSONResponse(response.model_dump(), status_code)
