import csv
from logging import Logger
from pathlib import Path

from PySide6.QtWidgets import QWidget, QFileDialog, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QLabel

from modules.model.data_manager import DataManager
from modules.view.draggable_labels.draggable_labels import DraggableLabelsContainer
from modules.view.index_table.droppable_table import DroppableTableWidget
from modules.view.metadata.index_kit_settings.index_kit_settings_widget import IndexKitSettingsWidget
from modules.view.metadata.resource_settings.resource_settings_widget import ResourceSettingsWidget
from modules.view.metadata.user_settings.user_settings_widget import UserSettingsWidget
from modules.view.ui.widget import Ui_Form


class CentralWidget(QWidget, Ui_Form):
    def __init__(self,
                 data_manager: DataManager,
                 draggable_labels_container_widget: DraggableLabelsContainer,
                 resources_settings_widget: ResourceSettingsWidget,
                 droppable_table_widget: DroppableTableWidget,
                 user_settings_widget: UserSettingsWidget,
                 index_kit_settings_widget: IndexKitSettingsWidget,
                 index_metadata,
                 logger: Logger,
                 ) -> None:

        super().__init__()

        self.setupUi(self)

        self._name_filters = {
            "tsv_ilmn": "Illumina Index file (*.tsv)",
            "csv": "Index CSV (*.csv)",
            "xlsx": "Excel XLSX (*.xlsx)"
        }

        self._logger = logger

        self._data_manager = data_manager
        self._draggable_labels_container_widget = draggable_labels_container_widget
        self._resources_settings_widget = resources_settings_widget
        self._droppable_table_widget = droppable_table_widget
        self._user_settings_widget = user_settings_widget
        self._index_kit_settings_widget = index_kit_settings_widget
        self._index_metadata = index_metadata


        self.stackedWidget.setCurrentWidget(self.data_page_widget)

        self.help_pushButton.setCheckable(True)

        self.setAcceptDrops(True)

        self._h_layout = QHBoxLayout()
        self._h_layout.addWidget(self._index_kit_settings_widget)
        self._h_layout.addWidget(self._resources_settings_widget)
        self._h_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self._v_layout = self.data_page_widget.layout()
        self._v_layout.setContentsMargins(0, 0, 0, 0)

        # self._v_layout.addWidget(self._message_toast)
        self._v_layout.addWidget(self._user_settings_widget)
        self._v_layout.addWidget(self._index_metadata)
        self._v_layout.addLayout(self._h_layout)
        self._v_layout.addWidget(self._draggable_labels_container_widget)
        self._v_layout.addWidget(self._droppable_table_widget)

        self._connect_signals()
    # #
    def _connect_signals(self):

        self.xlsx_radioButton.clicked.connect(self._set_source_format)
        self.csv_radioButton.clicked.connect(self._set_source_format)
        self.ilmn_radioButton.clicked.connect(self._set_source_format)

        self.load_pushButton.clicked.connect(self._load_data)
        self.export_pushButton.clicked.connect(self._export_data)
        self.help_pushButton.clicked.connect(self._toggle_help)

    def _set_source_format(self):
        if self.xlsx_radioButton.isChecked():
            self._data_manager.set_input_format('xlsx')
        elif self.csv_radioButton.isChecked():
            self._data_manager.set_input_format('csv')
        elif self.ilmn_radioButton.isChecked():
            self._data_manager.set_input_format('tsv_ilmn')

    def _toggle_help(self):
        self.stackedWidget.setCurrentWidget(
            self.help_page_widget if self.help_pushButton.isChecked() else self.data_page_widget
        )

    def _load_data(self):
        file = self._open_file_dialog()
        if file:
            self._data_manager.set_index_data(file)

            # self._data_container_widget.user_settings.set_source_filepath(file)
            # self._load_csv(file) if self.csv_radioButton.isChecked() else self._load_ikd(file)

    def _open_file_dialog(self) -> Path | None:
        self._logger.info(f"open file dialog clicked")

        source_format = self._data_manager.index_source_format

        if not source_format:
            return None

        name_filter = self._name_filters[source_format]

        if not name_filter:
            return None


        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(name_filter)

        if file_dialog.exec():
            return Path(file_dialog.selectedFiles()[0])
        return None

    def _export_data(self):
        filepath = self._export_file_dialog()
        if filepath:

            self._data_manager.save_json_data(filepath)

    def _export_file_dialog(self) -> str:
        source_file = Path(self._data_manager.import_filepath)
        proposed_filename = source_file.with_suffix(".json").name
        filepath, _ = QFileDialog().getSaveFileName(
            caption="Save Index JSON File",
            dir=proposed_filename,
            filter="JSON Files (*.json)"
        )

        return filepath
