"""Service module for the API."""

import time


from pathlib import Path
from typing import Iterator, TextIO
import json
from settings import LOGS_DIR
from fastapi import Request


def follow(file: TextIO, sleep_sec: int = 0.2) -> Iterator[str]:
    """
    Yield each line from a file as they are written.

    :param file: File object.
    :param sleep_sec: Time to sleep between reads of empty lines.
    """
    line = ''
    while True:
        tmp = file.readline()
        if tmp is not None and tmp != '':
            line += tmp
            if line.endswith('\n'):
                yield line
                line = ''
        elif sleep_sec:
            time.sleep(sleep_sec)


async def logfile_generator(request: Request, logfile: str) -> Iterator[str]:
    """
    Return generator that yields log lines as they are written to the logfile.

    :param request: Request object.
    :param logfile: Name of the logfile to stream.
    :return: A generator that yields log lines.
    """
    for line in follow(open(Path(LOGS_DIR, logfile))):
        done = 'DONE' in line
        yield json.dumps({'event': 'log', 'data': line, 'done': done})

        if await request.is_disconnected() or done:
            break
