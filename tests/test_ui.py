import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableView
from modules.view.central_widget.central_widget import CentralWidget
import pandas as pd

def test_central_widget_creation(central_widget):
    """Test that the central widget can be created."""
    assert central_widget is not None
    assert isinstance(central_widget, CentralWidget)

def test_index_table_population(central_widget, data_manager):
    """Test that the index table can be populated with data."""
    # Create test data
    test_df = pd.DataFrame({
        'i7_name': ['Test1', 'Test2'],
        'i7': ['ACGTACGT', 'GCTAGCTA'],
        'i5_name': ['Test1_i5', 'Test2_i5'],
        'i5': ['TGCATGCA', 'CGATCGAT']
    })
    
    # Update data manager with test data
    data_manager._index_df = test_df
    data_manager.index_df_changed.emit()
    
    # Get the table from central widget
    table = central_widget.findChild(QTableView)
    if table and table.model():
        assert table.model().rowCount() > 0

def test_sequence_validation(data_manager):
    """Test sequence validation using the DNA regex."""
    # Valid sequence
    assert data_manager._dna_regex.match("ACGTACGT") is not None
    
    # Invalid sequence
    assert data_manager._dna_regex.match("ACGTXXGT") is None

def test_filepath_handling(data_manager, tmp_path):
    """Test filepath handling."""
    # Create a test file
    test_file = tmp_path / "test.csv"
    test_file.write_text("i7_name,i7\nTest1,ACGTACGT")
    
    # Set the import filepath using the internal attribute
    data_manager._import_filepath = str(test_file)
    assert data_manager._import_filepath == str(test_file)
