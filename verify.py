#!/usr/bin/env python3
"""
System Verification Script
==========================
Checks all dependencies and components.
"""

import sys
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ❌ Python 3.8+ required")
        return False
    else:
        print("  ✅ Python version OK")
        return True


def check_dependencies():
    """Check if required packages are installed."""
    print("\nChecking dependencies...")
    
    dependencies = {
        'mss': 'Screenshot capture',
        'pytesseract': 'OCR',
        'PIL': 'Image processing (Pillow)',
        'cv2': 'Computer vision (opencv-python)',
        'yaml': 'Configuration (PyYAML)',
    }
    
    optional_dependencies = {
        'transformers': 'ML models (optional)',
        'torch': 'PyTorch (optional)',
    }
    
    all_ok = True
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            print(f"  ✅ {package:15s} - {description}")
        except ImportError:
            print(f"  ❌ {package:15s} - {description} (NOT INSTALLED)")
            all_ok = False
    
    print("\nOptional dependencies:")
    for package, description in optional_dependencies.items():
        try:
            __import__(package)
            print(f"  ✅ {package:15s} - {description}")
        except ImportError:
            print(f"  ⚠️  {package:15s} - {description} (will use fallback)")
    
    return all_ok


def check_tesseract():
    """Check if Tesseract OCR is installed."""
    print("\nChecking Tesseract OCR...")
    
    import subprocess
    try:
        result = subprocess.run(
            ['tesseract', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"  ✅ Tesseract found: {version_line}")
            return True
        else:
            print(f"  ❌ Tesseract not working properly")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print(f"  ❌ Tesseract not found")
        print("\n  Install instructions:")
        print("    Linux:   sudo apt install tesseract-ocr")
        print("    macOS:   brew install tesseract")
        print("    Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        return False


def check_directories():
    """Check if data directories exist."""
    print("\nChecking directories...")
    
    required_dirs = [
        'crisis_detection/data/screenshots',
        'crisis_detection/data/webcam_captures',
        'crisis_detection/data/logs',
        'crisis_detection/data/logs/alerts',
        'crisis_detection/data/evidence',
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ⚠️  {dir_path} (will be created)")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"     Created: {dir_path}")
            except Exception as e:
                print(f"     ❌ Failed to create: {e}")
                all_ok = False
    
    return all_ok


def check_config():
    """Check if configuration file exists."""
    print("\nChecking configuration...")
    
    config_path = Path('crisis_detection/config/config.yaml')
    
    if config_path.exists():
        print(f"  ✅ Configuration file found")
        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
            print(f"     Config sections: {', '.join(config.keys())}")
            return True
        except Exception as e:
            print(f"  ❌ Configuration file invalid: {e}")
            return False
    else:
        print(f"  ❌ Configuration file not found: {config_path}")
        return False


def check_modules():
    """Check if all Python modules can be imported."""
    print("\nChecking system modules...")
    
    modules = [
        'crisis_detection.core.screenshot_service',
        'crisis_detection.core.ocr_pipeline',
        'crisis_detection.core.nlp_model',
        'crisis_detection.core.risk_engine',
        'crisis_detection.core.webcam_capture',
        'crisis_detection.alerts.alert_manager',
        'crisis_detection.utils.config_loader',
        'crisis_detection.utils.logger',
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            module_name = module.split('.')[-1]
            print(f"  ✅ {module_name}")
        except Exception as e:
            print(f"  ❌ {module.split('.')[-1]}: {e}")
            all_ok = False
    
    return all_ok


def main():
    """Run all verification checks."""
    print("="*70)
    print(" " * 15 + "SYSTEM VERIFICATION")
    print("="*70)
    
    checks = {
        'Python version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Tesseract OCR': check_tesseract(),
        'Directories': check_directories(),
        'Configuration': check_config(),
        'Modules': check_modules(),
    }
    
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:20s}: {status}")
    
    all_passed = all(checks.values())
    
    print("\n" + "="*70)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED - System ready!")
        print("\nNext steps:")
        print("  python crisis_detection/main.py          # Run full system")
        print("  python demo.py                           # Run demo")
        print("  python crisis_detection/core/demo_nlp.py # Test NLP only")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Please fix issues above")
        print("\nCommon fixes:")
        print("  pip install -r requirements.txt         # Install dependencies")
        print("  python setup.py                         # Run setup script")
        return 1


if __name__ == "__main__":
    sys.exit(main())
