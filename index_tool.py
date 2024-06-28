import json
from pathlib import Path

import pandas as pd

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog

from modules.index_table import IndexTableContainer
from modules.kit_fields import KitTypeFields
from modules.notification import Toast
from ui.widget import Ui_Form
import qdarktheme
import qtawesome as qta
import sys
import yaml


class IndexDefinitionConverter(QWidget, Ui_Form):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.stackedWidget.setCurrentWidget(self.csv_page_widget)

        self.kit_type_fields = self.load_kit_type_fields(Path("config/kit_type_fields.yaml"))

        self.csv_radioButton.setChecked(True)
        self.help_pushButton.setCheckable(True)

        self.index_table_container = IndexTableContainer(self.kit_type_fields)
        self.tablewidget = self.index_table_container.tablewidget

        self.csv_page_widget.layout().addWidget(self.index_table_container)

        self.csv_radioButton.toggled.connect(self.change_view)
        self.csv_radioButton.toggled.connect(self.change_view)
        self.help_pushButton.clicked.connect(self.toggle_help)
        self.load_pushButton.clicked.connect(self.load_data)

        index_header = self.index_table_container.tablewidget.horizontalHeader()
        self.restore_pushButton.clicked.connect(index_header.restore_orig_header)
        self.index_table_container.resources_settings.widgets['kit_type'].currentTextChanged.connect(
            index_header.restore_orig_header)
        self.export_pushButton.clicked.connect(self.export)
        self.unhide_pushButton.clicked.connect(self.index_table_container.tablewidget.show_all_columns)

        self.index_table_container.notify_signal.connect(self.show_notification)

    def get_kit_type_label_sets(self):
        kit_type_sets = {}
        for key, value in self.kit_types.items():
            kit_type_sets[key] = value['labels']
        return kit_type_sets

    @staticmethod
    def load_kit_type_fields(file_path):
        kit_type_fields = dict()
        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
            for kit_type, data in yaml_data.items():
                kit_type_fields[kit_type] = KitTypeFields({kit_type: data})

        return kit_type_fields


    def show_notification(self, message, warn=False):
        toast = Toast(self, message, warn=warn)
        toast.show_toast()

    def toggle_help(self):
        if self.help_pushButton.isChecked():
            self.stackedWidget.setCurrentWidget(self.help_page_widget)
        else:
            if self.csv_radioButton.isChecked():
                self.stackedWidget.setCurrentWidget(self.csv_page_widget)
            if self.ilmn_radioButton.isChecked():
                self.stackedWidget.setCurrentWidget(self.ilmn_page_widget)

    def change_view(self):
        if self.help_pushButton.isChecked():
            return

        if self.csv_radioButton.isChecked():
            self.stackedWidget.setCurrentWidget(self.csv_page_widget)
        if self.ilmn_radioButton.isChecked():
            self.stackedWidget.setCurrentWidget(self.ilmn_page_widget)

    def load_data(self):
        file = self.open_file_dialog()
        self.index_table_container.user_settings.set_filepath(file)
        self.load_csv(file)

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if self.ilmn_radioButton.isChecked():
            file_dialog.setNameFilter("ILMN Index TSV files (*.tsv)")
        elif self.csv_radioButton.isChecked():
            file_dialog.setNameFilter("Index CSV files (*.csv)")

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            return Path(file_path)

    def load_csv(self, file_path):
        df = pd.read_csv(file_path)
        self.index_table_container.set_index_table_data(df)

    def load_ikd_tsv(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        self.plainTextEdit.setPlainText(content)

    def export(self):
        if self.csv_radioButton.isChecked():
            all_data = self.data()

            if all_data:
                self.save_dict_as_json(all_data)

    def save_dict_as_json(self, data_dict):
        # Create a file dialog

        loaded_file = self.index_table_container.user_settings.get_filepath()
        proposed_filename = loaded_file.with_suffix(".json").name

        file_dialog = QFileDialog()

        # Set the dialog to save mode and specify the filter for JSON files
        file_path, _ = file_dialog.getSaveFileName(
            caption="Save Index JSON File",
            dir=proposed_filename,
            filter="JSON Files (*.json)"
        )

        # Check if a file path was selected
        if file_path:
            # If the user didn't specify the .json extension, add it
            if not file_path.endswith('.json'):
                file_path += '.json'

            # Write the dictionary to the JSON file
            try:
                with open(file_path, 'w') as json_file:
                    json.dump(data_dict, json_file, indent=4)
                self.show_notification(f"Index JSON file saved to: {file_path}")
                return True
            except Exception as e:
                self.show_notification(f"Error saving JSON file: {str(e)}", warn=True)
                print(f"Error saving JSON file: {str(e)}")
                return False
        else:
            return False

    def data(self):
        try:
            table_settings = self.index_table_container.data()

        except Exception as e:
            self.show_notification(f"Error: {str(e)}", warn=True)
            return

        try:
            resource_settings = self.index_table_container.resources_settings.data()

        except Exception as e:
            self.show_notification(f"Error: {str(e)}", warn=True)
            return

        try:
            user_settings = self.index_table_container.user_settings.data()

        except Exception as e:
            self.show_notification(f"Error: {str(e)}", warn=True)
            return

        try:
            kit_settings = self.index_table_container.index_kit_settings.data()

        except Exception as e:
            self.show_notification(f"Error: {str(e)}", warn=True)
            return

        all_data = {
            'user_info': user_settings,
            'resource': resource_settings,
            'index_kit': kit_settings,
            'indexes': table_settings
        }

        return all_data


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(qta.icon('fa5b.jedi-order', color='blue'))

        self.setWindowTitle("index tool")
        convert_widget = IndexDefinitionConverter()

        # Set the central widget of the Window.
        self.setCentralWidget(convert_widget)


def main():
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("light")
    window = MainWindow()
    window.setMinimumSize(600, 600)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

