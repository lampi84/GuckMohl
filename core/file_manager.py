"""File management operations for GuckMohl"""
from pathlib import Path
from PySide6.QtWidgets import QMessageBox


class FileManager:
    """Handles file operations like archiving and deletion"""
    
    def __init__(self, translator=None):
        self.translator = translator
    
    def set_translator(self, translator):
        """Set translator for messages"""
        self.translator = translator
    
    def archive_image(self, image_path, archive_folder_name, parent_widget=None, archive_related_files=False):
        """Archive image to a subfolder"""
        try:
            image_path = Path(image_path)
            archive_folder = image_path.parent / archive_folder_name
            archive_folder.mkdir(exist_ok=True)
            
            archive_path = archive_folder / image_path.name
            
            # Handle filename collisions by appending counter
            counter = 1
            while archive_path.exists():
                stem = image_path.stem
                suffix = image_path.suffix
                archive_path = archive_folder / f"{stem}_{counter}{suffix}"
                counter += 1
            
            image_path.rename(archive_path)
            
            # Archive related files with same stem but different extension
            if archive_related_files:
                self._archive_related_files(image_path, archive_folder)
            
            if parent_widget and self.translator:
                QMessageBox.information(
                    parent_widget,
                    self.translator.translate("archive_success"),
                    self.translator.translate("archive_message", filename=image_path.name)
                )
            
            return True
        except Exception as e:
            if parent_widget and self.translator:
                QMessageBox.critical(
                    parent_widget,
                    self.translator.translate("archive_error"),
                    self.translator.translate("archive_error_message", error=str(e))
                )
            return False
    
    def _archive_related_files(self, original_image_path, archive_folder):
        """Archive files with same stem but different extension"""
        original_image_path = Path(original_image_path)
        parent_dir = original_image_path.parent
        stem = original_image_path.stem
        
        # Find all files in the same directory with the same stem
        for file in parent_dir.iterdir():
            if file.is_file() and file.stem == stem and file.suffix.lower() != original_image_path.suffix.lower():
                related_archive_path = archive_folder / file.name
                
                # Handle filename collisions for related files too
                counter = 1
                while related_archive_path.exists():
                    related_archive_path = archive_folder / f"{file.stem}_{counter}{file.suffix}"
                    counter += 1
                
                try:
                    file.rename(related_archive_path)
                except Exception as e:
                    # Continue with other related files if one fails
                    if self.translator:
                        print(f"Warning: Could not archive related file {file.name}: {e}")
    
    def delete_image(self, image_path, parent_widget=None, translator=None, delete_related_files=False):
        """Delete image with confirmation dialog"""
        try:
            image_path = Path(image_path)
            
            # Show confirmation dialog
            if parent_widget and self.translator:
                reply = QMessageBox.question(
                    parent_widget,
                    self.translator.translate("delete_confirm_title"),
                    self.translator.translate("delete_confirm_message", filename=image_path.name),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply != QMessageBox.StandardButton.Yes:
                    return False
            
            # Delete the file
            image_path.unlink()
            
            # Delete related files with same stem but different extension
            if delete_related_files:
                self._delete_related_files(image_path)
            
            if parent_widget and self.translator:
                QMessageBox.information(
                    parent_widget,
                    self.translator.translate("delete_success"),
                    self.translator.translate("delete_success_message", filename=image_path.name)
                )
            
            return True
        except Exception as e:
            if parent_widget and self.translator:
                QMessageBox.critical(
                    parent_widget,
                    self.translator.translate("delete_error"),
                    self.translator.translate("delete_error_message", error=str(e))
                )
            return False
    
    def _delete_related_files(self, original_image_path):
        """Delete files with same stem but different extension"""
        original_image_path = Path(original_image_path)
        parent_dir = original_image_path.parent
        stem = original_image_path.stem
        
        # Find all files in the same directory with the same stem
        for file in parent_dir.iterdir():
            if file.is_file() and file.stem == stem and file.suffix.lower() != original_image_path.suffix.lower():
                try:
                    file.unlink()
                except Exception as e:
                    # Continue with other related files if one fails
                    if self.translator:
                        print(f"Warning: Could not delete related file {file.name}: {e}")
