import getpass
import json
import re
from logging import Logger
from pathlib import Path
from pprint import pprint
from typing import Any

import pandas as pd

from modules.model.config_object import ConfigObject
from PySide6.QtCore import QObject, Signal
import yaml

from modules.model.index_set_processing import index_fields_validator, clean_df, index_seq_validator, \
    nonempty_validator, nonduplicate_validator, index_len
from modules.model.load.csvloader import CsvLoader


class DataManager(QObject):

    user_changed = Signal()
    ad_user_changed = Signal()
    source_filepath_changed = Signal()

    # Kit settings
    kit_name_changed = Signal()
    display_name_changed = Signal()
    version_changed = Signal()
    description_changed = Signal()

    # Resources
    adapter_read_1_changed = Signal()
    adapter_read_2_changed = Signal()
    selected_kit_type_name_changed = Signal()
    set_override_cycles_read_1_changed = Signal()
    override_cycles_read_2_changed = Signal()
    override_cycles_index_1_changed = Signal()
    override_cycles_index_2_changed = Signal()

    # Table
    index_df_changed = Signal()

    init_done = Signal()


    def __init__(self, csv_loader: CsvLoader, logger: Logger):
        super().__init__()

        self._csv_loader = csv_loader
        self._logger = logger
        self._config_definition_path = Path("config/config_objects.yaml")
        self._config_definition_data: dict | None = None

        self._dna_regex = re.compile(r'^[ATCG]+$', re.IGNORECASE)
        self._index_seq_col_names = ['index_i7', 'index_i5']

        self._uuid = None

        # User info
        self._index_df = pd.DataFrame()
        self._user = None
        self._ad_user = None
        self._source_filepath = None

        # Kit settings
        self._index_kit_name = None
        self._display_name = None
        self._version = None
        self._description = None

        # Resources
        self._adapter_read_1 = None
        self._adapter_read_2 = None
        self._config_type_name = None
        self._override_cycles_read_1 = "Y{r}"
        self._override_cycles_read_2 = "Y{r}"
        self._override_cycles_index_1 = "I{i}"
        self._override_cycles_index_2 = "I{i}"

        self._selected_config = None
        self._config_list = None

        self._index_i7_len = 0
        self._index_i5_len = 0

        self._init_settings_configs()

    def _index_validation(self, df, index_set_fields):

        df_cleaned = clean_df(df)

        for set_name, field_list in index_set_fields.items():
            if not index_fields_validator(df_cleaned, field_list):
                self._logger.error(f"all fields not set for {set_name}")
                return False

        for set_name, field_list in index_set_fields.items():
            for field in field_list:
                if not field in self._index_seq_col_names:
                    continue

                if not index_seq_validator(df, field):
                    self._logger.error(f"invalid index for {field}")
                    return False

        for set_name, field_list in index_set_fields.items():
            df_cleaned_field = df[field_list]
            df_cleaned_field_cleaned = clean_df(df_cleaned_field)

            print(df_cleaned_field_cleaned.to_string())

            if not nonempty_validator(df_cleaned_field_cleaned):
                self._logger.error(f"empty index for {set_name}")
                return False

            for field in field_list:
                if not nonduplicate_validator(df_cleaned_field_cleaned, field):
                    self._logger.error(f"duplicate values in {field}")
                    return False

        return True

    def save_json_data(self, filepath):

        df = self.index_df
        index_set_fields = self.selected_index_set_fields()

        if not self._index_validation(df, index_set_fields):
            return



        index_sets = {}

        for set_name, field_list in index_set_fields.items():
            df_set_cleaned = clean_df(df[field_list])
            dict_records = df_set_cleaned.to_dict(orient='records')
            index_sets[set_name] = dict_records

            if "index_i7" in df_set_cleaned.columns:
                try:
                    self._index_i7_len = index_len(df_set_cleaned, "index_i7")
                except ValueError as e:
                    self._logger.error(e)
                    return

            if "index_i5" in df_set_cleaned.columns:
                self._index_i5_len = index_len(df_set_cleaned, "index_i5")
                try:
                    self._index_i5_len = index_len(df_set_cleaned, "index_i5")
                except ValueError as e:
                    self._logger.error(e)
                    return




        data = {
            "UID": self.uuid,
            "IndexKitName": self.index_kit_name,
            "DisplayName": self.display_name,
            "Version": self.version,
            "Description": self.description,
            "Adapters": {
                "AdapterRead1": self.adapter_read_1,
                "AdapterRead2": self.adapter_read_2
            },
            "IndexStrategy": self.index_strategy,
            "IndexI7Len": self._index_i7_len,
            "IndexI5Len": self._index_i5_len,
            "IndexSets": index_sets
        }

        with open(filepath, "w") as file:
            json.dump(data, file, indent=4)

    def set_index_df_from_path(self, path: Path):
        if path.suffix == ".csv":
            try:
                df = self._csv_loader.load_csv(path)
            except Exception as e:
                self._logger.warning(e)
                return

            self.set_index_df(df)
            self.set_source_filepath(str(path))

    def set_selected_kit_type_name(self, name):
        self._selected_config = name
        self.selected_kit_type_name_changed.emit()

    def set_uuid(self, uuid):
        self._uuid = uuid

    @property
    def selected_config_obj(self):
        return self.config_definition_obj(self._selected_config)

    @property
    def index_strategy(self):
        conf_obj = self.selected_config_obj
        return conf_obj.index_strategy

    def selected_index_set_fields(self):
        conf_obj = self.selected_config_obj
        return conf_obj.index_sets

    @property
    def index_kit_name(self):
        return self._index_kit_name

    @property
    def uuid(self):
        return self._uuid or "None"

    @property
    def selected_kit_type_name(self):
        return self._selected_config

    @property
    def config_type_names(self) -> list:
        return list(self._config_definition_data.keys())

    def set_index_df(self, df: pd.DataFrame):
        if self._index_df.equals(df):
            return

        self._index_df = df
        self.index_df_changed.emit()

    def set_user(self, user: str):
        if self._user == user:
            return

        self._user = user
        self.user_changed.emit()

    def set_source_filepath(self, path: str):
        if self._source_filepath == path:
            return

        self._source_filepath = path
        self.source_filepath_changed.emit()

    def set_ad_user(self, ad_user: str):
        if self._ad_user == ad_user:
            return

        self._ad_user = ad_user
        self.ad_user_changed.emit()

    def set_kit_name(self, kit_name):
        if self._index_kit_name == kit_name:
            return

        self._index_kit_name = kit_name
        self.kit_name_changed.emit()

    def set_display_name(self, display_name):
        if self._display_name == display_name:
            return

        self._display_name = display_name
        self.display_name_changed.emit()

    def set_version(self, version):
        if self._version == version:
            return

        self._version = version
        self.version_changed.emit()

    def set_description(self, description):
        if self._description == description:
            return

        self._description = description
        self.description_changed.emit()

    def set_adapter_read_1(self, adapter_read_1):
        if self._adapter_read_1 == adapter_read_1:
            return

        self._adapter_read_1 = adapter_read_1
        self.adapter_read_1_changed.emit()

    def set_adapter_read_2(self, adapter_read_2):
        if self._adapter_read_2 == adapter_read_2:
            return

        self._adapter_read_2 = adapter_read_2
        self.adapter_read_2_changed.emit()

    def set_config_type_name(self, config_type_name):
        if self._config_type_name == config_type_name:
            return

        self._config_type_name = config_type_name
        self.selected_kit_type_name_changed.emit()

    def set_config_type_name_list(self, config_type_name_list):
        self._config_list = config_type_name_list

    def set_override_cycles_read_1(self, oc_read1):
        if self._override_cycles_read_1 == oc_read1:
            return

        self._override_cycles_read_1 = oc_read1
        self.set_override_cycles_read_1_changed.emit()

    def set_override_cycles_read_2(self, oc_read2):
        if self._override_cycles_read_2 == oc_read2:
            return

        self._override_cycles_read_2 = oc_read2
        self.override_cycles_read_2_changed.emit()

    def set_override_cycles_index_1(self, oc_index1):
        if self._override_cycles_index_1 == oc_index1:
            return

        self._override_cycles_index_1 = oc_index1
        self.override_cycles_index_1_changed.emit()

    def set_override_cycles_index_2(self, oc_index2):
        if self._override_cycles_index_2 == oc_index2:
            return

        self._override_cycles_index_2 = oc_index2
        self.override_cycles_index_2_changed.emit()

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
    def source_filepath(self):
        return self._source_filepath

    @property
    def kit_name(self):
        return self._index_kit_name

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
        return self._config_type_name

    @property
    def override_cycles_read_1(self):
        return self._override_cycles_read_1

    @property
    def override_cycles_read_2(self):
        return self._override_cycles_read_2

    @property
    def override_cycles_index_1(self):
        return self._override_cycles_index_1

    @property
    def override_cycles_index_2(self):
        return self._override_cycles_index_2

    @property
    def config_definition_data(self) -> dict:
        return self._config_definition_data

    def config_definition_obj(self, name) -> ConfigObject:
        return self._config_definition_data[name]

    @property
    def kit_config_definition_type_names(self) -> list:
        return list(self._config_definition_data.keys())

    def _init_settings_configs(self):

        try:
            with open(self._config_definition_path, 'r') as file:
                kit_config_data = yaml.safe_load(file)
        except Exception as e:
            self._logger.error(f"Error: {str(e)}")

        res = {}

        pprint(kit_config_data)

        for config in kit_config_data:
            kit_def_obj = ConfigObject(config)
            res[kit_def_obj.config_type_name] = kit_def_obj

        self._config_definition_data = res

        ad_user = getpass.getuser()
        self.set_ad_user(ad_user)

        print(f"Loaded {len(res)} kits")


