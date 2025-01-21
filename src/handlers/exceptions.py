from fastapi import HTTPException, status


class PermissionException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)


class RowNotFoundException(HTTPException):
    def __init__(self, message="User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class FileException(HTTPException):
    def __init__(self, message):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message
        )


class RowAlreadyExists(HTTPException):
    def __init__(self, message="Like already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class IntegrityViolationException(Exception):
    def __init__(self, message):
        self.message = message
