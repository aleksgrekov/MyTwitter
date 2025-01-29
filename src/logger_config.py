import sys
from pathlib import Path

log_folder_path = Path(__file__).parent.parent / "logs"
log_folder_path.mkdir(exist_ok=True)
log_file_path = log_folder_path / "logfile.log"


dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "fileFormatter": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%Z",
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
            "stream": sys.stdout,
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "WARNING",
            "formatter": "fileFormatter",
            "filename": str(log_file_path),
        },
    },
    "root": {"level": "DEBUG", "handlers": ["stream", "file"]},
}
