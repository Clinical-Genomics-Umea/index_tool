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
import csv


class IndexTableContainer(QWidget):

    notify_signal = Signal(str, bool)

    def __init__(self, kit_type_fields: dict):
        super().__init__()

        self.kit_type_fields = kit_type_fields

        self.setAcceptDrops(True)
        self.tablewidget = DroppableTableWidget(0, 0)
        self.tablewidget_h_header = self.tablewidget.horizontalHeader()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.draggable_fixed_labels_layout = QHBoxLayout()
        self.draggable_standard_labels_layout = QHBoxLayout()

        self.user_settings = UserInfo()
        self.resources_settings = ResourcesSettings(self.kit_type_fields)
        self.index_kit_settings = IndexKitSettings()

        self.input_settings_layout = QHBoxLayout()

        self.input_settings_layout.addWidget(self.index_kit_settings)
        self.input_settings_layout.addWidget(self.resources_settings)
        self.input_settings_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.layout.addWidget(self.user_settings)
        self.layout.addLayout(self.input_settings_layout)

        self.draggable_labels_container = DraggableLabelsContainer(self.kit_type_fields)
        self.layout.addWidget(self.draggable_labels_container)
        self.layout.addWidget(self.tablewidget)

        self.resources_settings.widgets['kit_type'].currentTextChanged.connect(self.set_draggable_layout)

        self.tablewidget_h_header.label_dropped.connect(self._override_cycles_autoset_label)

    @staticmethod
    def _detect_delimiter(file_path):
        with open(file_path, 'r') as csvfile:
            sample = csvfile.read()
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            return delimiter

    def _illumina_set_parameters(self, ikd):
        self.resources_settings.set_layout_illumina(ikd.kit_type)
        if 'name' in ikd.index_kit:
            self.index_kit_settings.widgets['name'].setText(ikd.index_kit['name'].replace(' ', '').replace('-', ''))
        if 'display_name' in ikd.index_kit:
            self.index_kit_settings.widgets['display_name'].setText(ikd.index_kit['display_name'])
        if 'version' in ikd.index_kit:
            self.index_kit_settings.widgets['version'].setText(ikd.index_kit['version'])
        if 'description' in ikd.index_kit:
            self.index_kit_settings.widgets['description'].setText(ikd.index_kit['description'])

        if 'adapter' in ikd.resources:
            self.resources_settings.widgets['adapter_read1'].setText(ikd.resources['adapter'])
        if 'adapter_read2' in ikd.resources:
            self.resources_settings.widgets['adapter_read2'].setText(ikd.resources['adapter_read2'])

    def illumina_preset(self, is_illumina_kit):
        self.resources_settings.widgets['kit_type'].setDisabled(is_illumina_kit)
        self.resources_settings.widgets['adapter_read1'].setDisabled(is_illumina_kit)
        self.resources_settings.widgets['adapter_read2'].setDisabled(is_illumina_kit)
        if is_illumina_kit:
            self.draggable_labels_container.hide()
        else:
            self.draggable_labels_container.show()

    def _override_preset(self):
        self.resources_settings.widgets['override_cycles_pattern_r1'].setText("Yx")
        self.resources_settings.widgets['override_cycles_pattern_r2'].setText("Yx")

    def _notify_error(self, message, warn=True):
        toast = Toast(self, message, warn=warn)
        toast.show_toast()

    def _override_cycles_autoset(self):
        df = self.tablewidget.to_dataframe()
        if df.empty:
            return

        for used_label in df.columns:
            if used_label in ['index_i7', 'index_i5'] and not self.valid_index_sequences(used_label, df):
                return

            if used_label in ['index_i7', 'index_i5'] and not self.valid_index_lengths(used_label, df):
                return
                
        for used_label in df.columns:
            if used_label == 'index_i7' and self.valid_index_sequences(used_label, df):
                index_length = df[used_label].str.len().unique()[0]
                self.resources_settings.widgets['override_cycles_pattern_i1'].setText(f"I{index_length}")

            elif used_label == 'index_i5' and self.valid_index_sequences(used_label, df):
                index_length = df[used_label].str.len().unique()[0]
                self.resources_settings.widgets['override_cycles_pattern_i2'].setText(f"I{index_length}")

    def _override_cycles_autoset_label(self, index, label):
        df = self.tablewidget.to_dataframe()
        if df.empty:
            return

        if label in ['index_i7', 'index_i5']:
            if not self.valid_index_sequences(label, df):
                self.resources_settings.widgets['override_cycles_pattern_i1'].setText("")
                self.tablewidget_h_header.restore_orig_header_for_label(label)
                return

            if not self.valid_index_lengths(label, df):
                self.tablewidget_h_header.restore_orig_header_for_label(label)
                return

            index_length = df[label].str.len().unique()[0]

            if label == 'index_i7':
                self.resources_settings.widgets['override_cycles_pattern_i1'].setText(f"I{index_length}")
            elif label == 'index_i5':
                self.resources_settings.widgets['override_cycles_pattern_i2'].setText(f"I{index_length}")

    def valid_index_sequences(self, label, df):
        # Custom function to check if a value should be considered empty

        _df_tmp = df[label].replace('nan', np.nan).dropna(how='any')

        # Check only non-empty sequences
        valid_sequences = _df_tmp.astype(str).str.match(r'^[ACGTacgt]+$')
        invalid_mask = ~valid_sequences
        invalid_count = invalid_mask.sum()

        if invalid_count > 0:
            invalid_rows = df.index[_df_tmp.index[invalid_mask]].tolist()
            invalid_rows = [v + 1 for v in invalid_rows]
            self.notify_signal.emit(f"{label} data contains {invalid_count} invalid non-empty sequences. "
                                    f"Invalid rows: {invalid_rows}", True)
            return False
        return True

    def valid_index_lengths(self, label, df):
        _df_tmp = df[label].replace('nan', np.nan).dropna(how='any')
        unique_lengths = _df_tmp.str.len().unique()
        print(unique_lengths)
        if len(unique_lengths) != 1:
            self.notify_signal.emit(f"{label} column contains indexes of different lengths", True)
            return False
        return True

    def current_labels(self):
        current_kit_type_name = self.resources_settings.widgets['kit_type'].currentText()
        return self.kit_type_fields[current_kit_type_name].fields

    def data(self):
        df = self.tablewidget.to_dataframe()

        if df.empty:
            raise ValueError('Table is empty')

        table_labels = set(df.columns)
        selected_layout_labels = set(self.current_labels())
        if unset_labels := selected_layout_labels - table_labels:
            raise ValueError(
                f"Required header labels are not set in the table: {', '.join(unset_labels)}"
            )

        kit_type_name = self.resources_settings.widgets['kit_type'].currentText()
        kit_type_object = self.kit_type_fields[kit_type_name]
        return self.tablewidget.to_index_container_dict(kit_type_object)

    def set_index_table_data(self, df):

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

        else:
            print("Drop event ignored.")

    def header_labels(self):
        labels = []
        for section in range(self.count()):
            label = self.model().headerData(section, self.orientation(), Qt.DisplayRole)
            labels.append(label)
        return labels

    def restore_orig_header(self):
        for index, label in self.original_labels.items():
            self.model().setHeaderData(index, Qt.Horizontal, label)

    def restore_orig_header_for_index(self, index):
        old_label = self.original_labels[index]
        self.model().setHeaderData(index, Qt.Horizontal, old_label)
        del self.original_labels[index]

    def restore_orig_header_for_label(self, label):
        index = self.find_header_index(label)
        self.restore_orig_header_for_index(index)

    def find_header_index(self, label):
        for section in range(self.count()):
            section_label = self.model().headerData(section, self.orientation(), Qt.DisplayRole)
            if section_label == label:
                return section
        return -1

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

    def to_dataframe(self) -> pd.DataFrame:
        # Get the number of rows and columns in the QTableWidget
        rows = self.rowCount()
        columns = self.columnCount()

        # Create a dictionary to hold the data, with column headers as keys
        data = {}

        # Get the headers for the columns
        headers = [self.horizontalHeaderItem(col).text() for col in range(columns)]

        # Initialize lists in the dictionary for each column
        for header in headers:
            data[header] = []

        # Iterate over the rows and columns to collect data
        for row in range(rows):
            for col in range(columns):
                item = self.item(row, col)
                # Add the item's text to the corresponding column list, or None if the item is empty
                data[headers[col]].append(item.text() if item else None)

        # Create a DataFrame from the collected data

        for key, obj in data.items():
            print(key, len(obj))

        return pd.DataFrame(data)

    def notify_error(self, message, warn=True):
        toast = Toast(self, message, warn=warn)
        toast.show_toast()

    def to_index_container_dict(self, kit_type_obj) -> dict:
        # Get the number of rows and columns in the QTableWidget
        rows = self.rowCount()
        columns = self.columnCount()

        # Create a dictionary to hold the data, with column headers as keys
        data = {}

        # Get the headers for the columns
        headers = [self.horizontalHeaderItem(col).text() for col in range(columns)]

        # Initialize lists in the dictionary for each column
        for header in headers:
            data[header] = []

        # Iterate over the rows and columns to collect data
        for row in range(rows):
            for col in range(columns):
                item = self.item(row, col)
                # Add the item's text to the corresponding column list, or None if the item is empty
                data[headers[col]].append(item.text() if item else None)

        # Create a DataFrame from the collected data

        df = pd.DataFrame(data)
        index_container_index_dict = {}

        for set_name in kit_type_obj.index_set_names:
            _fields = kit_type_obj.index_set_fields(set_name)
            _df = df[_fields].copy().replace('nan', np.nan).replace('', np.nan).dropna(how='all')

            if _df.isnull().any().any():
                raise ValueError(f"Error: NaN values in the index table for {set_name}")

            else:
                index_container_index_dict[set_name] = _df.to_dict(orient='records')

        return index_container_index_dict
