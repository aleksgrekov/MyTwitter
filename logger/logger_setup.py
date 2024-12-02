import logging.config

from .logger_config import dict_config


def get_logger(name):
    logging.config.dictConfig(dict_config)

    logger = logging.getLogger(name)

    return logger
