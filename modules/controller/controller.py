import logging

from PySide6.QtCore import QObject

from modules.model.data_manager import DataManager
from modules.model.load.csvloader import CsvLoader
from modules.view.central_widget.central_widget import CentralWidget
from modules.view.data_container_widget.data_container_widget import DataContainerWidget
from modules.view.draggable_labels.draggable_labels import DraggableLabelsContainer
from modules.view.index_table.droppable_table import DroppableTableWidget
from modules.view.logging.log_toast_handler import LogToastHandler
from modules.view.main_window import MainWindow
from modules.view.logging.message_toast import MessageToast
from modules.view.metadata.resource_settings.resource_settings_widget import ResourceSettingsWidget
from modules.view.metadata.index_kit_settings.index_kit_settings_widget import IndexKitSettingsWidget
from modules.view.metadata.user_settings.user_settings_widget import UserSettingsWidget


class MainController(QObject):
    def __init__(self):
        """
        Initialize main controller, setting up models, views, and connections.
        """
        super().__init__()

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._log_widget = None

        self._csv_loader = CsvLoader(self._logger)
        self._data_manager = DataManager(self._csv_loader, self._logger)
        self._resources_settings_widget = ResourceSettingsWidget(self._data_manager, self._logger)
        self._draggable_labels_container_widget = DraggableLabelsContainer(self._data_manager, self._logger)
        self._user_settings_widget = UserSettingsWidget(self._data_manager, self._logger)
        self._index_kit_settings_widget = IndexKitSettingsWidget(self._data_manager, self._logger)
        self._droppable_table_widget = DroppableTableWidget(0, 0, self._data_manager)

        self._central_widget = CentralWidget(self._data_manager,
                                             self._draggable_labels_container_widget,
                                             self._resources_settings_widget,
                                             self._droppable_table_widget,
                                             self._user_settings_widget,
                                             self._index_kit_settings_widget,
                                             self._logger)

        self._message_toast = MessageToast()
        self._log_toast_handler = LogToastHandler(self._message_toast)
        self.main_window = MainWindow(self._central_widget, self._message_toast)
        self._init_data()
        self._set_connections()

    def _init_data(self):
        self._draggable_labels_container_widget.show_labels()

    def _set_connections(self):
        self._set_user_connections()
        self._set_data_manager_connections()

    def _set_data_manager_connections(self):
        self._data_manager.selected_kit_type_name_changed.connect(self._draggable_labels_container_widget.show_labels)
        self._data_manager.index_df_changed.connect(self._droppable_table_widget.set_index_table_widget_data)


    def _set_user_connections(self):
        self._user_settings_widget.user_changed.connect(self._data_manager.set_user)

    # def _set_data_manager_connections(self):
    #
    #     self._resources_settings_widget._kit_type_name_combobox.currentTextChanged.connect(self._draggable_labels_container_widget.show_labels)
    #     self._data_manager.user_changed.connect(self._user_settings_widget.set_user)
    #     self._data_manager.ad_user_changed.connect(self._user_settings_widget.set_ad_user)
    #     self._data_manager.source_filepath_changed.connect(self._user_settings_widget.set_source_filepath)
    #
    #     self._data_manager.adapter_read_1_changed.connect(self._resources_settings_widget.set_adapter_read1_lineedit)
    #     self._data_manager.adapter_read_2_changed.connect(self._resources_settings_widget.set_adapter_read2_lineedit)
    #     self._data_manager.oc_read1_changed.connect(self._resources_settings_widget.set_override_cycles_pattern_r1_lineedit)
    #     self._data_manager.oc_read2_changed.connect(self._resources_settings_widget.set_override_cycles_pattern_r2_lineedit)
    #     self._data_manager.oc_index1_changed.connect(self._resources_settings_widget.set_override_cycles_pattern_i1_lineedit)
    #     self._data_manager.oc_index2_changed.connect(self._resources_settings_widget.set_override_cycles_pattern_i2_lineedit)


        # self._data_manager.index_df_changed.connect(self._data_container_widget.set_index_table_data)


        # self._data_manager.kit_name_changed.connect(self._resource_settings_widget.set_kit_name)
        # self._data_manager.display_name_changed
        # self._data_manager.version_changed
        # self._data_manager.description_changed
        #
        # # Resources
        # self._data_manager.adapter_read_1_changed
        # self._data_manager.adapter_read_2_changed
        # self._data_manager.kit_type_changed
        # self._data_manager.oc_read1_changed
        # self._data_manager.oc_read2_changed
        # self._data_manager.oc_index1_changed
        # self._data_manager.oc_index2_changed



