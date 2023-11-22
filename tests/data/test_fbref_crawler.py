"""Tests for the FbrefCrawler class."""
from pathlib import Path

from settings import TEST_DATA_DIR
from src.data.fbref_crawler import FbrefCrawler


def test_crawl(mocker, tmpdir, requests_mock):
    """Test crawl()."""
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
