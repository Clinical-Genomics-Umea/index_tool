from typing import Dict, List


class ConfigObject:
    def __init__(self, kit_def: dict[str, bool, str, dict]):
        self._def = kit_def

    @property
    def config_type_name(self) -> str:
        return self._def.get('ConfigTypeName', "")

    @property
    def well(self) -> bool:
        return self._def.get('Well', None)

    @property
    def index_strategy(self) -> str:
        return self._def.get('IndexStrategy', None)

    @property
    def all_index_fields(self) -> List[str]:
        output = []

        for index_set_name in self._def['IndexSets']:
            output.extend(self._def['IndexSets'][index_set_name])

        return output

    @property
    def index_set_names(self) -> List[str]:
        return list(self._def['IndexSets'].keys())

    def index_set_fields_by_name(self, index_set_name: str) -> List[str]:
        return self._def['IndexSetFields'][index_set_name]

    @property
    def index_sets(self):
        return self._def["IndexSets"]