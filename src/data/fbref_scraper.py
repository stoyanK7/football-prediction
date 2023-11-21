"""Contains the class that is responsible for scraping FBref."""
import re
from io import StringIO
from os import listdir
from pathlib import Path

from tqdm import tqdm
import pandas as pd

from src.data.fbref import categories


class FbrefScraper:

    """
    Scrapes data off FBref pages that have been crawled by
    :class:`FbrefCrawler`.
    """

    def __init__(
        self, html_folder_path: Path, raw_data_path: Path, competition: str
    ) -> None:
        """
        Initialize the scraper.

        :param html_folder_path: The path where the pages have been saved.
        :param raw_data_path: The path where the raw data will be saved.
        :param competition: The competition name.
        """
        self.html_folder_path = html_folder_path
        self.raw_data_path = raw_data_path
        if not self.raw_data_path.exists():
            self.raw_data_path.mkdir(parents=True)
            tqdm.write(f'Created {self.raw_data_path}')
        self.competition = competition

    def scrape(self) -> None:
        """Scrape the data off the saved pages."""
        pages = self.get_pages()
        teams_stats_pages_files = self.get_teams_stats_pages_files(pages)

        all_matches = []

        for team_stats_page_file in tqdm(teams_stats_pages_files):
            tqdm.write(f'Scraping {team_stats_page_file}')
            team_name = self.get_team_name(team_stats_page_file)
            team_stats_file = open(
                f'{self.html_folder_path}/{team_stats_page_file}', 'r'
            )
            # Wrap in StringIO to prevent warnings.
            team_stats_file_contents = StringIO(team_stats_file.read())

            team_scores_and_fixtures_df = pd.read_html(
                team_stats_file_contents, match='Scores & Fixtures'
            )[0]
            # Add team column because the table doesn't have it.
            team_scores_and_fixtures_df['Team'] = team_name

            for stat_href, stat_caption in categories.items():
                stat_df = self.get_stats_dataframe(
                    team_stats_page_file, stat_href, stat_caption, pages
                )
                team_scores_and_fixtures_df = team_scores_and_fixtures_df.merge(
                    stat_df, on=['Date', 'Time']
                )

            all_matches.append(team_scores_and_fixtures_df)

        all_matches_df = pd.concat(all_matches)
        path_to_save = Path(
            self.raw_data_path, f'{self.competition}_matches.csv'
        )
        all_matches_df.to_csv(path_to_save, index=False)
        tqdm.write(
            f'Saved {len(all_matches_df)} matches to '
            f'{path_to_save}_matches.csv'
        )

    @staticmethod
    def get_team_name(team_stats_page_file: str) -> str:
        """
        Get the team name from the team stats page file name.

        :param team_stats_page_file: The team stats page file name.
        :return: The team name.
        """
        # An example team stats page file name is:
        # https_((fbref.com(en(squads(60b5e41f(2018-2019(Hannover-96-Stats
        return (
            team_stats_page_file.split('(')[-1]  # Hannover-96-Stats
            .replace('-Stats', '')  # Hannover-96
            .replace('-', ' ')  # Hannover 96
        )

    def get_pages(self) -> list[str]:
        """
        Get a list of all pages that have been crawled by :class:`FbrefCrawler`.

        :return: A list of files.
        """
        pages = listdir(self.html_folder_path)
        tqdm.write(f'Found {len(pages)} pages')
        return pages

    @staticmethod
    def get_teams_stats_pages_files(pages: list[str]) -> list[str]:
        """
        Get a list of all teams stats pages. This excludes the Bundesliga stats
        as it does not contain any team stats.

        :param pages: The list of saved pages.
        :return: A list of teams stats pages.
        """
        stats_page_pattern = re.compile(r'^.*-Stats\.html$')
        stats_pages = list(filter(stats_page_pattern.match, pages))
        # Remove the Bundesliga stats page as it doesn't contain any team stats.
        teams_stats_pages = [
            page
            for page in stats_pages
            if not page.endswith('Bundesliga-Stats.html')
        ]
        return teams_stats_pages

    def get_stats_dataframe(
        self,
        team_stats_page_file: str,
        stat_href: str,
        stat_caption: str,
        pages: list[str],
    ) -> pd.DataFrame:
        """
        Get the stats dataframe for a given stat (shooting, for instance).

        :param team_stats_page_file: The team stats page file name.
        :param stat_href: The href for the stat.
        :param stat_caption: The caption for the stat.
        :param pages: The list of saved pages.
        :return: A dataframe containing the stats.
        """
        # An example team stats page file name is:
        # https_((fbref.com(en(squads(60b5e41f(2018-2019(Hannover-96-Stats
        link_without_team = '('.join(team_stats_page_file.split('(')[:-1])
        # link_without_team is now:
        # https_((fbref.com(en(squads(60b5e41f(2018-2019
        stats_page = [
            page
            for page in pages
            if link_without_team in page and f'({stat_href}(' in page
        ][0]
        # stats_page is now:
        # https_((fbref.com(en(squads(60b5e41f(2018-2019(matchlogs(all_comps(keeper(...html
        stats_file = open(f'{self.html_folder_path}/{stats_page}', 'r')
        # Wrap in StringIO to prevent warnings.
        stats_file_contents = StringIO(stats_file.read())
        stats_df = pd.read_html(stats_file_contents, match=stat_caption)[0]
        # Rename the 'For <team name>' columns as they are unique to each team
        stats_df = stats_df.rename(columns=lambda x: re.sub('^For .+', '', x))
        # Join the first two header rows
        stats_df.columns = stats_df.columns.map(' '.join)
        stats_df.rename(
            columns={stats_df.columns[0]: 'Date', stats_df.columns[1]: 'Time'},
            inplace=True,
        )
        stats_df.columns = ['Date', 'Time'] + [
            f'{stat_href} {column}'
            for column in stats_df.columns
            if column != 'Date' and column != 'Time'
        ]
        return stats_df
