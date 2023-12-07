"""Command line interface for the project."""

import typer

from src.cli.football_data_co_uk import football_data_co_uk_app
from src.cli.fbref import fbref_app

app = typer.Typer()

app.add_typer(fbref_app, name='fbref', help='Manage FBref data.')
app.add_typer(
    football_data_co_uk_app,
    name='football_data_co_uk',
    help='Manage football-data.co.uk data.',
)


if __name__ == '__main__':
    app()
