import pytest
import logging
from PySide6.QtWidgets import QApplication, QWidget
import sys

@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for the entire test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

@pytest.fixture
def logger():
    """Create a logger instance for testing."""
    return logging.getLogger("test_logger")

@pytest.fixture
def data_manager(qapp, logger):
    """Create a DataManager instance for testing."""
    from modules.model.data_manager import DataManager
    return DataManager(logger=logger)

@pytest.fixture
def sample_index_data():
    """Sample index data for testing."""
    return {
        "name": "Test Kit",
        "version": "1.0",
        "indices": [
            {"i7": "ACGTACGT", "i7_name": "Index1", "i5": "TGCATGCA", "i5_name": "Index1_i5"},
            {"i7": "GCTAGCTA", "i7_name": "Index2", "i5": "CGATCGAT", "i5_name": "Index2_i5"}
        ]
    }

@pytest.fixture
def central_widget(qapp, data_manager, logger):
    """Create a CentralWidget instance for testing."""
    from modules.view.central_widget.central_widget import CentralWidget
    from modules.view.metadata.resource_settings.resource_settings_widget import ResourceSettingsWidget
    from modules.view.metadata.user_settings.user_settings_widget import UserSettingsWidget
    from modules.view.metadata.index_metadata.index_metadata import IndexMetadata
    
    # Create required widget dependencies
    draggable_labels = QWidget()
    resources_settings = ResourceSettingsWidget(data_manager, logger)
    droppable_table = QWidget()
    user_settings = UserSettingsWidget(data_manager, logger)
    index_kit_settings = QWidget()
    index_metadata = IndexMetadata(data_manager, logger)
    
    return CentralWidget(
        data_manager=data_manager,
        draggable_labels_container_widget=draggable_labels,
        resources_settings_widget=resources_settings,
        droppable_table_widget=droppable_table,
        user_settings_widget=user_settings,
        index_kit_settings_widget=index_kit_settings,
        index_metadata=index_metadata,
        logger=logger
    )
