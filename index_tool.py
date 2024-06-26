import json
from pathlib import Path

import pandas as pd

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QTableWidgetItem

from modules.index_table import IndexTableContainer
from modules.notification import Toast
from ui.widget import Ui_Form
import qdarktheme
import qtawesome as qta
import sys


class IndexDefinitionConverter(QWidget, Ui_Form):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.stackedWidget.setCurrentWidget(self.csv_page_widget)

        self.index_label_sets = {
            'fixed_layout_single_index': ['fixed_pos', 'index_i7_name', 'index_i7'],
            'fixed_layout_dual_index': ['fixed_pos', 'index_i7_name', 'index_i7', 'index_i5_name', 'index_i5'],
            'fixed_layout_dual_index_single_name': ['fixed_pos', 'index_name', 'index_i7', 'index_i5'],
            'standard_layout_pos_dual_index': ['pos_i7', 'index_i7_name', 'index_i7', 'pos_i5', 'index_i5_name', 'index_i5'],
            'standard_layout_pos_single_index': ['pos_i7', 'index_i7_name', 'index_i7'],
            'standard_layout_dual_index': ['index_i7_name', 'index_i7', 'index_i5_name', 'index_i5'],
            'standard_layout_single_index': ['index_i7_name', 'index_i7'],
        }

        self.csv_radioButton.setChecked(True)
        self.help_pushButton.setCheckable(True)

        self.index_table_container = IndexTableContainer(self.index_label_sets)
        self.tablewidget = self.index_table_container.tablewidget

        self.csv_page_widget.layout().addWidget(self.index_table_container)

        self.csv_radioButton.toggled.connect(self.change_view)
        self.csv_radioButton.toggled.connect(self.change_view)
        self.help_pushButton.clicked.connect(self.toggle_help)
        self.load_pushButton.clicked.connect(self.load_data)

        index_header = self.tablewidget.horizontalHeader()
        self.restore_pushButton.clicked.connect(index_header.restore_orig_header)
        self.index_table_container.resources_settings.widgets['layout'].currentTextChanged.connect(
            index_header.restore_orig_header)
        self.export_pushButton.clicked.connect(self.export)
        self.unhide_pushButton.clicked.connect(self.index_table_container.tablewidget.show_all_columns)

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

    # def make_fixed_json(self):
    #     df = self.get_columns_as_dataframe(self.index_table_container.tablewidget, self.fixed_layout_labels)
    #     fixed_indices = df.to_dict(orient='records')
    #     user_info = self.index_table_container.user_settings.settings()
    #     resource = self.index_table_container.resources_settings.settings()
    #     index_kit = self.index_table_container.index_kit_settings.settings()
    #
    #     data = {
    #         'user_info': user_info,
    #         'resource': resource,
    #         'index_kit': index_kit,
    #         'indices_dual_fixed': fixed_indices
    #     }
    #
    #     print(json.dumps(data, indent=4))

        # data = json.dumps(data)
        # return data


    def dataframe_to_qtablewidget(self, df):
        self.tablewidget.setRowCount(df.shape[0])
        self.tablewidget.setColumnCount(df.shape[1])
        self.tablewidget.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.tablewidget.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

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
        self.dataframe_to_qtablewidget(df)

    def load_ikd_tsv(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        self.plainTextEdit.setPlainText(content)

    def export(self):
        if self.csv_radioButton.isChecked():
            all_data = self.data()

    def data(self):

        table_settings = self.index_table_container.data()
        if 'error' in table_settings:
            self.show_notification(table_settings['error'], warn=True)
            return

        resource_settings = self.index_table_container.resources_settings.data()
        if 'error' in resource_settings:
            self.show_notification(resource_settings['error'], warn=True)
            return

        user_settings = self.index_table_container.user_settings.data()
        if 'error' in user_settings:
            self.show_notification(user_settings['error'], warn=True)
            return

        kit_settings = self.index_table_container.index_kit_settings.data()
        if 'error' in kit_settings:
            self.show_notification(kit_settings['error'], warn=True)
            return

        all_data = {
            'user_info': user_settings,
            'resource': resource_settings,
            'index_kit': kit_settings,
            'indexes': table_settings
        }

        return all_data

    @staticmethod
    def get_columns_as_dataframe(table_widget, column_names):
        # Create a dictionary to store data for each column
        data = {col: [] for col in column_names}

        # Find the indexes of the required columns
        column_indexes = {table_widget.horizontalHeaderItem(col).text(): col for col in
                          range(table_widget.columnCount())}

        # Extract data from the specific columns
        for col_name in column_names:
            col_idx = column_indexes[col_name]
            for row in range(table_widget.rowCount()):
                item = table_widget.item(row, col_idx)
                data[col_name].append(item.text() if item else "")

        # Convert the dictionary to a pandas DataFrame
        df = pd.DataFrame(data)
        return df


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

