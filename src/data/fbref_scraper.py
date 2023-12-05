"""Contains the class that is responsible for scraping FBref."""
import re
from io import StringIO
from os import listdir
from pathlib import Path

import pandas as pd

from src.log import get_logger
from src.data.fbref import categories


class FbrefScraper:

    """
    Scrapes data off FBref pages that have been crawled by
    :class:`FbrefCrawler`.
    """

    logger_name = 'scraping'
    logger, logfile = get_logger(logger_name)

    def __init__(
        self,
        html_folder_path: Path,
        raw_data_folder_path: Path,
        competition: str,
    ) -> None:
        """
        Initialize the scraper.

        :param html_folder_path: The path where the pages have been saved.
        :param raw_data_folder_path: The path tot the folder where the raw data
            will be saved.
        :param competition: The name of the competition. Used for the name of
            the file that will be saved.
        """
        self.html_folder_path = html_folder_path
        self.raw_data_folder_path = raw_data_folder_path
        if not self.raw_data_folder_path.exists():
            self.raw_data_folder_path.mkdir(parents=True)
            FbrefScraper.logger.info(
                f'Created folder {self.raw_data_folder_path}'
            )

        self.competition = competition.lower().replace(' ', '_')
        self.html_pages = self.get_html_pages()
        self.latest_season = self.get_latest_season(self.html_pages)

    def scrape(self) -> None:
        """Scrape the data off the saved pages."""
        teams_stats_pages_files = self.get_teams_stats_pages_files()

        competition_matches_dfs = []

        for team_stats_page_file in teams_stats_pages_files:
            team_df = self.get_team_matches_df(team_stats_page_file)
            competition_matches_dfs.append(team_df)

        self.save_dataframe(pd.concat(competition_matches_dfs))
        FbrefScraper.logger.info('DONE')

    def get_html_pages(self) -> list[str]:
        """
        Get a list of all pages that have been crawled by :class:`FbrefCrawler`.

        :return: A list of files.
        """
        pages = listdir(self.html_folder_path)
        FbrefScraper.logger.info(f'Found {len(pages)} pages')
        return pages

    def get_teams_stats_pages_files(self) -> list[str]:
        """
        Get a list of all teams stats pages. This excludes the Bundesliga stats
        as it does not contain any team stats.

        :return: A list of teams stats pages.
        """
        # Remove the Bundesliga stats page as it doesn't contain any team stats.
        stats_page_pattern = re.compile(
            r'^((?!Bundesliga-Stats\.html).)*-Stats\.html$'
        )
        teams_stats_pages = list(
            filter(stats_page_pattern.match, self.html_pages)
        )
        return teams_stats_pages

    def get_team_matches_df(self, team_stats_page_file: str) -> pd.DataFrame:
        """
        Get the matches dataframe for a given team for a given season.

        :param team_stats_page_file: The name of the team stats page file.
        :return: A dataframe containing the matches and categories of stats.
        """
        FbrefScraper.logger.info(f'Scraping {team_stats_page_file}')
        team_name = self.get_team_name(team_stats_page_file)
        team_stats_file_path = Path(self.html_folder_path, team_stats_page_file)
        # Wrap in StringIO to prevent warnings.
        team_stats_file_contents = StringIO(team_stats_file_path.read_text())
        # Grab the 'Scores & Fixtures' table as a base.
        team_df = pd.read_html(
            team_stats_file_contents, match='Scores & Fixtures'
        )[0]
        # Add team column because the table doesn't have it.
        team_df['Team'] = team_name
        # Iterate trough each category and merge it.
        for category_href, category_caption in categories.items():
            category_df = self.get_category_dataframe(
                team_stats_page_file, category_href, category_caption
            )
            team_df = team_df.merge(category_df, on=['Date', 'Time'])
        return team_df

    @staticmethod
    def get_team_name(team_stats_page_file: str) -> str:
        """
        Get the team name from the team stats page file name.

        :param team_stats_page_file: The team stats page file name.
        :return: The team name.
        """
        # An example team stats page file name is:
        # https_((fbref.com(en(squads(60b5e41f(2018-2019(Hannover-96-Stats.html
        return (
            team_stats_page_file.split('(')[-1]  # Hannover-96-Stats.html
            .replace('-Stats', '')  # Hannover-96.html
            .replace('-', ' ')  # Hannover 96.html
            .replace('.html', '')  # Hannover 96
            .strip()  # Just in case.
        )

    def get_category_dataframe(
        self,
        team_stats_page_file: str,
        category_href: str,
        category_caption: str,
    ) -> pd.DataFrame:
        """
        Get the stats dataframe for a given category (shooting, for instance).

        :param team_stats_page_file: The team stats page file name.
        :param category_href: The href for the category.
        :param category_caption: The caption for the category.
        :return: A dataframe containing the stats.
        """
        # An example team stats page file name is:
        # https_((fbref.com(en(squads(60b5e41f(2018-2019(Hannover-96-Stats
        link_without_team = '('.join(team_stats_page_file.split('(')[:-1])
        # link_without_team is now:
        # https_((fbref.com(en(squads(60b5e41f(2018-2019

        # If the link_without_team doesn't end in a year-year, it means it's
        # the current season, and we need to add the current season to the link.
        if not re.search(r'\d{4}-\d{4}$', link_without_team):
            link_without_team += f'({self.latest_season}'

        link_without_team = link_without_team.replace('(', '\(')
        regex = re.compile(
            rf'^{link_without_team}\(matchlogs\(all_comps\({category_href}\(.+'
        )
        stats_page = list(filter(regex.match, self.html_pages))[0]
        # stats_page is now:
        # https_((fbref.com(en(squads(60b5e41f(2018-2019(matchlogs(all_comps(keeper(...html
        stats_file = Path(self.html_folder_path, stats_page)
        # Wrap in StringIO to prevent warnings.
        stats_file_contents = StringIO(stats_file.read_text())
        stats_df = pd.read_html(stats_file_contents, match=category_caption)[0]
        FbrefScraper.logger.info(f'Scraping {stats_file}')

        # Rename the 'For <team name>' columns as they are unique to each team.
        stats_df.rename(columns=lambda x: re.sub('^For.+', '', x), inplace=True)

        # Join the first two header rows.
        stats_df.columns = stats_df.columns.map(' '.join)
        # Keep first and second columns only strictly as 'Date' and 'Time'
        # so we can merge the dataframes later.
        stats_df.rename(
            columns={stats_df.columns[0]: 'Date', stats_df.columns[1]: 'Time'},
            inplace=True,
        )
        # Rename any other columns to include the category name, so we can
        # differentiate them later. Duplicate names exist in different
        # categories even though they are different stats.
        stats_df.columns = ['Date', 'Time'] + [
            f'{category_href} {column}'
            for column in stats_df.columns
            if column != 'Date' and column != 'Time'
        ]
        return stats_df

    def save_dataframe(self, df: pd.DataFrame) -> None:
        """
        Save the dataframe to a csv file.

        :param df: Dataframe to save.
        """
        path_to_save = Path(
            self.raw_data_folder_path, f'{self.competition}_matches.csv'
        )
        df.to_csv(path_to_save, index=False)
        FbrefScraper.logger.info(
            f'Saved {len(df)} matches to ' f'{path_to_save}_matches.csv'
        )

    @staticmethod
    def get_latest_season(html_pages: list[str]) -> str:
        """
        Get the latest season from the list of pages. This is used for the
        current season stat pages because they don't have the year in the
        filename.

        :param html_pages: The list of HTML pages.
        :return: The latest season.
        """
        return max(
            [
                re.search(r'\d{4}-\d{4}', page).group()
                for page in html_pages
                if re.search(r'\d{4}-\d{4}', page)
            ]
        )
