from typing import Coroutine

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.handlers.exceptions import (
    FileException,
    PermissionException,
    RowAlreadyExists,
    RowNotFoundException,
)
from src.logger_setup import get_logger
from src.schemas.base_schemas import ErrorResponseSchema

logger = get_logger(__name__)

EXCEPTION_HANDLERS = (
    PermissionException,
    RowNotFoundException,
    FileException,
    RowAlreadyExists,
)


async def exception_to_json(exc: HTTPException) -> JSONResponse:
    exc_type = exc.__class__.__name__
    exc_message = exc.detail

    logger.warning(
        "Error occurred!!!!\n error_type: %s\n error_message: %s", exc_type, exc_message
    )

    schema = ErrorResponseSchema(
        result=False, error_type=exc_type, error_message=exc_message
    )

    return JSONResponse(schema.model_dump(), exc.status_code)


async def secure_request(coroutine: Coroutine):
    try:
        return await coroutine
    except EXCEPTION_HANDLERS as exc:
        return await exception_to_json(exc)


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_type = exc.__class__.__name__
    error_message = str(exc)

    schema = ErrorResponseSchema(
        result=False, error_type=error_type, error_message=error_message
    ).model_dump()

    logger.exception(
        "Internal Error!!!\nerror_type: %s\nerror_message: %s",
        error_type,
        error_message,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=schema,
    )
