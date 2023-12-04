"""Deals with saving logs."""
import logging
from pathlib import Path

from settings import LOGS_DIR


def get_logger(file_name: str) -> logging.Logger:
    """
    Get logger for module.

    :param file_name: Name of the file to log.
    :return: Logger.
    """
    if not Path(LOGS_DIR).exists():
        Path(LOGS_DIR).mkdir(parents=True)

    log_path = Path(LOGS_DIR, f'{file_name}.log')
    if log_path.exists():
        log_path.unlink()

    logger = logging.getLogger(file_name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
