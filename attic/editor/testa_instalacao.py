#!/usr/bin/env python3
"""
Installation test script for OBI Auto-Login
Tests all requirements without attempting to login

Usage:
    python test_installation.py
"""

import sys
import shutil
import subprocess

def check_python():
    """Check Python version"""
    print("="*70)
    print("1. CHECKING PYTHON")
    print("="*70)
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 6:
        print("✓ Python version is OK (3.6+)")
        return True
    else:
        print("✗ Python version is too old (need 3.6+)")
        return False


def check_firefox():
    """Check if Firefox is installed"""
    print("\n" + "="*70)
    print("2. CHECKING FIREFOX")
    print("="*70)
    
    firefox = shutil.which('firefox')
    if firefox:
        print(f"✓ Firefox found: {firefox}")
        
        # Try to get version
        try:
            result = subprocess.run(
                ['firefox', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"  Version: {result.stdout.strip()}")
        except:
            pass
        
        return True
    else:
        print("✗ Firefox not found")
        print("\nPlease install Firefox:")
        print("  Ubuntu/Debian: sudo apt install firefox")
        print("  macOS:         brew install --cask firefox")
        print("  Windows:       https://www.mozilla.org/firefox/")
        return False


def check_geckodriver():
    """Check if geckodriver is installed"""
    print("\n" + "="*70)
    print("3. CHECKING GECKODRIVER")
    print("="*70)
    
    geckodriver = shutil.which('geckodriver')
    if geckodriver:
        print(f"✓ geckodriver found: {geckodriver}")
        
        # Try to get version
        try:
            result = subprocess.run(
                ['geckodriver', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    print(f"  Version: {lines[0]}")
        except:
            pass
        
        return True
    else:
        print("✗ geckodriver not found")
        print("\nPlease install geckodriver:")
        print("  Ubuntu/Debian: sudo apt install firefox-geckodriver")
        print("  macOS:         brew install geckodriver")
        print("  Windows:       https://github.com/mozilla/geckodriver/releases")
        return False


def check_pip():
    """Check if pip is available"""
    print("\n" + "="*70)
    print("4. CHECKING PIP")
    print("="*70)
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ pip is available")
            print(f"  {result.stdout.strip()}")
            return True
        else:
            print("✗ pip not found")
            return False
    except Exception as e:
        print(f"✗ Error checking pip: {e}")
        return False


def check_python_packages():
    """Check if required Python packages are installed"""
    print("\n" + "="*70)
    print("5. CHECKING PYTHON PACKAGES")
    print("="*70)
    
    packages = {
        'requests': 'requests',
        'selenium': 'selenium',
    }
    
    all_ok = True
    
    for package_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            print(f"⚠ {package_name} is NOT installed (will be auto-installed)")
            all_ok = False
    
    if not all_ok:
        print("\nNote: Missing packages will be automatically installed")
        print("      when you run auto_login.py for the first time.")
    
    return True  # Return True because auto-install will handle this


def check_internet():
    """Check internet connectivity"""
    print("\n" + "="*70)
    print("6. CHECKING INTERNET CONNECTION")
    print("="*70)
    
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("✓ Internet connection is OK")
        return True
    except OSError:
        print("⚠ No internet connection detected")
        print("  Internet is required for first-time setup and login")
        return False


def main():
    """Run all checks"""
    print("\n")
    print("*" * 70)
    print(" OBI AUTO-LOGIN - INSTALLATION TEST")
    print("*" * 70)
    print()
    
    results = {
        'Python': check_python(),
        'Firefox': check_firefox(),
        'geckodriver': check_geckodriver(),
        'pip': check_pip(),
        'Python packages': check_python_packages(),
        'Internet': check_internet(),
    }
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for name, ok in results.items():
        status = "✓ OK" if ok else "✗ FAIL"
        print(f"{name:20s} {status}")
    
    critical = ['Python', 'Firefox', 'geckodriver', 'pip']
    critical_ok = all(results[k] for k in critical)
    
    print("\n" + "="*70)
    if critical_ok:
        print("RESULT: ✓ System is ready for auto_login.py")
        print("="*70)
        print("\nYou can now run:")
        print("  python3 auto_login.py <username> <password>")
        print()
        sys.exit(0)
    else:
        print("RESULT: ✗ Some critical components are missing")
        print("="*70)
        print("\nPlease install the missing components listed above")
        print("and run this test again.")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
