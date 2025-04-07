from logging import Logger

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QLineEdit, QComboBox, QFormLayout, QGroupBox
from typing import Dict, Union

from modules.model.data_manager import DataManager


class IndexKitSettingsWidget(QGroupBox):
    def __init__(self, data_manager: DataManager, logger: Logger):
        super().__init__()
        self.setTitle("Index Kit Settings")
        self.setFixedWidth(500)
        self._data_manager = data_manager
        self._logger = logger

        self._name = self._create_name_input()
        self._display_name = QLineEdit()
        self._version = self._create_version_input()
        self._description = QLineEdit()

        self._setup_ui()

        self._name.textChanged.connect(self._save_name)
        self._display_name.textChanged.connect(self._save_display_name)
        self._version.textChanged.connect(self._save_version)
        self._description.textChanged.connect(self._save_description)

    def _save_name(self):
        self._data_manager.set_kit_name(self._name.text())

    def _save_display_name(self):
        self._data_manager.set_display_name(self._display_name.text())

    def _save_version(self):
        self._data_manager.set_version(self._version.text())

    def _save_description(self):
        self._data_manager.set_description(self._description.text())

    def _setup_ui(self):

        layout = QFormLayout()
        layout.addRow("name", self._name)
        layout.addRow("display name", self._display_name)
        layout.addRow("version", self._version)
        layout.addRow("description", self._description)

        self.setLayout(layout)

    @staticmethod
    def _create_name_input() -> QLineEdit:
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter name with no whitespace (e.g., GMS560_Index_Kit)")
        name_input.setValidator(NameValidator(name_input))
        return name_input

    @staticmethod
    def _create_version_input() -> QLineEdit:
        version_input = QLineEdit()
        version_input.setPlaceholderText("Enter version (e.g., 1.2.3)")
        version_input.setValidator(VersionValidator(version_input))
        return version_input

    def data(self) -> Dict[str, str]:
        data_dict = {key: widget.text() if isinstance(widget, QLineEdit) else widget.currentText()
                     for key, widget in self.widgets.items()}

        missing_required_fields = [item for item in ["name", "display_name", "version"] if not data_dict.get(item)]

        if missing_required_fields:
            raise ValueError(f"Missing required index kit fields: {', '.join(missing_required_fields)}")

        return data_dict


class VersionValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.regex = QRegularExpression(r'^(\d{1,3}\.){0,2}\d{1,3}$')

    def validate(self, input_string: str, pos: int) -> tuple:
        if not input_string:
            return QValidator.Acceptable, input_string, pos

        match = self.regex.match(input_string)
        if match.hasMatch():
            return QValidator.Acceptable, input_string, pos

        # Allow intermediate inputs
        if self.regex.match(input_string + '0').hasMatch():
            return QValidator.Intermediate, input_string, pos

        return QValidator.Invalid, input_string, pos


class NameValidator(QValidator):
    def validate(self, input_string: str, pos: int) -> tuple:
        if not input_string or input_string.isalnum() or '_' in input_string:
            return QValidator.Acceptable, input_string, pos
        return QValidator.Invalid, input_string, pos
