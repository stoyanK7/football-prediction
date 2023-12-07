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

    assert df['feat_team_code'].tolist() == [0, 1, 2, 3]
    assert df['feat_opponent_code'].tolist() == [0, 1, 2, 3]
    assert df['feat_venue_code'].tolist() == [1, 0, 1, 0]
    assert df['feat_hour'].tolist() == [21, 14, 8, 15]
    assert df['feat_day_code'].tolist() == [6, 5, 1, 5]
    assert df['feat_month_code'].tolist() == [3, 8, 12, 8]


def test_create_target_column():
    df = pd.DataFrame(
        {'result': ['W', 'D', 'L', 'W', 'W', 'W', 'W', 'L', 'D', 'W']}
    )

    df = FbrefProcessor.create_target_column(df)

    assert df['target'].tolist() == [1, 0, 0, 1, 1, 1, 1, 0, 0, 1]


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
    assert df['feat_ga_rolling_avg'].tolist() == [2.0]
    assert df['feat_gf_rolling_avg'].tolist() == [6.0]


def test_mark_information_columns():
    # dataframe with date, team, opponent, venue
    df = pd.DataFrame(
        {
            'date': ['2021-03-14', '2021-04-14', '2021-05-14', '2021-06-14'],
            'team': ['Arsenal', 'Arsenal', 'Arsenal', 'Arsenal'],
            'opponent': ['Brentford', 'Brentford', 'Brentford', 'Brentford'],
            'venue': ['Home', 'Home', 'Home', 'Home'],
        }
    )

    df = FbrefProcessor.mark_information_columns(df)

    assert df.columns.tolist() == [
        'date',
        'team',
        'opponent',
        'venue',
        'info_date',
        'info_team',
        'info_opponent',
        'info_venue',
    ]


def test_drop_all_irrelevant_columns():
    df = pd.DataFrame(
        {
            'date': ['2021-03-14', '2021-04-14', '2021-05-14', '2021-06-14'],
            'team': ['Arsenal', 'Arsenal', 'Arsenal', 'Arsenal'],
            'opponent': ['Brentford', 'Brentford', 'Brentford', 'Brentford'],
            'feat_venue': ['Home', 'Home', 'Home', 'Home'],
            'info_date': [
                '2021-03-14',
                '2021-04-14',
                '2021-05-14',
                '2021-06-14',
            ],
            'info_team': ['Arsenal', 'Arsenal', 'Arsenal', 'Arsenal'],
            'info_opponent': [
                'Brentford',
                'Brentford',
                'Brentford',
                'Brentford',
            ],
            'info_venue': ['Home', 'Home', 'Home', 'Home'],
            'target': [1, 0, 0, 1],
        }
    )

    df = FbrefProcessor.drop_all_irrelevant_columns(df)

    assert df.columns.tolist() == [
        'feat_venue',
        'info_date',
        'info_team',
        'info_opponent',
        'info_venue',
        'target',
    ]


def test_add_match_id_column():
    df = pd.DataFrame(
        {
            'date': ['2021-03-14', '2021-04-14', '2021-05-14', '2021-06-14'],
            'team': ['Arsenal', 'Oxford', 'Manchester', 'Arsenal'],
            'opponent': ['Brentford', 'Leverkusen', 'Levski', 'Bayer Munich'],
            'venue': ['Home', 'Away', 'Home', 'Away'],
        }
    )

    df = FbrefProcessor.add_match_id_column(df)

    assert df['match_id'].tolist() == [
        '2021-03-14_Arsenal_Brentford',
        '2021-04-14_Leverkusen_Oxford',
        '2021-05-14_Manchester_Levski',
        '2021-06-14_Bayer Munich_Arsenal',
    ]
