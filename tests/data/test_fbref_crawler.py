"""Tests for the FbrefCrawler class."""
from pathlib import Path

from settings import TEST_DATA_DIR
from src.data.fbref_crawler import FbrefCrawler


def test_crawl(mocker, tmpdir):
    """Test crawl()."""
    crawler = FbrefCrawler(
        competition_stats_href='/en/comps/20/Bundesliga-Stats',
        html_folder_path=Path(tmpdir, '.pages'),
    )
    mock_sleep = mocker.patch('src.data.fbref_crawler.sleep')
    mocker_get_html = mocker.patch.object(FbrefCrawler, 'get_html')
    test_files = [
        'stats_table',
        'leverkusen_filter',
        'shooting_table',
        'goalkeeping_table',
        'passing_table',
        'passtypes_table',
        'goal_and_shot_creation_table',
        'defensive_actions_table',
        'possession_table',
        'misc_table',
    ]
    mocker_get_html.side_effect = [
        open(Path(TEST_DATA_DIR, 'test_fbref_crawler', file)).read()
        for file in test_files
    ]

    crawler.crawl()

    assert mock_sleep.call_count == len(test_files)
    assert len(list(crawler.html_folder_path.glob('*'))) == len(test_files)
