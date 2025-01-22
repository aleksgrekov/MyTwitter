from fastapi import HTTPException, status


class PermissionException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)


class RowNotFoundException(HTTPException):
    default_message = "User not found"

    def __init__(self, message: str = default_message):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class FileException(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message
        )


class RowAlreadyExists(HTTPException):
    default_message = "Like already exists"

    def __init__(self, message: str = default_message):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class IntegrityViolationException(Exception):
    def __init__(self, message: str):
        self.message = message
