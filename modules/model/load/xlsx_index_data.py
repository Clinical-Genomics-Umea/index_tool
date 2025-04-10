import csv
from pathlib import Path

import pandas as pd

class XlsxIndexData:
    def __init__(self, filepath, logger):
        self._logger = logger
        self._indexes: pd.DataFrame | None = None

        self._load_xlsx(filepath)

    @staticmethod
    def _detect_delimiter(filepath: Path) -> str:
        with open(filepath, 'r') as csvfile:
            content = csvfile.read()
            dialect = csv.Sniffer().sniff(content)

            return dialect.delimiter

    def _load_xlsx(self, filepath: Path):
        self._indexes = pd.read_excel(filepath)

    @property
    def indexes(self) -> pd.DataFrame | None:
        return self._indexes
