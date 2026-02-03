"""EXIF metadata handling for image ratings"""
import piexif
from PySide6.QtWidgets import QMessageBox


class ExifHandler:
    """Handles EXIF metadata operations, particularly image ratings"""
    
    RATING_TAG = 18246  # Windows Rating Tag
    ORIENTATION_TAG = 274
    
    def __init__(self, translator=None):
        self.translator = translator
    
    def set_translator(self, translator):
        """Set translator for error messages"""
        self.translator = translator
    
    def get_image_rating(self, image_path):
        """Read rating (0-5) from EXIF tag 18246 (Windows Rating Tag)"""
        try:
            exif_dict = piexif.load(str(image_path))
            # Tag 18246 stores the Windows rating value
            if "0th" in exif_dict and self.RATING_TAG in exif_dict["0th"]:
                rating = exif_dict["0th"][self.RATING_TAG]
                return min(max(rating, 0), 5)  # Clamp to 0-5 range
        except Exception:
            pass
        return 0
    
    def set_image_rating(self, image_path, rating, parent_widget=None):
        """Write rating (0-5) to EXIF tag 18246 (Windows Rating Tag)"""
        try:
            rating = min(max(rating, 0), 5)  # Clamp to valid range
            
            # Load existing EXIF data or create new structure
            try:
                exif_dict = piexif.load(str(image_path))
            except Exception:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}
            
            # Store rating in Windows Rating Tag
            exif_dict["0th"][self.RATING_TAG] = rating
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, str(image_path))
            
            return True
        except Exception as e:
            if parent_widget and self.translator:
                QMessageBox.warning(
                    parent_widget,
                    self.translator.translate("rating_error"),
                    self.translator.translate("rating_error_message", error=str(e))
                )
            return False
    
    def format_rating_display(self, rating):
        """Format rating as stars (★☆)"""
        if rating <= 0:
            return ""
        return "★" * rating + "☆" * (5 - rating)
