"""Tests for the FbrefScraper class."""
import shutil
from pathlib import Path

from settings import TEST_DATA_DIR
from src.data.fbref_scraper import FbrefScraper


def test_scrape():
    """Test scrape()."""
    raw_data_folder_path = Path('.data')
    scraper = FbrefScraper(
        html_folder_path=Path(TEST_DATA_DIR, 'test_scrape'),
        raw_data_folder_path=raw_data_folder_path,
        competition='Bundesliga',
    )

    scraper.scrape()

    output_file = Path(
        raw_data_folder_path, 'bundesliga_matches.csv'
    ).read_text()
    expected_output_file = Path(
        TEST_DATA_DIR, 'test_scrape', 'bundesliga_matches.csv'
    ).read_text()
    assert ',Team,' in output_file
    assert output_file == expected_output_file

    shutil.rmtree(raw_data_folder_path)
