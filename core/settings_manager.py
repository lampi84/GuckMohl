"""Settings management for GuckMohl application"""
import json
from pathlib import Path


class SettingsManager:
    """Handles loading and saving application settings to a JSON file"""
    
    DEFAULT_SETTINGS = {
        'archive_folder': 'archiv',
        'language': 'en',
        'archive_related_files': False,
        'delete_related_files': False
    }
    
    def __init__(self):
        """Initialize settings manager and load settings from file"""
        self.settings_dir = Path.home() / '.guckmohl'
        self.settings_file = self.settings_dir / 'settings.json'
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file, create default if doesn't exist"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle missing keys
                    self.settings = {**self.DEFAULT_SETTINGS, **loaded}
            else:
                # Create settings directory and file with defaults
                self.settings_dir.mkdir(parents=True, exist_ok=True)
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            self.settings_dir.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key, default=None):
        """Get a setting value by key"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value and save to file"""
        self.settings[key] = value
        self.save_settings()
    
    def update(self, settings_dict):
        """Update multiple settings at once and save to file"""
        self.settings.update(settings_dict)
        self.save_settings()
    
    def get_all(self):
        """Get all settings as a dictionary"""
        return self.settings.copy()
