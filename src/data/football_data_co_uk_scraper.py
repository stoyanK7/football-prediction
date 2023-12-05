"""Contains the class that is responsible for scraping FootballDataCoUk."""
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup

from src.log import get_logger


class FootballDataCoUkScraper:

    """Scrapes odds data from FootballDataCoUk."""

    logger_name = 'scraping'
    logger, logfile = get_logger(logger_name)

    base_url = 'https://www.football-data.co.uk'
    notes_url = f'{base_url}/notes.txt'

    def __init__(
        self,
        odds_href: str,
        competition: str,
        raw_data_folder_path: Path,
        seconds_to_sleep_between_requests: int = 4,
        request_headers: dict[str, str] = None,
    ) -> None:
        """
        Initialize the scraper.

        :param odds_href: The href of the odds data page to scrape.
        :param competition: The name of the competition to scrape. This is the
            string that is used next to the csv file name on the website.
        :param raw_data_folder_path:  The path to the raw data directory to save the
            scraped data to.
        :param request_headers: The headers to use for the requests.
        :param seconds_to_sleep_between_requests: The number of seconds to sleep
            between requests to FootballDataCoUk. This is to avoid getting
            blocked by the server.
        """
        self.odds_href = odds_href
        self.competition = competition
        self.raw_data_folder_path = raw_data_folder_path
        if not self.raw_data_folder_path.exists():
            self.raw_data_folder_path.mkdir(parents=True)
            FootballDataCoUkScraper.logger.info(
                f'Created folder {self.raw_data_folder_path}'
            )
        self.seconds_to_sleep = seconds_to_sleep_between_requests
        self.request_headers = request_headers

    def scrape(self) -> None:
        """Scrape the odds data from the provided page."""
        self.save_notes()
        sleep(self.seconds_to_sleep)
        self.save_odds()
        FootballDataCoUkScraper.logger.info('DONE')

    def save_notes(self) -> None:
        """Save the notes from the website."""
        notes_path = Path(self.raw_data_folder_path, 'notes.txt')
        # If the notes file already exists, don't save it again.
        if notes_path.is_file():
            return
        notes_response = requests.get(self.notes_url)
        notes = notes_response.text
        with open(notes_path, 'w') as f:
            f.write(notes)
            FootballDataCoUkScraper.logger.info(f'Saved {notes_path}')

    def save_odds(self) -> None:
        """Save the odds data from the provided page."""
        csv_hrefs = self.get_csv_hrefs()

        for href in csv_hrefs:
            href = href.lstrip('/')
            csv_url = f'{self.base_url}/{href}'
            # An example of href is '/mmz4281/2122/D1.csv'.
            year = href.split('/')[-2]
            csv_response = requests.get(csv_url, headers=self.request_headers)
            csv_content = csv_response.text

            file_name = (
                f'{self.competition.lower().replace(" ", "_")}_odds_{year}.csv'
            )
            odds_path = Path(self.raw_data_folder_path, file_name)
            with open(odds_path, 'w') as f:
                f.write(csv_content)
                FootballDataCoUkScraper.logger.info(f'Saved {odds_path}')

            sleep(self.seconds_to_sleep)

    def get_csv_hrefs(self) -> list[BeautifulSoup]:
        """
        Get the hrefs to the csv files containing the odds data.

        :return: List of hrefs to the csv files containing the odds data.
        """
        self.odds_href = self.odds_href.lstrip('/')
        odds_url = f'{self.base_url}/{self.odds_href}'
        response = requests.get(odds_url, headers=self.request_headers)
        soup = BeautifulSoup(response.text, features='html.parser')
        csv_anchors = soup.find_all('a', href=True, string=self.competition)
        return [anchor['href'] for anchor in csv_anchors]
