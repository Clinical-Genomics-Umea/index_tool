from logging import Logger

from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QVBoxLayout

from modules.model.data_manager import DataManager



class IndexMetadata(QGroupBox):
    def __init__(self, data_manager: DataManager, logger: Logger):
        super().__init__()
        self.setTitle("Index Metadata")
        self.setFixedWidth(1006)
        self._data_manager = data_manager
        self._logger = logger

        self._import_filepath = QLineEdit()
        self._import_filetype = QLineEdit()
        self._ilmn_seq_strategy = QLineEdit()
        self._ilmn_fixed_layout = QLineEdit()
        self._index_i5_count = QLineEdit()
        self._index_i7_count = QLineEdit()
        self._ilmn_umi_compatible = QLineEdit()

        self._setup_ui()

    def set_import_filepath(self):
        self._import_filepath.setText(str(self._data_manager.import_filepath))

    def set_import_filetype(self):
        self._import_filetype.setText(self._data_manager.import_filetype)

    def set_ilmn_seq_strategy(self):
        self._ilmn_seq_strategy.setText(self._data_manager.ilmn_seq_strategy)

    def set_ilmn_fixed_layout(self):
        self._ilmn_fixed_layout.setText(str(self._data_manager.ilmn_fixed_layout))

    def set_index_i5_count(self):
        self._index_i5_count.setText(str(self._data_manager.index_i5_count))

    def set_index_i7_count(self):
        self._index_i7_count.setText(str(self._data_manager.index_i7_count))

    def set_ilmn_umi_compatible(self):
        self._ilmn_umi_compatible.setText(self._data_manager.ilmn_umi_compatible)

    def _setup_ui(self):
        self._import_filepath.setReadOnly(True)
        self._import_filetype.setReadOnly(True)
        self._ilmn_seq_strategy.setReadOnly(True)
        self._ilmn_fixed_layout.setReadOnly(True)
        self._index_i5_count.setReadOnly(True)
        self._index_i7_count.setReadOnly(True)
        self._ilmn_umi_compatible.setReadOnly(True)

        main_layout = QVBoxLayout()
        hbox_layout = QHBoxLayout()

        top_form_layout = QFormLayout()
        top_form_layout.addRow("Import Filepath", self._import_filepath)

        left_form_layout = QFormLayout()
        left_form_layout.addRow("Import Filetype", self._import_filetype)
        left_form_layout.addRow("Ilmn Sequencing Strategy", self._ilmn_seq_strategy)
        left_form_layout.addRow("Fixed Layout", self._ilmn_fixed_layout)

        right_form_layout = QFormLayout()
        right_form_layout.addRow("Index I7 Count", self._index_i7_count)
        right_form_layout.addRow("Index I5 Count", self._index_i5_count)
        right_form_layout.addRow("UMI Compatible", self._ilmn_umi_compatible)


        hbox_layout.addLayout(left_form_layout)
        hbox_layout.addLayout(right_form_layout)

        main_layout.addLayout(top_form_layout)
        main_layout.addLayout(hbox_layout)

        self.setLayout(main_layout)

