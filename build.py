"""
Build script to create standalone executable with PyInstaller
Run: python build.py
"""
import subprocess
import sys
import os

def build_executable():
    """Build standalone executable using PyInstaller"""
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Create single .exe file
        "--windowed",                   # No console window
        "--icon=icon.ico",             # Icon (optional - create/add icon.ico if needed)
        "--add-data=lang:lang",        # Include translation files
        "--name=GuckMohl",             # Application name
        "main.py"
    ]
    
    print("Building executable...")
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    if result.returncode == 0:
        print("\n✓ Build successful!")
        print("Executable: dist/GuckMohl.exe")
    else:
        print("\n✗ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()
