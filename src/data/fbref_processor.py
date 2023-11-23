"""Contains the class that is responsible for processing FBref data."""
from pathlib import Path
import pandas as pd
from tqdm import tqdm


class FbrefProcessor:

    """Processes data cleaned from :class:`FbrefCleaner`."""

    # At the end of the processing, we want to drop all columns that don't
    # start with this prefix.
    keep_prefix = 'keep_'

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
        matches_df = self.convert_obj_columns_to_int(matches_df)
        matches_df = self.create_target_column(matches_df)
        matches_df = self.drop_all_irrelevant_columns(matches_df)
        matches_df = self.remove_keep_prefix_from_column_names(matches_df)

        save_path = Path(
            self.processed_data_folder_path, self.cleaned_data_file_path.name
        )
        matches_df.to_csv(save_path, index=False)
        tqdm.write(
            f'Saved {matches_df.shape[0]} rows and '
            f'{matches_df.shape[1]} cols of data to {save_path}.'
        )

    @staticmethod
    def create_target_column(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create a target column from the result column. The target column will
        contain 1 if the result is a win and 0 otherwise (draw or loss).

        :param df: Dataframe containing the result column.
        :return: Dataframe with the target column.
        """
        df = df.copy()
        df[FbrefProcessor.keep('target')] = (df['result'] == 'W').astype('int')
        tqdm.write('Created target column.')
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
        df[FbrefProcessor.keep('team_code')] = (
            df['team'].astype('category').cat.codes
        )
        df[FbrefProcessor.keep('opponent_code')] = (
            df['opponent'].astype('category').cat.codes
        )
        df[FbrefProcessor.keep('venue_code')] = (
            df['venue'].astype('category').cat.codes
        )
        df[FbrefProcessor.keep('hour')] = (
            df['time'].str.replace(':.+', '', regex=True).astype('int')
        )
        df[FbrefProcessor.keep('day_code')] = df['date'].dt.dayofweek
        df[FbrefProcessor.keep('month_code')] = df['date'].dt.month
        tqdm.write('Converted object columns to int columns.')
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
            FbrefProcessor.keep(f'{col}_rolling_avg') for col in numeric_columns
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
        tqdm.write('Created rolling average columns.')

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
    def keep(s: str) -> str:
        """
        Add a prefix to a string to mark it as a feature column.

        :param s: String to add a prefix to.
        :return: String with a prefix added.
        """
        return f'{FbrefProcessor.keep_prefix}{s}'

    @staticmethod
    def drop_all_irrelevant_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop all columns that don't start with the prefix.

        :param df: Dataframe containing columns to drop.
        :return: Dataframe with columns dropped.
        """
        df = df.copy()
        # Drop all columns that don't start with the prefix.
        df = df.loc[:, df.columns.str.startswith(FbrefProcessor.keep_prefix)]
        return df

    @staticmethod
    def remove_keep_prefix_from_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove the prefix from the column names.

        :param df: Dataframe containing columns to remove the prefix from.
        :return: Dataframe with the prefix removed from the column names.
        """
        df = df.copy()
        # Remove the prefix from the column names.
        df.columns = df.columns.str.replace(
            f'^{FbrefProcessor.keep_prefix}', '', regex=True
        )
        return df
