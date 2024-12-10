from logging import Logger
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from werkzeug.utils import secure_filename

from database.schemas import ErrorResponseSchema

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def exception_handler(logger: Logger, error_type: str, error_message: str):
    logger.exception(
        "error_type: {error_type}, error_message: {error_message}".format(
            error_type=error_type,
            error_message=error_message
        )
    )
    return ErrorResponseSchema(error_type=error_type, error_message=error_message)


def allowed_file(filename):
    global ALLOWED_EXTENSIONS
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


async def save_uploaded_file(api_key: str, file: UploadFile) -> str:
    """Сохраняет файл на диск асинхронно."""
    upload_folder = Path(__file__).parent.parent / "media" / secure_filename(api_key)
    upload_folder.mkdir(parents=True, exist_ok=True)

    if not allowed_file(file.filename):
        raise ValueError("File format is not allowed. Please upload a valid file.")

    filename = secure_filename(file.filename)
    output_file = (upload_folder / filename).resolve()

    if not str(output_file).startswith(str(upload_folder)):
        raise ValueError("Attempt to write outside the media directory.")

    async with aiofiles.open(output_file, 'wb') as f:
        await f.write(await file.read())

    return str(output_file)
