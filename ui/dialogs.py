"""UI dialogs for GuckMohl"""
from pathlib import Path
from PIL import Image, ImageQt
from PySide6.QtWidgets import (QDialog, QFormLayout, QLabel, QPushButton, QHBoxLayout, 
                               QComboBox, QDialogButtonBox, QInputDialog, QMessageBox, QCheckBox, QVBoxLayout,
                               QGridLayout, QScrollArea, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap


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

class CompareDialog(QDialog):
    """Dialog for comparing marked images in a grid layout"""
    
    def __init__(self, parent, marked_image_paths, translator):
        super().__init__(parent)
        self.translator = translator
        self.marked_image_paths = marked_image_paths
        self.setWindowTitle(self.translator.translate("compare_title"))
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout()
        
        # Title with image count
        count_text = self.translator.translate("compare_count", count=len(marked_image_paths))
        title_label = QLabel(count_text)
        title_font = QFont()
        title_font.setPointSize(title_font.pointSize() + 2)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Create scroll area for image grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Grid widget and layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(10)
        
        # Add images in grid (4 columns)
        columns = 4
        row = 0
        col = 0
        
        for image_path in marked_image_paths:
            # Create container for each image
            image_container = self.create_image_thumbnail(image_path)
            grid_layout.addWidget(image_container, row, col)
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
        
        # Add stretch to fill remaining rows
        grid_layout.setRowStretch(row + 1, 1)
        scroll_area.setWidget(grid_widget)
        layout.addWidget(scroll_area)
        
        # Close button
        close_button = QPushButton(self.translator.translate("button_back"))
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
    
    def create_image_thumbnail(self, image_path):
        """Create a thumbnail widget for an image"""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        try:
            # Load and scale image
            pil_image = Image.open(str(image_path))
            pil_image.thumbnail((200, 200), Image.Resampling.LANCZOS)
            qimage = ImageQt.ImageQt(pil_image)
            pixmap = QPixmap.fromImage(qimage)
            
            # Create image label
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Create filename label
            filename_label = QLabel(image_path.name)
            filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            filename_font = QFont()
            filename_font.setPointSize(filename_font.pointSize() - 1)
            filename_label.setFont(filename_font)
            filename_label.setWordWrap(True)
            
            container_layout.addWidget(image_label)
            container_layout.addWidget(filename_label)
            
        except Exception as e:
            # Show error label if image cannot be loaded
            error_label = QLabel(f"Error loading:\n{image_path.name}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_font = QFont()
            error_font.setPointSize(error_font.pointSize() - 1)
            error_label.setFont(error_font)
            container_layout.addWidget(error_label)
        
        return container