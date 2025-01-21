import pytest

from src.functions import allowed_file


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
async def test_allowed_file(filename, expected):
    assert await allowed_file(filename) == expected
