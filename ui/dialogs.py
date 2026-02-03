"""UI dialogs for GuckMohl"""
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QFormLayout, QLabel, QPushButton, QHBoxLayout, 
                               QComboBox, QDialogButtonBox, QInputDialog, QMessageBox, QCheckBox, QVBoxLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SettingsDialog(QDialog):
    """Settings dialog for configuring archive folder and language"""
    
    def __init__(self, parent, current_archive_folder, current_language, available_languages, translator, archive_related_files=False, delete_related_files=False):
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.translate("settings_title"))
        self.setMinimumWidth(500)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Form layout for settings
        layout = QFormLayout()
        
        # Archive folder input field
        self.archive_input = QInputDialog()
        self.archive_folder = current_archive_folder
        archive_label = QLabel(current_archive_folder)
        change_archive_btn = QPushButton("...")
        change_archive_btn.clicked.connect(lambda: self.change_archive_folder(archive_label))
        
        archive_layout = QHBoxLayout()
        archive_layout.addWidget(archive_label)
        archive_layout.addWidget(change_archive_btn)
        
        # Archive related files checkbox
        self.archive_related_files_checkbox = QCheckBox()
        self.archive_related_files_checkbox.setChecked(archive_related_files)
        
        # Delete related files checkbox
        self.delete_related_files_checkbox = QCheckBox()
        self.delete_related_files_checkbox.setChecked(delete_related_files)
        
        # Language selection dropdown
        self.language_combo = QComboBox()
        for lang_code, lang_name in available_languages.items():
            self.language_combo.addItem(lang_name, lang_code)
        
        # Set current language as selected
        index = self.language_combo.findData(current_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        layout.addRow(self.translator.translate("settings_archive_folder"), archive_layout)
        layout.addRow(self.translator.translate("settings_archive_related_files"), self.archive_related_files_checkbox)
        layout.addRow(self.translator.translate("settings_delete_related_files"), self.delete_related_files_checkbox)
        layout.addRow(self.translator.translate("settings_language"), self.language_combo)
        
        main_layout.addLayout(layout)
        
        # Settings location info
        settings_path = Path.home() / '.guckmohl' / 'settings.json'
        info_label = QLabel()
        info_font = QFont()
        info_font.setPointSize(info_font.pointSize() - 1)
        info_label.setFont(info_font)
        info_label.setStyleSheet("color: gray; margin-top: 15px; padding-top: 10px; border-top: 1px solid #ccc;")
        info_label.setText(f"Settings stored at:\n{settings_path}")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)
        self.archive_label = archive_label
    
    def change_archive_folder(self, label):
        text, ok = QInputDialog.getText(
            self,
            self.translator.translate("settings_title"),
            self.translator.translate("settings_archive_folder"),
            text=self.archive_folder
        )
        
        if ok and text.strip():
            # Validate folder name (check for invalid characters)
            invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            if any(char in text for char in invalid_chars):
                QMessageBox.warning(
                    self,
                    self.translator.translate("settings_invalid_name"),
                    self.translator.translate("settings_invalid_chars")
                )
                return
            
            self.archive_folder = text.strip()
            label.setText(self.archive_folder)
    
    def get_settings(self):
        return {
            'archive_folder': self.archive_folder,
            'language': self.language_combo.currentData(),
            'archive_related_files': self.archive_related_files_checkbox.isChecked(),
            'delete_related_files': self.delete_related_files_checkbox.isChecked()
        }
