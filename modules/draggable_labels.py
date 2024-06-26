from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QSpacerItem, QLabel, QGroupBox


class DraggableLabelsContainer(QGroupBox):
    def __init__(self, index_label_sets):
        super().__init__()

        self.index_label_sets = index_label_sets

        self.setFixedWidth(1006)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setTitle("Draggable Header Labels")

        self.index_label_sets = index_label_sets

        self.label_widgets = {}

        for label_set_name, label_set in index_label_sets.items():
            self.label_widgets[label_set_name] = QWidget()
            self.label_widgets[label_set_name].setFixedWidth(1006)

            label_layout = QHBoxLayout()
            label_layout.setContentsMargins(0, 0, 0, 0)

            for label in label_set:
                label_layout.addWidget(DraggableLabel(label))

            label_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            self.label_widgets[label_set_name].setLayout(label_layout)
            self.layout.addWidget(self.label_widgets[label_set_name])

            first_key = next(iter(self.index_label_sets))
            self.selected_labels = set(self.index_label_sets[first_key])
            self.show_labels(first_key)

    def show_labels(self, selected_label_name):
        for label_set_name in self.label_widgets:
            if label_set_name == selected_label_name:
                self.label_widgets[label_set_name].show()
                self.selected_labels = set(self.index_label_sets[label_set_name])
            else:
                self.label_widgets[label_set_name].hide()


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

