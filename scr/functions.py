ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def exception_handler(error_type: str, error_message: str):
    return {
        "result": False,
        "error_type": error_type,
        "error_message": error_message
    }


def allowed_file(filename):
    global ALLOWED_EXTENSIONS
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
