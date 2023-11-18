"""Contains global settings for the project."""

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(ROOT_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')


FDCUK_DIR = os.path.join(ROOT_DIR, 'data', 'football-data.co.uk')
FDCUK_BUNDESLIGA_DIR = os.path.join(FDCUK_DIR, 'bundesliga')

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Accept-Language': 'en-US,en;q=0.5',
}
