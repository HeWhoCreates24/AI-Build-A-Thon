"""
Quick Setup Script
==================
Automated setup for development environment.
"""

import os
import sys
from pathlib import Path


def create_venv():
    """Create virtual environment."""
    print("Creating virtual environment...")
    os.system(f"{sys.executable} -m venv venv")
    print("✓ Virtual environment created")


def install_dependencies():
    """Install Python dependencies."""
    print("\nInstalling dependencies...")
    
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"
    
    os.system(f"{pip_path} install -r requirements.txt")
    print("✓ Dependencies installed")


def create_directories():
    """Ensure all data directories exist."""
    print("\nCreating data directories...")
    
    directories = [
        "crisis_detection/data/screenshots",
        "crisis_detection/data/webcam_captures",
        "crisis_detection/data/logs",
        "crisis_detection/data/logs/alerts",
        "crisis_detection/data/evidence",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Directories created")


def check_tesseract():
    """Check if Tesseract OCR is installed."""
    print("\nChecking for Tesseract OCR...")
    
    result = os.system("tesseract --version > /dev/null 2>&1")
    
    if result == 0:
        print("✓ Tesseract OCR found")
    else:
        print("⚠ Tesseract OCR not found!")
        print("\nPlease install Tesseract:")
        print("  Linux:   sudo apt install tesseract-ocr")
        print("  macOS:   brew install tesseract")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")


def main():
    """Run setup."""
    print("="*60)
    print("Crisis Detection System - Setup")
    print("="*60)
    
    create_venv()
    install_dependencies()
    create_directories()
    check_tesseract()
    
    print("\n" + "="*60)
    print("Setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Activate virtual environment:")
    if sys.platform == "win32":
        print("     venv\\Scripts\\activate")
    else:
        print("     source venv/bin/activate")
    print("  2. Run the system:")
    print("     python crisis_detection/main.py")
    print("\n")


if __name__ == "__main__":
    main()
