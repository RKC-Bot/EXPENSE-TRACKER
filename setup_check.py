#!/usr/bin/env python3
"""
Setup and Dependency Checker for AI Expense Tracker
Checks for required dependencies and installs missing ones
"""

import subprocess
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def check_and_install_packages():
    """Check and install required packages"""
    
    print("=" * 60)
    print("AI Expense Tracker - Setup & Dependency Checker")
    print("=" * 60)
    print()
    
    # Required packages
    required_packages = {
        'streamlit': 'streamlit==1.31.0',
        'pandas': 'pandas==2.1.4',
        'openpyxl': 'openpyxl==3.1.2',
        'pytesseract': 'pytesseract==0.3.10',
        'PIL': 'pillow==10.2.0',
        'easyocr': 'easyocr==1.7.1',
        'speech_recognition': 'SpeechRecognition==3.10.1',
        'plotly': 'plotly==5.18.0',
        'gspread': 'gspread==5.12.4',
        'google.auth': 'google-auth==2.27.0',
        'sklearn': 'scikit-learn==1.4.0',
    }
    
    missing_packages = []
    installed_packages = []
    
    # Check each package
    for package_import, package_install in required_packages.items():
        try:
            __import__(package_import)
            print(f"✓ {package_import:<20} - Already installed")
            installed_packages.append(package_import)
        except ImportError:
            print(f"✗ {package_import:<20} - Missing")
            missing_packages.append(package_install)
    
    print()
    print(f"Summary: {len(installed_packages)} installed, {len(missing_packages)} missing")
    print()
    
    # Install missing packages
    if missing_packages:
        print("Installing missing packages...")
        print("-" * 60)
        
        for package in missing_packages:
            print(f"\nInstalling {package}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    package, "--quiet", "--break-system-packages"
                ])
                print(f"✓ Successfully installed {package}")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {package}")
                print(f"  Try manually: pip install {package} --break-system-packages")
        
        print()
        print("-" * 60)
        print("Installation complete!")
    else:
        print("✓ All required packages are already installed!")
    
    print()
    
    # Check optional dependencies
    print("Checking optional dependencies...")
    print("-" * 60)
    
    optional_packages = {
        'torch': 'PyTorch (for EasyOCR)',
        'cv2': 'OpenCV (for image processing)',
        'PyAudio': 'PyAudio (for microphone input)',
    }
    
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"✓ {description:<40} - Available")
        except ImportError:
            print(f"⚠ {description:<40} - Not available (optional)")
    
    print()
    
    # Check Tesseract OCR installation
    print("Checking Tesseract OCR...")
    print("-" * 60)
    
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ Tesseract OCR is installed: {version}")
        else:
            print("✗ Tesseract OCR not properly configured")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ Tesseract OCR not found")
        print("  Install instructions:")
        print("  - Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  - MacOS: brew install tesseract")
        print("  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
    
    print()
    print("=" * 60)
    print("Setup check complete!")
    print("=" * 60)
    print()
    
    return len(missing_packages) == 0

def create_directory_structure():
    """Create necessary directories"""
    
    directories = [
        'data/invoices',
        'db',
        'modules'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created/verified directory: {directory}")

def run_tests():
    """Run basic tests to verify installation"""
    
    print("\nRunning basic tests...")
    print("-" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Database creation
    try:
        from modules.database import ExpenseDatabase
        db = ExpenseDatabase(':memory:')
        print("✓ Database module working")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Database module failed: {e}")
        tests_failed += 1
    
    # Test 2: Categorizer
    try:
        from modules.categorizer import AIExpenseCategorizer
        categorizer = AIExpenseCategorizer()
        category = categorizer.categorize("milk")
        assert category in ['Dairy', 'Groceries', 'Miscellaneous']
        print("✓ Categorizer module working")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Categorizer module failed: {e}")
        tests_failed += 1
    
    # Test 3: Excel importer
    try:
        from modules.excel_import import ExcelImporter
        importer = ExcelImporter()
        template = importer.create_sample_excel()
        assert template is not None
        print("✓ Excel importer module working")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Excel importer module failed: {e}")
        tests_failed += 1
    
    print()
    print(f"Tests: {tests_passed} passed, {tests_failed} failed")
    print()
    
    return tests_failed == 0

def main():
    """Main setup function"""
    
    print("\n" + "=" * 60)
    print("STEP 1: Creating directory structure...")
    print("=" * 60)
    create_directory_structure()
    
    print("\n" + "=" * 60)
    print("STEP 2: Checking and installing dependencies...")
    print("=" * 60)
    dependencies_ok = check_and_install_packages()
    
    print("\n" + "=" * 60)
    print("STEP 3: Running tests...")
    print("=" * 60)
    tests_ok = run_tests()
    
    print("\n" + "=" * 60)
    print("SETUP SUMMARY")
    print("=" * 60)
    
    if dependencies_ok and tests_ok:
        print("✓ Setup completed successfully!")
        print()
        print("To run the application:")
        print("  streamlit run main.py")
        print()
        print("To create sample data for testing:")
        print("  python sample_data_generator.py")
        print()
    else:
        print("⚠ Setup completed with warnings")
        print("Please review the errors above and fix them manually")
        print()
    
    print("=" * 60)

if __name__ == "__main__":
    main()
