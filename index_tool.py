import json
from pathlib import Path

import pandas as pd

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog

from modules.illumina_indexes import IlluminaFormatIndexKitDefinition
from modules.index_table import IndexTableContainer
from modules.kit_type import KitTypeFields
from modules.notification import Toast
from ui.widget import Ui_Form
import qdarktheme
import qtawesome as qta
import sys
import yaml
import csv
from typing import Dict, Any


class IndexDefinitionConverter(QWidget, Ui_Form):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.stackedWidget.setCurrentWidget(self.data_page_widget)

        self.kit_type_obj = self._load_kit_type(Path("config/kit_type_fields.yaml"))

        self.csv_radioButton.setChecked(True)
        self.help_pushButton.setCheckable(True)

        self.index_table_container = IndexTableContainer(self.kit_type_obj)
        self.tablewidget = self.index_table_container.tablewidget

        self.data_page_widget.layout().addWidget(self.index_table_container)

        self._connect_signals()

    def _connect_signals(self):
        self.help_pushButton.clicked.connect(self._toggle_help)
        self.load_pushButton.clicked.connect(self._load_data)

        index_header = self.index_table_container.tablewidget.horizontalHeader()
        self.restore_pushButton.clicked.connect(index_header.restore_orig_header)
        self.index_table_container.resources_settings.widgets['kit_type'].currentTextChanged.connect(
            index_header.restore_orig_header)

        self.export_pushButton.clicked.connect(self._export)
        self.unhide_pushButton.clicked.connect(self.index_table_container.tablewidget.show_all_columns)
        self.index_table_container.notify_signal.connect(self.show_notification)
        self.csv_radioButton.toggled.connect(self._illumina_preset)

    @staticmethod
    def _detect_delimiter(file_path: Path) -> str:
        with open(file_path, 'r') as csvfile:
            content = csvfile.read()
            dialect = csv.Sniffer().sniff(content)

            return dialect.delimiter

    def _illumina_preset(self):
        self.index_table_container.illumina_preset(self.ilmn_radioButton.isChecked())

    def _load_kit_type(self, file_path: Path) -> Dict[str, KitTypeFields]:
        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)

        try:
            return {kit_type: KitTypeFields({kit_type: data}) for kit_type, data in yaml_data.items()}
        except Exception as e:
            self.show_notification(f"Error: {str(e)}", warn=True)

    def show_notification(self, message: str, warn: bool = False):
        Toast(self, message, warn=warn).show_toast()

    def _toggle_help(self):
        self.stackedWidget.setCurrentWidget(
            self.help_page_widget if self.help_pushButton.isChecked() else self.data_page_widget
        )

    def _load_data(self):
        file = self._open_file_dialog()
        if file:
            self.index_table_container.user_settings.set_filepath(file)
            self._load_csv(file) if self.csv_radioButton.isChecked() else self._load_ikd(file)

    def _open_file_dialog(self) -> Path | None:
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(
            "ILMN Index TSV files (*.tsv)" if self.ilmn_radioButton.isChecked() else "Index CSV files (*.csv)")

        if file_dialog.exec():
            return Path(file_dialog.selectedFiles()[0])
        return None

    def _load_data(self):
        file = self._open_file_dialog()
        if file:
            self.index_table_container.user_settings.set_filepath(file)
            self._load_csv(file) if self.csv_radioButton.isChecked() else self._load_ikd(file)

    def _load_csv(self, file_path: Path):
        delim = self._detect_delimiter(file_path)
        df = pd.read_csv(file_path, sep=delim)
        self._set_index_table_data(df)


    def _load_ikd(self, file_path: Path):
        illumina_ikd = IlluminaFormatIndexKitDefinition(file_path)
        self._set_index_table_data(illumina_ikd.indices_df)
        self.index_table_container.illumina_set_parameters(illumina_ikd)
        self.index_table_container.override_cycles_autoset()

    def _set_index_table_data(self, df: pd.DataFrame):
        self.index_table_container.set_index_table_data(df)
        self.index_table_container.override_preset()

    def _export(self):
        all_data = self.data()
        if not all_data:
            return

        file_path = self._get_save_file_path()
        if file_path:
            self._save_json_file(file_path, all_data)

    def _get_save_file_path(self) -> str:
        loaded_file = self.index_table_container.user_settings.get_filepath()
        proposed_filename = loaded_file.with_suffix(".json").name
        file_path, _ = QFileDialog().getSaveFileName(
            caption="Save Index JSON File",
            dir=proposed_filename,
            filter="JSON Files (*.json)"
        )
        return file_path + '.json' if file_path and not file_path.endswith('.json') else file_path

    def _save_json_file(self, file_path: str, data: Dict[str, Any]):
        try:
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            self.show_notification(f"Index JSON file saved to: {file_path}")
        except Exception as e:
            self.show_notification(f"Error saving JSON file: {str(e)}", warn=True)
            print(f"Error saving JSON file: {str(e)}")

    def data(self) -> Dict[str, Any] | None:
        try:
            table_settings = self.index_table_container.data()
            resource_settings = self.index_table_container.resources_settings.data()
            user_settings = self.index_table_container.user_settings.data()
            kit_settings = self.index_table_container.index_kit_settings.data()

            kit_type = resource_settings['kit_type']
            kit_settings['kit_type'] = self.kit_type_obj[kit_type].data

            return {
                'user_info': user_settings,
                'resource': resource_settings,
                'index_kit': kit_settings,
                'indexes': table_settings,
            }
        except Exception as e:
            self.show_notification(f"Error: {str(e)}", warn=True)
            return None


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(qta.icon('fa5b.jedi-order', color='blue'))
        self.setWindowTitle("index tool")
        self.setCentralWidget(IndexDefinitionConverter())
        self.setMinimumSize(600, 600)


def main():
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("light")
    window = MainWindow()
    # window.setMinimumSize(600, 600)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

