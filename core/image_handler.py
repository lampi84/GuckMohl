"""Image handling and display functionality for GuckMohl"""
from pathlib import Path
from PIL import Image, ImageQt
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class ImageHandler:
    """Handles image loading, display, and manipulation"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    def __init__(self):
        self.image_files = []
        self.current_index = 0
        self.current_pixmap = None
        self.marked_images = set()  # Store marked image paths
    
    def load_images_from_folder(self, folder_path):
        """Load all supported image files from a folder"""
        self.image_files = []
        folder = Path(folder_path)
        
        # Scan directory for supported image files
        for file in folder.iterdir():
            if file.is_file() and file.suffix.lower() in self.SUPPORTED_FORMATS:
                self.image_files.append(file)
        
        # Sort files alphabetically for consistent navigation
        self.image_files.sort()
        
        if self.image_files:
            self.current_index = 0
        
        return self.image_files
    
    def get_current_image_path(self):
        """Return path to current image or None"""
        if not self.image_files or self.current_index >= len(self.image_files):
            return None
        return self.image_files[self.current_index]
    
    def open_image(self, image_path):
        """Load and prepare image for display"""
        try:
            pil_image = Image.open(str(image_path))
            pil_image = self.correct_image_orientation(pil_image)
            self.current_pixmap = QPixmap.fromImage(ImageQt.ImageQt(pil_image))
            return self.current_pixmap
        except Exception as e:
            raise Exception(f"Error loading image: {str(e)}")
    
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
    
    def scale_pixmap_for_display(self, widget_size):
        """Scale current pixmap to fit widget while maintaining aspect ratio"""
        if self.current_pixmap and not self.current_pixmap.isNull():
            scaled_pixmap = self.current_pixmap.scaled(
                widget_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            return scaled_pixmap
        return None
    
    def next_image(self):
        """Move to next image"""
        if self.image_files and self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            return True
        return False
    
    def previous_image(self):
        """Move to previous image"""
        if self.image_files and self.current_index > 0:
            self.current_index -= 1
            return True
        return False
    
    def get_image_count(self):
        """Return total number of images"""
        return len(self.image_files)
    
    def get_current_index(self):
        """Return current image index"""
        return self.current_index
    
    def can_go_next(self):
        """Check if there's a next image available"""
        return self.image_files and self.current_index < len(self.image_files) - 1
    
    def can_go_previous(self):
        """Check if there's a previous image available"""
        return self.image_files and self.current_index > 0
    
    def has_images(self):
        """Check if any images are loaded"""
        return len(self.image_files) > 0
    
    def remove_current_image(self):
        """Remove current image from list"""
        if self.image_files and self.current_index < len(self.image_files):
            removed_image = self.image_files.pop(self.current_index)
            # Remove from marked images if it was marked
            self.marked_images.discard(removed_image)
            
            # Adjust index if necessary
            if self.current_index >= len(self.image_files) and self.image_files:
                self.current_index = len(self.image_files) - 1
            
            return True
        return False
    
    def toggle_mark_current_image(self):
        """Toggle mark status for current image"""
        image_path = self.get_current_image_path()
        if image_path:
            if image_path in self.marked_images:
                self.marked_images.remove(image_path)
                return False
            else:
                self.marked_images.add(image_path)
                return True
        return None
    
    def is_current_image_marked(self):
        """Check if current image is marked"""
        image_path = self.get_current_image_path()
        return image_path in self.marked_images if image_path else False
    
    def get_marked_images(self):
        """Return list of marked image paths"""
        return sorted(list(self.marked_images))
    
    def clear_marked_images(self):
        """Clear all marked images"""
        self.marked_images.clear()
    
    def get_marked_image_count(self):
        """Return number of marked images"""
        return len(self.marked_images)
