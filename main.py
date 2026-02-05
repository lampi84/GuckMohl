"""
GuckMohl - PySide6 Multilingual Image Viewer
Refactored main module using separated core and UI components
"""
import sys
import json
from pathlib import Path
from core import __version__
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QMessageBox, QFileDialog, QSizePolicy, QDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPixmap

from core.translator import Translator
from core.image_handler import ImageHandler
from core.exif_handler import ExifHandler
from core.file_manager import FileManager
from core.settings_manager import SettingsManager
from ui.dialogs import SettingsDialog, CompareDialog


class MainWindow(QMainWindow):
    """Main application window for GuckMohl image viewer"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Initialize core components
        initial_language = self.settings_manager.get('language', 'en')
        self.translator = Translator(initial_language)
        self.image_handler = ImageHandler()
        self.exif_handler = ExifHandler(self.translator)
        self.file_manager = FileManager(self.translator)
        
        # Load application settings
        self.archive_folder_name = self.settings_manager.get('archive_folder', 'archiv')
        self.archive_related_files = self.settings_manager.get('archive_related_files', False)
        self.delete_related_files = self.settings_manager.get('delete_related_files', False)
        
        # UI references
        self.image_label = None
        self.info_label = None
        self.button_container = None
        self.welcome_label = None
        self.prev_button = None
        self.next_button = None
        self.archive_button = None
        self.delete_button = None
        self.mark_button = None
        self.compare_button = None
        self.open_folder_button = None
        
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
        self.setWindowTitle(self.translator.translate("app_title"))
        self.setGeometry(100, 100, 800, 600)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Image display label
        self.image_label = QLabel("")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setScaledContents(False)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Open folder button (welcome screen)
        self.open_folder_button = QPushButton()
        self.open_folder_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DirOpenIcon))
        self.open_folder_button.setText(self.translator.translate("open_folder_button"))
        self.open_folder_button.clicked.connect(self.open_folder)
        self.open_folder_button.setMinimumSize(200, 50)
        self.open_folder_button.setMaximumSize(300, 60)
        self.open_folder_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Welcome screen container
        button_container = QWidget()
        button_container_layout = QVBoxLayout()
        button_container_layout.addStretch()
        self.welcome_label = QLabel(self.translator.translate("welcome_message"))
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_container_layout.addWidget(self.welcome_label)
        button_container_layout.addWidget(self.open_folder_button, alignment=Qt.AlignmentFlag.AlignCenter)
        button_container_layout.addStretch()
        button_container.setLayout(button_container_layout)
        self.button_container = button_container
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Navigation and action buttons
        button_layout = QHBoxLayout()
        
        # Previous button
        self.prev_button = QPushButton()
        self.prev_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ArrowLeft))
        self.prev_button.setText(self.translator.translate("button_back"))
        self.prev_button.setToolTip(self.translator.translate("tooltip_previous"))
        self.prev_button.clicked.connect(self.previous_image)
        self.prev_button.setEnabled(False)
        self.prev_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Next button
        self.next_button = QPushButton()
        self.next_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ArrowRight))
        self.next_button.setText(self.translator.translate("button_forward"))
        self.next_button.setToolTip(self.translator.translate("tooltip_next"))
        self.next_button.clicked.connect(self.next_image)
        self.next_button.setEnabled(False)
        self.next_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Archive button
        self.archive_button = QPushButton()
        self.archive_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton))
        self.archive_button.setText(self.translator.translate("button_archive"))
        self.archive_button.setToolTip(self.translator.translate("tooltip_archive"))
        self.archive_button.clicked.connect(self.archive_current_image)
        self.archive_button.setEnabled(False)
        self.archive_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Delete button
        self.delete_button = QPushButton()
        self.delete_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_TrashIcon))
        self.delete_button.setText(self.translator.translate("button_delete"))
        self.delete_button.setToolTip(self.translator.translate("tooltip_delete"))
        self.delete_button.clicked.connect(self.delete_current_image)
        self.delete_button.setEnabled(False)
        self.delete_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Mark button
        self.mark_button = QPushButton()
        self.mark_button.setText(self.translator.translate("button_mark"))
        self.mark_button.setToolTip(self.translator.translate("tooltip_mark"))
        self.mark_button.clicked.connect(self.toggle_mark_image)
        self.mark_button.setEnabled(False)
        self.mark_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Compare button
        self.compare_button = QPushButton()
        self.compare_button.setText(self.translator.translate("button_compare"))
        self.compare_button.setToolTip(self.translator.translate("tooltip_compare"))
        self.compare_button.clicked.connect(self.show_compare_dialog)
        self.compare_button.setEnabled(False)
        self.compare_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Add buttons to layout
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        button_layout.addStretch()
        button_layout.addWidget(self.mark_button)
        button_layout.addWidget(self.compare_button)
        button_layout.addWidget(self.archive_button)
        button_layout.addWidget(self.delete_button)
        
        # Add widgets to main layout
        layout.addWidget(self.image_label)
        layout.addWidget(self.button_container)
        layout.addWidget(self.info_label)
        layout.addLayout(button_layout)
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(self.translator.translate("menu_file"))
        
        open_action = QAction(self.translator.translate("menu_open"), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(self.translator.translate("menu_exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Mark menu
        mark_menu = menubar.addMenu(self.translator.translate("menu_mark"))
        
        mark_action = QAction(self.translator.translate("button_mark"), self)
        mark_action.setShortcut("M")
        mark_action.triggered.connect(self.toggle_mark_image)
        mark_menu.addAction(mark_action)
        
        compare_action = QAction(self.translator.translate("button_compare"), self)
        compare_action.triggered.connect(self.show_compare_dialog)
        mark_menu.addAction(compare_action)
        
        mark_menu.addSeparator()
        
        archive_marked_action = QAction(self.translator.translate("button_archive_marked"), self)
        archive_marked_action.triggered.connect(self.archive_marked_images)
        mark_menu.addAction(archive_marked_action)
        
        delete_marked_action = QAction(self.translator.translate("button_delete_marked"), self)
        delete_marked_action.triggered.connect(self.delete_marked_images)
        mark_menu.addAction(delete_marked_action)
        
        # Edit menu
        edit_menu = menubar.addMenu(self.translator.translate("menu_edit"))
        
        settings_action = QAction(self.translator.translate("menu_settings"), self)
        settings_action.setShortcut("Ctrl+E")
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu(self.translator.translate("menu_help"))
        
        about_action = QAction(self.translator.translate("menu_about"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def open_folder(self):
        """Open folder selection dialog"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            self.translator.translate("dialog_select_folder"),
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path:
            self.load_folder(folder_path)
    
    def load_folder(self, folder_path):
        """Load images from specified folder"""
        self.image_handler.load_images_from_folder(folder_path)
        
        if self.image_handler.has_images():
            self.button_container.setVisible(False)
            self.image_label.setVisible(True)
            self.display_current_image()
            self.update_button_states()
        else:
            self.button_container.setVisible(True)
            self.image_label.setVisible(False)
            self.info_label.setText(self.translator.translate("info_no_images"))
            self.update_button_states()
    
    def display_current_image(self):
        """Display the current image"""
        image_path = self.image_handler.get_current_image_path()
        
        if not image_path:
            return
        
        try:
            self.image_handler.open_image(image_path)
            self.scale_and_display_image()
            self.setWindowTitle(f"{self.translator.translate('app_title')} - {image_path.name}")
            
            # Get and display rating
            rating = self.exif_handler.get_image_rating(image_path)
            rating_stars = self.exif_handler.format_rating_display(rating)
            rating_text = f" {rating_stars}" if rating_stars else ""
            
            self.info_label.setText(self.translator.translate("info_images_format",
                current=self.image_handler.get_current_index() + 1,
                total=self.image_handler.get_image_count(),
                filename=image_path.name,
                rating=rating_text
            ))
        except Exception as e:
            self.image_label.setText(self.translator.translate("error_loading",
                filename=image_path.name, error=str(e)))
    
    def scale_and_display_image(self):
        """Scale and display the current image"""
        scaled_pixmap = self.image_handler.scale_pixmap_for_display(self.image_label.size())
        if scaled_pixmap:
            self.image_label.setPixmap(scaled_pixmap)
    
    def next_image(self):
        """Display next image"""
        if self.image_handler.next_image():
            self.display_current_image()
            self.update_button_states()
    
    def previous_image(self):
        """Display previous image"""
        if self.image_handler.previous_image():
            self.display_current_image()
            self.update_button_states()
    
    def rate_current_image(self, rating):
        """Set rating for current image"""
        image_path = self.image_handler.get_current_image_path()
        if not image_path:
            return
        
        if self.exif_handler.set_image_rating(image_path, rating, self):
            rating_stars = self.exif_handler.format_rating_display(rating)
            rating_text = f" {rating_stars}" if rating_stars else ""
            
            self.info_label.setText(self.translator.translate("info_images_format",
                current=self.image_handler.get_current_index() + 1,
                total=self.image_handler.get_image_count(),
                filename=image_path.name,
                rating=rating_text
            ))
    
    def archive_current_image(self):
        """Archive current image"""
        image_path = self.image_handler.get_current_image_path()
        if not image_path:
            return
        
        if self.file_manager.archive_image(image_path, self.archive_folder_name, self, self.archive_related_files):
            self.image_handler.remove_current_image()
            
            if self.image_handler.has_images():
                self.display_current_image()
            else:
                self.button_container.setVisible(True)
                self.image_label.setVisible(False)
                self.info_label.setText(self.translator.translate("info_no_more_images"))
            
            self.update_button_states()
    
    def delete_current_image(self):
        """Delete current image"""
        image_path = self.image_handler.get_current_image_path()
        if not image_path:
            return
        
        if self.file_manager.delete_image(image_path, self, self.translator, self.delete_related_files):
            self.image_handler.remove_current_image()
            
            if self.image_handler.has_images():
                self.display_current_image()
            else:
                self.button_container.setVisible(True)
                self.image_label.setVisible(False)
                self.info_label.setText(self.translator.translate("info_no_more_images"))
            
            self.update_button_states()
    
    def toggle_mark_image(self):
        """Toggle mark status for current image"""
        image_path = self.image_handler.get_current_image_path()
        if not image_path:
            return
        
        self.image_handler.toggle_mark_current_image()
        self.update_button_states()
    
    def show_compare_dialog(self):
        """Show comparison dialog with all marked images"""
        marked_images = self.image_handler.get_marked_images()
        
        if not marked_images:
            QMessageBox.information(
                self,
                self.translator.translate("compare_title"),
                self.translator.translate("compare_empty")
            )
            return
        
        # Create and show comparison dialog
        compare_dialog = CompareDialog(self, marked_images, self.translator)
        compare_dialog.exec()
    
    def archive_marked_images(self):
        """Archive all marked images"""
        marked_images = self.image_handler.get_marked_images()
        
        if not marked_images:
            QMessageBox.information(
                self,
                self.translator.translate("compare_title"),
                self.translator.translate("compare_empty")
            )
            return
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            self.translator.translate("archive_success"),
            self.translator.translate("archive_marked_confirm"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        archived_count = 0
        for image_path in marked_images:
            try:
                if self.file_manager.archive_image(image_path, self.archive_folder_name, self, self.archive_related_files):
                    archived_count += 1
                    # Remove from displayed list if it's the current image
                    if self.image_handler.get_current_image_path() == image_path:
                        self.image_handler.remove_current_image()
            except Exception as e:
                print(f"Error archiving {image_path}: {e}")
        
        # Clear marked images
        self.image_handler.clear_marked_images()
        
        # Refresh display
        if self.image_handler.has_images():
            self.display_current_image()
        else:
            self.button_container.setVisible(True)
            self.image_label.setVisible(False)
            self.info_label.setText(self.translator.translate("info_no_more_images"))
        
        self.update_button_states()
        
        # Show success message
        QMessageBox.information(
            self,
            self.translator.translate("archive_success"),
            self.translator.translate("archive_marked_success", count=archived_count)
        )
    
    def delete_marked_images(self):
        """Delete all marked images"""
        marked_images = self.image_handler.get_marked_images()
        
        if not marked_images:
            QMessageBox.information(
                self,
                self.translator.translate("compare_title"),
                self.translator.translate("compare_empty")
            )
            return
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            self.translator.translate("delete_success"),
            self.translator.translate("delete_marked_confirm", count=len(marked_images)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        deleted_count = 0
        for image_path in marked_images:
            try:
                if self.file_manager.delete_image(image_path, self, self.translator, self.delete_related_files):
                    deleted_count += 1
                    # Remove from displayed list if it's the current image
                    if self.image_handler.get_current_image_path() == image_path:
                        self.image_handler.remove_current_image()
            except Exception as e:
                print(f"Error deleting {image_path}: {e}")
        
        # Clear marked images
        self.image_handler.clear_marked_images()
        
        # Refresh display
        if self.image_handler.has_images():
            self.display_current_image()
        else:
            self.button_container.setVisible(True)
            self.image_label.setVisible(False)
            self.info_label.setText(self.translator.translate("info_no_more_images"))
        
        self.update_button_states()
        
        # Show success message
        QMessageBox.information(
            self,
            self.translator.translate("delete_success"),
            self.translator.translate("delete_marked_success", count=deleted_count)
        )
    
    def update_button_states(self):
        """Update button enabled states based on image availability"""
        has_images = self.image_handler.has_images()
        has_marked = self.image_handler.get_marked_image_count() > 0
        
        self.prev_button.setEnabled(self.image_handler.can_go_previous())
        self.next_button.setEnabled(self.image_handler.can_go_next())
        self.archive_button.setEnabled(has_images)
        self.delete_button.setEnabled(has_images)
        self.mark_button.setEnabled(has_images)
        self.compare_button.setEnabled(has_marked)
        
        # Update mark button text based on current image state
        if has_images:
            if self.image_handler.is_current_image_marked():
                self.mark_button.setText(self.translator.translate("button_unmark"))
            else:
                self.mark_button.setText(self.translator.translate("button_mark"))
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        self.scale_and_display_image()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Right or event.key() == Qt.Key.Key_Down:
            self.next_image()
        elif event.key() == Qt.Key.Key_Left:
            self.previous_image()
        elif event.key() == Qt.Key.Key_Up:
            self.archive_current_image()
        elif event.key() == Qt.Key.Key_M:
            self.toggle_mark_image()
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
        """Show settings dialog"""
        dialog = SettingsDialog(
            self,
            self.archive_folder_name,
            self.translator.get_current_language(),
            self.translator.get_available_languages(),
            self.translator,
            self.archive_related_files,
            self.delete_related_files
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            
            # Save settings to file
            self.settings_manager.update(settings)
            
            # Update archive folder
            if settings['archive_folder'] != self.archive_folder_name:
                self.archive_folder_name = settings['archive_folder']
            
            # Update archive related files setting
            self.archive_related_files = settings['archive_related_files']
            
            # Update delete related files setting
            self.delete_related_files = settings['delete_related_files']
            
            # Update language
            if settings['language'] != self.translator.get_current_language():
                self.translator.load_language(settings['language'])
                self.exif_handler.set_translator(self.translator)
                self.file_manager.set_translator(self.translator)
                self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh all UI texts with current language"""
        self.setWindowTitle(self.translator.translate("app_title"))
        self.welcome_label.setText(self.translator.translate("welcome_message"))
        self.open_folder_button.setText(self.translator.translate("open_folder_button"))
        
        self.prev_button.setText(self.translator.translate("button_back"))
        self.prev_button.setToolTip(self.translator.translate("tooltip_previous"))
        
        self.next_button.setText(self.translator.translate("button_forward"))
        self.next_button.setToolTip(self.translator.translate("tooltip_next"))
        
        self.archive_button.setText(self.translator.translate("button_archive"))
        self.archive_button.setToolTip(self.translator.translate("tooltip_archive"))
        
        self.delete_button.setText(self.translator.translate("button_delete"))
        self.delete_button.setToolTip(self.translator.translate("tooltip_delete"))
        
        self.mark_button.setText(self.translator.translate("button_mark"))
        self.mark_button.setToolTip(self.translator.translate("tooltip_mark"))
        
        self.compare_button.setText(self.translator.translate("button_compare"))
        self.compare_button.setToolTip(self.translator.translate("tooltip_compare"))
        
        # Recreate menu bar
        self.menuBar().clear()
        self.create_menu_bar()
        
        # Update current image display
        if self.image_handler.has_images():
            self.display_current_image()
    
    def show_about(self):
        """Show about dialog"""
        about_text = self.translator.translate("about_message").replace("Version 1.0", f"Version {__version__}")
        QMessageBox.about(self, self.translator.translate("about_title"), about_text)


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
