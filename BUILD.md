# GuckMohl - Build Instructions

## Für Entwickler (Erstellen einer .exe)

### Voraussetzungen
- Python 3.8+ installiert
- Repository geklont

### Schritt 1: Dependencies installieren
```bash
pip install -r requirements-build.txt
```

### Schritt 2: Executable bauen
```bash
python build.py
```

Die fertige `.exe` befindet sich dann in `dist/GuckMohl.exe`

### Alternative: Manueller Build mit PyInstaller
```bash
pyinstaller --onefile --windowed --add-data "lang:lang" --name GuckMohl main.py
```

## Für Nutzer (Programm ausführen)

1. **GuckMohl.exe** herunterladen
2. Doppelklick zum Ausführen
3. Fertig - **keine Python-Installation nötig!**

## Größe
Die .exe ist ca. 100-150 MB (enthält Python + alle Libraries)

## Verteilung
- GitHub Releases verwenden für Downloads
- Oder direkt als Attachment bereitstellen
