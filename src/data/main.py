"""Main entrypoint for data collection, cleaning, and processing source code."""

from pathlib import Path

from settings import RAW_DATA_DIR, REQUEST_HEADERS
from src.data.fbref_crawler import FbrefCrawler


def main() -> None:
    """Run all data collection, cleaning, and processing."""
    crawler = FbrefCrawler(
        base_url='https://fbref.com',
        stats_href='/en/comps/20/Bundesliga-Stats',
        pages_path=Path(RAW_DATA_DIR, 'fbref_pages', 'bundesliga'),
        seasons_to_crawl=7,
        seconds_to_sleep=10,
        request_headers=REQUEST_HEADERS,
    )
    crawler.crawl()


if __name__ == '__main__':
    main()
