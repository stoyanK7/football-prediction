"""
Contains the class that is responsible for cleaning the scraped data
from FBref.
"""
from itertools import combinations
from pathlib import Path
from tqdm import tqdm
import pandas as pd


class FbrefCleaner:

    """Cleans data scraped from :class:`FbrefScraper`."""

    def __init__(
        self,
        raw_data_file_path: Path,
        cleaned_data_folder_path: Path,
        competition: str = None,
    ) -> None:
        """
        Initialize the cleaner.

        :param raw_data_file_path: Path to the raw data file that was created
            by the scraper.
        :param cleaned_data_folder_path: Path to the file that will contain the
            cleaned data.
        :param competition: The competition to narrow down to. If None, all
            competitions will be kept.
        """
        self.raw_data_file_path = raw_data_file_path
        self.cleaned_data_folder_path = cleaned_data_folder_path
        self.competition = competition

    def clean(self) -> None:
        """Clean the data."""
        matches_df = pd.read_csv(self.raw_data_file_path)

        # Column operations.
        matches_df = self.normalize_column_names(matches_df)
        matches_df = self.drop_equal_columns(matches_df)
        matches_df = self.drop_irrelevant_columns(matches_df)
        matches_df = self.split_goals_columns_into_goals_and_penalties_columns(
            matches_df
        )
        matches_df = self.convert_goals_columns_to_int(matches_df)

        # Row operations.
        if self.competition:
            matches_df = self.narrow_down_to_single_competition(
                matches_df, self.competition
            )
        matches_df = self.remove_rows_with_lots_of_missing_values(
            matches_df, threshold=10
        )
        matches_df = self.normalize_team_names(matches_df)

        # Save.
        save_path = Path(
            self.cleaned_data_folder_path, self.raw_data_file_path.name
        )
        matches_df.to_csv(save_path, index=False)
        tqdm.write(
            f'Saved {matches_df.shape[0]} rows and {matches_df.shape[1]} cols '
            f'of data to {save_path}.'
        )

    @staticmethod
    def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize the column names. Make them lowercase, replace spaces with
        underscores, and remove unnecessary parts of the column names that
        happened during scraping.

        :param df: DataFrame to normalize the column names of.
        :return: DataFrame with normalized column names.
        """
        df = df.copy()
        df.columns = df.columns.str.replace('  ', ' ')
        df.columns = df.columns.str.lower()
        df.columns = df.columns.str.replace(' ', '_')
        # For example:
        # possession_unnamed:_33_level_0_match_report
        df.columns = df.columns.str.replace(
            r'(.*)_unnamed:_\d+_level_0_(.*)', r'\1_\2', regex=True
        )  # possession_match_report
        tqdm.write('Normalized column names.')
        return df

    @staticmethod
    def drop_equal_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop columns that are equal (have the same values).

        :param df: DataFrame to drop equal columns from.
        :return: DataFrame with equal columns dropped.
        """
        df = df.copy()
        list_of_equal_cols = FbrefCleaner.get_list_of_equal_cols(df)
        cols_to_drop = [j for i, j in list_of_equal_cols]
        df.drop(columns=cols_to_drop, inplace=True)
        tqdm.write(f'Dropped equal columns {cols_to_drop}.')

        # Unfortunately, this doesn't catch all equal columns, so we have to
        # manually add some more.
        regex = (
            '.+_(comp|round|day|venue|result|opponent|match_report|notes|gf|ga)'
        )
        cols_to_drop = df.filter(regex=regex).columns
        df.drop(cols_to_drop, axis=1, inplace=True)
        tqdm.write(f'Dropped more equal columns {cols_to_drop}.')

        cols_to_drop = ['shooting_standard_gls']
        df.drop(columns=cols_to_drop, axis=1, inplace=True)
        tqdm.write(f'Dropped columns {cols_to_drop}.')
        return df

    @staticmethod
    def get_list_of_equal_cols(df: pd.DataFrame) -> list[tuple[str, str]]:
        """
        Get a list of equal columns. Columns are considered equal if they have
        the same values. Borrowed from:
        https://stackoverflow.com/a/58002867/9553927.

        :param df: DataFrame to get the list of equal columns from.
        :return: List of equal columns.
        """
        return [(i, j) for i, j in combinations(df, 2) if df[i].equals(df[j])]

    @staticmethod
    def drop_irrelevant_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop columns that do not contain any relevant information.

        :param df: DataFrame to drop irrelevant columns from.
        :return: DataFrame with irrelevant columns dropped.
        """
        df = df.copy()
        regex = '.*(notes|match_report).*'
        cols_to_drop = df.filter(regex=regex).columns
        df.drop(cols_to_drop, axis=1, inplace=True)
        tqdm.write(f'Dropped irrelevant columns {cols_to_drop}.')
        return df

    @staticmethod
    def split_goals_columns_into_goals_and_penalties_columns(
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Split the goals columns into goals and penalties columns. Some goal rows
        are described as '1 (3)' which means that the team scored 1 goal and 3
        penalties. We want to split these into two columns: 'gf' and 'pen_gf'.
        Same for 'ga' and 'pen_ga'. If there are no penalties, the value will be
        -1.

        :param df: DataFrame to split the goals columns of.
        :return: DataFrame with goals columns split into goals and penalties
        """
        df = df.copy()
        df['pen_gf'] = df['gf'].str.extract(r'\((\d+)\)')
        df['pen_ga'] = df['ga'].str.extract(r'\((\d+)\)')

        # Fill NaNs with -1s. 0 would be a valid value, so we can't use that.
        df['pen_gf'].fillna(-1, inplace=True)
        df['pen_ga'].fillna(-1, inplace=True)
        tqdm.write('Split goals columns into goals and penalties columns.')
        return df

    @staticmethod
    def convert_goals_columns_to_int(df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the goals columns to int. They are currently strings because
        they contain the number of penalties in parentheses or the goals
        as a float (e.g. '1.0').

        :param df: DataFrame to convert the goals columns of.
        :return: DataFrame with goals columns converted to int.
        """
        df = df.copy()
        goals_cols = ['gf', 'ga']
        for col in goals_cols:
            df[col] = df[col].str.split(' ').str[0]
            df[col] = df[col].str.split('.').str[0]
            df[col] = df[col].astype('int')

        tqdm.write(f'Converted goals columns({goals_cols}) to int.')
        return df

    @staticmethod
    def narrow_down_to_single_competition(
        df: pd.DataFrame, competition: str
    ) -> pd.DataFrame:
        """
        Narrow down the DataFrame to a single competition.

        :param df: DataFrame to narrow down.
        :param competition: Competition to narrow down to.
        :return: DataFrame narrowed down to a single competition.
        """
        df = df.copy()
        df = df[df['comp'] == competition]
        tqdm.write(f'Narrowed down to {competition} competition.')
        return df

    @staticmethod
    def remove_rows_with_lots_of_missing_values(
        df: pd.DataFrame, threshold: int
    ) -> pd.DataFrame:
        """
        Remove rows with lots of missing values. If a row has more than
        `threshold` missing values, it will be dropped.

        :param df: DataFrame to remove rows with lots of missing values from.
        :param threshold:  Amount of missing values a row can have before it
            gets dropped.
        :return: DataFrame with rows with lots of missing values removed.
        """
        df = df.copy()
        amount_of_rows_to_drop = len(df[df.isnull().sum(axis=1) > threshold])
        df.dropna(thresh=threshold, inplace=True)
        tqdm.write(
            f'Dropped {amount_of_rows_to_drop} rows with more than {threshold} '
            f'missing values.'
        )
        return df

    @staticmethod
    def normalize_team_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize the team names. For example, 'Düsseldorf' becomes
        'Dusseldorf'.

        :param df: DataFrame to normalize the team names of.
        :return: DataFrame with normalized team names.
        """
        df = df.copy()
        mapping = {
            'Düsseldorf': 'Dusseldorf',
            'Eint Frankfurt': 'Eintracht Frankfurt',
            'Greuther Fürth': 'Greuther Furth',
            'Köln': 'Koln',
            "M'Gladbach": 'Monchengladbach',
            'Nürnberg': 'Nurnberg',
            'Leverkusen': 'Bayer Leverkusen',
        }
        # Normalize team name or leave as is if not in mapping.
        df['opponent'] = df['opponent'].map(mapping).fillna(df['opponent'])

        teams = df['team'].unique().tolist()
        opponents = df['opponent'].unique().tolist()
        teams.sort()
        opponents.sort()
        if len(teams) != len(opponents):
            msg = (
                f'Amount of teams ({len(teams)}) and opponents '
                f'({len(opponents)}) is not equal.'
                f'\nTeams: {teams}'
                f'\nOpponents: {opponents}'
                f'\nDifference: {set(teams) ^ set(opponents)}'
            )
            raise ValueError(msg)

        tqdm.write('Normalized team names.')
        return df
