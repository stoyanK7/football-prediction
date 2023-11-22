"""Tests for the FootballDataCoUkScraper class."""
import shutil
from pathlib import Path

from settings import TEST_DATA_DIR
from src.data.football_data_co_uk_scraper import FootballDataCoUkScraper


def test_scrape(mocker):
    """Test scrape()."""
    raw_data_folder_path = Path('.data')
    scraper = FootballDataCoUkScraper(
        odds_href='germanym.php',
        raw_data_folder_path=raw_data_folder_path,
        competition='Bundesliga 1',
    )
    mock_sleep = mocker.patch('src.data.football_data_co_uk_scraper.sleep')
    mock_requests_get = mocker.patch(
        'src.data.football_data_co_uk_scraper.requests.get'
    )
    mock_requests_get.side_effect = [
        mocker.Mock(text='notes blah blah'),
        mocker.Mock(
            text=open(
                Path(
                    TEST_DATA_DIR,
                    'test_football_data_co_uk_scraper',
                    'odds_page',
                )
            ).read()
        ),
        mocker.Mock(
            text=open(
                Path(TEST_DATA_DIR, 'test_football_data_co_uk_scraper', '1')
            ).read()
        ),
        mocker.Mock(
            text=open(
                Path(TEST_DATA_DIR, 'test_football_data_co_uk_scraper', '2')
            ).read()
        ),
        mocker.Mock(
            text=open(
                Path(TEST_DATA_DIR, 'test_football_data_co_uk_scraper', '3')
            ).read()
        ),
    ]

    scraper.scrape()

    assert mock_sleep.call_count == 4
    assert len(list(raw_data_folder_path.iterdir())) == 4

    shutil.rmtree(raw_data_folder_path)
