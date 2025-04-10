import re
from pathlib import Path
from pprint import pprint

import pandas as pd
from io import StringIO


class IlluminaIndexData:
    def __init__(self, filepath, logger):
        self._logger = logger

        self._index_name_pair_pattern = re.compile(r'^[^\s\-]+-[^\s\-]+$')

        # indata from parser

        self._indata: dict | None = None

        # sections

        self._index_kit: dict | None = None
        self._supported_library_prep_kits: list | None = None
        self._resources = pd.DataFrame()
        self._indexes = pd.DataFrame()

        # index_kit data
        self._checksum: str | None = None
        self._name: str | None = None
        self._display_name: str | None = None
        self._file_format_version: int | None = None
        self._version: int | None = None
        self._description: str | None = None
        self._index_strategy: str | None = None

        # adapters

        self._adapter_read_1: str | None = None
        self._adapter_read_2: str | None = None

        # index dataframes
        self._i7_indexes = pd.DataFrame()
        self._i5_indexes = pd.DataFrame()
        self._fixed_layout_data = pd.DataFrame()
        self._fixed_dual_indexes = pd.DataFrame()
        self._fixed_single_indexes = pd.DataFrame()
        self._standard_indexes = pd.DataFrame()

        # Meta

        self._i7_indexes_count = None
        self._i5_indexes_count = None

        self._import_filetype = None
        self._ilmn_index_strategy = None
        self._ilmn_fixed_layout = None
        self._index_i7_count = None
        self._index_i5_count = None
        self._ilmn_umi_compatible = None

        self._set_data(filepath)

    def _set_data(self, filepath: Path):
        self._read_file_to_indata(filepath)
        self._set_import_filetype(filepath.suffix)

        self._set_sections()

        self._set_index_kit_data()
        self._set_ilmn_index_strategy()
        self._set_adapters()
        self._set_fixed_layout()

        self._set_indexes()
        self._set_i7_indexes()
        self._set_i5_indexes()

        self._set_ilmn_umi_compatible()

        self._set_fixed_dual_indexes()
        self._set_standard_indexes()

    def _set_import_filetype(self, value):
        self._import_filetype = value

    def _set_ilmn_index_strategy(self):
        if "IndexStrategy" in self._index_kit:
            self._ilmn_index_strategy = self._index_kit["IndexStrategy"]

    def _set_ilmn_fixed_layout(self, value):
        self._ilmn_fixed_layout = value

    def _set_index_i7_count(self, value):
        self._index_i7_count = value

    def _set_index_i5_count(self, value):
        self._index_i5_count = value

    def _set_ilmn_umi_compatible(self):
        if "UMICompatible" in self._resources["Name"].values:
            umi_compat = bool(self._resources.loc[self._resources["Name"] == "UMICompatible", "Value"].values[0])
            self._ilmn_umi_compatible = umi_compat

    @property
    def import_filetype(self):
        return self._import_filetype

    @property
    def ilmn_seq_strategy(self):
        return self._ilmn_index_strategy

    @property
    def ilmn_fixed_layout(self):
        return self._ilmn_fixed_layout

    @property
    def index_i7_count(self):
        return self._index_i7_count

    @property
    def index_i5_count(self):
        return self._index_i5_count

    @property
    def ilmn_umi_compatible(self):
        return self._ilmn_umi_compatible

    def _set_indexes(self):

        indices_list = self._indata['Indices']
        indices_str = "\n".join(indices_list)

        self._indexes = pd.read_csv(StringIO(indices_str), sep='\t')

    def _set_i7_indexes(self):
        self._i7_indexes = self._indexes[self._indexes["IndexReadNumber"] == 1].copy()
        self._i7_indexes.rename(columns={'Name': 'IndexI7Name', 'Sequence': 'IndexI7'}, inplace=True)
        self._i7_indexes.drop(columns=['IndexReadNumber'], inplace=True)

        self._set_index_i7_count(self._i7_indexes.shape[0])

    def _set_i5_indexes(self):
        self._i5_indexes = self._indexes[self._indexes["IndexReadNumber"] == 2].copy()
        self._i5_indexes.rename(columns={'Name': 'IndexI5Name', 'Sequence': 'IndexI5'}, inplace=True)
        self._i5_indexes.drop(columns=['IndexReadNumber'], inplace=True)

        self._set_index_i5_count(self._i5_indexes.shape[0])

    def _set_fixed_dual_indexes(self):

        self._fixed_dual_indexes = (self._fixed_layout_data.drop(columns=['Type', 'Format', 'Value'])
                                    .merge(self._i7_indexes, on='IndexI7Name')
                                    .merge(self._i5_indexes, on='IndexI5Name')).copy()

    def _set_standard_indexes(self):
        self._standard_indexes = pd.concat([self._i7_indexes, self._i5_indexes], axis=1)

    def _set_fixed_layout(self):

        if "FixedLayout" in self._resources["Name"].values:
            fixed_layout = bool(self._resources.loc[self._resources["Name"] == "FixedLayout", "Value"].values[0])

            if not fixed_layout:
                return

            self._fixed_layout_data =  self._resources[
                self._resources['Type'].str.contains('FixedIndexPosition', na=False)
            ].rename(columns={'Name': 'Well'})

            self._fixed_layout_data[['IndexI7Name', 'IndexI5Name']] = self._fixed_layout_data['Value'].str.split('-', expand=True)

            self._set_ilmn_fixed_layout(fixed_layout)

        else:
            self._set_ilmn_fixed_layout(False)

    def _set_index_kit_data(self):
        self._checksum = self._index_kit.get('Checksum', None)
        self._name = self._index_kit.get('Name', None)
        self._display_name = self._index_kit.get('DisplayName', None)
        self._file_format_version = self._index_kit.get('FileFormatVersion', None)
        self._version = self._index_kit.get('Version', None)
        self._description = self._index_kit.get('Description', None)
        self._index_strategy = self._index_kit.get('IndexStrategy', None)

    def _set_resources(self):

        resources_list = self._indata['Resources']
        resources_str = "\n".join(resources_list)

        self._resources = pd.read_csv(StringIO(resources_str), sep='\t')

    def _set_adapters(self):
        if "Adapter" in self._resources["Name"].values:
            self._adapter_read_1 = self._resources.loc[self._resources["Name"] == "Adapter", "Value"].values[0]

        if "AdapterRead1" in self._resources["Name"].values:
            self._adapter_read_1 = self._resources.loc[self._resources["Name"] == "AdapterRead1", "Value"].values[0]

        if "AdapterRead2" in self._resources["Name"].values:
            self._adapter_read_2 = self._resources.loc[self._resources["Name"] == "AdapterRead2", "Value"].values[0]

    def _set_sections(self):
        self._set_index_kit()
        self._supported_library_prep_kits = self._indata.get('SupportedLibraryPrepKits', [])
        self._set_resources()
        self._set_indexes()

    def _read_file_to_indata(self, filepath: Path):
        sections = {}
        current_section = None
        content = filepath.read_text(encoding="utf-8")

        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                sections[current_section] = []
            else:
                sections[current_section].append(line)

        self._indata = sections

    def _set_index_kit(self):
        kit_section = self._indata.get('IndexKit') or self._indata.get('Kit', [])

        self._index_kit = {}

        for row in kit_section:
            key, value = row.strip().split('\t')
            self._index_kit[key] = value

    @property
    def supported_library_prep_kits(self) -> list | None:
        return self._supported_library_prep_kits

    @property
    def checksum(self) -> str | None:
        return self._checksum

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def display_name(self) -> str | None:
        return self._display_name

    @property
    def file_format_version(self) -> int | None:
        return self._file_format_version

    @property
    def version(self) -> str | None:
        return self._version

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def index_strategy(self) -> str | None:
        return self._index_strategy

    @property
    def adapter_read_1(self) -> str | None:
        return self._adapter_read_1

    @property
    def adapter_read_2(self) -> str | None:
        return self._adapter_read_2

    @property
    def i7_indexes(self) -> pd.DataFrame | None:
        return self._i7_indexes

    @property
    def i5_indexes(self) -> pd.DataFrame | None:
        return self._i5_indexes

    @property
    def fixed_layout_data(self) -> pd.DataFrame | None:
        return self._fixed_layout_data

    @property
    def fixed_dual_indexes(self) -> pd.DataFrame | None:
        return self._fixed_dual_indexes

    @property
    def fixed_single_indexes(self) -> pd.DataFrame | None:
        return self._fixed_single_indexes

    @property
    def standard_indexes(self) -> pd.DataFrame | None:
        return self._standard_indexes

    def __repr__(self):
        return f"IlluminaIndexData({self.__dict__})"