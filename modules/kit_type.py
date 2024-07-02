

class KitTypeFields:
    def __init__(self, kit_type_data: dict):
        self._kit_type_data = kit_type_data

    @property
    def data(self):
        return self._kit_type_data

    @property
    def kit_type(self):
        return list(self._kit_type_data)[0]

    @property
    def data(self):
        return self._kit_type_data

    @property
    def index_set_names(self):
        _kit_type = self.kit_type
        return [_set.get('name') for _set in self._kit_type_data[_kit_type]]

    @property
    def fields(self):
        _kit_type = self.kit_type
        _fields = []

        for _index_set in self._kit_type_data[_kit_type]:
            _fields.extend(_index_set.get('fields'))

        return _fields

    def index_set_fields(self, set_name):
        _kit_type = self.kit_type

        for _index_set in self._kit_type_data[_kit_type]:
            if _index_set.get('name') == set_name:
                return _index_set.get('fields')

    def field_container(self, field):
        kit_type = self.kit_type()

        for container in self._kit_type_data[kit_type]:
            if field in container['fields']:
                return container['name']
