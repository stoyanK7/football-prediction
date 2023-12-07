"""Tests for the FbrefScraper class."""
from pathlib import Path

import pytest

from settings import TEST_DATA_DIR
from src.data.fbref_scraper import FbrefScraper


def test_scrape(tmpdir):
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


@pytest.mark.parametrize(
    'file_name,expected_team_name',
    [
        (
            '_sl4sh_en_sl4sh_squads_sl4sh_4eaa11d7_sl4sh_2021-2022_sl4sh_Wolfsburg-Stats.html',
            'Wolfsburg',
        ),
        (
            '_sl4sh_en_sl4sh_squads_sl4sh_4eaa11d7_sl4sh_2021-2022_sl4sh_Hannover-96-Stats.html',
            'Hannover 96',
        ),
    ],
)
def test_get_team_name(file_name, expected_team_name):
    scraper = FbrefScraper(
        html_folder_path=Path(TEST_DATA_DIR, 'test_fbref_scraper'),
        raw_data_folder_path=Path(),
        competition='Bundesliga',
    )

    team_name = scraper.get_team_name(file_name)

    assert team_name == expected_team_name
