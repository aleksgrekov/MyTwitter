import logging
from logging.config import dictConfig

from src.logger_config import dict_config


def get_logger(name):
    """
    Initializes and returns a logger instance configured
    with a predefined configuration.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: A logger instance with the specified name.
    """
    dictConfig(dict_config)

    return logging.getLogger(name)
