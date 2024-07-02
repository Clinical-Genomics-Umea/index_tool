from pathlib import Path
import pandas as pd
from camel_converter import to_snake
from io import StringIO


class IlluminaFormatIndexKitDefinition:
    def __init__(self, ilmn_index_file_path: Path):
        self.indata = self._ingest_index_file(ilmn_index_file_path)
        self.index_kit = self.indata['index_kit']
        self.supported_library_prep_kits = self.indata['supported_library_prep_kits']
        self.resources = self._get_resources()
        self.indices_i7 = self._get_index_df(1, "i7")
        self.indices_i5 = self._get_index_df(2, "i5")
        self.indices_dual_fixed = self._get_fixed_index_df("DualOnly")
        self.indices_single_fixed = self._get_fixed_index_df("SingleOnly")

    def _ingest_index_file(self, index_file: Path) -> dict:
        sections = self._parse_sections(index_file)
        return {
            'index_kit': self._parse_index_kit(sections),
            'supported_library_prep_kits': sections.get('SupportedLibraryPrepKits', []),
            'resources': self._parse_resources(sections),
            'indices': self._parse_indices(sections)
        }

    @staticmethod
    def _parse_sections(index_file: Path) -> dict:
        sections = {}
        current_section = None
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
        return sections

    @staticmethod
    def _parse_index_kit(sections: dict) -> dict:
        kit_section = sections.get('IndexKit') or sections.get('Kit', [])
        return {to_snake(key): value for key, value in (row.strip().split('\t') for row in kit_section)}

    @staticmethod
    def _parse_resources(sections: dict) -> pd.DataFrame:
        if 'Resources' not in sections:
            return pd.DataFrame()
        resources_content = '\n'.join(sections['Resources'])
        df = pd.read_csv(StringIO(resources_content), sep='\t')
        return df.rename(columns=lambda x: to_snake(x))

    @staticmethod
    def _parse_indices(sections: dict) -> pd.DataFrame:
        if 'Indices' not in sections:
            return pd.DataFrame()
        indices_content = '\n'.join(sections['Indices'])
        df = pd.read_csv(StringIO(indices_content), sep='\t')
        return df.rename(columns=lambda x: to_snake(x))

    def _get_resources(self) -> dict:
        other_resources = self.indata['resources'][
            ~self.indata['resources']['type'].str.contains('FixedIndexPosition', na=False)
        ].copy()
        other_resources['snake_name'] = other_resources['name'].apply(to_snake)
        return dict(zip(other_resources['snake_name'], other_resources['value']))

    def _get_index_df(self, index_read_number: int, index_type: str) -> pd.DataFrame:
        return (self.indata['indices'][self.indata['indices']['index_read_number'] == index_read_number]
                .rename(columns={"name": f"index_{index_type}_name", "sequence": f"index_{index_type}"})
                .drop(columns=['index_read_number'])
                .reset_index(drop=True))

    def _get_fixed_index_df(self, strategy: str) -> pd.DataFrame:
        if self.index_kit['index_strategy'] != strategy or not self.indata['resources']['type'].str.contains(
                'FixedIndexPosition', na=False).any():
            return pd.DataFrame()

        fixed_indices = self.indata['resources'][
            self.indata['resources']['type'].str.contains('FixedIndexPosition', na=False)
        ].rename(columns={'name': 'fixed_pos'})

        if strategy == "DualOnly":
            fixed_indices[['index_i7_name', 'index_i5_name']] = fixed_indices['value'].str.split('-', expand=True)
            return (fixed_indices.drop(columns=['type', 'format', 'value'])
                    .merge(self.indices_i7, on='index_i7_name')
                    .merge(self.indices_i5, on='index_i5_name'))
        else:  # SingleOnly
            fixed_indices['index_i7_name'] = fixed_indices['value']
            return fixed_indices.drop(columns=['type', 'format', 'value'])

    @property
    def kit_type(self) -> str:
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
    def indices_df(self) -> pd.DataFrame:
        if not self.indices_dual_fixed.empty:
            return self.indices_dual_fixed
        elif not self.indices_i7.empty and not self.indices_i5.empty:
            return pd.concat([self.indices_i7, self.indices_i5], axis=1)
        elif not self.indices_i7.empty:
            return self.indices_i7
        else:
            return pd.DataFrame()
