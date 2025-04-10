import re

import numpy as np
import pandas as pd

dna_regex = re.compile(r'^[ATCG]+$', re.IGNORECASE)

def index_fields_validator(df: pd.DataFrame, fields: list) -> bool:
    return all(col in df.columns for col in fields)

def index_seq_validator(df: pd.DataFrame, column: str) -> bool:
    return df[column].str.fullmatch(r'[ACGT]+').all()

def clean_df(df: pd.DataFrame):
    df_cleaned = df.replace(r'^\s*$', np.nan, regex=True)
    df_cleaned = df_cleaned.dropna(how='all')

    return df_cleaned

def nonempty_validator(df: pd.DataFrame) -> bool:
    df_checked = df.replace(r'^\s*$', np.nan, regex=True)

    return not df_checked.isnull().values.any()

def nonduplicate_validator(df: pd.DataFrame, column: str) -> bool:
    return df[column].is_unique

def index_len(df: pd.DataFrame, column):
     if column in df.columns:
        lengths_list = sorted(df[column]
                              .apply(lambda x: len(x) if isinstance(x, str) else None)
                              .dropna()
                              .unique())

        if len(lengths_list) == 1:
            return int(lengths_list[0])

        else:
            raise ValueError(f"Multiple index lengths in {column}")
