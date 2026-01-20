"""
GuckMohl - PySide6 Multilingual Image Viewer
"""
import sys
import os
import json
from pathlib import Path
from PIL import Image, ImageQt
import piexif
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QMessageBox, QFileDialog, QSizePolicy, 
                               QInputDialog, QDialog, QFormLayout, QComboBox, QDialogButtonBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPixmap, QIcon


class SettingsDialog(QDialog):
    """Settings dialog for configuring archive folder and language"""
    def __init__(self, parent, current_archive_folder, current_language, available_languages, translations):
        super().__init__(parent)
        self.translations = translations
        self.setWindowTitle(self.translations.get("settings_title", "Settings"))
        self.setMinimumWidth(400)
        
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
        
        # Language selection dropdown
        self.language_combo = QComboBox()
        for lang_code, lang_name in available_languages.items():
            self.language_combo.addItem(lang_name, lang_code)
        
        # Set current language as selected
        index = self.language_combo.findData(current_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        layout.addRow(self.translations.get("settings_archive_folder", "Archive folder name:"), archive_layout)
        layout.addRow(self.translations.get("settings_language", "Language:"), self.language_combo)
        
        # OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        self.archive_label = archive_label
    
    def change_archive_folder(self, label):
        text, ok = QInputDialog.getText(
            self,
            self.translations.get("settings_title", "Settings"),
            self.translations.get("settings_archive_folder", "Archive folder name:"),
            text=self.archive_folder
        )
        
        if ok and text.strip():
            # Validate folder name (check for invalid characters)
            invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            if any(char in text for char in invalid_chars):
                QMessageBox.warning(
                    self,
                    self.translations.get("settings_invalid_name", "Invalid Name"),
                    self.translations.get("settings_invalid_chars", "Invalid characters").format(
                        chars=' '.join(invalid_chars)
                    )
                )
                return
            
            self.archive_folder = text.strip()
            label.setText(self.archive_folder)
    
    def get_settings(self):
        return {
            'archive_folder': self.archive_folder,
            'language': self.language_combo.currentData()
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Image list and current index for navigation
        self.image_files = []
        self.current_index = 0
        self.current_folder = None
        self.current_pixmap = None  # Store original pixmap for better scaling
        
        # Application settings
        self.archive_folder_name = "archiv"  # Default archive folder name  # Default archive folder name
        self.current_language = "en"  # Default language is English
        self.translations = {}  # Translation dictionary loaded from JSON
        self.available_languages = {  # Available language options
            "en": "English",
            "de": "Deutsch",
            "fr": "Français",
            "es": "Español",
            "zh_CN": "简体中文"
        }
        self.load_language(self.current_language)
        
        # Supported image file formats
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
        # Initialize the user interface
        self.init_ui()
    
    def load_language(self, lang_code):
        """Load the translation file for the specified language"""
        lang_file = Path(__file__).parent / "lang" / f"{lang_code}.json"
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            self.current_language = lang_code
        except Exception as e:
            print(f"Error loading language file {lang_file}: {e}")
            # Fallback to English if loading fails
            if lang_code != "en":
                self.load_language("en")
    
    def tr(self, key, **kwargs):
        """Translate a key and format with kwargs placeholders"""
        text = self.translations.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text
    
    def init_ui(self):
        """Initialize all UI components and layout"""
        self.setWindowTitle(self.tr("app_title"))
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height
        
        # Create menu bar
        self.create_menu_bar()
        
        # Central widget to hold all UI elements
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main vertical layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Main image display label
        self.image_label = QLabel("")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setScaledContents(False)  # Manual scaling for better quality
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Allow label to grow  # Allow label to grow
        
        # Open folder button (shown on welcome screen)
        self.open_folder_button = QPushButton()
        self.open_folder_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DirOpenIcon))
        self.open_folder_button.setText(self.tr("open_folder_button"))
        self.open_folder_button.clicked.connect(self.open_folder)
        self.open_folder_button.setMinimumSize(200, 50)
        self.open_folder_button.setMaximumSize(300, 60)
        self.open_folder_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Prevent focus to allow arrow key navigation
        
        # Container for centered welcome button
        button_container = QWidget()
        button_container_layout = QVBoxLayout()
        button_container_layout.addStretch()
        self.welcome_label = QLabel(self.tr("welcome_message"))
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_container_layout.addWidget(self.welcome_label)
        button_container_layout.addWidget(self.open_folder_button, alignment=Qt.AlignmentFlag.AlignCenter)
        button_container_layout.addStretch()
        button_container.setLayout(button_container_layout)
        self.button_container = button_container
        
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Navigation and action button bar
        button_layout = QHBoxLayout()
        
        # Previous image button
        self.prev_button = QPushButton()
        self.prev_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ArrowLeft))
        self.prev_button.setText(self.tr("button_back"))
        self.prev_button.setToolTip(self.tr("tooltip_previous"))
        self.prev_button.clicked.connect(self.previous_image)
        self.prev_button.setEnabled(False)  # Disabled until images are loaded
        self.prev_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Prevent focus for keyboard navigation  # Prevent focus for keyboard navigation
        
        # Next image button
        self.next_button = QPushButton()
        self.next_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ArrowRight))
        self.next_button.setText(self.tr("button_forward"))
        self.next_button.setToolTip(self.tr("tooltip_next"))
        self.next_button.clicked.connect(self.next_image)
        self.next_button.setEnabled(False)
        self.next_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Prevent focus for keyboard navigation
        
        # Archive button
        self.archive_button = QPushButton()
        self.archive_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton))
        self.archive_button.setText(self.tr("button_archive"))
        self.archive_button.setToolTip(self.tr("tooltip_archive"))
        self.archive_button.clicked.connect(self.archive_image)
        self.archive_button.setEnabled(False)
        self.archive_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Prevent focus for keyboard navigation
        
        # Delete button
        self.delete_button = QPushButton()
        self.delete_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_TrashIcon))
        self.delete_button.setText(self.tr("button_delete"))
        self.delete_button.setToolTip(self.tr("tooltip_delete"))
        self.delete_button.clicked.connect(self.delete_image)
        self.delete_button.setEnabled(False)
        self.delete_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Prevent focus for keyboard navigation
        
        # Add buttons to button bar layout
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        button_layout.addStretch()  # Spacer to push archive/delete buttons to the right
        button_layout.addWidget(self.archive_button)
        button_layout.addWidget(self.delete_button)
        
        # Add all widgets to main layout
        layout.addWidget(self.image_label)
        layout.addWidget(self.button_container)
        layout.addWidget(self.info_label)
        layout.addLayout(button_layout)
    
    def create_menu_bar(self):
        """Create the application menu bar with File, Edit, and Help menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(self.tr("menu_file"))
      
        open_action = QAction(self.tr("menu_open"), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(self.tr("menu_exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu(self.tr("menu_edit"))
        
        settings_action = QAction(self.tr("menu_settings"), self)
        settings_action.setShortcut("Ctrl+E")
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # Help Menu
        help_menu = menubar.addMenu(self.tr("menu_help"))
        
        about_action = QAction(self.tr("menu_about"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def open_folder(self):
        # Show folder selection dialog to user
        folder_path = QFileDialog.getExistingDirectory(
            self,
            self.tr("dialog_select_folder"),
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path:
            self.current_folder = folder_path
            self.load_images_from_folder(folder_path)
    
    def load_images_from_folder(self, folder_path):
        self.image_files = []
        folder = Path(folder_path)
        
        # Scan directory for supported image files
        for file in folder.iterdir():
            if file.is_file() and file.suffix.lower() in self.image_extensions:
                self.image_files.append(file)
        
        # Sort files alphabetically for consistent navigation
        self.image_files.sort()
        
        if self.image_files:
            self.current_index = 0
            self.button_container.setVisible(False)
            self.image_label.setVisible(True)
            self.display_current_image()
            self.update_button_states()
        else:
            self.button_container.setVisible(True)
            self.image_label.setVisible(False)
            self.info_label.setText(self.tr("info_no_images"))
            self.update_button_states()
    
    def display_current_image(self):
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        current_file = self.image_files[self.current_index]
        
        try:
            pil_image = Image.open(str(current_file))
            pil_image = self.correct_image_orientation(pil_image)
            self.current_pixmap = QPixmap.fromImage(ImageQt.ImageQt(pil_image))
            
            if self.current_pixmap.isNull():
                self.image_label.setText(self.tr("error_loading", filename=current_file.name, error="Invalid image"))
                return
            
            self.scale_and_display_image()
            self.setWindowTitle(f"{self.tr('app_title')} - {current_file.name}")
            
            rating = self.get_image_rating(current_file)
            rating_stars = "★" * rating + "☆" * (5 - rating) if rating > 0 else ""
            rating_text = f" {rating_stars}" if rating_stars else ""
            
            self.info_label.setText(self.tr("info_images_format",
                current=self.current_index + 1,
                total=len(self.image_files),
                filename=current_file.name,
                rating=rating_text
            ))
        except Exception as e:
            self.image_label.setText(self.tr("error_loading", filename=current_file.name, error=str(e)))
    
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
    
    def get_image_rating(self, image_path):
        """Read rating (0-5) from EXIF tag 18246 (Windows Rating Tag)"""
        try:
            exif_dict = piexif.load(str(image_path))
            # Tag 18246 stores the Windows rating value
            if "0th" in exif_dict and 18246 in exif_dict["0th"]:
                rating = exif_dict["0th"][18246]
                return min(max(rating, 0), 5)  # Clamp to 0-5 range
        except Exception:
            pass
        return 0
    
    def set_image_rating(self, image_path, rating):
        """Write rating (0-5) to EXIF tag 18246 (Windows Rating Tag)"""
        try:
            rating = min(max(rating, 0), 5)  # Clamp to valid range
            
            # Load existing EXIF data or create new structure
            try:
                exif_dict = piexif.load(str(image_path))
            except Exception:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}
            
            # Store rating in Windows Rating Tag
            exif_dict["0th"][18246] = rating
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, str(image_path))
            
            return True
        except Exception as e:
            QMessageBox.warning(self, self.tr("rating_error"), 
                              self.tr("rating_error_message", error=str(e)))
            return False
    
    def rate_current_image(self, rating):
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        current_file = self.image_files[self.current_index]
        
        if self.set_image_rating(current_file, rating):
            rating_stars = "★" * rating + "☆" * (5 - rating) if rating > 0 else ""
            rating_text = f" {rating_stars}" if rating_stars else ""
            self.info_label.setText(self.tr("info_images_format",
                current=self.current_index + 1,
                total=len(self.image_files),
                filename=current_file.name,
                rating=rating_text
            ))
    
    def scale_and_display_image(self):
        if self.current_pixmap and not self.current_pixmap.isNull():
            scaled_pixmap = self.current_pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
    
    def next_image(self):
        if self.image_files and self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.display_current_image()
            self.update_button_states()
    
    def previous_image(self):
        if self.image_files and self.current_index > 0:
            self.current_index -= 1
            self.display_current_image()
            self.update_button_states()
    
    def update_button_states(self):
        has_images = len(self.image_files) > 0
        
        self.prev_button.setEnabled(has_images and self.current_index > 0)
        self.next_button.setEnabled(has_images and self.current_index < len(self.image_files) - 1)
        
        self.archive_button.setEnabled(has_images)
        self.delete_button.setEnabled(has_images)
    
    def archive_image(self):
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        current_file = self.image_files[self.current_index]
        archive_folder = current_file.parent / self.archive_folder_name
        archive_folder.mkdir(exist_ok=True)
        
        archive_path = archive_folder / current_file.name
        
        # Handle filename collisions by appending counter
        counter = 1
        while archive_path.exists():
            stem = current_file.stem
            suffix = current_file.suffix
            archive_path = archive_folder / f"{stem}_{counter}{suffix}"
            counter += 1
        
        try:
            current_file.rename(archive_path)
            QMessageBox.information(self, self.tr("archive_success"), 
                                  self.tr("archive_message", filename=current_file.name))
            
            # Remove archived file from image list
            self.image_files.pop(self.current_index)
            
            # Update display with next image or show welcome screen
            if self.image_files:
                if self.current_index >= len(self.image_files):
                    self.current_index = len(self.image_files) - 1
                self.display_current_image()
            else:
                # No more images - show welcome screen
                self.button_container.setVisible(True)
                self.image_label.setVisible(False)
                self.info_label.setText(self.tr("info_no_more_images"))
                self.current_pixmap = None
            
            self.update_button_states()
            
        except Exception as e:
            QMessageBox.critical(self, self.tr("archive_error"), 
                               self.tr("archive_error_message", error=str(e)))
    
    def delete_image(self):
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        current_file = self.image_files[self.current_index]
        
        # Show confirmation dialog before permanent deletion
        reply = QMessageBox.question(
            self, 
            self.tr("delete_confirm_title"), 
            self.tr("delete_confirm_message", filename=current_file.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                current_file.unlink()
                QMessageBox.information(self, self.tr("delete_success"), 
                                      self.tr("delete_success_message", filename=current_file.name))
                
                self.image_files.pop(self.current_index)
                
                if self.image_files:
                    if self.current_index >= len(self.image_files):
                        self.current_index = len(self.image_files) - 1
                    self.display_current_image()
                else:
                    self.button_container.setVisible(True)
                    self.image_label.setVisible(False)
                    self.info_label.setText(self.tr("info_no_more_images"))
                    self.current_pixmap = None
                
                self.update_button_states()
                
            except Exception as e:
                QMessageBox.critical(self, self.tr("delete_error"), 
                                   self.tr("delete_error_message", error=str(e)))
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scale_and_display_image()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for navigation and rating"""
        # Arrow keys for navigation: Right/Down = next, Left = previous, Up = archive
        if event.key() == Qt.Key.Key_Right or event.key() == Qt.Key.Key_Down:
            self.next_image()
        elif event.key() == Qt.Key.Key_Left:
            self.previous_image()
        elif event.key() == Qt.Key.Key_Up:
            self.archive_image()
        # Number keys (0-5) for rating
        elif event.key() == Qt.Key.Key_0:
            self.rate_current_image(0)
        elif event.key() == Qt.Key.Key_1:
            self.rate_current_image(1)
        elif event.key() == Qt.Key.Key_2:
            self.rate_current_image(2)
        elif event.key() == Qt.Key.Key_3:
            self.rate_current_image(3)
        elif event.key() == Qt.Key.Key_4:
            self.rate_current_image(4)
        elif event.key() == Qt.Key.Key_5:
            self.rate_current_image(5)
        else:
            super().keyPressEvent(event)
    
    def show_settings(self):
        dialog = SettingsDialog(
            self,
            self.archive_folder_name,
            self.current_language,
            self.available_languages,
            self.translations
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            
            # Update archive folder name if changed
            if settings['archive_folder'] != self.archive_folder_name:
                self.archive_folder_name = settings['archive_folder']
            
            # Update language if changed
            if settings['language'] != self.current_language:
                self.available_languages.get(settings['language'], settings['language'])
                # Load new language and refresh UI
                self.load_language(settings['language'])
                self.refresh_ui()
    
    def refresh_ui(self):
        """Update all UI texts with the new language"""
        self.setWindowTitle(self.tr("app_title"))
        self.welcome_label.setText(self.tr("welcome_message"))
        self.open_folder_button.setText(self.tr("open_folder_button"))
        
        self.prev_button.setText(self.tr("button_back"))
        self.prev_button.setToolTip(self.tr("tooltip_previous"))
        
        self.next_button.setText(self.tr("button_forward"))
        self.next_button.setToolTip(self.tr("tooltip_next"))
        
        self.archive_button.setText(self.tr("button_archive"))
        self.archive_button.setToolTip(self.tr("tooltip_archive"))
        
        self.delete_button.setText(self.tr("button_delete"))
        self.delete_button.setToolTip(self.tr("tooltip_delete"))
        
        # Recreate menu bar with new language
        self.menuBar().clear()
        self.create_menu_bar()
        
        # Update current image info display
        if self.image_files:
            self.display_current_image()
    
    def show_about(self):
        QMessageBox.about(self, self.tr("about_title"), self.tr("about_message"))


def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
