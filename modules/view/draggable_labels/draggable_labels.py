from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy,
                               QSpacerItem, QLabel, QGroupBox)

from modules.model.configuration_manager import ConfigurationManager


class DraggableLabelsContainer(QGroupBox):
    def __init__(self, configuration_manager: ConfigurationManager):
        super().__init__("Draggable Header Labels")
        self._configuration_manager = configuration_manager
        self.setFixedWidth(1006)
        self.layout = QVBoxLayout(self)
        self.kit_type_label_widgets = {}

        self._setup()

    def _setup(self):

        for kit_type_name, kit_object in self._configuration_manager.kit_type_definition_data.items():
            widget = self._create_kit_type_widget(kit_object.all_index_set_fields)
            self.kit_type_label_widgets[kit_type_name] = widget
            self.layout.addWidget(widget)

        first_key = list(self.kit_type_label_widgets.keys())[0]
        self.show_labels(first_key)

    def _create_kit_type_widget(self, fields):
        widget = QWidget()
        widget.setFixedWidth(1006)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        for field in fields:
            layout.addWidget(DraggableLabel(field))

        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        return widget

    def show_labels(self, selected_kit_type_name):
        for kit_type_name, widget in self.kit_type_label_widgets.items():
            widget.setVisible(kit_type_name == selected_kit_type_name)


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