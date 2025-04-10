from PySide6.QtCore import QRegularExpression, Signal
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import (QGroupBox, QFormLayout, QLineEdit, QComboBox,
                               QHBoxLayout, QLabel, QWidget)

from modules.model.data_manager import DataManager


class ResourceSettingsWidget(QGroupBox):

    def __init__(self, data_manager: DataManager, logger):
        super().__init__("Resources Settings")

        # self._draggable_labels_widget = draggable_labels_widget
        self._data_manager = data_manager
        self._logger = logger

        self._adapter_read1_lineedit = QLineEdit()
        self._adapter_read2_lineedit = QLineEdit()
        self._config_type_name_combobox = QComboBox()
        self._override_cycles_pattern_r1_lineedit = QLineEdit()
        self._override_cycles_pattern_i1_lineedit = QLineEdit()
        self._override_cycles_pattern_i2_lineedit = QLineEdit()
        self._override_cycles_pattern_r2_lineedit = QLineEdit()

        self.setFixedWidth(500)
        self._setup()

        self._config_type_name_combobox.currentTextChanged.connect(self._save_kit_config_name)

        self._adapter_read1_lineedit.textChanged.connect(self._save_adapter_read1)
        self._adapter_read2_lineedit.textChanged.connect(self._save_adapter_read2)
        self._override_cycles_pattern_r1_lineedit.textChanged.connect(self._save_override_cycles_pattern_r1)
        self._override_cycles_pattern_i1_lineedit.textChanged.connect(self._save_override_cycles_pattern_i1)
        self._override_cycles_pattern_i2_lineedit.textChanged.connect(self._save_override_cycles_pattern_i2)
        self._override_cycles_pattern_r2_lineedit.textChanged.connect(self._save_override_cycles_pattern_r2)

    def _save_adapter_read1(self):
        self._data_manager.set_adapter_read_1(self._adapter_read1_lineedit.text())

    def _save_adapter_read2(self):
        self._data_manager.set_adapter_read_2(self._adapter_read2_lineedit.text())

    def _save_override_cycles_pattern_r1(self):
        self._data_manager.set_override_cycles_read_1(self._override_cycles_pattern_r1_lineedit.text())

    def _save_override_cycles_pattern_i1(self):
        self._data_manager.set_override_cycles_index_1(self._override_cycles_pattern_i1_lineedit.text())

    def _save_override_cycles_pattern_i2(self):
        self._data_manager.set_override_cycles_index_2(self._override_cycles_pattern_i2_lineedit.text())

    def _save_override_cycles_pattern_r2(self):
        self._data_manager.set_override_cycles_read_2(self._override_cycles_pattern_r2_lineedit.text())

    def _setup(self):
        form_layout = QFormLayout(self)
        self._config_type_name_combobox.addItems(self._data_manager.config_type_names)

        override_header_layout = QHBoxLayout()
        for label in ["read1", "index1", "index2", "read2"]:
            override_header_layout.addWidget(QLabel(label))

        override_lineedit_layout = QHBoxLayout()
        override_lineedit_layout.addWidget(self._override_cycles_pattern_r1_lineedit)
        override_lineedit_layout.addWidget(self._override_cycles_pattern_i1_lineedit)
        override_lineedit_layout.addWidget(self._override_cycles_pattern_i2_lineedit)
        override_lineedit_layout.addWidget(self._override_cycles_pattern_r2_lineedit)

        form_layout.addRow("adapter read1", self._adapter_read1_lineedit)
        form_layout.addRow("adapter read2", self._adapter_read2_lineedit)
        form_layout.addRow("config name", self._config_type_name_combobox)
        form_layout.addRow("", override_header_layout)
        form_layout.addRow("override cycles pattern", override_lineedit_layout)

        self._save_kit_config_name()
        self.set_validators()

        self._adapter_read1_lineedit.textChanged.connect(self.on_adapter_read1_lineedit_change)
        self._adapter_read2_lineedit.textChanged.connect(self.on_adapter_read2_lineedit_change)

        self._override_cycles_pattern_i1_lineedit.setText(self._data_manager.override_cycles_index_1)
        self._override_cycles_pattern_i2_lineedit.setText(self._data_manager.override_cycles_index_2)
        self._override_cycles_pattern_r1_lineedit.setText(self._data_manager.override_cycles_read_1)
        self._override_cycles_pattern_r2_lineedit.setText(self._data_manager.override_cycles_read_2)

        self._override_cycles_pattern_i1_lineedit.textChanged.connect(self.on_override_cycles_pattern_i1_lineedit_change)
        self._override_cycles_pattern_i2_lineedit.textChanged.connect(self.on_override_cycles_pattern_i2_lineedit_change)
        self._override_cycles_pattern_r1_lineedit.textChanged.connect(self.on_override_cycles_pattern_r1_lineedit_change)
        self._override_cycles_pattern_r2_lineedit.textChanged.connect(self.on_override_cycles_pattern_r2_lineedit_change)

        self._config_type_name_combobox.currentTextChanged.connect(self._on_selected_kit_type_name_change)



    def set_validators(self):
        self._adapter_read1_lineedit.setValidator(AdapterValidator())
        self._adapter_read2_lineedit.setValidator(AdapterValidator())
        self._override_cycles_pattern_i1_lineedit.setValidator(IndexValidator())
        self._override_cycles_pattern_i2_lineedit.setValidator(IndexValidator())
        self._override_cycles_pattern_r1_lineedit.setValidator(ReadValidator())
        self._override_cycles_pattern_r2_lineedit.setValidator(ReadValidator())

    def set_adapter_read_1(self):
        self._adapter_read1_lineedit.setText(self._data_manager.adapter_read_1)

    def set_adapter_read_2(self):
        self._adapter_read2_lineedit.setText(self._data_manager.adapter_read_2)

    def set_override_cycles_pattern_i1(self):
        self._override_cycles_pattern_i1_lineedit.setText(self._data_manager.override_cycles_index_1)

    def set_override_cycles_pattern_i2(self):
        self._override_cycles_pattern_i2_lineedit.setText(self._data_manager.override_cycles_index_2)

    def set_override_cycles_pattern_r1(self):
        self._override_cycles_pattern_r1_lineedit.setText(self._data_manager.override_cycles_read_1)

    def set_override_cycles_pattern_r2(self):
        self._override_cycles_pattern_r2_lineedit.setText(self._data_manager.override_cycles_read_2)

    def _save_kit_config_name(self):
        self._data_manager.set_kit_config_name(self._config_type_name_combobox.currentText())

    def on_adapter_read1_lineedit_change(self):
        value = self._adapter_read1_lineedit.text()
        self._data_manager.set_adapter_read_1(value)

    def on_adapter_read2_lineedit_change(self):
        value = self._adapter_read2_lineedit.text()
        self._data_manager.set_adapter_read_2(value)

    def on_override_cycles_pattern_i1_lineedit_change(self):
        value = self._override_cycles_pattern_i1_lineedit.text()
        self._data_manager.set_override_cycles_index_1(value)

    def on_override_cycles_pattern_i2_lineedit_change(self):
        value = self._override_cycles_pattern_i2_lineedit.text()
        self._data_manager.set_override_cycles_index_2(value)

    def on_override_cycles_pattern_r1_lineedit_change(self):
        value = self._override_cycles_pattern_r1_lineedit.text()
        self._data_manager.set_override_cycles_read_1(value)

    def on_override_cycles_pattern_r2_lineedit_change(self):
        value = self._override_cycles_pattern_r2_lineedit.text()
        self._data_manager.set_override_cycles_read_2(value)

    def _on_selected_kit_type_name_change(self):
        self._data_manager.set_kit_config_name(self._config_type_name_combobox.currentText())


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
    regex = QRegularExpression(r'^(?!.*{i}.*{i})([IUN](?:\d+|{i}))+$')

    def __init__(self, parent=None):
        super().__init__(self.regex.pattern(), parent)


class ReadValidator(BaseValidator):
    regex = QRegularExpression(r'^(?!.*{r}.*{r})([YUN](?:\d+|{r}))+$')

    def __init__(self, parent=None):
        super().__init__(self.regex.pattern(), parent)


class AdapterValidator(QValidator):
    def validate(self, input_string, pos):
        return QValidator.Acceptable if set(input_string.upper()) <= set('ACGT+') else QValidator.Invalid

