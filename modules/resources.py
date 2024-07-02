from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import (QGroupBox, QFormLayout, QLineEdit, QComboBox,
                               QHBoxLayout, QLabel, QWidget)


class ResourcesSettings(QGroupBox):
    def __init__(self, kit_type_fields: dict):
        super().__init__("Resources Settings")
        self.setFixedWidth(500)
        self.kit_type_fields = kit_type_fields
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        self.widgets = {
            "adapter_read1": QLineEdit(),
            "adapter_read2": QLineEdit(),
            'kit_type': QComboBox(),
            'override_cycles_pattern_r1': QLineEdit(),
            'override_cycles_pattern_i1': QLineEdit(),
            'override_cycles_pattern_i2': QLineEdit(),
            'override_cycles_pattern_r2': QLineEdit(),
        }

        self.widgets['kit_type'].addItems(list(self.kit_type_fields))

        override_layout = QHBoxLayout()
        override_h_layout = QHBoxLayout()
        for label in ["read1", "index1", "index2", "read2"]:
            override_h_layout.addWidget(QLabel(label))

        for widget in ['r1', 'i1', 'i2', 'r2']:
            override_layout.addWidget(self.widgets[f'override_cycles_pattern_{widget}'])

        override_h_widget = QWidget()
        override_h_widget.setLayout(override_h_layout)

        override_widget = QWidget()
        override_widget.setLayout(override_layout)

        layout.addRow("adapter read1", self.widgets['adapter_read1'])
        layout.addRow("adapter read2", self.widgets['adapter_read2'])
        layout.addRow("kit type", self.widgets['kit_type'])
        layout.addRow("", override_h_widget)
        layout.addRow("override cycles pattern", override_widget)

        self.set_validators()

    def set_validators(self):
        self.widgets['adapter_read1'].setValidator(AdapterValidator())
        self.widgets['adapter_read2'].setValidator(AdapterValidator())
        self.widgets['override_cycles_pattern_i1'].setValidator(IndexValidator())
        self.widgets['override_cycles_pattern_i2'].setValidator(IndexValidator())
        self.widgets['override_cycles_pattern_r1'].setValidator(ReadValidator())
        self.widgets['override_cycles_pattern_r2'].setValidator(ReadValidator())

    def set_layout_illumina(self, value):
        self.widgets['kit_type'].setCurrentText(value)

    def data(self):
        data_dict = {key: widget.text() if isinstance(widget, QLineEdit) else widget.currentText()
                     for key, widget in self.widgets.items()}

        for k in ["override_cycles_pattern_i1", "override_cycles_pattern_i2"]:
            if not IndexValidator.regex.match(data_dict[k]).hasMatch():
                raise ValueError(f"Incomplete override cycle pattern field: {k}")

        for k in ["override_cycles_pattern_r1", "override_cycles_pattern_r2"]:
            if not ReadValidator.regex.match(data_dict[k]).hasMatch():
                raise ValueError(f"Incomplete override cycle pattern field: {k}")

        return data_dict


class BaseValidator(QValidator):
    def __init__(self, regex, parent=None):
        super().__init__(parent)
        self.regex = QRegularExpression(regex)

    def validate(self, input_string, pos):
        if not input_string:
            return QValidator.Acceptable, input_string, pos

        if self.regex.match(input_string).hasMatch():
            return QValidator.Acceptable, input_string, pos

        partial_regex = QRegularExpression(self.regex.pattern().replace('+', '*') + r'([' + self.regex.pattern()[2] + r'](?:\d*|x)?)?$')
        if partial_regex.match(input_string).hasMatch():
            return QValidator.Intermediate, input_string, pos

        return QValidator.Invalid, input_string, pos


class IndexValidator(BaseValidator):
    regex = QRegularExpression(r'^(?!.*x.*x)([IUN](?:\d+|x))+$')

    def __init__(self, parent=None):
        super().__init__(self.regex.pattern(), parent)


class ReadValidator(BaseValidator):
    regex = QRegularExpression(r'^(?!.*x.*x)([YUN](?:\d+|x))+$')

    def __init__(self, parent=None):
        super().__init__(self.regex.pattern(), parent)


class AdapterValidator(QValidator):
    def validate(self, input_string, pos):
        return QValidator.Acceptable if set(input_string.upper()) <= set('ACGT+') else QValidator.Invalid

