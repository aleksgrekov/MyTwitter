def exception_handler(error_type: str, error_message: str):
    return {
        "result": False,
        "error_type": error_type,
        "error_message": error_message
    }
