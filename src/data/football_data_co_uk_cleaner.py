"""
Contains the class that is responsible for cleaning the scraped data
from FootballDataCoUk.
"""
from pathlib import Path

import pandas as pd

from src.log import get_logger


class FootballDataCoUkCleaner:

    """Cleans data scraped from :class:`FootballDataCoUkScraper`."""

    logger_name = 'football_data_co_uk_cleaner'
    logger, logfile = get_logger(logger_name)

    def __init__(
        self,
        raw_data_folder_path: Path,
        cleaned_data_folder_path: Path,
        competition: str,
    ) -> None:
        """
        Initialize the cleaner.

        :param raw_data_folder_path: Folder path to the raw data.
        :param cleaned_data_folder_path: Folder path to save the cleaned data
            to.
        :param competition: The name of the competition that was scraped. Used
            to determine which files to clean.
        """
        self.raw_data_folder_path = raw_data_folder_path
        self.cleaned_data_folder_path = cleaned_data_folder_path
        self.competition = competition

    def clean(self) -> None:
        """Clean the data."""
        odds_df = self.get_odds_df()

        # Column operations.
        odds_df = self.normalize_column_names(odds_df)
        odds_df = self.drop_irrelevant_columns(odds_df)
        odds_df = self.rename_columns(odds_df)

        # Row operations.
        odds_df = self.normalize_team_names(odds_df)
        odds_df = self.normalize_dates(odds_df)

        # Save.
        save_path = Path(
            self.cleaned_data_folder_path, f'{self.competition}_odds.csv'
        )
        odds_df.to_csv(save_path, index=False)
        FootballDataCoUkCleaner.logger.info(
            f'Saved {odds_df.shape[0]} rows and {odds_df.shape[1]} cols '
            f'of data to {save_path}.'
        )
        FootballDataCoUkCleaner.logger.info('DONE')

    def get_odds_df(self) -> pd.DataFrame:
        """
        Find all the odds csv files and combine them into one dataframe.

        :return: Dataframe containing all the odds' data.
        """
        odds_dfs = []
        for csv_file_path in self.raw_data_folder_path.glob(
            f'*{self.competition}*odds*.csv'
        ):
            odds_df = pd.read_csv(csv_file_path)
            odds_dfs.append(odds_df)
        odds_df = pd.concat(odds_dfs)
        return odds_df

    @staticmethod
    def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize the column names of the dataframe. This is done by making
        all the column names lowercase.

        :param df: Dataframe to normalize the column names of.
        :return: Dataframe with normalized column names.
        """
        df = df.copy()
        df.columns = df.columns.str.lower()
        FootballDataCoUkCleaner.logger.info(
            'Normalized column names of dataframe.'
        )
        return df

    @staticmethod
    def drop_irrelevant_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop irrelevant columns from the dataframe.

        :param df: Dataframe to drop the columns from.
        :return: Dataframe with the irrelevant columns dropped.
        """
        df = df.copy()
        cols_to_drop = ['div', 'time']
        df = df.drop(columns=cols_to_drop)
        FootballDataCoUkCleaner.logger.info(
            f'Dropped {len(cols_to_drop)} irrelevant columns from dataframe. '
            f'Columns dropped: {cols_to_drop}.'
        )
        return df

    @staticmethod
    def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename the columns of the dataframe.

        :param df: Dataframe to rename the columns of.
        :return: Dataframe with the columns renamed.
        """
        df = df.copy()
        mapping = {'hometeam': 'team', 'awayteam': 'opponent'}
        df = df.rename(columns=mapping)
        FootballDataCoUkCleaner.logger.info('Renamed columns of dataframe.')
        return df

    @staticmethod
    def normalize_team_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize the team names in the dataframe to match the names in
        the scraped data from FBref.

        :param df: Dataframe to normalize the team names of.
        :return: Dataframe with the team names normalized.
        """
        df = df.copy()
        mapping = {
            'Ein Frankfurt': 'Eintracht Frankfurt',
            "M'gladbach": 'Monchengladbach',
            'FC Koln': 'Koln',
            'Leverkusen': 'Bayer Leverkusen',
            'Fortuna Dusseldorf': 'Dusseldorf',
            'Hamburg': 'Hamburger SV',
            'Darmstadt': 'Darmstadt 98',
            'Paderborn': 'Paderborn 07',
            'Hannover': 'Hannover 96',
            'Hertha': 'Hertha BSC',
            'Mainz': 'Mainz 05',
            'Bielefeld': 'Arminia',
        }
        df['team'] = df['team'].map(mapping).fillna(df['team'])
        df['opponent'] = df['opponent'].map(mapping).fillna(df['opponent'])
        FootballDataCoUkCleaner.logger.info(
            'Normalized team names of dataframe.'
        )
        return df

    @staticmethod
    def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize the dates in the dataframe to match the dates in
        the scraped data from FBref.

        :param df: Dataframe to normalize the dates of.
        :return: Dataframe with the dates normalized.
        """
        df = df.copy()
        df['date'] = df['date'].str.replace('/', '-')
        df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=True)
        FootballDataCoUkCleaner.logger.info('Normalized dates of dataframe.')
        return df
