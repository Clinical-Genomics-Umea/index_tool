from typing import Dict, List, Union


class KitTypeFields:
    def __init__(self, kit_type_data: Dict[str, List[Dict[str, Union[str, List[str]]]]]):
        if not kit_type_data or len(kit_type_data) != 1:
            raise ValueError("kit_type_data must contain exactly one key-value pair")
        self._kit_type = next(iter(kit_type_data))
        self._kit_type_data = kit_type_data[self._kit_type]

    @property
    def kit_type(self) -> str:
        return self._kit_type

    @property
    def data(self) -> Dict[str, List[Dict[str, Union[str, List[str]]]]]:
        return {self._kit_type: self._kit_type_data}

    @property
    def index_set_names(self) -> List[str]:
        return [_set['name'] for _set in self._kit_type_data if 'name' in _set]

    @property
    def fields(self) -> List[str]:
        return [field for _set in self._kit_type_data for field in _set.get('fields', [])]

    def index_set_fields(self, set_name: str) -> List[str]:
        for _index_set in self._kit_type_data:
            if _index_set.get('name') == set_name:
                return _index_set.get('fields', [])
        return []

    def field_container(self, field: str) -> str:
        for container in self._kit_type_data:
            if field in container.get('fields', []):
                return container.get('name', '')
        return ''

