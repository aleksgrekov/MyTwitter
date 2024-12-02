from logging import Logger

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def exception_handler(logger: Logger, error_type: str, error_message: str):
    logger.exception(
        "error_type: {error_type}, error_message: {error_message}".format(
            error_type=error_type,
            error_message=error_message
        )
    )
    return {
        "result": False,
        "error_type": error_type,
        "error_message": error_message
    }


def allowed_file(filename):
    global ALLOWED_EXTENSIONS
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
