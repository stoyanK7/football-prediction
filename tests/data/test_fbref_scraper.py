"""Tests for the FbrefScraper class."""
from pathlib import Path

from settings import TEST_DATA_DIR
from src.data.fbref_scraper import FbrefScraper


def test_scrape(tmpdir):
    """Test scrape()."""
    raw_data_folder_path = Path(tmpdir, '.data')
    scraper = FbrefScraper(
        html_folder_path=Path(TEST_DATA_DIR, 'test_fbref_scraper'),
        raw_data_folder_path=raw_data_folder_path,
        competition='Bundesliga',
    )

    scraper.scrape()

    output_file = Path(
        raw_data_folder_path, 'bundesliga_matches.csv'
    ).read_text()
    expected_output_file = Path(
        TEST_DATA_DIR, 'test_fbref_scraper', 'bundesliga_matches.csv'
    ).read_text()
    assert ',Team,' in output_file
    assert output_file == expected_output_file


def test_get_latest_season():
    """Test get_latest_season()."""
    scraper = FbrefScraper(
        html_folder_path=Path(TEST_DATA_DIR, 'test_fbref_scraper'),
        raw_data_folder_path=Path(),
        competition='Bundesliga',
    )

    latest_season = scraper.get_latest_season(
        [
            'https_((fbref.com(en(squads(054efa67(2020-2021(matchlogs(all_comps(shooting(Bayern-Munich-Match-Logs-All-Competitions.html',
            'https_((fbref.com(en(squads(054efa67(2019-2020(matchlogs(all_comps(keeper(Bayern-Munich-Match-Logs-All-Competitions.html',
            'https_((fbref.com(en(squads(054efa67(2019-2020(matchlogs(all_comps(passing(Bayern-Munich-Match-Logs-All-Competitions.html',
            'https_((fbref.com(en(squads(054efa67(2017-2018(matchlogs(all_comps(passing_types(Bayern-Munich-Match-Logs-All-Competitions.html',
            'https_((fbref.com(en(squads(054efa67(2022-2023(matchlogs(all_comps(gca(Bayern-Munich-Match-Logs-All-Competitions.html',
            'https_((fbref.com(en(squads(054efa67(2018-2019(matchlogs(all_comps(defense(Bayern-Munich-Match-Logs-All-Competitions.html',
            'https_((fbref.com(en(squads(054efa67(2024-2025(matchlogs(all_comps(possession(Bayern-Munich-Match-Logs-All-Competitions.html',
            'https_((fbref.com(en(squads(054efa67(2023-2024(matchlogs(all_comps(misc(Bayern-Munich-Match-Logs-All-Competitions.html',
        ]
    )

    assert latest_season == '2024-2025'
