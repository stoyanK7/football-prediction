"""
Contains the class that is responsible for cleaning the scraped data
from FBref.
"""
from itertools import combinations
from pathlib import Path
import pandas as pd
from src.log import get_logger


logger = get_logger(__name__)


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
        # low_memory=False is needed because some columns contain a mix of
        # types.
        matches_df = pd.read_csv(self.raw_data_file_path, low_memory=False)

        # Column operations.
        matches_df = self.normalize_column_names(matches_df)
        matches_df = self.drop_equal_columns(matches_df)
        matches_df = self.drop_irrelevant_columns(matches_df)
        matches_df = self.create_penalties_columns_from_goals_columns(
            matches_df
        )

        # Row operations.
        matches_df = self.narrow_down_to_single_competition(
            matches_df, self.competition
        )
        matches_df = self.normalize_team_names(matches_df)
        matches_df = self.remove_rows_with_lots_of_missing_values(
            matches_df, threshold=10
        )

        # Convert goals columns to int. It's a column operation, but it has to
        # be done after the row operations because the goals columns contain
        # NaNs.
        matches_df = self.convert_goals_columns_to_int(matches_df)

        # Save.
        save_path = Path(
            self.cleaned_data_folder_path, self.raw_data_file_path.name
        )
        matches_df.to_csv(save_path, index=False)
        logger.info(
            f'Saved {matches_df.shape[0]} rows and {matches_df.shape[1]} cols '
            f'of data to {save_path}.'
        )
        logger.info('DONE')

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
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True)
        df.columns = df.columns.str.lower()
        df.columns = df.columns.str.replace(' ', '_')
        # For example:
        # possession_unnamed:_33_level_0_match_report
        df.columns = df.columns.str.replace(
            r'(.*)_unnamed:_\d+_level_0_(.*)', r'\1_\2', regex=True
        )  # possession_match_report
        logger.info('Normalized column names.')
        return df

    @staticmethod
    def drop_equal_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop columns that are equal (have the same values).

        :param df: DataFrame to drop equal columns from.
        :return: DataFrame with equal columns dropped.
        """
        df = df.copy()
        list_of_equal_cols = FbrefCleaner.get_list_of_equal_columns(df)
        cols_to_drop = [j for i, j in list_of_equal_cols]
        df.drop(columns=cols_to_drop, inplace=True)
        logger.info(f'Dropped equal columns {cols_to_drop}.')

        # Unfortunately, this doesn't catch all equal columns, so we have to
        # manually add some more.
        regex = (
            '.+_(comp|round|day|venue|result|opponent|match_report|notes|gf|ga)'
        )
        cols_to_drop = df.filter(regex=regex).columns
        df.drop(cols_to_drop, axis=1, inplace=True)
        logger.info(f'Dropped more equal columns {cols_to_drop}.')

        cols_to_drop = ['shooting_standard_gls']
        # Filter is created because some columns might not exist.
        cols_filter = df.filter(cols_to_drop)
        df.drop(cols_filter, axis=1, inplace=True)
        logger.info(f'Dropped columns {cols_to_drop}.')
        return df

    @staticmethod
    def get_list_of_equal_columns(df: pd.DataFrame) -> list[tuple[str, str]]:
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
        logger.info(f'Dropped irrelevant columns {cols_to_drop}.')
        return df

    @staticmethod
    def create_penalties_columns_from_goals_columns(
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
        logger.info('Split goals columns into goals and penalties columns.')
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

        def convert_goals_column_to_int(x: str) -> int:
            if isinstance(x, int):
                return x
            if ' ' in x:
                x = x.split(' ')[0]
            if '.' in x:
                x = x.split('.')[0]
            return int(x)

        for col in goals_cols:
            df[col] = df[col].apply(convert_goals_column_to_int)

        logger.info(f'Converted goals columns({goals_cols}) to int.')
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
        logger.info(f'Narrowed down to {competition} competition.')
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
        # Drop rows where team or opponent is NaN.
        df = df.dropna(subset=['team'])
        df = df.dropna(subset=['opponent'])
        # Convert date column to datetime.
        df['date'] = pd.to_datetime(df['date'])
        # Rows of future matches will have lots of missing values, however, we
        # want to keep them because we want to predict them. Extract one match
        # per team that is after now and keep those rows.
        future_matches = df[df['date'] > pd.Timestamp.now()]
        # Resetting index to make 'team' a regular column.
        future_matches = future_matches.groupby('team').first().reset_index()
        # Fill with -1 as we don't care about the values. This is the future.
        future_matches = future_matches.fillna(-1)
        df = df[df['date'] <= pd.Timestamp.now()]
        # Threshold is the amount of missing values a row can have before it
        # gets dropped. So we need to subtract the threshold from the total
        # amount of columns.
        threshold = df.shape[1] - threshold
        initial_amount_of_rows = df.shape[0]
        df = df.dropna(thresh=threshold)
        logger.info(
            f'Dropped {initial_amount_of_rows - df.shape[0]} rows with '
            f'{threshold} or more missing values.'
        )
        df = pd.concat([df, future_matches])
        logger.info(
            f'Added {future_matches.shape[0]} rows of future matches back.'
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

        logger.info('Normalized team names.')
        return df
