import sys

dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "fileFormatter": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%Z"
        },
        "consoleFormatter": {
            "format": "%(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "stream": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "consoleFormatter",
            "stream": sys.stdout
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "WARNING",
            "formatter": "fileFormatter",
            "filename": "../logs/logfile.log"
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["stream", "file"]
    },
}
