from logging import Logger

from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy,
                               QSpacerItem, QLabel, QGroupBox, QComboBox, QFormLayout)

from modules.model.data_manager import DataManager


class DraggableLabelsContainer(QGroupBox):
    def __init__(self, data_manager: DataManager, logger: Logger):
        super().__init__("Draggable field labels")
        self._data_manager = data_manager
        self._logger = logger
        self.setFixedWidth(1006)
        self.layout = QVBoxLayout(self)

        self._config_name_combobox = QComboBox()

        self.kit_type_label_widgets = {}

        self._config_name_combobox.currentTextChanged.connect(self._set_selected_config_name)

        self._setup()

    def _setup(self):

        form_layout = QFormLayout()
        form_layout.addRow("config name", self._config_name_combobox)
        self._config_name_combobox.addItems(self._data_manager.config_name_list)
        self.layout.addLayout(form_layout)

        for kit_type_name, kit_object in self._data_manager.config_definition_data.items():
            kit_fields_widget = self._create_kit_fields_widget(kit_object.all_index_fields)
            self.kit_type_label_widgets[kit_type_name] = kit_fields_widget
            self.layout.addWidget(kit_fields_widget)

        self._set_selected_config_name()
        self.show_labels()

    def show_labels(self):
        selected_config_name = self._data_manager.config_name

        for labels_kit_type_name, widget in self.kit_type_label_widgets.items():
            widget.setVisible(labels_kit_type_name == selected_config_name)

    def _set_selected_config_name(self):
        current_config_name = self._config_name_combobox.currentText()
        self._data_manager.set_config_name(current_config_name)

    @staticmethod
    def _create_kit_fields_widget(fields):
        widget = QWidget()
        widget.setFixedWidth(1006)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        for field in fields:
            layout.addWidget(DraggableLabel(field))

        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        return widget



    def init_labels(self):
        self._setup()


class DraggableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QLabel {
                border: 1px solid lightgrey;
                text-align: center;
            }
        """)
        self.setFixedSize(100, 30)
        self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.text())
            drag.setMimeData(mime_data)
            drag.exec(Qt.MoveAction)