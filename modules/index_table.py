import numpy as np
import pandas as pd
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QMenu, QHeaderView, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, \
    QTableWidget, QTableWidgetItem

from modules.draggable_labels import DraggableLabelsContainer
from modules.index_kit import IndexKitSettings
from modules.resources import ResourcesSettings
from modules.user import UserInfo
from modules.notification import Toast
from typing import Dict, Any, List


class IndexTableContainer(QWidget):
    notify_signal = Signal(str, bool)

    def __init__(self, kit_type_fields: Dict[str, Any]):
        super().__init__()
        self.kit_type_fields = kit_type_fields
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setAcceptDrops(True)
        self.tablewidget = DroppableTableWidget(0, 0)
        self.tablewidget_h_header = self.tablewidget.horizontalHeader()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.user_settings = UserInfo()
        self.resources_settings = ResourcesSettings(self.kit_type_fields)
        self.index_kit_settings = IndexKitSettings()

        self.input_settings_layout = QHBoxLayout()
        self.input_settings_layout.addWidget(self.index_kit_settings)
        self.input_settings_layout.addWidget(self.resources_settings)
        self.input_settings_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.draggable_labels_container = DraggableLabelsContainer(self.kit_type_fields)

        self.layout.addWidget(self.user_settings)
        self.layout.addLayout(self.input_settings_layout)
        self.layout.addWidget(self.draggable_labels_container)
        self.layout.addWidget(self.tablewidget)

    def _connect_signals(self):
        self.resources_settings.widgets['kit_type'].currentTextChanged.connect(self.set_draggable_layout)
        self.tablewidget_h_header.label_dropped.connect(self._override_cycles_autoset_label)

    def illumina_set_parameters(self, ikd: Dict[str, Any]):
        self.resources_settings.set_layout_illumina(ikd.kit_type)
        for key, widget_name in [('name', 'name'), ('display_name', 'display_name'),
                                 ('version', 'version'), ('description', 'description')]:
            if key in ikd.index_kit:
                self.index_kit_settings.widgets[widget_name].setText(
                    ikd.index_kit[key].replace(' ', '').replace('-', ''))

        if 'adapter' in ikd.resources:
            self.resources_settings.widgets['adapter_read1'].setText(ikd.resources['adapter'])
        if 'adapter_read2' in ikd.resources:
            self.resources_settings.widgets['adapter_read2'].setText(ikd.resources['adapter_read2'])

    def illumina_preset(self, is_illumina_kit: bool):
        for widget in ['kit_type', 'adapter_read1', 'adapter_read2']:
            self.resources_settings.widgets[widget].setDisabled(is_illumina_kit)
        self.draggable_labels_container.setVisible(not is_illumina_kit)

    def override_preset(self):
        self.resources_settings.widgets['override_cycles_pattern_r1'].setText("Yx")
        self.resources_settings.widgets['override_cycles_pattern_r2'].setText("Yx")

    def override_cycles_autoset(self):
        df = self.tablewidget.to_dataframe()
        if df.empty:
            return

        for used_label in df.columns:
            if used_label in ['index_i7', 'index_i5']:
                if not self.valid_index_sequences(used_label, df) or not self.valid_index_lengths(used_label, df):
                    return

        for used_label in ['index_i7', 'index_i5']:
            if used_label in df.columns and self.valid_index_sequences(used_label, df):
                index_length = df[used_label].str.len().unique()[0]
                widget_name = 'override_cycles_pattern_i1' if used_label == 'index_i7' else 'override_cycles_pattern_i2'
                self.resources_settings.widgets[widget_name].setText(f"I{index_length}")

    def _override_cycles_autoset_label(self, index: int, label: str):
        df = self.tablewidget.to_dataframe()
        if df.empty or label not in ['index_i7', 'index_i5']:
            return

        if not self.valid_index_sequences(label, df) or not self.valid_index_lengths(label, df):
            widget_name = 'override_cycles_pattern_i1' if label == 'index_i7' else 'override_cycles_pattern_i2'
            self.resources_settings.widgets[widget_name].setText("")
            self.tablewidget_h_header.restore_orig_header_for_label(label)
            return

        index_length = df[label].str.len().unique()[0]
        widget_name = 'override_cycles_pattern_i1' if label == 'index_i7' else 'override_cycles_pattern_i2'
        self.resources_settings.widgets[widget_name].setText(f"I{index_length}")

    def valid_index_sequences(self, label: str, df: pd.DataFrame) -> bool:
        _df_tmp = df[label].replace('nan', np.nan).dropna()
        valid_sequences = _df_tmp.astype(str).str.match(r'^[ACGTacgt]+$')
        invalid_mask = ~valid_sequences
        invalid_count = invalid_mask.sum()

        if invalid_count > 0:
            invalid_rows = [v + 1 for v in df.index[_df_tmp.index[invalid_mask]].tolist()]
            self.notify_signal.emit(f"{label} data contains {invalid_count} invalid non-empty sequences. "
                                    f"Invalid rows: {invalid_rows}", True)
            return False
        return True

    def valid_index_lengths(self, label: str, df: pd.DataFrame) -> bool:
        _df_tmp = df[label].replace('nan', np.nan).dropna()
        unique_lengths = _df_tmp.str.len().unique()
        if len(unique_lengths) != 1:
            self.notify_signal.emit(f"{label} column contains indexes of different lengths", True)
            return False
        return True

    def current_labels(self) -> List[str]:
        current_kit_type_name = self.resources_settings.widgets['kit_type'].currentText()
        return self.kit_type_fields[current_kit_type_name].fields

    def data(self) -> Dict[str, Any]:
        df = self.tablewidget.to_dataframe()
        if df.empty:
            raise ValueError('Table is empty')

        table_labels = set(df.columns)
        selected_layout_labels = set(self.current_labels())
        if unset_labels := selected_layout_labels - table_labels:
            raise ValueError(f"Required header labels are not set in the table: {', '.join(unset_labels)}")

        kit_type_name = self.resources_settings.widgets['kit_type'].currentText()
        kit_type_object = self.kit_type_fields[kit_type_name]
        return self.tablewidget.to_index_set_dict(kit_type_object)

    def set_index_table_data(self, df: pd.DataFrame):
        df = df.dropna(axis=1, how='all').loc[:, (df != '').any()]
        self.tablewidget.setRowCount(df.shape[0])
        self.tablewidget.setColumnCount(df.shape[1])
        self.tablewidget.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.tablewidget.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

    def set_draggable_layout(self):
        text = self.resources_settings.widgets['kit_type'].currentText()
        self.draggable_labels_container.show_labels(text)


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

    def to_index_set_dict(self, kit_type_obj) -> Dict[str, List[Dict[str, Any]]]:
        df = self.to_dataframe()
        index_set_dict = {}

        for set_name in kit_type_obj.index_set_names:
            fields = kit_type_obj.index_set_fields(set_name)
            _df = df[fields].copy().replace(['nan', ''], np.nan).dropna(how='all')

            if _df.isnull().any().any():
                raise ValueError(f"Error: NaN values in the index table for {set_name}")
            else:
                index_set_dict[set_name] = _df.to_dict(orient='records')

        return index_set_dict
