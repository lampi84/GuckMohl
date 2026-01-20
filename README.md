# GuckMohl

A multilingual image viewer application built with PySide6 (Qt for Python). Browse, rate, archive, and manage your image collections with ease.
Image sorting app, which helps you to easily sort your images from vacation, trips or events. Start by having your photos from a hicking trip in one folder. You can either rate them from 1 to 5 stars, archive them (move presented image into a subfolder named archive) or simply delete them. I'm planning on some further features (so mor to come).

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

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Keyboard Shortcuts

### Navigation
- **Left Arrow** - Previous image
- **Right Arrow / Down Arrow** - Next image
- **Up Arrow** - Archive current image

### Rating
- **0-5 (Number keys)** - Rate current image (0 removes rating)

### Menu Shortcuts
- **Ctrl+O** - Open folder
- **Ctrl+E** - Settings
- **Ctrl+Q** - Quit application

## Project Structure

```
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
- **Language**: Choose your preferred interface language

## Image Rating System

The application stores ratings directly in image files using EXIF metadata (Windows Rating Tag 18246). Ratings are:
- Compatible with Windows Explorer and other EXIF-aware applications
- Permanently stored with the image file
- Displayed as stars (★) in the image information bar

## Technical Details

### Dependencies
- **PySide6** (>=6.6.0) - Qt bindings for Python
- **Pillow** (>=10.0.0) - Image processing library
- **piexif** (>=1.1.3) - EXIF metadata manipulation

### Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff)
- WebP (.webp)

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is provided as-is for educational and personal use.

