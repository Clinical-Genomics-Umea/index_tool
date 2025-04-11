from logging import Logger
from pathlib import Path
from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QVBoxLayout

from modules.model.data_manager import DataManager


class UserSettingsWidget(QGroupBox):

    def __init__(self, data_manager: DataManager, logger: Logger):
        super().__init__("User settings")

        self._data_manager = data_manager
        self._logger = logger

        self.setFixedWidth(1006)

        self._user_lineedit = QLineEdit()
        self._ad_user_lineedit = QLineEdit()
        self._ad_user_lineedit.setReadOnly(True)

        self._setup_ui()

        self._user_lineedit.textChanged.connect(self._save_user)
        self._ad_user_lineedit.textChanged.connect(self._save_ad_user)

    def _save_user(self):
        self._data_manager.set_user(self._user_lineedit.text())

    def _save_ad_user(self):
        self._data_manager.set_ad_user(self._ad_user_lineedit.text())

    def _setup_ui(self):

        layout_v = QVBoxLayout(self)
        layout_h = QHBoxLayout(self)

        form_1 = QFormLayout()
        form_2 = QFormLayout()

        form_1.addRow("user", self._user_lineedit)
        form_2.addRow("ad user", self._ad_user_lineedit)


        layout_h.addLayout(form_1)
        layout_h.addLayout(form_2)

        layout_v.addLayout(layout_h)

        self.setLayout(layout_v)

    def set_user(self, user: str):
        self._user_lineedit.setText(user)

    def set_ad_user(self):
        self._ad_user_lineedit.setText(self._data_manager.ad_user)

    @property
    def user(self):
        return self._user_lineedit.text()

    @property
    def ad_user(self):
        return self._ad_user_lineedit.text()

