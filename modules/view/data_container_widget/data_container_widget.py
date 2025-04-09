import numpy as np
import pandas as pd
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, \
    QTableWidgetItem

from modules.model.data_manager import DataManager
from modules.view.draggable_labels.draggable_labels import DraggableLabelsContainer
from modules.view.metadata.index_kit_settings.index_kit_settings_widget import IndexKitSettingsWidget
from modules.view.index_table.droppable_table import DroppableTableWidget
from modules.view.metadata.resource_settings.resource_settings_widget import ResourceSettingsWidget
from modules.view.metadata.user_settings.user_settings_widget import UserSettingsWidget
from typing import Dict, Any, List


class DataContainerWidget(QWidget):
    notify_signal = Signal(str, bool)

    def __init__(self,
                 data_manager: DataManager,
                 droppable_table_widget: DroppableTableWidget,
                 resources_settings_widget: ResourceSettingsWidget,
                 draggable_labels_container_widget: DraggableLabelsContainer,
                 user_settings_widget: UserSettingsWidget,
                 metadata_settings_widget: IndexKitSettingsWidget):

        super().__init__()

        self._data_manager = data_manager
        self._draggable_labels_container_widget = draggable_labels_container_widget
        self._resources_settings_widget = resources_settings_widget
        self._droppable_table_widget = droppable_table_widget
        self._tablewidget_h_header = self._droppable_table_widget.horizontalHeader()
        self._user_settings_widget = user_settings_widget
        self._metadata_settings_widget = metadata_settings_widget

        self._setup_ui()
        # self._connect_signals()

    def _setup_ui(self):
        self.setAcceptDrops(True)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self._input_settings_layout = QHBoxLayout()
        self._input_settings_layout.addWidget(self._metadata_settings_widget)
        self._input_settings_layout.addWidget(self._resources_settings_widget)
        self._input_settings_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.layout.addWidget(self._user_settings_widget)
        self.layout.addLayout(self._input_settings_layout)
        self.layout.addWidget(self._draggable_labels_container_widget)
        self.layout.addWidget(self._droppable_table_widget)

    def _update_data(self):
        self._data_manager.set_index_df(self._droppable_table_widget.to_dataframe())
        self._data_manager.set_user(self._user_settings_widget.get_user_info())

    def illumina_set_parameters(self, ikd: Dict[str, Any]):
        self._resources_settings_widget.set_layout_illumina(ikd.kit_type)
        for key, widget_name in [('name', 'name'), ('display_name', 'display_name'),
                                 ('version', 'version'), ('description', 'description')]:
            if key in ikd.index_kit:
                self.index_kit_settings.widgets[widget_name].setText(
                    ikd.index_kit[key].replace(' ', '').replace('-', ''))

        if 'adapter' in ikd.resources:
            self._resources_settings_widget.widgets['adapter_read1'].setText(ikd.resources['adapter'])
        if 'adapter_read2' in ikd.resources:
            self._resources_settings_widget.widgets['adapter_read2'].setText(ikd.resources['adapter_read2'])

    def illumina_preset(self, is_illumina_kit: bool):
        for widget in ['kit_type', 'adapter_read1', 'adapter_read2']:
            self._resources_settings_widget.widgets[widget].setDisabled(is_illumina_kit)
        self._draggable_labels_container_widget.setVisible(not is_illumina_kit)

    def override_preset(self):
        self._resources_settings_widget.widgets['override_cycles_pattern_r1'].setText("Y{x}")
        self._resources_settings_widget.widgets['override_cycles_pattern_r2'].setText("Y{x}")

    def override_cycles_autoset(self):
        df = self._droppable_table_widget.to_dataframe()
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
                self._resources_settings_widget.widgets[widget_name].setText(f"I{index_length}")

    def _override_cycles_autoset_label(self, index: int, label: str):
        df = self._droppable_table_widget.to_dataframe()
        if df.empty or label not in ['index_i7', 'index_i5']:
            return

        if not self.valid_index_sequences(label, df) or not self.valid_index_lengths(label, df):
            widget_name = 'override_cycles_pattern_i1' if label == 'index_i7' else 'override_cycles_pattern_i2'
            self._resources_settings_widget.widgets[widget_name].setText("")
            self._tablewidget_h_header.restore_orig_header_for_label(label)
            return

        index_length = df[label].str.len().unique()[0]
        widget_name = 'override_cycles_pattern_i1' if label == 'index_i7' else 'override_cycles_pattern_i2'
        self._resources_settings_widget.widgets[widget_name].setText(f"I{index_length}")

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
        current_kit_type_name = self._resources_settings_widget.widgets['kit_type'].currentText()
        return self._data_manager[current_kit_type_name].all_index_fields

    def data(self, index_kit_def_name: str) -> Dict[str, Any]:
        df = self._droppable_table_widget.to_dataframe()
        if df.empty:
            raise ValueError('Table is empty')

        table_labels = set(df.columns)
        selected_layout_labels = set(self.current_labels())
        if unset_labels := selected_layout_labels - table_labels:
            raise ValueError(f"Required header labels are not set in the table: {', '.join(unset_labels)}")

        return self._droppable_table_widget.index_sets_dict(self._kit_def_objs_dict[index_kit_def_name])

    def set_index_table_data(self, df: pd.DataFrame):
        df = df.dropna(axis=1, how='all').loc[:, (df != '').any()]
        self._droppable_table_widget.setRowCount(df.shape[0])
        self._droppable_table_widget.setColumnCount(df.shape[1])
        self._droppable_table_widget.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self._droppable_table_widget.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
    #
    # def set_draggable_layout(self):
    #     text = self._resources_settings_widget.currentText()
    #     self._draggable_labels_container_widget.show_labels(text)

