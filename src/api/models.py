"""Pydantic models for the API."""
from pydantic import BaseModel


class CrawlModel(BaseModel):

    """Request body expected for the crawling task."""

    competition_stats_href: str
    seasons_to_crawl: int


class ScrapeModel(BaseModel):

    """Request body expected for the scraping task."""

    competition: str


class CleanModel(BaseModel):

    """Request body expected for the cleaning task."""

    competition: str
