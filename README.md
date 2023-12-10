# Football Match Event Prediction

<p align="center">
    <a href="https://python.org">
        <img src="https://img.shields.io/badge/python-3.12-blue.svg?logo=python&logoColor=white&label=python" alt="Python version">
    </a>
    <a href="https://www.gnu.org/licenses/gpl-3.0">
        <img src="https://img.shields.io/badge/License-GPLv3-blue.svg"/>
    </a>
</p>

## Project structure

```sh
├── data                  #  All data.
│   ├── interim           #  Cleaned data.
│   ├── processed         #  Processed data (ready for training).
│   ├── raw               #  Raw scraped data.
│   └── test              #  Data used for tests.
├── logs                  #  Logfiles from different tasks.
├── notebooks             #  Notebooks with experiments.
├── src                   #  Source code for use in this project.
│   ├── cli               #  Code for the CLI interface.
│   └── data              #  Code for data scraping, cleaning and processing.
└── tests                 #  Unit and integration tests.
```

## Environment Setup

```sh
pipenv install --dev
```

## CLI

```sh
python -m src.cli.main crawl
python -m src.cli.main scrape
python -m src.cli.main clean
python -m src.cli.main process
```

## Run Tests

```sh
pytest tests
```
