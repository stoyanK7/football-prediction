"""Contains the class that is responsible for crawling FBref."""

from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup

from src.log import get_logger
from src.data.fbref import categories


class FbrefCrawler:

    """
    Crawls FBref and saves the HTML pages so that they
    can be scraped later.
    """

    logger_name = 'crawling'
    logger, logfile = get_logger(logger_name)

    # The base URL of the website.
    base_url: str = 'https://fbref.com'

    def __init__(
        self,
        competition_stats_href: str,
        html_folder_path: Path,
        seasons_to_crawl: int = 1,
        seconds_to_sleep_between_requests: int = 4,
        request_headers: dict[str, str] = None,
    ) -> None:
        """
        Initialize the crawler.

        :param competition_stats_href: The href of the competition statistics
            page. This page contains the standings table. It could be for any
            competition and year. For example
            '/en/comps/20/2022-2023/2022-2023-Bundesliga-Stats'.
        :param html_folder_path: The path where the pages should be saved. If
            the folder does not exist, it will be created.
        :param seasons_to_crawl: The number of seasons to crawl back including
            the current season. For example if the current season is 2021-2022
            and seasons_to_crawl is 3, then the seasons 2021-2022, 2020-2021
            and 2019-2020 will be crawled.
        :param seconds_to_sleep_between_requests: The number of seconds to sleep
            between requests to FBref. This is to avoid getting blocked by
            the server.
        :param request_headers: The headers to use for the requests. It is
            recommended to pass a User-Agent header.
        """
        self.competition_stats_href = competition_stats_href
        self.html_folder_path = html_folder_path
        if not self.html_folder_path.exists():
            self.html_folder_path.mkdir(parents=True)
            FbrefCrawler.logger.info(f'Created folder {self.html_folder_path}')

        self.seasons_to_crawl = seasons_to_crawl
        self.seconds_to_sleep = seconds_to_sleep_between_requests
        self.request_headers = request_headers

    def crawl(self) -> None:
        """
        Crawl each season and each team in the competition. For each team,
        crawl the team page and the page for each category. Then crawl the
        previous season.
        """
        current_season_stats_href = self.competition_stats_href

        for _ in range(self.seasons_to_crawl):
            stats_page_html = self.save_page(current_season_stats_href)
            stats_page_soup = BeautifulSoup(
                stats_page_html, features='html.parser'
            )
            teams_hrefs = self.get_teams_hrefs(stats_page_soup)

            for team_href in teams_hrefs:
                self.crawl_team(team_href)

            # Point to the previous season for the next iteration.
            current_season_stats_href = self.get_href_to_previous_season(
                stats_page_soup
            )

        FbrefCrawler.logger.info('DONE')

    def save_page(self, href: str) -> str:
        """
        Save the page from the given href. Build the url from the href and
        make a request to it. Save the response to a file.

        :param href: href to save the page from.
        :return: Response from the request.
        """
        url = self.build_url(href)
        html = self.get_html(url)

        file_name = f'{self.convert_to_valid_file_name(url)}.html'
        self.save_file(file_name, html)

        sleep(self.seconds_to_sleep)
        return html

    @staticmethod
    def get_teams_hrefs(stats_page_soup: BeautifulSoup) -> list[str]:
        """
        Get the hrefs to the teams from the stats page.

        :param stats_page_soup: The soup of the stats page.
        :return: A list of hrefs to the teams stats pages.
        """
        # Get the standings table with points, ranking, etc.
        standings_table = stats_page_soup.select_one('table.stats_table')
        teams_anchors = standings_table.select('tr td:nth-of-type(1) a')
        teams_hrefs = [anchor['href'] for anchor in teams_anchors]
        return teams_hrefs

    def crawl_team(self, team_href: str) -> None:
        """
        Crawl the given team. Save the team page and the pages for the
        categories.

        :param team_href: The href to the team.
        """
        team_page_html = self.save_page(team_href)
        team_page_soup = BeautifulSoup(team_page_html, features='html.parser')

        for category in categories:
            self.save_page(self.get_category_href(team_page_soup, category))

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
        file_path = Path(self.html_folder_path, file_name)
        with open(file_path, 'w') as f:
            f.write(text)
            FbrefCrawler.logger.info(f'Saved {file_path}')

    def get_html(self, url: str) -> str:
        """
        Get the HTML from the given url.

        :param url: The url to get the HTML from.
        :return: The HTML page as a string.
        """
        html = requests.get(url, headers=self.request_headers)
        FbrefCrawler.logger.info(f'Made a request to {url}')
        return html.text

    def build_url(self, href: str) -> str:
        """
        Build the url from the href. Append the href to the base url.

        :param href: Href to build the url from.
        :return: The url.
        """
        href = href.lstrip('/')
        url = f'{self.base_url}/{href}'
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
