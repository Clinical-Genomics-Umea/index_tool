import os
from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QComboBox, QHBoxLayout
from datetime import datetime



class UserInfo(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("User Info")
        self.setFixedWidth(1006)

        self.widgets = {
            "user": QLineEdit(),
            "ad_user": QLineEdit(),
            "file_path": QLineEdit(),
            'timestamp': QLineEdit(),
        }

        layout = QHBoxLayout()

        first_col = QFormLayout()
        second_col = QFormLayout()

        first_col.addRow("user", self.widgets['user'])
        first_col.addRow("ad user", self.widgets['ad_user'])
        second_col.addRow("source file path", self.widgets['file_path'])
        second_col.addRow("timestamp", self.widgets['timestamp'])

        layout.addLayout(first_col)
        layout.addLayout(second_col)

        self.setLayout(layout)

        logged_in_user = os.getlogin()
        self.widgets['ad_user'].setText(logged_in_user)
        self.widgets['ad_user'].setReadOnly(True)
        self.widgets['timestamp'].setText("< current datetime >")
        self.widgets['timestamp'].setReadOnly(True)
        self.widgets['file_path'].setReadOnly(True)

    def set_filepath(self, filepath):
        self.widgets['file_path'].setText(str(filepath))

    def settings(self):
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

        self.widgets['timestamp'].setText(date_time)

        data = dict()
        for key, widget in self.widgets.items():
            if isinstance(widget, QLineEdit):
                data[key] = widget.text()
            elif isinstance(widget, QComboBox):
                data[key] = widget.currentText()

        return data
