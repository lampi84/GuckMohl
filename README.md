# GuckMohl

A fast, multilingual image viewer and manager built with PySide6 (Qt for Python). Organize, rate, and archive your image collections with ease.

GuckMohl is a practical image sorting application that helps you efficiently organize photos from vacations, trips, and events. Load a folder of images and quickly sort them by rating (1-5 stars), archiving to subfolders, or deleting unwanted photos.

## Features

### Image Viewing
- **Automatic orientation correction** based on EXIF data
- **Responsive image scaling** that maintains aspect ratio
- **Support for multiple formats**: JPG, JPEG, PNG, GIF, BMP, TIFF, WebP
- **Keyboard navigation** through images using arrow keys

### Image Management
- **Star rating system** (0-5 stars) with EXIF metadata storage
- **Archive functionality** to organize images into subfolders
- **Delete images** with confirmation dialog
- **Automatic image list updates** after archiving or deleting

### Multilingual Support
- **5 languages available**: English, German (Deutsch), French (Français), Spanish (Español), and Simplified Chinese (简体中文)
- **Dynamic language switching** without restart
- **All UI elements translated** including menus, buttons, dialogs, and messages

### User Interface
- **Clean, intuitive design** with centered welcome screen
- **Navigation buttons** with icons for easy browsing
- **Keyboard shortcuts** for all major functions
- **Customizable archive folder name** via settings
- **File-related actions** options to archive/delete associated sidecar files (e.g., .xmp, .dng) alongside images
- **Image information bar** showing file name, current position, and star rating

## Installation

### From Source (For Developers)

1. Clone the repository:
```bash
git clone https://github.com/your-repo/GuckMohl.git
cd GuckMohl
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python main.py
```

### Standalone Executable (For Users)

Download the latest `GuckMohl.exe` from the [Releases](https://github.com/your-repo/GuckMohl/releases) page. No Python installation needed!

## Keyboard Shortcuts

### Navigation
- **Left Arrow** - Previous image
- **Right Arrow / Down Arrow** - Next image
- **Up Arrow** - Archive current image

### Rating
- **0-5 (Number keys)** -        # Main application entry point
├── build.py                     # PyInstaller build script
├── requirements.txt             # Python dependencies (pip)
├── requirements-build.txt       # Build dependencies (PyInstaller, etc.)
├── README.md                    # This file
├── BUILD.md                     # Build instructions (German)
├── icon.ico                     # Application icon
├── .gitignore                   # Git ignore patterns
├── core/                        # Core application logic
│   ├── __init__.py
│   ├── image_handler.py         # Image loading and display
│   ├── exif_handler.py          # EXIF metadata (ratings)
│   ├── file_manager.py          # File operations (archive, delete)
│   ├── settings_manager.py      # Settings persistence
│   └── translator.py            # Multilingual support
├── ui/                          # User interface components
│   ├── __init__.py
│   └── dialogs.py               # Settings dialog and other dialogs
└── lang/                        # Language translations
    ├── en.json                  # English
    ├── de.json                  # German
    ├── fr.json                  # French
    ├── es.json                  # Spanish
    └── zh_CN.json               # Simplified Chinese
GuckMohl/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore patterns
└── lang/               # Language files
    ├── en.json         # English translations
    ├── de.json         # German translations
    ├── fr.json         # French translations
    ├── es.json         # Spanish translations
    └── zh_CN.json      # Simplified Chinese translations
```

## Settings

Access settings via **Edit → Settings** (Ctrl+E):

- **Archive Folder Name**: Customize the name of the folder where archived images are stored (default: "archiv")
- **Language**: Choose your preferred interface language (English, German, French, Spanish, Simplified Chinese)
- **Archive Related Files**: Optionally archive associated sidecar files (e.g., .xmp, .dng, .raw) when archiving an image
- **Delete Related Files**: Optionally delete associated sidecar files when deleting an image

Settings are stored in a JSON file at `~/.guckmohl/settings.json` and persist between sessions.

## Image Rating System

The application stores ratings directly in image files using EXIF metadata (Windows Rating Tag 18246). Ratings are:
- Compatible with Windows Explorer and other EXIF-aware applications
- Permanently stored with the image file
- Displayed as stars (★) in the image information bar
- Can be set to 0-5 stars using keyboard shortcuts (number keys 0-5)

## Technical Details

### Architecture
The application is organized using a modular architecture:
- **Core modules** handle business logic (image handling, EXIF metadata, file operations, settings)
- **UI layer** (PySide6) handles the graphical interface
- **Translator** provides dynamic language switching

### Dependencies
- **PySide6** (>=6.6.0) - Qt for Python, native cross-platform GUI framework
- **Pillow** (>=10.0.0) - Image processing library with EXIF support
- **piexif** (>=1.1.3) - EXIF metadata manipulation library

### Build
- **PyInstaller** - Bundles the application into a standalone .exe for Windows
- Complete build setup in `build.py` and build instructions in `BUILD.md`

### Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- WebP (.webp)

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is provided as-is for educational and personal use.

