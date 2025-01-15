from logging import Logger

import pytest

from src.functions import allowed_file, exception_handler
from src.schemas.base_schemas import ErrorResponseSchema


def test_exception_handler(mocker):
    logger = mocker.MagicMock(spec=Logger)
    error_type = "ValidationError"
    error_message = "Invalid input data."

    result = exception_handler(logger, error_type, error_message)

    logger.exception.assert_called_once_with(
        "error_type: ValidationError, error_message: Invalid input data."
    )

    assert isinstance(result, ErrorResponseSchema)
    assert result.error_type == error_type
    assert result.error_message == error_message


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("document.pdf", True),
        ("image.jpeg", True),
        ("archive.zip", False),
        ("file_without_extension", False),
        (".hiddenfile", False),
    ],
)
def test_allowed_file(filename, expected):
    assert allowed_file(filename) == expected
