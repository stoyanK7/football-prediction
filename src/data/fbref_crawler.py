"""
Contains the class that is responsible for crawling
https://fbref.com.
"""

from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup
from requests import Response
from tqdm import tqdm


class FbrefCrawler:

    """
    Crawls https://fbref.com and saves the HTML pages so that they can be
    parsed later.
    """

    def __init__(
        self,
        base_url: str,
        stats_href: str,
        pages_path: Path,
        seasons_to_crawl: int,
        seconds_to_sleep: int,
        request_headers: dict[str, str] = None,
    ) -> None:
        """
        Initialize the crawler.

        :param base_url: The base url of the website.
        :param stats_href: The href of the stats page. This can be swapped out
            for other leagues.
        :param pages_path: The path where the pages should be saved.
        :param seasons_to_crawl: The number of seasons to crawl from the
            stats page.
        :param seconds_to_sleep: The number of seconds to sleep
            between requests.
        :param request_headers: The headers to use for the requests.
        """
        self.base_url = base_url
        self.stats_href = stats_href
        self.pages_path = pages_path
        if not self.pages_path.exists():
            self.pages_path.mkdir(parents=True)
            tqdm.write(f'Created {self.pages_path}')
        self.seasons_to_crawl = seasons_to_crawl
        self.seconds_to_sleep = seconds_to_sleep
        self.request_headers = request_headers

    def crawl(self) -> None:
        """Crawls the website and saves the pages."""
        current_season_stats_href = self.stats_href

        for season_no in tqdm(
            range(self.seasons_to_crawl), desc='Seasons crawled'
        ):
            stats_page_html = self.save_page(current_season_stats_href)
            stats_page_soup = BeautifulSoup(
                stats_page_html.text, features='html.parser'
            )
            teams_hrefs = self.get_teams_hrefs(stats_page_soup)

            for team_href in teams_hrefs:
                self.crawl_team(team_href)

            href_to_previous_season = self.get_href_to_previous_season(
                stats_page_soup
            )
            current_season_stats_href = href_to_previous_season
            sleep(self.seconds_to_sleep)

    @staticmethod
    def get_href_to_previous_season(stats_page_soup: BeautifulSoup) -> str:
        """
        Get the href to the previous season from the stats page. Find the
        button that contains the text "Previous Season" and get the href
        from it.

        :param stats_page_soup: The soup of the stats page.
        :return: The href to the previous season.
        """
        return stats_page_soup.select_one(
            'div.prevnext a:-soup-contains("Previous Season")'
        )['href']

    @staticmethod
    def get_teams_hrefs(stats_page_soup: BeautifulSoup) -> list[str]:
        """
        Get the hrefs to the teams from the stats page.

        :param stats_page_soup: The soup of the stats page.
        :return: A list of hrefs to the teams.
        """
        standings_table = stats_page_soup.select_one('table.stats_table')
        teams_anchors = standings_table.select('tr td:nth-of-type(1) a')
        teams_hrefs = [anchor['href'] for anchor in teams_anchors]
        return teams_hrefs

    def crawl_team(self, team_href: str) -> None:
        """
        Crawl the team from the given href. Save all categories.

        :param team_href: The href to the team.
        """
        team_page_html = self.save_page(team_href)
        team_page_soup = BeautifulSoup(
            team_page_html.text, features='html.parser'
        )

        self.save_page(self.get_category_href(team_page_soup, 'shooting'))
        self.save_page(self.get_category_href(team_page_soup, 'keeper'))
        self.save_page(self.get_category_href(team_page_soup, 'passing'))
        self.save_page(self.get_category_href(team_page_soup, 'passing_types'))
        self.save_page(self.get_category_href(team_page_soup, 'gca'))
        self.save_page(self.get_category_href(team_page_soup, 'defense'))
        self.save_page(self.get_category_href(team_page_soup, 'possession'))
        self.save_page(self.get_category_href(team_page_soup, 'misc'))

    def save_page(self, href: str) -> Response:
        """
        Save the page from the given href.

        :param href: href to save the page from.
        :return: Response from the request.
        """
        url = self.build_url(href)
        html = self.get_html(url)

        file_name = f'{self.convert_to_valid_file_name(url)}.html'
        self.save_file(file_name, html.text)

        sleep(self.seconds_to_sleep)
        return html

    @staticmethod
    def convert_to_valid_file_name(name_to_convert: str) -> str:
        """
        Convert the given name to a valid file name. For example, file
        names are not allowed to contain slashes (/) or colons (:).

        :param name_to_convert: The name to convert.
        :return: The valid file name.
        """
        return name_to_convert.replace('/', '(').replace(':', '_')

    def save_file(self, file_name: str, text: str) -> None:
        """
        Save the given text to the given file name.

        :param file_name: Name of the file to save the text to.
        :param text: The text to save.
        """
        file_path = Path(self.pages_path, file_name)
        with open(file_path, 'w') as f:
            f.write(text)
            tqdm.write(f'Saved {file_path}')

    def get_html(self, url: str) -> Response:
        """
        Get the HTML from the given url.

        :param url: The url to get the HTML from.
        :return: The HTML.
        """
        html = requests.get(url, headers=self.request_headers)
        tqdm.write(f'Got HTML from {url}')
        return html

    def build_url(self, href: str) -> str:
        """
        Build the url from the href. Append the href to the base url.

        :param href: Href to build the url from.
        :return: The url.
        """
        url = f'{self.base_url}{href}'
        return url

    @staticmethod
    def get_category_href(soup: BeautifulSoup, category: str) -> str:
        """
        Get the href to the category.

        :param soup: Soup to search in.
        :param category: Category to search for.
        :return: The href to the category.
        """
        category = soup.select_one(
            f'div.filter div a[href*="all_comps/{category}"]'
        )
        return category['href']
