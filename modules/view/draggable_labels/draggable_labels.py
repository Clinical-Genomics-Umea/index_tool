from logging import Logger

from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy,
                               QSpacerItem, QLabel, QGroupBox)

from modules.model.data_manager import DataManager


class DraggableLabelsContainer(QGroupBox):
    def __init__(self, data_manager: DataManager, logger: Logger):
        super().__init__("Draggable field labels")
        self._data_manager = data_manager
        self._logger = logger
        self.setFixedWidth(1006)
        self.layout = QVBoxLayout(self)
        self.kit_type_label_widgets = {}

        self._setup()

    def _setup(self):

        for kit_type_name, kit_object in self._data_manager.kit_type_definition_data.items():
            kit_fields_widget = self._create_kit_fields_widget(kit_object.all_index_set_fields)
            self.kit_type_label_widgets[kit_type_name] = kit_fields_widget
            self.layout.addWidget(kit_fields_widget)
            print("draggable_labels_container", kit_type_name)

        self.show_labels()

    def show_labels(self):
        print("show labels")
        selected_kit_type_name = self._data_manager.selected_kit_type_name

        print(selected_kit_type_name)

        for labels_kit_type_name, widget in self.kit_type_label_widgets.items():
            print(labels_kit_type_name)

            widget.setVisible(labels_kit_type_name == selected_kit_type_name)

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