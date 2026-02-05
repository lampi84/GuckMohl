"""UI dialogs for GuckMohl"""
from pathlib import Path
from PIL import Image, ImageQt
from PySide6.QtWidgets import (QDialog, QFormLayout, QLabel, QPushButton, QHBoxLayout, 
                               QComboBox, QDialogButtonBox, QInputDialog, QMessageBox, QCheckBox, QVBoxLayout,
                               QGridLayout, QScrollArea, QWidget, QScrollBar)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap, QCursor


class ClickableImageLabel(QLabel):
    """Custom QLabel that emits clicked signal"""
    image_clicked = Signal(Path)
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setToolTip("Click to remove from selection")
    
    def mousePressEvent(self, event):
        """Handle mouse click events"""
        self.image_clicked.emit(self.image_path)


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
    
    # Signal emitted when an image is unmarked
    image_unmarked = Signal(Path)
    
    def __init__(self, parent, marked_image_paths, translator):
        super().__init__(parent)
        self.translator = translator
        self.marked_image_paths = list(marked_image_paths)  # Make a mutable copy
        self.image_labels = {}  # Store image labels for dynamic resizing
        self.image_containers = {}  # Store containers by path for removal
        self.setWindowTitle(self.translator.translate("compare_title"))
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout()
        
        # Title with image count
        #self.count_label = QLabel()
        #title_font = QFont()
        #title_font.setPointSize(title_font.pointSize() + 2)
        #title_font.setBold(True)
        #self.count_label.setFont(title_font)
        #self.update_count_label()
        
        # Combined info label with count and deselection instruction
        self.info_label = QLabel()
        info_font = QFont()
        info_font.setPointSize(info_font.pointSize() - 1)
        self.info_label.setFont(info_font)
        self.info_label.setStyleSheet("color: white; padding: 8px; background-color: #333333; border-radius: 3px;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        self.update_info_label()
        
        #layout.addWidget(self.count_label)
        layout.addWidget(self.info_label)
        
        # Create scroll area for image grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Grid widget and layout
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        
        # Add images in grid (4 columns)
        self.columns = 4
        row = 0
        col = 0
        
        for image_path in self.marked_image_paths:
            # Create container for each image
            image_container = self.create_image_thumbnail(image_path)
            self.grid_layout.addWidget(image_container, row, col)
            self.image_containers[str(image_path)] = (image_container, row, col)
            
            col += 1
            if col >= self.columns:
                col = 0
                row += 1
        
        # Add stretch to fill remaining rows
        self.grid_layout.setRowStretch(row + 1, 1)
        self.scroll_area.setWidget(self.grid_widget)
        layout.addWidget(self.scroll_area)
        
        # Close button
        close_button = QPushButton(self.translator.translate("button_back"))
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        
        # Timer for delayed resize updates
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.update_thumbnails_size)
    
    def update_count_label(self):
        """Update the count label text"""
        count_text = self.translator.translate("compare_count", count=len(self.marked_image_paths))
        self.count_label.setText(count_text)
    
    def update_info_label(self):
        """Update the info label with combined text"""
        count_text = self.translator.translate("compare_count", count=len(self.marked_image_paths))
        info_text = self.translator.translate("compare_info", default="Klicke auf ein Bild, um es zu deselektieren")
        combined_text = f"{count_text}\n{info_text}"
        self.info_label.setText(combined_text)
    
    def correct_image_orientation(self, image):
        """Correct image orientation based on EXIF tag 274 (Orientation)"""
        try:
            exif = image.getexif()
            orientation = exif.get(274, 1)  # Tag 274 = Orientation, default = 1 (normal)
            
            # Handle all 8 EXIF orientation values
            if orientation == 2:  # Horizontal flip
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:  # 180 degree rotation
                image = image.rotate(180, expand=True)
            elif orientation == 4:  # Vertical flip
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
            elif orientation == 5:  # Horizontal flip + 90 CW rotation
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
                image = image.rotate(90, expand=True)
            elif orientation == 6:  # 90 CW rotation
                image = image.rotate(270, expand=True)
            elif orientation == 7:  # Horizontal flip + 270 CW rotation
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
                image = image.rotate(270, expand=True)
            elif orientation == 8:  # 270 CW rotation
                image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass
        
        return image
    
    def create_image_thumbnail(self, image_path):
        """Create a thumbnail widget for an image"""
        container = QWidget()
        container.setMinimumHeight(250)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(5, 5, 5, 5)
        
        try:
            # Load and correct orientation
            pil_image = Image.open(str(image_path))
            pil_image = self.correct_image_orientation(pil_image)
            
            # Store original image for later rescaling
            container.original_pil_image = pil_image
            container.image_path = image_path
            
            # Create clickable image label
            image_label = ClickableImageLabel(image_path)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setMinimumHeight(200)
            image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
            
            # Connect click signal
            image_label.image_clicked.connect(self.on_image_clicked)
            
            # Initial pixmap scaling (max 200x200)
            self.scale_and_set_pixmap(image_label, pil_image, 200)
            
            # Store for dynamic resizing
            self.image_labels[id(container)] = (image_label, pil_image)
            container.image_label = image_label
            
            # Create filename label
            filename_label = QLabel(image_path.name)
            filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            filename_font = QFont()
            filename_font.setPointSize(filename_font.pointSize() - 1)
            filename_label.setFont(filename_font)
            filename_label.setWordWrap(True)
            
            container_layout.addWidget(image_label, 1)
            container_layout.addWidget(filename_label, 0)
            
        except Exception as e:
            # Show error label if image cannot be loaded
            error_label = QLabel(f"Error loading:\n{image_path.name}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_font = QFont()
            error_font.setPointSize(error_font.pointSize() - 1)
            error_label.setFont(error_font)
            container_layout.addWidget(error_label)
        
        return container
    
    def on_image_clicked(self, image_path):
        """Handle image click - remove from marked images"""
        image_path = Path(image_path)
        
        # Remove from marked list
        if image_path in self.marked_image_paths:
            self.marked_image_paths.remove(image_path)
        
        # Remove from containers
        path_str = str(image_path)
        if path_str in self.image_containers:
            container, row, col = self.image_containers[path_str]
            
            # Remove widget from layout
            self.grid_layout.removeWidget(container)
            container.deleteLater()
            
            # Remove from tracking
            del self.image_containers[path_str]
            
            # Clean up image_labels
            for key in list(self.image_labels.keys()):
                if id(container) == key:
                    del self.image_labels[key]
                    break
            
            # Emit signal to notify parent about deselection
            self.image_unmarked.emit(image_path)
            
            # Update count label and info label
            self.update_count_label()
            self.update_info_label()
            
            # Reorganize remaining images to maintain 4-column layout
            self.reorganize_grid()
    
    def reorganize_grid(self):
        """Reorganize grid after removing an image"""
        # Clear layout
        while self.grid_layout.count() > 0:
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Re-add all containers in correct positions
        row = 0
        col = 0
        for path_str in sorted(self.image_containers.keys()):
            container, _, _ = self.image_containers[path_str]
            self.grid_layout.addWidget(container, row, col)
            self.image_containers[path_str] = (container, row, col)
            
            col += 1
            if col >= self.columns:
                col = 0
                row += 1
        
        # Add stretch to fill remaining rows
        self.grid_layout.setRowStretch(row + 1, 1)
    
    def scale_and_set_pixmap(self, label, pil_image, max_size):
        """Scale PIL image and set as pixmap on label, maintaining aspect ratio"""
        pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        qimage = ImageQt.ImageQt(pil_image)
        pixmap = QPixmap.fromImage(qimage)
        label.setPixmap(pixmap)
    
    def update_thumbnails_size(self):
        """Update all thumbnail sizes based on current scroll area width"""
        # Calculate available width for each column
        scrollbar_width = self.scroll_area.verticalScrollBar().width() if self.scroll_area.verticalScrollBar().isVisible() else 0
        available_width = self.scroll_area.width() - scrollbar_width - (self.columns + 1) * 10
        max_thumb_width = max(100, available_width // self.columns)
        
        # Update all image labels
        for key, (label, pil_image) in list(self.image_labels.items()):
            try:
                # Reload and correct orientation
                original_path = None
                for container in self.grid_widget.findChildren(QWidget):
                    if id(container) == key:
                        original_path = container.image_path
                        break
                
                if original_path:
                    pil_reloaded = Image.open(str(original_path))
                    pil_reloaded = self.correct_image_orientation(pil_reloaded)
                    self.scale_and_set_pixmap(label, pil_reloaded, max_thumb_width)
            except Exception:
                pass
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        # Debounce resize updates
        self.resize_timer.stop()
        self.resize_timer.start(250)