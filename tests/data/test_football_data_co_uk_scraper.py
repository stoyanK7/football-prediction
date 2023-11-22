"""Tests for the FootballDataCoUkScraper class."""
from pathlib import Path

from settings import TEST_DATA_DIR
from src.data.football_data_co_uk_scraper import FootballDataCoUkScraper


def test_scrape(mocker, tmpdir, requests_mock):
    """Test scrape()."""
    raw_data_folder_path = Path(tmpdir, '.data')
    scraper = FootballDataCoUkScraper(
        odds_href='germanym.php',
        raw_data_folder_path=raw_data_folder_path,
        competition='Bundesliga 1',
    )
    mock_sleep = mocker.patch('src.data.football_data_co_uk_scraper.sleep')
    requests_mock.get(
        'https://www.football-data.co.uk/notes.txt', text='notes blah blah'
    )
    requests_mock.get(
        'https://www.football-data.co.uk/germanym.php',
        text=open(
            Path(TEST_DATA_DIR, 'test_football_data_co_uk_scraper', 'odds_page')
        ).read(),
    )
    requests_mock.get(
        'https://www.football-data.co.uk/mmz4281/2324/D1.csv',
        text=open(
            Path(TEST_DATA_DIR, 'test_football_data_co_uk_scraper', '1')
        ).read(),
    )
    requests_mock.get(
        'https://www.football-data.co.uk/mmz4281/2223/D1.csv',
        text=open(
            Path(TEST_DATA_DIR, 'test_football_data_co_uk_scraper', '2')
        ).read(),
    )
    requests_mock.get(
        'https://www.football-data.co.uk/mmz4281/2122/D1.csv',
        text=open(
            Path(TEST_DATA_DIR, 'test_football_data_co_uk_scraper', '3')
        ).read(),
    )

    scraper.scrape()

    assert mock_sleep.call_count == 4
    assert len(list(raw_data_folder_path.iterdir())) == 4
    assert Path(raw_data_folder_path, 'notes.txt').is_file()
    assert Path(raw_data_folder_path, 'bundesliga_1_odds_2324.csv').is_file()
    assert Path(raw_data_folder_path, 'bundesliga_1_odds_2223.csv').is_file()
    assert Path(raw_data_folder_path, 'bundesliga_1_odds_2122.csv').is_file()
    assert (
        open(Path(raw_data_folder_path, 'bundesliga_1_odds_2223.csv')).read()
        == 'odds csv file 2'
    )
