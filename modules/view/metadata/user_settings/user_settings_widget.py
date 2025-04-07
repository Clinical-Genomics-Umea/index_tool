from logging import Logger
from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QVBoxLayout

from modules.model.data_manager import DataManager


class UserSettingsWidget(QGroupBox):

    user_changed = Signal(str)

    def __init__(self, data_manager: DataManager, logger: Logger):
        super().__init__("User settings")

        self._data_manager = data_manager
        self._logger = logger

        self.setFixedWidth(1006)

        self._user_lineedit = QLineEdit()
        self._ad_user_lineedit = QLineEdit()
        self._ad_user_lineedit.setReadOnly(True)
        self._source_filepath_lineedit = QLineEdit()
        self._source_filepath_lineedit.setReadOnly(True)

        self._setup_ui()

        self._user_lineedit.textChanged.connect(self.user_changed)


    def _setup_ui(self):

        layout_v = QVBoxLayout(self)
        layout_h = QHBoxLayout(self)

        form_1 = QFormLayout()
        form_2 = QFormLayout()
        form_3 = QFormLayout()

        form_1.addRow("user", self._user_lineedit)
        form_2.addRow("ad user", self._ad_user_lineedit)
        form_3.addRow("source file path", self._source_filepath_lineedit)


        layout_h.addLayout(form_1)
        layout_h.addLayout(form_2)

        layout_v.addLayout(layout_h)
        layout_v.addLayout(form_3)

        self.setLayout(layout_v)

    def set_source_filepath(self, filepath):
        self._source_filepath_lineedit.setText(str(filepath))

    def set_user(self, user: str):
        self._user_lineedit.setText(user)

    def set_ad_user(self, user: str):
        self._ad_user_lineedit.setText(user)

    @property
    def source_filepath(self):
        return Path(self._source_filepath_lineedit.text())

    @property
    def user(self):
        return self._user_lineedit.text()

    @property
    def ad_user(self):
        return self._ad_user_lineedit.text()

