"""Command line interface for the project."""
from pathlib import Path
from typing import Annotated

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from src.data.fbref_processor import FbrefProcessor
from src.data.fbref_scraper import FbrefScraper
from src.data.fbref_cleaner import FbrefCleaner
from settings import (
    RAW_DATA_DIR,
    REQUEST_HEADERS,
    INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
)
from src.data.fbref_crawler import FbrefCrawler

app = typer.Typer()


@app.command(help='Crawl football data.')
def crawl(
    competition_name: Annotated[
        str,
        typer.Option(
            help='The name of the competition.',
            prompt='Competition name',
            show_default=True,
            prompt_required=True,
        ),
    ] = 'Bundesliga',
    competition_stats_href: Annotated[
        str,
        typer.Option(
            help='The href of the competition statistics page. This page'
            'contains the standings table. It could be for any competition'
            'and year.',
            prompt='Competition statistics href',
            show_default=True,
            prompt_required=True,
        ),
    ] = '/en/comps/20/Bundesliga-Stats',
    seasons_to_crawl: Annotated[
        int,
        typer.Option(
            help='The number of seasons to crawl back including the current'
            'season.',
            prompt='Seasons to crawl',
            show_default=True,
            prompt_required=True,
        ),
    ] = 1,
):
    fbref_crawler = FbrefCrawler(
        competition_stats_href=competition_stats_href,
        html_folder_path=Path(RAW_DATA_DIR, 'fbref_pages', competition_name),
        seasons_to_crawl=seasons_to_crawl,
        seconds_to_sleep_between_requests=5,
        request_headers=REQUEST_HEADERS,
    )
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        transient=True,
    ) as progress:
        progress.add_task(description='Crawling...', total=None)
        fbref_crawler.crawl()


@app.command(help='Recrawl errored pages.')
def recrawl(
    competition_name: Annotated[
        str,
        typer.Option(
            help='The name of the competition.',
            prompt='Competition name',
            show_default=True,
            prompt_required=True,
        ),
    ] = 'Bundesliga',
):
    fbref_crawler = FbrefCrawler(
        competition_stats_href='',
        html_folder_path=Path(RAW_DATA_DIR, 'fbref_pages', competition_name),
        seasons_to_crawl=0,
        seconds_to_sleep_between_requests=5,
        request_headers=REQUEST_HEADERS,
    )
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        transient=True,
    ) as progress:
        progress.add_task(description='Recrawling...', total=None)
        fbref_crawler.recrawl_errored_pages()


@app.command(help='Scrape football data.')
def scrape(
    competition_name: Annotated[
        str,
        typer.Option(
            help='The name of the competition that was used during crawling.',
            prompt='Competition name',
            show_default=True,
            prompt_required=True,
        ),
    ] = 'Bundesliga',
):
    fbref_scraper = FbrefScraper(
        html_folder_path=Path(RAW_DATA_DIR, 'fbref_pages', competition_name),
        raw_data_folder_path=Path(RAW_DATA_DIR),
        competition=competition_name,
    )
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        transient=True,
    ) as progress:
        progress.add_task(description='Scraping...', total=None)
        fbref_scraper.scrape()


@app.command(help='Clean scraped football data.')
def clean(
    competition_name: Annotated[
        str,
        typer.Option(
            help='The name of the competition that was used during crawling.',
            prompt='Competition name',
            show_default=True,
            prompt_required=True,
        ),
    ] = 'Bundesliga',
):
    fbref_cleaner = FbrefCleaner(
        raw_data_file_path=Path(
            RAW_DATA_DIR,
            f'{competition_name.lower().replace(' ', '_')}_matches.csv',
        ),
        cleaned_data_folder_path=INTERIM_DATA_DIR,
        competition='Bundesliga',
    )
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        transient=True,
    ) as progress:
        progress.add_task(description='Cleaning...', total=None)
        fbref_cleaner.clean()


@app.command(help='Process cleaned football data.')
def process(
    competition_name: Annotated[
        str,
        typer.Option(
            help='The name of the competition that was used during crawling.',
            prompt='Competition name',
            show_default=True,
            prompt_required=True,
        ),
    ] = 'Bundesliga',
):
    processor = FbrefProcessor(
        cleaned_data_file_path=Path(
            INTERIM_DATA_DIR,
            f'{competition_name.lower().replace(' ', '_')}_matches.csv',
        ),
        processed_data_folder_path=PROCESSED_DATA_DIR,
    )
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        transient=True,
    ) as progress:
        progress.add_task(description='Processing...', total=None)
        processor.process()


if __name__ == '__main__':
    app()
