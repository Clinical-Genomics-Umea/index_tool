

class KitTypeFields:
    def __init__(self, kit_type_data: dict):
        self.kit_type_data = kit_type_data

    def kit_type(self):
        return list(self.kit_type_data)[0]

    def all_container_names(self):
        kit_type = self.kit_type()
        container_names = []

        for container in self.kit_type_data[kit_type]:
            container_names.append(container['container_name'])

        return container_names

    def all_fields(self):
        kit_type = self.kit_type()
        all_fields = []

        for container in self.kit_type_data[kit_type]:
            all_fields.extend(container['fields'])

        return all_fields

    def container_fields(self, container_name):
        kit_type = self.kit_type()

        for container in self.kit_type_data[kit_type]:
            if container['container_name'] == container_name:
                return container['fields']

    def field_container(self, field):
        kit_type = self.kit_type()

        for container in self.kit_type_data[kit_type]:
            if field in container['fields']:
                return container['container_name']
