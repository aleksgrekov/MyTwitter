from typing import Annotated, Union

from fastapi import APIRouter, Depends, Header, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.media_repository import add_media
from src.database.service import create_session
from src.functions import exception_handler, save_uploaded_file
from src.logger_setup import get_logger
from src.schemas.base_schemas import ErrorResponseSchema
from src.schemas.tweet_schemas import NewMediaResponseSchema

routers_logger = get_logger(__name__)
media_router = APIRouter(
    prefix="/api/medias",
    tags=["MEDIA"],
)


@media_router.post(
    "",
    response_model=Union[NewMediaResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Upload a media file",
    description="Uploads a media file to the server and returns a link to the file.",
    responses={
        201: {
            "description": "Media file uploaded successfully",
            "model": NewMediaResponseSchema,
        },
        400: {"description": "Bad request", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    },
)
async def upload_media(
    api_key: Annotated[str, Header(description="User's API key")],
    file: UploadFile,
    db: AsyncSession = Depends(create_session),
) -> Union[NewMediaResponseSchema, ErrorResponseSchema]:
    try:
        link = await save_uploaded_file(api_key, file)
    except OSError as exc:
        return exception_handler(routers_logger, exc.__class__.__name__, str(exc))
    finally:
        await file.close()

    try:
        return await add_media(link, session=db)
    except SQLAlchemyError as exc:
        return exception_handler(routers_logger, exc.__class__.__name__, str(exc))
