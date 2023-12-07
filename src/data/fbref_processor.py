"""Contains the class that is responsible for processing FBref data."""
from pathlib import Path
import pandas as pd

from src.log import get_logger

logger = get_logger(__name__)


class FbrefProcessor:

    """Processes data cleaned from :class:`FbrefCleaner`."""

    # This prefix is used to mark columns that are important for the model.
    feat_perfix = 'feat_'
    # We also want to keep some columns that are important for merging the
    # dataset with the betting odds dataset.
    info_prefix = 'info_'

    def __init__(
        self, cleaned_data_file_path: Path, processed_data_folder_path: Path
    ) -> None:
        """
        Initialize the processor.

        :param cleaned_data_file_path: Path to the cleaned data file.
        :param processed_data_folder_path: Path to the folder where the
            processed data will be saved.
        """
        self.cleaned_data_file_path = cleaned_data_file_path
        self.processed_data_folder_path = processed_data_folder_path

    def process(self) -> None:
        """Process cleaned data."""
        matches_df = pd.read_csv(self.cleaned_data_file_path)

        matches_df = self.create_rolling_average_columns(matches_df)
        matches_df = self.fill_na_values_with_mean(matches_df)
        matches_df = self.convert_obj_columns_to_int(matches_df)
        matches_df = self.add_match_id_column(matches_df)

        matches_df = self.create_target_column(matches_df)
        matches_df = self.mark_information_columns(matches_df)
        matches_df = self.drop_all_irrelevant_columns(matches_df)

        save_path = Path(
            self.processed_data_folder_path, self.cleaned_data_file_path.name
        )
        matches_df.to_csv(save_path, index=False)
        logger.info(
            f'Saved {matches_df.shape[0]} rows and '
            f'{matches_df.shape[1]} cols of data to {save_path}.'
        )
        logger.info('DONE')

    @staticmethod
    def create_target_column(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create a target column from the result column. The target column will
        contain 1 if the result is a win and 0 otherwise (draw or loss).

        :param df: Dataframe containing the result column.
        :return: Dataframe with the target column.
        """
        df = df.copy()
        df['target'] = (df['result'] == 'W').astype('int')
        logger.info('Created target column.')
        return df

    @staticmethod
    def convert_obj_columns_to_int(df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert object columns to int columns.

        :param df: Dataframe containing object columns.
        :return: Dataframe with int columns.
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df[f'{FbrefProcessor.feat_perfix}team_code'] = (
            df['team'].astype('category').cat.codes
        )
        df[f'{FbrefProcessor.feat_perfix}opponent_code'] = (
            df['opponent'].astype('category').cat.codes
        )
        df[f'{FbrefProcessor.feat_perfix}venue_code'] = (
            df['venue'].astype('category').cat.codes
        )
        df[f'{FbrefProcessor.feat_perfix}hour'] = (
            df['time'].str.replace(':.+', '', regex=True).astype('int')
        )
        df[f'{FbrefProcessor.feat_perfix}day_code'] = df['date'].dt.dayofweek
        df[f'{FbrefProcessor.feat_perfix}month_code'] = df['date'].dt.month
        logger.info('Converted object columns to int columns.')
        return df

    @staticmethod
    def add_match_id_column(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add a match id column to the dataframe. The match id is a combination of
        the date and team columns. If the match is played at home, the team
        column is used. If the match is played away, the opponent column is
        used.

        For example, if Arsenal plays at home against Brentford on 2021-08-13,
        the match id will be 2021-08-13_Arsenal_Brentford. If Arsenal plays away
        against Brentford on 2021-08-13, the match id will be
        2021-08-13_Brentford_Arsenal.

        :param df: Dataframe containing the date and team columns.
        :return: Dataframe with the match id column.
        """
        df = df.copy()
        df['match_id'] = df.apply(
            lambda row: f'{row["date"]}_{row["team"]}_{row["opponent"]}'
            if row['venue'] == 'Home'
            else f'{row["date"]}_{row["opponent"]}_{row["team"]}',
            axis=1,
        )
        logger.info('Added match id column.')
        return df

    @staticmethod
    def create_rolling_average_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create rolling average columns for all numeric columns.

        :param df: Dataframe containing numeric columns.
        :return: Dataframe with rolling average columns.
        """
        df = df.copy()
        # Grab all numeric columns to compute rolling averages for.
        # Those should be only statistics columns.
        numeric_columns = df.select_dtypes(include='number').columns.tolist()
        # Create names for the new rolling average columns.
        rolling_avg_columns = [
            f'{FbrefProcessor.feat_perfix}{col}_rolling_avg'
            for col in numeric_columns
        ]

        # Group by team so that we can compute rolling averages for each team.
        grouped_teams_df = df.groupby('team')
        # Compute rolling averages for each team.
        df = grouped_teams_df.apply(
            lambda group: FbrefProcessor.calculate_rolling_averages(
                group, numeric_columns, rolling_avg_columns
            )
        )

        # Drop the team index level because we don't need it.
        df = df.droplevel(0)
        # Fix the index because there might be duplicate indices.
        df.reset_index(drop=True, inplace=True)
        logger.info('Created rolling average columns.')

        return df

    @staticmethod
    def calculate_rolling_averages(
        df: pd.DataFrame, cols: list[str], new_cols: list[str]
    ) -> pd.DataFrame:
        """
        Compute rolling averages for the specified columns.

        :param df: the dataframe to use.
        :param cols: the columns to compute rolling averages for.
        :param new_cols: the names of the new columns that will contain the
            rolling averages.
        :return: the dataframe with the new columns added.
        """
        df = df.copy()
        # Sort by date because we want to look at the last 3 matches.
        df = df.sort_values('date')

        # Compute rolling averages for the specified columns.
        # The closed parameter is set to 'left' so that the current match is not
        # included in the average.
        rolling_stats = df[cols].rolling(3, closed='left').mean()

        # Add the rolling averages to the dataframe.
        rolling_stats.columns = new_cols
        df = pd.concat([df, rolling_stats], axis=1)

        # Drop rows that contain NaN values in the new columns. These are going
        # to be the first 3 rows of the dataframe because we are computing
        # rolling averages for the next row.
        df.dropna(subset=new_cols, how='all', inplace=True)

        return df

    @staticmethod
    def fill_na_values_with_mean(df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill NaN values with the mean of the column.

        :param df: Dataframe containing NaN values.
        :return: Dataframe with NaN values filled with mean.
        """
        df = df.copy()
        numeric_columns = df.select_dtypes(include=['number']).columns
        df.fillna(df[numeric_columns].mean(), inplace=True)
        logger.info('Filled NaN values with mean.')
        return df

    @staticmethod
    def mark_information_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Preserve the important columns. These columns are needed to merge the
        dataset with the betting odds dataset.

        :param df: Dataframe containing the important columns.
        :return: Dataframe with the important columns with a prefix added.
        """
        df = df.copy()
        info_columns = ['date', 'team', 'opponent', 'venue']
        for col in info_columns:
            df[f'{FbrefProcessor.info_prefix}{col}'] = df[col]
        logger.info('Marked information columns.')
        return df

    @staticmethod
    def drop_all_irrelevant_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop all columns that don't start with either prefix defined in this
        class. Also doesn't drop the target column.

        :param df: Dataframe containing columns to drop.
        :return: Dataframe with columns dropped.
        """
        df = df.copy()
        df = df.filter(
            regex=f'^({FbrefProcessor.feat_perfix}|'
            f'{FbrefProcessor.info_prefix}|target)'
        )
        logger.info('Dropped all irrelevant columns.')
        return df
