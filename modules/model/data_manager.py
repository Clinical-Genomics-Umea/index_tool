import getpass
from logging import Logger
from pathlib import Path

import pandas as pd

from modules.model.kit_def_loader import mk_kit_def_obj
from PySide6.QtCore import QObject, Signal
import yaml

from modules.model.load.csvloader import CsvLoader


class DataManager(QObject):

    user_changed = Signal(str)
    ad_user_changed = Signal(str)
    source_filepath_changed = Signal(str)

    # Kit settings
    kit_name_changed = Signal(str)
    display_name_changed = Signal(str)
    version_changed = Signal(str)
    description_changed = Signal(str)

    # Resources
    adapter_read_1_changed = Signal(str)
    adapter_read_2_changed = Signal(str)
    kit_type_changed = Signal(str)
    oc_read1_changed = Signal(str)
    oc_read2_changed = Signal(str)
    oc_index1_changed = Signal(str)
    oc_index2_changed = Signal(str)

    # Table
    index_df_changed = Signal()
    selected_kit_type_name_changed = Signal()

    init_done = Signal()


    def __init__(self, csv_loader: CsvLoader, logger: Logger):
        super().__init__()

        self._csv_loader = csv_loader
        self._logger = logger
        self._kit_type_definition_file = Path("config/kit_type_fields.yaml")
        self._kit_type_definition_data: dict | None = None

        # User info
        self._index_df = pd.DataFrame()
        self._user = None
        self._ad_user = None
        self._source_filepath = None

        # Kit settings
        self._kit_name = None
        self._display_name = None
        self._version = None
        self._description = None

        # Resources
        self._adapter_read_1 = None
        self._adapter_read_2 = None
        self._kit_type = None
        self._oc_read1 = None
        self._oc_read2 = None
        self._oc_index1 = None
        self._oc_index2 = None

        self._selected_kit_type_name = None

        self._init_settings()

    def set_index_df_from_path(self, path: Path):
        if path.suffix == ".csv":
            df = self._csv_loader.load_csv(path)
            self.set_index_df(df)


    def set_selected_kit_type_name(self, name):
        self._selected_kit_type_name = name
        self.selected_kit_type_name_changed.emit()

    @property
    def selected_kit_type_name(self):
        return self._selected_kit_type_name

    @property
    def kit_names(self) -> list:
        return list(self._kit_type_definition_data.keys())

    def set_index_df(self, df: pd.DataFrame):
        if self._index_df.equals(df):
            return

        print("set_index_df")

        self._index_df = df
        self.index_df_changed.emit()

    def set_user(self, user: str):
        if self._user == user:
            return

        self._user = user
        self.user_changed.emit(user)

    def set_source_filepath(self, path: str):
        if self._source_filepath == path:
            return

        self._source_filepath = path
        self.source_filepath_changed.emit(path)

    def set_ad_user(self, ad_user: str):
        if self._ad_user == ad_user:
            return

        self._ad_user = ad_user
        self.ad_user_changed.emit(ad_user)

    def set_kit_name(self, kit_name):
        if self._kit_name == kit_name:
            return

        self._kit_name = kit_name
        self.kit_name_changed.emit(kit_name)

    def set_display_name(self, display_name):
        if self._display_name == display_name:
            return

        self._display_name = display_name
        self.display_name_changed.emit(display_name)

    def set_version(self, version):
        if self._version == version:
            return

        self._version = version
        self.version_changed.emit(version)

    def set_description(self, description):
        if self._description == description:
            return

        self._description = description
        self.description_changed.emit(description)

    def set_adapter_read_1(self, adapter_read_1):
        if self._adapter_read_1 == adapter_read_1:
            return

        self._adapter_read_1 = adapter_read_1
        self.adapter_read_1_changed.emit(adapter_read_1)

    def set_adapter_read_2(self, adapter_read_2):
        if self._adapter_read_2 == adapter_read_2:
            return

        self._adapter_read_2 = adapter_read_2
        self.adapter_read_2_changed.emit(adapter_read_2)

    def set_kit_type(self, kit_type):
        if self._kit_type == kit_type:
            return

        self._kit_type = kit_type
        self.kit_type_changed.emit(kit_type)

    def set_kit_type_list(self, kit_list):
        self._kit_type_list = kit_list


    def set_oc_read1(self, oc_read1):
        if self._oc_read1 == oc_read1:
            return

        self._oc_read1 = oc_read1
        self.oc_read1_changed.emit(oc_read1)

    def set_oc_read2(self, oc_read2):
        if self._oc_read2 == oc_read2:
            return

        self._oc_read2 = oc_read2
        self.oc_read2_changed.emit(oc_read2)

    def set_oc_index1(self, oc_index1):
        if self._oc_index1 == oc_index1:
            return

        self._oc_index1 = oc_index1
        self.oc_index1_changed.emit(oc_index1)

    def set_oc_index2(self, oc_index2):
        if self._oc_index2 == oc_index2:
            return

        self._oc_index2 = oc_index2
        self.oc_index2_changed.emit(oc_index2)

    @property
    def index_df(self):
        return self._index_df

    @property
    def user(self):
        return self._user

    @property
    def ad_user(self):
        return self._ad_user

    @property
    def source_file_path(self):
        return self._source_filepath

    @property
    def kit_name(self):
        return self._kit_name

    @property
    def display_name(self):
        return self._display_name

    @property
    def version(self):
        return self._version

    @property
    def description(self):
        return self._description

    @property
    def adapter_read_1(self):
        return self._adapter_read_1

    @property
    def adapter_read_2(self):
        return self._adapter_read_2

    @property
    def kit_type(self):
        return self._kit_type

    @property
    def oc_read1(self):
        return self._oc_read1

    @property
    def oc_read2(self):
        return self._oc_read2

    @property
    def oc_index1(self):
        return self._oc_index1

    @property
    def oc_index2(self):
        return self._oc_index2

    @property
    def kit_type_definition_data(self) -> dict:
        return self._kit_type_definition_data

    def kit_type_definition_obj(self, name) -> dict:
        return self._kit_type_definition_data[name]

    @property
    def kit_type_definition_names(self) -> list:
        return list(self._kit_type_definition_data.keys())

    # def load_csv(self, file_path: Path):
    #     try:
    #         self._index_df = self._csv_loader.load_csv(file_path)
    #         self._source_filepath = str(file_path)
    #     except Exception as e:
    #         self._logger.error(f"Error loading CSV: {str(e)}")

    def _init_settings(self):

        try:
            with open(self._kit_type_definition_file, 'r') as file:
                kit_def_data = yaml.safe_load(file)
        except Exception as e:
            self._logger.error(f"Error: {str(e)}")

        self._kit_type_definition_data = mk_kit_def_obj(kit_def_data)

        ad_user = getpass.getuser()
        self.set_ad_user(ad_user)


