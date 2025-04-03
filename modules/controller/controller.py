import logging

from PySide6.QtCore import QObject

from modules.model.configuration_manager import ConfigurationManager
from modules.view.central_widget.central_widget import CentralWidget
from modules.view.data_container_widget.data_container_widget import DataContainerWidget
from modules.view.draggable_labels.draggable_labels import DraggableLabelsContainer
from modules.view.index_table.droppable_table import DroppableTableWidget
from modules.view.logging.log_toast_handler import LogToastHandler
from modules.view.main_window import MainWindow
from modules.view.logging.message_toast import MessageToast
from modules.view.metadata.adapters_override_cycles_widget import AdaptersOverrideCyclesWidget


class MainController(QObject):
    def __init__(self):
        """
        Initialize main controller, setting up models, views, and connections.
        """
        super().__init__()

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._log_widget = None


        self._configuration_manager = ConfigurationManager(self._logger)
        self._draggable_labels_container_widget = DraggableLabelsContainer(self._configuration_manager)
        self._resource_settings_widget = AdaptersOverrideCyclesWidget(self._configuration_manager, self._draggable_labels_container_widget)

        self._droppable_table_widget = DroppableTableWidget(0, 0)
        self._data_container_widget = DataContainerWidget(self._configuration_manager, self._droppable_table_widget, self._resource_settings_widget, self._draggable_labels_container_widget)

        self._central_widget = CentralWidget(self._data_container_widget, self._logger)


        self._message_toast = MessageToast()
        self._log_toast_handler = LogToastHandler(self._message_toast)

        self.main_window = MainWindow(self._central_widget, self._message_toast)


