import csv
from pathlib import Path

import pandas as pd

from modules.model.load.illumina_index_parser import IlluminaIndexKitParser


class CsvLoader:
    def __init__(self, logger):
        self._logger = logger

    @staticmethod
    def _detect_delimiter(file_path: Path) -> str:
        with open(file_path, 'r') as csvfile:
            content = csvfile.read()
            dialect = csv.Sniffer().sniff(content)

            return dialect.delimiter

    def load_csv(self, file_path: Path) -> pd.DataFrame:
        delimiter = self._detect_delimiter(file_path)
        df = pd.read_csv(file_path, sep=delimiter)
        return df

