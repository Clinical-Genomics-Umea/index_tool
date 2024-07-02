from pathlib import Path
import json
from io import StringIO

import pandas as pd
from camel_converter import to_snake

kit_types = [
    'fixed_single_index', 
    'fixed_dual_index', 
    'standard_pos_dual_index', 
    'standard_pos_single_index', 
    'standard_dual_index', 
    'standard_single_index'
]


class IlluminaFormatIndexKitDefinition:

    def __init__(self, ilmn_index_file_path):

        self.overridecycles_pattern = None
        self.index_kit = None
        self.supported_library_prep_kits = None
        self.resources = None
        self.indices_i7 = pd.DataFrame()
        self.indices_i5 = pd.DataFrame
        self.indices_dual_fixed = pd.DataFrame()
        self.indices_single_fixed = pd.DataFrame()
        self.index_import_error = None

        self.indata = {}
        self._ingest_index_file(ilmn_index_file_path)

        self.index_kit = self.indata['index_kit']
        self.supported_library_prep_kits = self.indata['supported_library_prep_kits']

        self.indices_i7 = self._get_i7_df()
        self.indices_i5 = self._get_i5_df()
        self.resources = self._get_resources()
        self.indices_dual_fixed = self._get_index_dual_fixed_df()
        self.indices_single_fixed = self._get_index_single_fixed_df()

    def _get_i7_df(self):
        return (self.indata['indices'][self.indata['indices']['index_read_number'] == 1]
         .copy()
         .rename(columns={"name": "index_i7_name", "sequence": "index_i7"})
         .drop(columns=['index_read_number'])
         .reset_index(drop=True)
         )

    def _get_i5_df(self):
        return (self.indata['indices'][self.indata['indices']['index_read_number'] == 2]
                .copy()
                .rename(columns={"name": "index_i5_name", "sequence": "index_i5"})
                .drop(columns=['index_read_number'])
                .reset_index(drop=True)
                )

    def _get_resources(self):
        _other_resources = self.indata['resources'][
            ~self.indata['resources']['type'].str.contains('FixedIndexPosition')].copy()
        _other_resources['snake_name'] = _other_resources['name'].apply(to_snake)

        return dict(zip(_other_resources['snake_name'], _other_resources['value']))

    def _get_index_dual_fixed_df(self):
        if self.index_kit['index_strategy'] == "DualOnly" and self.indata['resources']['type'].str.contains(
                'FixedIndexPosition').any():
            _idxs_dual_fix_ = self.indata['resources'][
                self.indata['resources']['type'].str.contains('FixedIndexPosition')]

            _idxs_dual_fix_ = _idxs_dual_fix_.rename(columns={'name': 'fixed_pos'})
            _idxs_dual_fix_[['index_i7_name', 'index_i5_name']] = _idxs_dual_fix_['value'].str.split('-',
                                                                                                     expand=True)
            _idxs_dual_fix_ = _idxs_dual_fix_.drop(columns=['type', 'format', 'value']).reset_index(
                drop=True)

            return (_idxs_dual_fix_.merge(self.indices_i7, on='index_i7_name')
                    .merge(self.indices_i5, on='index_i5_name')
                    .copy())

        else:
            return pd.DataFrame()

    def _get_index_single_fixed_df(self):
        if self.index_kit['index_strategy'] == "SingleOnly" and self.indata['resources']['type'].str.contains(
                'FixedIndexPosition').any():
            _idxs_single_fix_ = self.indata['resources'][
                self.indata['resources']['type'].str.contains('FixedIndexPosition')]

            _idxs_single_fix_ = _idxs_single_fix_.rename(columns={'name': 'fixed_pos'})
            _idxs_single_fix_['index_i7_name'] = _idxs_single_fix_['value']
            _idxs_single_fix_ = _idxs_single_fix_.drop(columns=['type', 'format', 'value']).reset_index(
                drop=True)

            return _idxs_single_fix_.copy()

        else:
            return pd.DataFrame()

    @property
    def kit_type(self):
        # kit_types = [
        #     'fixed_single_index',
        #     'fixed_dual_index',
        #     'standard_pos_dual_index',
        #     'standard_pos_single_index',
        #     'standard_dual_index',
        #     'standard_single_index'
        # ]

        if not self.indices_single_fixed.empty:
            return 'fixed_single_index'

        elif not self.indices_dual_fixed.empty:
            return 'fixed_dual_index'

        elif not self.indices_i7.empty and not self.indices_i5.empty:
            return 'standard_dual_index'

        elif not self.indices_i7.empty:
            return 'standard_single_index'

        else:
            return None

    @property
    def indices_df(self):
        print(self.indices_dual_fixed)
        if not self.indices_dual_fixed.empty:
            return self.indices_dual_fixed

        elif not self.indices_i7.empty and not self.indices_i5.empty:
            return pd.concat([self.indices_i7, self.indices_i5], axis=1)

        elif not self.indices_i7.empty:
            return self.indices_i7

    def _ingest_index_file(self, index_file):
        sections = {}
        current_section = None

        resources_orig_header = ["Name", "Type", "Format", "Value"]
        resources_snake_header_dict = {x: to_snake(x) for x in resources_orig_header}
        resources_snake_header = list(resources_snake_header_dict.values())

        indices_orig_header = ["Name", "Sequence", "IndexReadNumber"]
        indices_snake_header_dict = {x: to_snake(x) for x in indices_orig_header}
        indices_snake_header = list(indices_snake_header_dict.values())

        content = index_file.read_text(encoding="utf-8")

        for line in content.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                sections[current_section] = []
            else:
                sections[current_section].append(line)

        if 'IndexKit' in sections or 'Kit' in sections:
            self.indata['index_kit'] = {to_snake(key): value for key, value in
                                        (row.strip().split('\t') for row in sections['IndexKit'])}

        if 'SupportedLibraryPrepKits' in sections:
            self.indata['supported_library_prep_kits'] = [row.strip() for row in sections['SupportedLibraryPrepKits']]

        if 'Resources' in sections:
            resources_content = '\n'.join(sections['Resources'])

            self.indata['resources'] = pd.read_csv(StringIO(resources_content), sep='\t', header=0)
            self.indata['resources'] = self.indata['resources'].rename(columns=resources_snake_header_dict).copy()
            self.indata['resources'] = self.indata['resources'][resources_snake_header].copy()

        if 'Indices' in sections:
            indexes_content = '\n'.join(sections['Indices'])
            self.indata['indices'] = pd.read_csv(StringIO(indexes_content), sep='\t', header=0)
            self.indata['indices'] = self.indata['indices'].rename(columns=indices_snake_header_dict).copy()
            self.indata['indices'] = self.indata['indices'][indices_snake_header].copy()

    # def _make_output_dict(self):
    #     return {
    #         'index_kit': self.index_kit,
    #         'resources': self.resources,
    #         'indices_i7': self._df_to_json_compat(self.indices_i7),
    #         'indices_i5': self._df_to_json_compat(self.indices_i5),
    #         'indices_dual_fixed': self._df_to_json_compat(self.indices_dual_fixed),
    #         'supported_library_prep_kits': self.supported_library_prep_kits,
    #     }
    #
    # @staticmethod
    # def _df_to_json_compat(data):
    #     if isinstance(data, pd.DataFrame):
    #         return data.to_dict(orient='records')
    #     if data is None:
    #         return pd.DataFrame().to_dict(orient='records')

