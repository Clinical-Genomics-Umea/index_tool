from pathlib import Path
from modules.model.kit_def_loader import mk_kit_def_obj
from PySide6.QtCore import QObject
import yaml


class ConfigurationManager(QObject):
    def __init__(self, logger):
        super().__init__()

        self._kit_type_definition_file = Path("config/kit_type_fields.yaml")
        self._kit_type_definition_data: dict | None = None

        self._setup()

    def _setup(self):

        try:

            with open(self._kit_type_definition_file, 'r') as file:
                kit_def_data = yaml.safe_load(file)
        except Exception as e:
            print(f"Error: {str(e)}")
            # self.show_notification(f"Error: {str(e)}", warn=True)

        self._kit_type_definition_data = mk_kit_def_obj(kit_def_data)

    @property
    def kit_type_definition_data(self) -> dict:
        return self._kit_type_definition_data


    def kit_type_definition_obj(self, name):
        return self._kit_type_definition_data[name]