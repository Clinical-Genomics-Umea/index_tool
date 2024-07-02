from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QComboBox, QHBoxLayout, QLabel, QWidget


class ResourcesSettings(QGroupBox):
    def __init__(self, kit_type_fields: dict):
        super().__init__()
        layout = QFormLayout()
        self.setTitle("Resources Settings")
        self.setFixedWidth(500)

        self.regex_index = QRegularExpression(r'^(?!.*x.*x)([IUN](?:\d+|x))+$')
        self.regex_read = QRegularExpression(r'^(?!.*x.*x)([YUN](?:\d+|x))+$')

        self.kit_type_fields = kit_type_fields
        print(kit_type_fields)

        self.widgets = {
            "adapter_read1": QLineEdit(),
            "adapter_read2": QLineEdit(),
            'kit_type': QComboBox(),
            'override_cycles_pattern_r1': QLineEdit(),
            'override_cycles_pattern_i1': QLineEdit(),
            'override_cycles_pattern_i2': QLineEdit(),
            'override_cycles_pattern_r2': QLineEdit(),
        }

        self.widgets['kit_type'].addItems(list(kit_type_fields))

        override_layout = QHBoxLayout()
        override_layout.setContentsMargins(0, 0, 0, 0)

        override_h_layout = QHBoxLayout()
        override_h_layout.setContentsMargins(0, 0, 0, 0)
        override_h_layout.addWidget(QLabel("read1"))
        override_h_layout.addWidget(QLabel("index1"))
        override_h_layout.addWidget(QLabel("index2"))
        override_h_layout.addWidget(QLabel("read2"))

        override_layout.addWidget(self.widgets['override_cycles_pattern_r1'])
        override_layout.addWidget(self.widgets['override_cycles_pattern_i1'])
        override_layout.addWidget(self.widgets['override_cycles_pattern_i2'])
        override_layout.addWidget(self.widgets['override_cycles_pattern_r2'])

        override_h_widget = QWidget()
        override_h_widget.setLayout(override_h_layout)

        override_widget = QWidget()
        override_widget.setLayout(override_layout)

        layout.addRow("adapter read1", self.widgets['adapter_read1'])
        layout.addRow("adapter read2", self.widgets['adapter_read2'])
        layout.addRow("kit type", self.widgets['kit_type'])

        layout.addRow("", override_h_widget)
        layout.addRow("override cycles pattern", override_widget)

        # Setting validators for input fields
        self.widgets['adapter_read1'].setValidator(AdapterValidator(self.widgets['adapter_read1']))
        self.widgets['adapter_read2'].setValidator(AdapterValidator(self.widgets['adapter_read2']))
        self.widgets['override_cycles_pattern_i1'].setValidator(
            IndexValidator(self.widgets['override_cycles_pattern_i1']))
        self.widgets['override_cycles_pattern_i2'].setValidator(
            IndexValidator(self.widgets['override_cycles_pattern_i2']))
        self.widgets['override_cycles_pattern_r1'].setValidator(
            ReadValidator(self.widgets['override_cycles_pattern_r1']))
        self.widgets['override_cycles_pattern_r2'].setValidator(
            ReadValidator(self.widgets['override_cycles_pattern_r2']))

        self.setLayout(layout)

    def set_layout_illumina(self, value):
        self.widgets['kit_type'].setCurrentText(value)

    def data(self):
        data_dict = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, QLineEdit):
                data_dict[key] = widget.text()
            elif isinstance(widget, QComboBox):
                data_dict[key] = widget.currentText()

        index_keys = ["override_cycles_pattern_i1", "override_cycles_pattern_i2"]

        for k in index_keys:
            if not self.regex_index.match(data_dict[k]).hasMatch():
                raise ValueError(f"Incomplete override cycle pattern field: {k}")

        read_keys = ["override_cycles_pattern_r1", "override_cycles_pattern_r2"]
        for k in read_keys:
            if not self.regex_read.match(data_dict[k]).hasMatch():
                raise ValueError(f"Incomplete override cycle pattern field: {k}")

        return data_dict


class IndexValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.regex = QRegularExpression(r'^(?!.*x.*x)([IUN](?:\d+|x))+$')

    def validate(self, input_string, pos):
        if input_string == "":
            return QValidator.Acceptable, input_string, pos

        # Check if the input matches the full pattern
        if self.regex.match(input_string).hasMatch():
            return QValidator.Acceptable, input_string, pos

        # Check if the input is a valid partial match
        partial_regex = QRegularExpression(r'^(?!.*x.*x)([IUN](?:\d+|x))*([IUN](?:\d*|x)?)?$')
        if partial_regex.match(input_string).hasMatch():
            return QValidator.Intermediate, input_string, pos

        return QValidator.Invalid, input_string, pos


class ReadValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.regex = QRegularExpression(r'^(?!.*x.*x)([YUN](?:\d+|x))+$')

    def validate(self, input_string, pos):
        if input_string == "":
            return QValidator.Acceptable, input_string, pos

        # Check if the input matches the full pattern
        if self.regex.match(input_string).hasMatch():
            return QValidator.Acceptable, input_string, pos

        # Check if the input is a valid partial match
        partial_regex = QRegularExpression(r'^(?!.*x.*x)([YUN](?:\d+|x))*([YUN](?:\d*|x)?)?$')
        if partial_regex.match(input_string).hasMatch():
            return QValidator.Intermediate, input_string, pos

        return QValidator.Invalid, input_string, pos


class AdapterValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.regex = QRegularExpression(r'^(?!.*x.*x)([YUN](?:\d+|x))+$')

    def validate(self, input_string, pos):
        valid_chars = 'ACGT+'

        for char in input_string:
            if char.upper() not in valid_chars:
                return QValidator.Invalid

        return QValidator.Acceptable

