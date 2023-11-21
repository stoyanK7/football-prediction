"""Main entrypoint for data collection, cleaning, and processing source code."""

from pathlib import Path

from src.data.football_data_co_uk_scraper import FootballDataCoUkScraper
from src.data.fbref_crawler import FbrefCrawler
from src.data.fbref_scraper import FbrefScraper
from settings import RAW_DATA_DIR, REQUEST_HEADERS


def crawl_fbref() -> None:
    """Crawl FBref."""
    fbref_crawler = FbrefCrawler(
        competition_stats_href='/en/comps/20/Bundesliga-Stats',
        html_folder_path=Path(RAW_DATA_DIR, 'fbref_pages', 'bundesliga'),
        seasons_to_crawl=7,
        seconds_to_sleep_between_requests=10,
        request_headers=REQUEST_HEADERS,
    )
    fbref_crawler.crawl()


def scrape_fbref() -> None:
    """Scrape FBref."""
    fbref_scraper = FbrefScraper(
        html_folder_path=Path(RAW_DATA_DIR, 'fbref_pages', 'bundesliga'),
        competition='bundesliga',
    )
    fbref_scraper.scrape()


def scrape_football_data_co_uk() -> None:
    """Scrape https://football-data.co.uk."""
    football_data_co_uk_crawler = FootballDataCoUkScraper(
        odds_href='germanym.php',
        competition='Bundesliga 1',
        raw_data_path=Path(RAW_DATA_DIR),
        seconds_to_sleep=10,
    )
    football_data_co_uk_crawler.scrape()


def main() -> None:
    """Run all data collection, cleaning, and processing."""
    crawl_fbref()
    scrape_fbref()
    scrape_football_data_co_uk()


if __name__ == '__main__':
    main()
