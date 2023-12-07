"""Command line interface for FootballDataCoUk tasks."""
from pathlib import Path
from typing import Annotated

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from data.football_data_co_uk_cleaner import FootballDataCoUkCleaner
from data.football_data_co_uk_processor import FootballDataCoUkProcessor
from settings import (
    RAW_DATA_DIR,
    REQUEST_HEADERS,
    INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
)
from src.data.football_data_co_uk_scraper import FootballDataCoUkScraper

football_data_co_uk_app = typer.Typer()


@football_data_co_uk_app.command(help='Scrape football data.')
def scrape(
    odds_href: Annotated[
        str,
        typer.Option(
            help='The href of the odds data page to scrape.',
            prompt='Odds href',
            show_default=True,
            prompt_required=True,
        ),
    ] = '/germanym.php',
    competition_name: Annotated[
        str,
        typer.Option(
            help='The name of the competition to scrape. This is the string'
            'that is used next to the csv file name on the website.',
            prompt='Competition name',
            show_default=True,
            prompt_required=True,
        ),
    ] = 'Bundesliga 1',
):
    scraper = FootballDataCoUkScraper(
        odds_href=odds_href,
        competition=competition_name,
        raw_data_folder_path=Path(RAW_DATA_DIR),
        request_headers=REQUEST_HEADERS,
    )
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        transient=True,
    ) as progress:
        progress.add_task(description='Scraping...', total=None)
        scraper.scrape()


@football_data_co_uk_app.command(help='Clean scraped football data.')
def clean(
    competition_name: Annotated[
        str,
        typer.Option(
            help='The name of the competition that was used during crawling.',
            prompt='Competition name',
            show_default=True,
            prompt_required=True,
        ),
    ] = 'Bundesliga 1',
):
    cleaner = FootballDataCoUkCleaner(
        raw_data_folder_path=Path(RAW_DATA_DIR),
        cleaned_data_folder_path=Path(INTERIM_DATA_DIR),
        competition=competition_name,
    )
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        transient=True,
    ) as progress:
        progress.add_task(description='Cleaning...', total=None)
        cleaner.clean()


@football_data_co_uk_app.command(help='Process cleaned football data.')
def process():
    processor = FootballDataCoUkProcessor(
        cleaned_data_file_path=Path(INTERIM_DATA_DIR, 'bundesliga_1_odds.csv'),
        processed_data_folder_path=Path(PROCESSED_DATA_DIR),
    )
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        transient=True,
    ) as progress:
        progress.add_task(description='Processing...', total=None)
        processor.process()
