import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QMenu, QHeaderView, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, \
    QTableWidget

from modules.draggable_labels import DraggableLabelsContainer
from modules.index_kit import IndexKitSettings
from modules.resource import ResourcesSettings
from modules.user import UserInfo


class IndexTableContainer(QWidget):
    def __init__(self, index_label_sets: dict):
        super().__init__()

        self.index_label_sets = index_label_sets

        self.setAcceptDrops(True)
        self.tablewidget = DroppableTableWidget(0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.draggable_fixed_labels_layout = QHBoxLayout()
        self.draggable_standard_labels_layout = QHBoxLayout()

        self.user_settings = UserInfo()
        self.resources_settings = ResourcesSettings(self.index_label_sets.keys())
        self.index_kit_settings = IndexKitSettings()

        self.input_settings_layout = QHBoxLayout()

        self.input_settings_layout.addWidget(self.index_kit_settings)
        self.input_settings_layout.addWidget(self.resources_settings)
        self.input_settings_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.layout.addWidget(self.user_settings)
        self.layout.addLayout(self.input_settings_layout)

        self.draggable_labels_container = DraggableLabelsContainer(self.index_label_sets)
        self.layout.addWidget(self.draggable_labels_container)
        self.layout.addWidget(self.tablewidget)

        self.resources_settings.widgets['layout'].currentTextChanged.connect(self.set_draggable_layout)

    def table_settings(self):
        df = self.index_table_to_dataframe()
        used_labels = set(df.columns)
        selected_labels = set(self.draggable_labels_container.selected_labels)

        if not used_labels.issubset(selected_labels):
            unset_labels = selected_labels - used_labels


    def index_table_to_dataframe(self) -> pd.DataFrame:
        # Get the number of rows and columns in the QTableWidget
        rows = self.tablewidget.rowCount()
        columns = self.tablewidget.columnCount()

        # Create a dictionary to hold the data, with column headers as keys
        data = {}

        # Get the headers for the columns
        headers = [self.tablewidget.horizontalHeaderItem(col).text() for col in range(columns)]

        # Initialize lists in the dictionary for each column
        for header in headers:
            data[header] = []

        # Iterate over the rows and columns to collect data
        for row in range(rows):
            for col in range(columns):
                item = self.tablewidget.item(row, col)
                # Add the item's text to the corresponding column list, or None if the item is empty
                data[headers[col]].append(item.text() if item else None)

        # Create a DataFrame from the collected data
        df = pd.DataFrame(data)
        return df

    def set_draggable_layout(self):
        text = self.resources_settings.widgets['layout'].currentText()
        self.draggable_labels_container.show_labels(text)


class DroppableHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setAcceptDrops(True)
        self.original_labels = dict()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            print("Drag enter event ignored.")

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            print("Drag move event ignored.")

    def dropEvent(self, event):
        if event.mimeData().hasText():
            index = self.logicalIndexAt(event.position().toPoint())

            old_data = self.model().headerData(index, Qt.Horizontal)
            if index not in self.original_labels:
                self.original_labels[index] = old_data

            self.model().setHeaderData(index, Qt.Horizontal, event.mimeData().text())

            event.acceptProposedAction()
        else:
            print("Drop event ignored.")

    def restore_orig_header(self):
        for index, label in self.original_labels.items():
            self.model().setHeaderData(index, Qt.Horizontal, label)

    def restore_orig_header_column(self, index):
        label = self.original_labels[index]
        self.model().setHeaderData(index, Qt.Horizontal, label)

    def contextMenuEvent(self, event):
        if self.logicalIndexAt(event.pos()) != -1:
            header_index = self.logicalIndexAt(event.pos())
            menu = QMenu(self)

            # Add actions to the menu
            action1 = QAction(f"restore orig header", self)
            action2 = QAction(f"hide column", self)
            menu.addAction(action1)
            menu.addAction(action2)

            # Connect actions to slots
            action1.triggered.connect(lambda: self.restore_header(header_index))
            action2.triggered.connect(lambda: self.hide_column(header_index))

            # Show the context menu
            menu.exec(event.globalPos())
        else:
            super().contextMenuEvent(event)

    def hide_column(self, index):
        self.setSectionHidden(index, True)

    def restore_header(self, index):
        self.restore_orig_header_column(index)


class DroppableTableWidget(QTableWidget):
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns, parent)
        self.setHorizontalHeader(DroppableHeader(Qt.Horizontal, self))
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def contextMenuEvent(self, event):
        if self.horizontalHeader().logicalIndexAt(event.pos()) != -1:
            header_index = self.horizontalHeader().logicalIndexAt(event.pos())
            menu = QMenu(self)

            # Add actions to the menu
            action1 = QAction(f"restore orig header", self)
            action2 = QAction(f"hide column", self)
            menu.addAction(action1)
            menu.addAction(action2)

            # Connect actions to slots
            action1.triggered.connect(lambda: self.restore_header(header_index))
            action2.triggered.connect(lambda: self.hide_column(header_index))

            # Show the context menu
            menu.exec(event.globalPos())
        else:
            super().contextMenuEvent(event)

    def hide_column(self, index):
        self.horizontalHeader().setSectionHidden(index, True)

    def restore_header(self, index):
        header = self.horizontalHeader()
        header.restore_orig_header(index)

    def show_all_columns(self):
        for column in range(self.columnCount()):
            self.setColumnHidden(column, False)

