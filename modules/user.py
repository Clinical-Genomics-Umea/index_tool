import os
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QHBoxLayout


class UserInfo(QGroupBox):
    def __init__(self):
        super().__init__("User Info")
        self.setFixedWidth(1006)
        self.setup_ui()
        self.initialize_values()

    def setup_ui(self):
        self.widgets = {
            "user": QLineEdit(),
            "ad_user": QLineEdit(),
            "file_path": QLineEdit(),
            'timestamp': QLineEdit(),
        }

        layout = QHBoxLayout(self)
        for column in self.create_form_layouts():
            layout.addLayout(column)

    def create_form_layouts(self):
        layouts = []
        fields = [
            ("user", "user"),
            ("ad user", "ad_user"),
            ("source file path", "file_path"),
            ("timestamp", "timestamp")
        ]

        for i in range(0, len(fields), 2):
            column = QFormLayout()
            for label, widget_key in fields[i:i + 2]:
                column.addRow(label, self.widgets[widget_key])
            layouts.append(column)

        return layouts

    def initialize_values(self):
        logged_in_user = os.getlogin()
        self.widgets['ad_user'].setText(logged_in_user)
        self.widgets['timestamp'].setText("< current datetime >")

        for widget in ['ad_user', 'timestamp', 'file_path']:
            self.widgets[widget].setReadOnly(True)

    def set_filepath(self, filepath):
        self.widgets['file_path'].setText(str(filepath))

    def get_filepath(self):
        return Path(self.widgets['file_path'].text())

    def data(self):
        current_time = datetime.now().strftime("%y%m%d %H.%M.%S")
        self.widgets['timestamp'].setText(current_time)

        data = {key: widget.text() for key, widget in self.widgets.items()}

        if not data['user']:
            data['user'] = data['ad_user']

        return data
