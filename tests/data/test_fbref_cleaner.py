"""Tests for the FbrefCleaner class."""
import pandas as pd
import pytest

from src.data.fbref_cleaner import FbrefCleaner


def test_normalize_column_names():
    df = pd.DataFrame(
        {
            '  pLaYeR ': [],
            'Player    1    ': [],
            'shooting Unnamed: 25_level_0 Match Report': [],
            'Player.3': [],
        }
    )

    df = FbrefCleaner.normalize_column_names(df)

    assert df.columns.tolist() == [
        'player',
        'player_1',
        'shooting_match_report',
        'player.3',
    ]


def test_drop_equal_columns():
    df = pd.DataFrame(
        {
            'a': [1, 2, 3],
            'b': [1, 4, 3],
            'c': [1, 2, 3],
            'd': [1, 4, 3],
            'e': [1, 1, 3],
        }
    )

    df = FbrefCleaner.drop_equal_columns(df)

    assert df.columns.tolist() == ['a', 'b', 'e']


def test_get_list_of_equal_columns():
    df = pd.DataFrame(
        {
            'a': [1, 2, 3],
            'b': [1, 4, 3],
            'c': [1, 2, 3],
            'd': [1, 4, 3],
            'e': [1, 1, 3],
        }
    )

    equal_cols = FbrefCleaner.get_list_of_equal_columns(df)

    assert equal_cols == [('a', 'c'), ('b', 'd')]


def test_drop_irrelevant_columns():
    df = pd.DataFrame(
        {
            'notes': [1, 2, 3],
            'match_report': [1, 4, 3],
            ' aaxnotes %': [1, 2, 3],
            '! asdmatch_reporta  X': [1, 4, 3],
            'e': [1, 1, 3],
        }
    )

    df = FbrefCleaner.drop_irrelevant_columns(df)

    assert df.columns.tolist() == ['e']


def test_create_penalties_columns_from_goals_columns():
    df = pd.DataFrame(
        {
            'gf': ['1 (1)', '2 (1)', '3 (1)', '1'],
            'ga': ['1 (1)', '4 (4)', '3 (2)', '2'],
        }
    )

    df = FbrefCleaner.create_penalties_columns_from_goals_columns(df)

    assert df.columns.tolist() == ['gf', 'ga', 'pen_gf', 'pen_ga']
    assert df['pen_gf'].tolist() == ['1', '1', '1', -1]
    assert df['pen_ga'].tolist() == ['1', '4', '2', -1]


def test_convert_goals_columns_to_int():
    df = pd.DataFrame(
        {
            'gf': ['1 (1)', '2 (1)', '3 (1)', '1', '1.0'],
            'ga': ['1 (1)', '4 (4)', '3 (2)', '2', '8.0'],
        }
    )

    df = FbrefCleaner.convert_goals_columns_to_int(df)

    assert df.columns.tolist() == ['gf', 'ga']
    assert df['gf'].tolist() == [1, 2, 3, 1, 1]
    assert df['ga'].tolist() == [1, 4, 3, 2, 8]


def test_narrow_down_to_single_competition():
    df = pd.DataFrame(
        {
            'comp': ['Premier League', 'Premier League', 'La Liga', 'La Liga'],
            'a': [1, 2, 3, 4],
        }
    )

    df = FbrefCleaner.narrow_down_to_single_competition(df, 'Premier League')

    assert df.columns.tolist() == ['comp', 'a']
    assert df['comp'].tolist() == ['Premier League', 'Premier League']
    assert df['a'].tolist() == [1, 2]


def test_remove_rows_with_lots_of_missing_values():
    df = pd.DataFrame(
        {
            'a': [1, 2, None, 4, 5],
            'b': [1, 2, 3, 4, 5],
            'c': [None, None, None, None, 5],
            'd': [None, 2, 3, 4, 5],
            'e': [None, None, None, 4, 5],
        }
    )

    df = FbrefCleaner.remove_rows_with_lots_of_missing_values(df, 2)

    assert df.columns.tolist() == ['a', 'b', 'c', 'd', 'e']
    assert len(df) == 3


def test_normalize_team_names():
    df = pd.DataFrame(
        {
            'team': [
                'Dusseldorf',
                'Eintracht Frankfurt',
                'Greuther Furth',
                'Koln',
                'Nurnberg',
            ],
            'opponent': [
                'Düsseldorf',
                'Eint Frankfurt',
                'Greuther Furth',
                'Köln',
                'Nürnberg',
            ],
        }
    )

    df = FbrefCleaner.normalize_team_names(df)

    assert df.columns.tolist() == ['team', 'opponent']
    assert df['opponent'].tolist() == [
        'Dusseldorf',
        'Eintracht Frankfurt',
        'Greuther Furth',
        'Koln',
        'Nurnberg',
    ]


def test_normalize_team_names_length_difference():
    df = pd.DataFrame(
        {
            'team': [
                'Dusseldorf',
                'Eintracht Frankfurt',
                'Greuther Furth',
                'Dusseldorf',
            ],
            'opponent': ['Düsseldorf', 'Eint Frankfurt', 'Köln', 'Nürnberg'],
        }
    )

    with pytest.raises(ValueError):
        FbrefCleaner.normalize_team_names(df)
