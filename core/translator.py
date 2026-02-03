"""Translation and localization management for GuckMohl"""
import json
from pathlib import Path


class Translator:
    """Manages translation and language selection"""
    
    def __init__(self, default_language="en"):
        self.current_language = default_language
        self.translations = {}
        self.available_languages = {
            "en": "English",
            "de": "Deutsch",
            "fr": "Français",
            "es": "Español",
            "zh_CN": "简体中文"
        }
        self.load_language(default_language)
    
    def load_language(self, lang_code):
        """Load the translation file for the specified language"""
        lang_file = Path(__file__).parent.parent / "lang" / f"{lang_code}.json"
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            self.current_language = lang_code
        except Exception as e:
            print(f"Error loading language file {lang_file}: {e}")
            # Fallback to English if loading fails
            if lang_code != "en":
                self.load_language("en")
    
    def translate(self, key, **kwargs):
        """Translate a key and format with kwargs placeholders"""
        text = self.translations.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text
    
    def get_available_languages(self):
        """Return dictionary of available languages"""
        return self.available_languages.copy()
    
    def get_current_language(self):
        """Return current language code"""
        return self.current_language
