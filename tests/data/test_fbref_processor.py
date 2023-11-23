"""Tests for the FbrefProcessor class."""
import pandas as pd

from src.data.fbref_processor import FbrefProcessor


def test_convert_obj_columns_to_int():
    df = pd.DataFrame(
        {
            'date': ['2021-03-14', '2021-08-14', '2021-12-14', '2021-08-14'],
            'team': ['Arsenal', 'Brsenal', 'Crsenal', 'Drsenal'],
            'opponent': ['Brentford', 'Crentford', 'Drentford', 'Erentford'],
            'time': ['21:00', '14:00', '08:00', '15:00'],
            'venue': ['Home', 'Away', 'Home', 'Away'],
        }
    )

    df = FbrefProcessor.convert_obj_columns_to_int(df)

    assert df['keep_team_code'].tolist() == [0, 1, 2, 3]
    assert df['keep_opponent_code'].tolist() == [0, 1, 2, 3]
    assert df['keep_venue_code'].tolist() == [1, 0, 1, 0]
    assert df['keep_hour'].tolist() == [21, 14, 8, 15]
    assert df['keep_day_code'].tolist() == [6, 5, 1, 5]
    assert df['keep_month_code'].tolist() == [3, 8, 12, 8]


def test_create_target_column():
    df = pd.DataFrame(
        {'result': ['W', 'D', 'L', 'W', 'W', 'W', 'W', 'L', 'D', 'W']}
    )

    df = FbrefProcessor.create_target_column(df)

    assert df['keep_target'].tolist() == [1, 0, 0, 1, 1, 1, 1, 0, 0, 1]


def test_create_rolling_average_columns():
    df = pd.DataFrame(
        {
            'team': ['Arsenal', 'Arsenal', 'Arsenal', 'Arsenal'],
            'date': ['2021-03-14', '2021-04-14', '2021-05-14', '2021-06-14'],
            'ga': [1, 2, 3, 4],  # (1 + 2 + 3) / 3 = 2
            'gf': [10, 3, 5, 4],  # (10 + 3 + 5) / 3 = 6
        }
    )

    df = FbrefProcessor.create_rolling_average_columns(df)

    # The first 3 rows should have NaN values and be dropped.
    assert df['keep_ga_rolling_avg'].tolist() == [2.0]
    assert df['keep_gf_rolling_avg'].tolist() == [6.0]


def test_drop_all_irrelevant_columns():
    pref = FbrefProcessor.keep_prefix
    df = pd.DataFrame(
        {
            f'{pref}team': ['Arsenal', 'Arsenal', 'Arsenal', 'Arsenal'],
            'date': ['2021-03-14', '2021-04-14', '2021-05-14', '2021-06-14'],
            f'{pref}ga': [1, 2, 3, 4],
            'gf': [10, 3, 5, 4],
        }
    )

    df = FbrefProcessor.drop_all_irrelevant_columns(df)

    assert df.columns.tolist() == [f'{pref}team', f'{pref}ga']


def test_remove_keep_prefix_from_column_names():
    pref = FbrefProcessor.keep_prefix
    df = pd.DataFrame(
        {
            f'{pref}team': ['Arsenal', 'Arsenal', 'Arsenal', 'Arsenal'],
            'date': ['2021-03-14', '2021-04-14', '2021-05-14', '2021-06-14'],
            f'{pref}ga': [1, 2, 3, 4],
            'gf': [10, 3, 5, 4],
        }
    )

    df = FbrefProcessor.remove_keep_prefix_from_column_names(df)

    assert df.columns.tolist() == ['team', 'date', 'ga', 'gf']
