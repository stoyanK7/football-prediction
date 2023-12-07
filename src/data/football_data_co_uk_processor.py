"""
Contains the class that is responsible for processing
FootballDataCoUk data.
"""
from pathlib import Path
import pandas as pd

from src.log import get_logger

logger = get_logger(__name__)


class FootballDataCoUkProcessor:

    """Processes data cleaned from :class:`FootballDataCoUkCleaner`."""

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
        odds_df = pd.read_csv(self.cleaned_data_file_path)

        odds_df = self.add_match_id_column(odds_df)

        save_path = Path(
            self.processed_data_folder_path, self.cleaned_data_file_path.name
        )
        odds_df.to_csv(save_path, index=False)
        logger.info(
            f'Saved {odds_df.shape[0]} rows and '
            f'{odds_df.shape[1]} cols of data to {save_path}.'
        )
        logger.info('DONE')

    @staticmethod
    def add_match_id_column(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add a match id column to the dataframe. The match id is a combination of
        the date and teams columns.

        :param df: Dataframe containing the date and team columns.
        :return: Dataframe with the match id column.
        """
        df = df.copy()
        df['match_id'] = df.apply(
            lambda row: f'{row["date"]}_{row["team"]}_{row["opponent"]}', axis=1
        )
        logger.info('Added match id column.')
        return df
