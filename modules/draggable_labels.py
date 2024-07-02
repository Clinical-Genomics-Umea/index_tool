from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QSpacerItem, QLabel, QGroupBox


class DraggableLabelsContainer(QGroupBox):
    def __init__(self, kit_type_fields):
        super().__init__()

        self.kit_type_fields = kit_type_fields

        self.setFixedWidth(1006)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setTitle("Draggable Header Labels")

        self.kit_type_label_widgets = {}

        for kit_type_name, kit_object in kit_type_fields.items():
            self.kit_type_label_widgets[kit_type_name] = QWidget()
            self.kit_type_label_widgets[kit_type_name].setFixedWidth(1006)

            field_layout = QHBoxLayout()
            field_layout.setContentsMargins(0, 0, 0, 0)

            for field in kit_object.fields:
                field_layout.addWidget(DraggableLabel(field))

            field_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            self.kit_type_label_widgets[kit_type_name].setLayout(field_layout)
            self.layout.addWidget(self.kit_type_label_widgets[kit_type_name])

            first_key = next(iter(self.kit_type_fields))
            self.selected_kit_type_labels = set(self.kit_type_fields[first_key].fields)
            self.show_labels(first_key)

    def show_labels(self, selected_kit_type_name):
        for kit_type_name in self.kit_type_label_widgets:
            if kit_type_name == selected_kit_type_name:
                self.kit_type_label_widgets[kit_type_name].show()
            else:
                self.kit_type_label_widgets[kit_type_name].hide()


class DraggableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                border: 1px solid lightgrey;
                text-align: center;
            }
        """)
        self.setFixedWidth(100)
        self.setFixedHeight(30)
        self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.text())
            drag.setMimeData(mime_data)
            drag.exec(Qt.MoveAction)

