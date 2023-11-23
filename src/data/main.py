"""Main entrypoint for data collection, cleaning, and processing source code."""

from pathlib import Path

from src.data.fbref_cleaner import FbrefCleaner
from src.data.fbref_processor import FbrefProcessor
from src.data.football_data_co_uk_scraper import FootballDataCoUkScraper
from src.data.fbref_crawler import FbrefCrawler
from src.data.fbref_scraper import FbrefScraper
from settings import (
    RAW_DATA_DIR,
    REQUEST_HEADERS,
    INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
)


def crawl_fbref() -> None:
    """Crawl FBref."""
    fbref_crawler = FbrefCrawler(
        competition_stats_href='/en/comps/20/Bundesliga-Stats',
        html_folder_path=Path(RAW_DATA_DIR, 'fbref_pages', 'bundesliga'),
        seasons_to_crawl=7,
        seconds_to_sleep_between_requests=5,
        request_headers=REQUEST_HEADERS,
    )
    fbref_crawler.crawl()


def scrape_fbref() -> None:
    """Scrape crawlerd FBref pages."""
    fbref_scraper = FbrefScraper(
        html_folder_path=Path(RAW_DATA_DIR, 'fbref_pages', 'bundesliga'),
        raw_data_folder_path=Path(RAW_DATA_DIR),
        competition='bundesliga',
    )
    fbref_scraper.scrape()


def clean_fbref_data() -> None:
    """Clean scraped FBref data."""
    fbref_cleaner = FbrefCleaner(
        raw_data_file_path=Path(RAW_DATA_DIR, 'bundesliga_matches.csv'),
        cleaned_data_folder_path=INTERIM_DATA_DIR,
        competition='Bundesliga',
    )
    fbref_cleaner.clean()


def process_fbref_data() -> None:
    """Process cleaned FBref data."""
    processor = FbrefProcessor(
        cleaned_data_file_path=Path(INTERIM_DATA_DIR, 'bundesliga_matches.csv'),
        processed_data_folder_path=PROCESSED_DATA_DIR,
    )
    processor.process()


def scrape_football_data_co_uk() -> None:
    """Scrape FootballDataCoUk."""
    football_data_co_uk_crawler = FootballDataCoUkScraper(
        odds_href='germanym.php',
        competition='Bundesliga 1',
        raw_data_folder_path=Path(RAW_DATA_DIR),
        seconds_to_sleep_between_requests=5,
        request_headers=REQUEST_HEADERS,
    )
    football_data_co_uk_crawler.scrape()


def main() -> None:
    """Run all data collection, cleaning, and processing."""
    crawl_fbref()
    scrape_fbref()
    clean_fbref_data()
    process_fbref_data()

    scrape_football_data_co_uk()


if __name__ == '__main__':
    main()
