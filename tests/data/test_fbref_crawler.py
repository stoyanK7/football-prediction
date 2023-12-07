"""Tests for the FbrefCrawler class."""
from pathlib import Path

import pytest

from settings import TEST_DATA_DIR
from src.data.fbref_crawler import FbrefCrawler


def test_crawl(mocker, tmpdir, requests_mock):
    crawler = FbrefCrawler(
        competition_stats_href='/en/comps/20/Bundesliga-Stats',
        html_folder_path=Path(tmpdir, '.pages'),
    )
    mock_sleep = mocker.patch('src.data.fbref_crawler.sleep')
    requests_mock.get(
        'https://fbref.com/en/comps/20/Bundesliga-Stats',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'stats_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/Bayer-Leverkusen-Stats',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'leverkusen_filter')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/shooting/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'shooting_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/keeper/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'goalkeeping_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/passing/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'passing_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/passing_types/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'passtypes_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/gca/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(
                TEST_DATA_DIR,
                'test_fbref_crawler',
                'goal_and_shot_creation_table',
            )
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/defense/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'defensive_actions_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/possession/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'possession_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/misc/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'misc_table')
        ).read(),
    )

    crawler.crawl()

    assert mock_sleep.call_count == 10
    assert len(list(crawler.html_folder_path.glob('*'))) == 10
    assert (
        crawler.html_folder_path.glob('**/*.html').__next__().name
        == '_sl4sh_en_sl4sh_squads_sl4sh_c7a9f859_sl4sh_2023-2024_sl4sh_matchlogs_sl4sh_all_comps_sl4sh_passing_sl4sh_Bayer-Leverkusen-Match-Logs-All-Competitions.html'
    )


def test_recrawl_errored_pages(mocker, tmpdir, requests_mock):
    crawler = FbrefCrawler(
        competition_stats_href='/en/comps/20/Bundesliga-Stats',
        html_folder_path=Path(tmpdir, '.pages'),
    )
    mock_sleep = mocker.patch('src.data.fbref_crawler.sleep')
    requests_mock.get(
        'https://fbref.com/en/comps/20/Bundesliga-Stats',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'stats_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/Bayer-Leverkusen-Stats',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'leverkusen_filter')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/shooting/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'shooting_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/keeper/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'goalkeeping_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/passing/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'passing_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/passing_types/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'passtypes_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/gca/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(
                TEST_DATA_DIR,
                'test_fbref_crawler',
                'goal_and_shot_creation_table',
            )
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/defense/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'defensive_actions_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/possession/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'possession_table')
        ).read(),
    )
    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/misc/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text="""
        <html>
            <head>
                <title>Page Title</title>
            </head>
            <body>
                <h1>403 error</h1>
            </body>
        </html>
        """,
    )

    crawler.crawl()

    assert mock_sleep.call_count == 10
    assert len(list(crawler.html_folder_path.glob('**/*.html'))) == 10
    assert (
        crawler.html_folder_path.glob('**/*.html').__next__().name
        == '_sl4sh_en_sl4sh_squads_sl4sh_c7a9f859_sl4sh_2023-2024_sl4sh_matchlogs_sl4sh_all_comps_sl4sh_passing_sl4sh_Bayer-Leverkusen-Match-Logs-All-Competitions.html'
    )

    requests_mock.get(
        'https://fbref.com/en/squads/c7a9f859/2023-2024/matchlogs/all_comps/misc/Bayer-Leverkusen-Match-Logs-All-Competitions',
        text=open(
            Path(TEST_DATA_DIR, 'test_fbref_crawler', 'misc_table')
        ).read(),
    )

    crawler.recrawl_errored_pages()

    assert mock_sleep.call_count == 11


@pytest.mark.parametrize(
    'href,expected_file_name',
    [
        (
            '/en/comps/20/Bundesliga-Stats',
            '_sl4sh_en_sl4sh_comps_sl4sh_20_sl4sh_Bundesliga-Stats.html',
        ),
        (
            '/en/squads/054efa67/2022-2023/matchlogs/all_comps/passing_types/Bayern-Munich-Match-Logs-All-Competitions',
            '_sl4sh_en_sl4sh_squads_sl4sh_054efa67_sl4sh_2022-2023_sl4sh_matchlogs_sl4sh_all_comps_sl4sh_passing_types_sl4sh_Bayern-Munich-Match-Logs-All-Competitions.html',
        ),
    ],
)
def test_convert_href_to_file_name(tmpdir, href, expected_file_name):
    crawler = FbrefCrawler(
        competition_stats_href='/en/comps/20/Bundesliga-Stats',
        html_folder_path=Path(tmpdir, '.pages'),
    )

    file_name = crawler.convert_href_to_file_name(href)

    assert file_name == expected_file_name


@pytest.mark.parametrize(
    'file_name,expected_href',
    [
        (
            '_sl4sh_en_sl4sh_comps_sl4sh_20_sl4sh_Bundesliga-Stats.html',
            '/en/comps/20/Bundesliga-Stats',
        ),
        (
            '_sl4sh_en_sl4sh_squads_sl4sh_054efa67_sl4sh_2022-2023_sl4sh_matchlogs_sl4sh_all_comps_sl4sh_passing_types_sl4sh_Bayern-Munich-Match-Logs-All-Competitions.html',
            '/en/squads/054efa67/2022-2023/matchlogs/all_comps/passing_types/Bayern-Munich-Match-Logs-All-Competitions',
        ),
    ],
)
def test_convert_file_name_to_href(tmpdir, file_name, expected_href):
    crawler = FbrefCrawler(
        competition_stats_href='/en/comps/20/Bundesliga-Stats',
        html_folder_path=Path(tmpdir, '.pages'),
    )

    href = crawler.convert_file_name_to_href(file_name)

    assert href == expected_href
