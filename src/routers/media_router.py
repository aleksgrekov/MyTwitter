from typing import Annotated, Union

from fastapi import APIRouter, Depends, Header, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.media_repository import add_media
from src.database.service import create_session
from src.functions import save_uploaded_file
from src.handlers.exceptions import FileException
from src.handlers.handlers import exception_to_json
from src.schemas.base_schemas import ErrorResponseSchema
from src.schemas.tweet_schemas import NewMediaResponseSchema

media_router = APIRouter(
    prefix="/api/medias",
    tags=["MEDIA"],
)


@media_router.post(
    "",
    response_model=Union[NewMediaResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Upload a media file",
    description="Upload a media file to the server and save link to database.",
    responses={
        201: {
            "description": "Media file added successfully",
            "model": NewMediaResponseSchema,
        },
        400: {"description": "Bad request", "model": ErrorResponseSchema},
    },
)
async def upload_media(
    api_key: Annotated[str, Header(description="User's API key")],
    file: UploadFile,
    db: AsyncSession = Depends(create_session),
) -> Union[NewMediaResponseSchema, JSONResponse]:
    try:
        link = await save_uploaded_file(api_key, file)
    except FileException as exc:
        return await exception_to_json(exc)
    finally:
        await file.close()

    return await add_media(link, session=db)
