import csv
from pathlib import Path

import pandas as pd

from modules.model.load.illumina_index_parser import IlluminaIndexKitParser


class Loader:
    def __init__(self, logger):
        self._logger = logger
        self._illumina_index_kit_parser = IlluminaIndexKitParser()

    @staticmethod
    def _detect_delimiter(file_path: Path) -> str:
        with open(file_path, 'r') as csvfile:
            content = csvfile.read()
            dialect = csv.Sniffer().sniff(content)

            return dialect.delimiter

    def _load_csv(self, file_path: Path) -> pd.DataFrame:
        delimiter = self._detect_delimiter(file_path)
        df = pd.read_csv(file_path, sep=delimiter)
        return df

    def _load_illumina_index_kit(self, file_path: Path) -> pd.DataFrame:
        df = self._illumina_index_kit_parser.parse(file_path)
        return df
