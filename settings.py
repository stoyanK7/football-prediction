"""Contains global settings for the project."""

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(ROOT_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
INTERIM_DATA_DIR = os.path.join(DATA_DIR, 'interim')
TEST_DATA_DIR = os.path.join(DATA_DIR, 'test')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Accept-Language': 'en-US,en;q=0.5',
}
