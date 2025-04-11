import pytest
import pandas as pd
from pathlib import Path
import json
import tempfile
import getpass
import re

def test_data_manager_initialization(data_manager):
    """Test that DataManager initializes with default values."""
    assert data_manager is not None
    assert hasattr(data_manager, '_user')
    assert hasattr(data_manager, '_import_filepath')
    assert isinstance(data_manager._index_df, pd.DataFrame)

def test_dna_sequence_validation(data_manager):
    """Test DNA sequence validation using the internal regex."""
    # Valid sequences
    assert data_manager._dna_regex.match("ACGTACGT")
    assert data_manager._dna_regex.match("TGCATGCA")
    
    # Invalid sequences
    assert not data_manager._dna_regex.match("ACGTXXGT")
    assert not data_manager._dna_regex.match("12345678")
    assert not data_manager._dna_regex.match("")

def test_index_data_handling(data_manager):
    """Test index data handling capabilities."""
    # Create test data
    test_df = pd.DataFrame({
        'i7_name': ['Index1', 'Index2'],
        'i7': ['ACGTACGT', 'GCTAGCTA'],
        'i5_name': ['Index1_i5', 'Index2_i5'],
        'i5': ['TGCATGCA', 'CGATCGAT']
    })
    
    # Set the index data
    data_manager._index_df = test_df
    
    # Verify the data was set
    assert len(data_manager._index_df) == 2
    assert all(col in data_manager._index_df.columns for col in ['i7_name', 'i7', 'i5_name', 'i5'])

def test_kit_settings(data_manager):
    """Test kit settings properties."""
    # Test kit name
    data_manager._index_kit_name = "Test Kit"
    assert data_manager._index_kit_name == "Test Kit"
    
    # Test version
    data_manager._version = "1.0"
    assert data_manager._version == "1.0"
    
    # Test description
    data_manager._description = "Test Description"
    assert data_manager._description == "Test Description"
