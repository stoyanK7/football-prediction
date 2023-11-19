"""
Contains the class that is responsible for scraping
https://football-data.co.uk.
"""
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class FootballDataCoUkScraper:

    """Scrapes odds data from https://football-data.co.uk."""

    base_url = 'https://football-data.co.uk'
    notes_url = f'{base_url}/notes.txt'

    def __init__(
        self,
        odds_href: str,
        competition: str,
        raw_data_path: Path,
        request_headers: dict[str, str] = None,
        seconds_to_sleep: int = 5,
    ) -> None:
        """
        Initialize the scraper.

        :param odds_href: The href of the odds data page to scrape.
        :param competition: The name of the competition to scrape.
        :param raw_data_path:  The path to the raw data directory to save the
            scraped data to.
        :param request_headers: The headers to use for the requests.
        :param seconds_to_sleep: The number of seconds to sleep
            between requests.
        """
        self.odds_href = odds_href
        self.competition = competition
        self.raw_data_path = raw_data_path
        self.request_headers = request_headers
        self.seconds_to_sleep = seconds_to_sleep

    def scrape(self) -> None:
        """Scrape the odds data from the provided page."""
        notes_response = requests.get(self.notes_url)
        notes = notes_response.text

        notes_path = Path(self.raw_data_path, 'notes.txt')
        with open(notes_path, 'w') as f:
            f.write(notes)
            tqdm.write(f'Saved {notes_path}')

        odds_url = f'{self.base_url}/{self.odds_href}'
        response = requests.get(odds_url, headers=self.request_headers)
        soup = BeautifulSoup(response.text, features='html.parser')

        csv_anchors = soup.find_all('a', href=True, string=self.competition)

        for anchor in tqdm(csv_anchors):
            href = anchor['href']
            csv_url = f'{self.base_url}/{href}'
            year = href.split('/')[-2]
            csv_response = requests.get(csv_url, headers=self.request_headers)
            csv_content = csv_response.content

            odds_path = Path(
                self.raw_data_path,
                f'{self.competition.lower().replace(" ", "_")}_odds_{year}.csv',
            )
            with open(odds_path, 'wb') as f:
                f.write(csv_content)
                tqdm.write(f'Saved {odds_path}')

            sleep(self.seconds_to_sleep)
