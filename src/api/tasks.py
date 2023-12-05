"""API endpoints for running background tasks."""
from pathlib import Path

from fastapi import APIRouter
from starlette.background import BackgroundTasks

from src.data.fbref_processor import FbrefProcessor
from src.data.fbref_scraper import FbrefScraper
from src.api.models import CleanModel, CrawlModel, ScrapeModel
from src.data.fbref_crawler import FbrefCrawler
from src.data.fbref_cleaner import FbrefCleaner
from settings import (
    RAW_DATA_DIR,
    INTERIM_DATA_DIR,
    REQUEST_HEADERS,
    PROCESSED_DATA_DIR,
)

router = APIRouter(prefix='/tasks')


@router.post('/crawl')
def crawl_for_data(data: CrawlModel, background_tasks: BackgroundTasks):
    """Crawl for data."""
    fbref_crawler = FbrefCrawler(
        competition_stats_href=data.competition_stats_href,
        html_folder_path=Path(RAW_DATA_DIR, 'fbref_pages', 'bundesliga'),
        seasons_to_crawl=data.seasons_to_crawl,
        seconds_to_sleep_between_requests=5,
        request_headers=REQUEST_HEADERS,
    )
    background_tasks.add_task(fbref_crawler.crawl)
    return {'logfile': FbrefCrawler.logfile}


@router.post('/scrape')
def scrape_data(data: ScrapeModel, background_tasks: BackgroundTasks):
    """Scrape crawled data."""
    fbref_scraper = FbrefScraper(
        html_folder_path=Path(RAW_DATA_DIR, 'fbref_pages', 'bundesliga'),
        raw_data_folder_path=Path(RAW_DATA_DIR),
        competition=data.competition,
    )
    background_tasks.add_task(fbref_scraper.scrape)
    return {'logfile': FbrefScraper.logfile}


@router.post('/clean')
def clean_data(data: CleanModel, background_tasks: BackgroundTasks):
    """Clean collected data."""
    fbref_cleaner = FbrefCleaner(
        raw_data_file_path=Path(RAW_DATA_DIR, 'bundesliga_matches.csv'),
        cleaned_data_folder_path=INTERIM_DATA_DIR,
        competition=data.competition,
    )
    background_tasks.add_task(fbref_cleaner.clean)
    return {'logfile': FbrefCleaner.logfile}


@router.post('/process')
def process_data(background_tasks: BackgroundTasks):
    """Process cleaned data."""
    processor = FbrefProcessor(
        cleaned_data_file_path=Path(INTERIM_DATA_DIR, 'bundesliga_matches.csv'),
        processed_data_folder_path=PROCESSED_DATA_DIR,
    )
    background_tasks.add_task(processor.process)
    return {'logfile': FbrefProcessor.logfile}
