from typing import Dict, List


class ConfigObject:
    def __init__(self, kit_def: dict[str, bool, str, dict]):
        self._def = kit_def

    @property
    def config_type_name(self) -> str:
        return self._def.get('config_type_name', "")

    @property
    def well(self) -> bool:
        return self._def.get('well', None)

    @property
    def index_strategy(self) -> str:
        return self._def.get('index_strategy', None)

    @property
    def all_index_fields(self) -> List[str]:
        output = []

        for index_set_name in self._def['index_sets']:
            output.extend(self._def['index_sets'][index_set_name])

        return output

    @property
    def index_set_names(self) -> List[str]:
        return list(self._def['index_sets'].keys())

    def index_set_fields_by_name(self, index_set_name: str) -> List[str]:
        return self._def['index_set_fields'][index_set_name]

    @property
    def index_sets(self):
        return self._def["index_sets"]