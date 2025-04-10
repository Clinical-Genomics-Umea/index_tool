import csv
from pathlib import Path

import pandas as pd


class CsvIndexData:
    def __init__(self, filepath, logger):
        self._logger = logger
        self._indexes: pd.DataFrame | None = None

        self._load_csv(filepath)

    @staticmethod
    def _detect_delimiter(filepath: Path) -> str:
        with open(filepath, 'r') as csvfile:
            content = csvfile.read()
            dialect = csv.Sniffer().sniff(content)

            return dialect.delimiter

    def _load_csv(self, filepath: Path):
        delimiter = self._detect_delimiter(filepath)
        self._indexes = pd.read_csv(filepath, sep=delimiter)

    @property
    def indexes(self) -> pd.DataFrame | None:
        return self._indexes

