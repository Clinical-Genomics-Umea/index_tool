from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QLineEdit, QComboBox, QFormLayout, QGroupBox


class IndexKitSettings(QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        self.setTitle("Index Kit Settings")
        self.setFixedWidth(500)

        self.widgets = {
            "name": QLineEdit(),
            "display_name": QLineEdit(),
            'version': QLineEdit(),
            'description': QLineEdit(),
        }

        for name, widget in self.widgets.items():
            layout.addRow(name, widget)

        self.widgets['version'].setPlaceholderText("Enter version (e.g., 1.2.3)")
        version_validator = VersionValidator(self.widgets['version'])
        self.widgets['version'].setValidator(version_validator)

        self.widgets['name'].setPlaceholderText("Enter name with no whitespace (e.g., GMS560_Index_Kit)")
        name_validator = NameValidator(self.widgets['name'])
        self.widgets['name'].setValidator(name_validator)

        self.setLayout(layout)

    def settings(self):
        data = dict()
        for key, widget in self.widgets.items():
            if isinstance(widget, QLineEdit):
                data[key] = widget.text()
            elif isinstance(widget, QComboBox):
                data[key] = widget.currentText()

        return data


class VersionValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        # This regex allows 1-3 groups of digits separated by dots
        self.regex = QRegularExpression(r'^(\d+\.){0,2}\d+$')

    def validate(self, input_string, pos):
        if input_string == "":
            return QValidator.Acceptable, input_string, pos

        match = self.regex.match(input_string)
        if match.hasMatch():
            # Check if each number is within a valid range (0-999)
            parts = input_string.split('.')
            if all(0 <= int(part) <= 999 for part in parts):
                return QValidator.Acceptable, input_string, pos

        # Allow intermediate inputs
        if self.regex.match(input_string + '0').hasMatch():
            return QValidator.Intermediate, input_string, pos

        return QValidator.Invalid, input_string, pos


class NameValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        # This regex allows 1-3 groups of digits separated by dots

    def validate(self, input_string, pos):
        if input_string == "":
            return QValidator.Acceptable, input_string, pos

        for char in input_string:
            if char.isspace():
                return QValidator.Invalid

        return QValidator.Acceptable



