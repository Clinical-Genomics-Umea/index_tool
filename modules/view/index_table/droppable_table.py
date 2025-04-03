from typing import Dict, List, Any

import numpy as np
import pandas as pd
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QTableWidget, QHeaderView, QMenu

from modules.model.kit_type import KitDefObject


class DroppableTableWidget(QTableWidget):
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns, parent)
        self.setHorizontalHeader(DroppableHeader(Qt.Horizontal, self))
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def contextMenuEvent(self, event):
        header_index = self.horizontalHeader().logicalIndexAt(event.pos())
        if header_index != -1:
            menu = QMenu(self)
            action1 = QAction("Restore original header", self)
            action2 = QAction("Hide column", self)
            menu.addAction(action1)
            menu.addAction(action2)

            action1.triggered.connect(lambda: self.horizontalHeader().restore_orig_header_for_index(header_index))
            action2.triggered.connect(lambda: self.hideColumn(header_index))

            menu.exec(event.globalPos())
        else:
            super().contextMenuEvent(event)

    def show_all_columns(self):
        for column in range(self.columnCount()):
            self.setColumnHidden(column, False)

    def to_dataframe(self) -> pd.DataFrame:
        rows, columns = self.rowCount(), self.columnCount()
        headers = [self.horizontalHeaderItem(col).text() for col in range(columns)]
        data = {header: [] for header in headers}

        for row in range(rows):
            for col, header in enumerate(headers):
                item = self.item(row, col)
                data[header].append(item.text() if item else None)

        return pd.DataFrame(data)

    def index_sets_dict(self, index_kit_def_obj: KitDefObject) -> Dict[str, List[Dict[str, Any]]]:

        fields = index_kit_def_obj.all_index_set_fields

        df = self.to_dataframe()
        _df = df[fields].copy().replace(['nan', ''], np.nan).dropna(how='all')
        if _df.isnull().any().any():
            raise ValueError(f"Error: NaN values in the index table for {index_kit_def_obj.kit_name}")

        index_sets_dict = {}

        for index_set_name in index_kit_def_obj.index_set_names:
            index_set_fields = index_kit_def_obj.index_set_fields(index_set_name)
            _df2 = _df[index_set_fields]
            index_sets_dict[index_set_name] = _df2.to_dict(orient='records')

        return index_sets_dict


class DroppableHeader(QHeaderView):
    label_dropped = Signal(int, str)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setAcceptDrops(True)
        self.original_labels = {}

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            index = self.logicalIndexAt(event.position().toPoint())
            new_label = event.mimeData().text()
            old_label = self.model().headerData(index, Qt.Horizontal)

            set_labels = self.header_labels()
            if new_label in set_labels:
                other_label_index = set_labels.index(new_label)
                self.restore_orig_header_for_index(other_label_index)

            if index not in self.original_labels:
                self.original_labels[index] = old_label

            self.model().setHeaderData(index, Qt.Horizontal, new_label)
            event.acceptProposedAction()

            if old_label != new_label:
                self.label_dropped.emit(index, new_label)

    def header_labels(self) -> List[str]:
        return [self.model().headerData(section, self.orientation(), Qt.DisplayRole) for section in range(self.count())]

    def restore_orig_header(self):
        for index, label in self.original_labels.items():
            self.model().setHeaderData(index, Qt.Horizontal, label)

    def restore_orig_header_for_index(self, index: int):
        old_label = self.original_labels.pop(index, None)
        if old_label:
            self.model().setHeaderData(index, Qt.Horizontal, old_label)

    def restore_orig_header_for_label(self, label: str):
        index = self.find_header_index(label)
        if index != -1:
            self.restore_orig_header_for_index(index)

    def find_header_index(self, label: str) -> int:
        return next((section for section in range(self.count())
                     if self.model().headerData(section, self.orientation(), Qt.DisplayRole) == label), -1)

    def contextMenuEvent(self, event):
        header_index = self.logicalIndexAt(event.pos())
        if header_index != -1:
            menu = QMenu(self)
            action1 = QAction("Restore original header", self)
            action2 = QAction("Hide column", self)
            menu.addAction(action1)
            menu.addAction(action2)

            action1.triggered.connect(lambda: self.restore_orig_header_for_index(header_index))
            action2.triggered.connect(lambda: self.setSectionHidden(header_index, True))

            menu.exec(event.globalPos())
        else:
            super().contextMenuEvent(event)