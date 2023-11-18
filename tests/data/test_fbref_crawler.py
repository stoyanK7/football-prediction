"""Tests for the FbrefCrawler class."""

from pathlib import Path

from bs4 import BeautifulSoup
from requests.models import Response

from settings import TEST_DATA_DIR, REQUEST_HEADERS
from src.data.fbref_crawler import FbrefCrawler


def test_init():
    """Test __init__."""
    crawler = FbrefCrawler(
        base_url='https://fbref.com',
        stats_href='/en/comps/9/history/Premier-League-Seasons',
        pages_path=Path('.pages'),
        seasons_to_crawl=1,
        seconds_to_sleep=1,
    )

    assert crawler.base_url == 'https://fbref.com'
    assert crawler.stats_href == '/en/comps/9/history/Premier-League-Seasons'
    assert crawler.pages_path == Path('.pages')
    assert crawler.seasons_to_crawl == 1
    assert crawler.seconds_to_sleep == 1


def test_crawl(mocker):
    """Test crawl()."""
    crawler = FbrefCrawler(
        base_url='https://fbref.com',
        stats_href='/en/comps/20/Bundesliga-Stats',
        pages_path=Path('.pages'),
        seasons_to_crawl=1,
        seconds_to_sleep=10,
        request_headers=REQUEST_HEADERS,
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
        mocker.Mock(
            spec=Response,
            text=open(Path(TEST_DATA_DIR, 'test_crawl', file)).read(),
        )
        for file in test_files
    ]

    crawler.crawl()

    assert mock_sleep.call_count == 11
    assert len(list(crawler.pages_path.glob('*.html'))) == 10

    for file in crawler.pages_path.glob('*.html'):
        file.unlink()
    crawler.pages_path.rmdir()


def test_save_page(mocker):
    """Test save_page."""
    mock_get_html = mocker.patch.object(FbrefCrawler, 'get_html')
    mock_convert_to_valid_file_name = mocker.patch.object(
        FbrefCrawler, 'convert_to_valid_file_name'
    )
    mock_save_file = mocker.patch.object(FbrefCrawler, 'save_file')
    mock_sleep = mocker.patch('src.data.fbref_crawler.sleep')
    mock_response = mocker.Mock(spec=Response)
    mock_response.text = '<html></html>'
    mock_get_html.return_value = mock_response
    mock_convert_to_valid_file_name.return_value = 'valid_file_name'
    crawler = FbrefCrawler(
        'https://fbref.com',
        '/en/comps/9/history/Premier-League-Seasons',
        Path('.pages'),
        1,
        1,
    )
    href = '/en/comps/9/history/Premier-League-Seasons'

    response = crawler.save_page(href)

    mock_get_html.assert_called_once_with(
        'https://fbref.com/en/comps/9/history/Premier-League-Seasons'
    )
    mock_convert_to_valid_file_name.assert_called_once_with(
        'https://fbref.com/en/comps/9/history/Premier-League-Seasons'
    )
    mock_save_file.assert_called_once_with(
        'valid_file_name.html', '<html></html>'
    )
    mock_sleep.assert_called_once_with(1)
    assert response == mock_response


def test_convert_to_valid_file_name():
    """Test convert_to_valid_file_name."""
    crawler = FbrefCrawler(
        base_url='https://fbref.com',
        stats_href='/en/comps/9/history/Premier-League-Seasons',
        pages_path=Path('.pages'),
        seasons_to_crawl=1,
        seconds_to_sleep=1,
    )
    name_to_convert = 'test/name:to_convert'

    file_name = crawler.convert_to_valid_file_name(name_to_convert)

    assert file_name == 'test(name_to_convert'


def test_save_file(mocker):
    """Test save_file."""
    mock_open = mocker.patch('builtins.open', mocker.mock_open())
    crawler = FbrefCrawler(
        base_url='https://fbref.com',
        stats_href='/en/comps/9/history/Premier-League-Seasons',
        pages_path=Path('.pages'),
        seasons_to_crawl=1,
        seconds_to_sleep=1,
    )
    file_name = 'test_file'
    text = 'test text'

    crawler.save_file(file_name, text)

    mock_open.assert_called_once_with(Path(crawler.pages_path, file_name), 'w')
    mock_open().write.assert_called_once_with(text)


def test_get_html(mocker):
    """Test get_html."""
    mock_get = mocker.patch('requests.get')
    mock_response = mocker.Mock(spec=Response)
    mock_response.text = '<html></html>'
    mock_get.return_value = mock_response
    crawler = FbrefCrawler(
        base_url='https://fbref.com',
        stats_href='/en/comps/9/history/Premier-League-Seasons',
        pages_path=Path('.pages'),
        seasons_to_crawl=1,
        seconds_to_sleep=1,
    )

    response = crawler.get_html(
        'https://fbref.com/en/comps/9/history/Premier-League-Seasons'
    )

    mock_get.assert_called_once_with(
        'https://fbref.com/en/comps/9/history/Premier-League-Seasons',
        headers=crawler.request_headers,
    )
    assert response == mock_response


def test_build_url():
    """Test build_url."""
    crawler = FbrefCrawler(
        base_url='https://fbref.com',
        stats_href='/en/comps/9/history/Premier-League-Seasons',
        pages_path=Path('.pages'),
        seasons_to_crawl=1,
        seconds_to_sleep=1,
    )

    url = crawler.build_url('/en/comps/9/history/Premier-League-Seasons')

    assert url == 'https://fbref.com/en/comps/9/history/Premier-League-Seasons'


def test_get_category_href():
    """Test get_category_href."""
    html_doc = """
        <div class="filter">
            <h4>2017-2018 Match Log Types</h4>
            <div class=" current">
                <a>Scores & Fixtures</a>
            </div>
            <div class="">
                <a href="/en/squads/0cdc4311/2017-2018/matchlogs/all_comps/shooting/Augsburg-Match-Logs-All-Competitions">
                    Shooting
                </a>
            </div>
        </div>
    """
    soup = BeautifulSoup(html_doc, 'html.parser')
    crawler = FbrefCrawler(
        'https://fbref.com',
        '/en/comps/9/history/Premier-League-Seasons',
        Path('.pages'),
        1,
        1,
    )

    href = crawler.get_category_href(soup, 'shooting')

    assert (
        href
        == '/en/squads/0cdc4311/2017-2018/matchlogs/all_comps/shooting/Augsburg-Match-Logs-All-Competitions'
    )
