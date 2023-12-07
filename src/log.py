"""Deals with saving logs."""
import logging
from pathlib import Path

from settings import LOGS_DIR


def get_logger(logger_name: str) -> logging.Logger:
    """
    Get logger for module.

    :param logger_name: Name of the file to log.
    :return: Logger.
    """
    # Create logs folder if it doesn't exist.
    if not Path(LOGS_DIR).exists():
        Path(LOGS_DIR).mkdir(parents=True)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Logfile.
    logfile = f'{logger_name}.log'
    log_path = Path(LOGS_DIR, logfile)
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)

    # Formatter.
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
