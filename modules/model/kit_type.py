from typing import Dict, List


class KitDefObject:
    def __init__(self, kit_def: dict[str, str, int, dict]):
        self._kit_def = kit_def

    @property
    def kit_name(self) -> str:
        return self._kit_def.get('name', "")

    @property
    def type(self) -> str:
        return self._kit_def.get('kit_type', "")

    @property
    def well_field_count(self) -> int:
        return self._kit_def.get('well_field_count', None)

    @property
    def all_index_set_fields(self) -> List[str]:
        output = []

        for index_set_name in self._kit_def['index_set_fields']:
            output.extend(self._kit_def['index_set_fields'][index_set_name])

        return output

    @property
    def index_set_names(self) -> List[str]:
        return list(self._kit_def['index_set_fields'].keys())

    def index_set_fields(self, index_set_name: str) -> List[str]:
        return self._kit_def['index_set_fields'][index_set_name]