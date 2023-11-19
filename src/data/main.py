"""Main entrypoint for data collection, cleaning, and processing source code."""

from pathlib import Path

from src.data.fbref_crawler import FbrefCrawler
from src.data.fbref_scraper import FbrefScraper
from settings import RAW_DATA_DIR, INTERIM_DATA_DIR, REQUEST_HEADERS


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

    scraper = FbrefScraper(
        pages_path=Path(RAW_DATA_DIR, 'fbref_pages', 'bundesliga'),
        interim_data_path=Path(INTERIM_DATA_DIR),
    )
    scraper.scrape()


if __name__ == '__main__':
    main()
