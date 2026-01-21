#!/usr/bin/env python3
"""
Auto-login script for OBI Compiler
Logs into olimpiada.ic.unicamp.br and opens the editor in a browser
with authenticated session cookies.
"""

import requests
import json
import os
import sys
import time
from pathlib import Path
import subprocess
import platform

# Configuration
SERVER_URL = "https://olimpiada.ic.unicamp.br"
LOGIN_URL = f"{SERVER_URL}/contas/login/"  # Your Django login page
TOKEN_API_URL = f"{SERVER_URL}/api/auth/login"  # Token API endpoint
EDITOR_URL = f"{SERVER_URL}/editor/"  # Editor URL
EDITOR_TOKEN_URL = f"{SERVER_URL}/editor/auth?token="  # Token auth URL

# Cookie storage
COOKIE_FILE = Path.home() / ".obi_session_cookies.json"


def login(username, password):
    """
    Perform login and return session cookies
    
    Returns:
        dict: Session cookies or None if login failed
    """
    session = requests.Session()
    
    print(f"[Login] Attempting to login as '{username}'...")
    
    # Step 1: Get CSRF token (if needed)
    try:
        # First, visit the login page to get any CSRF tokens
        response = session.get(LOGIN_URL)
        response.raise_for_status()
        
        # If your Django site uses CSRF protection, extract the token
        # This assumes the token is in cookies (standard Django behavior)
        csrf_token = session.cookies.get('csrftoken', '')
        
    except Exception as e:
        print(f"[Error] Failed to access login page: {e}")
        return None
    
    # Step 2: Submit login credentials
    try:
        login_data = {
            'username': username,
            'password': password,
        }
        
        # Add CSRF token if present
        if csrf_token:
            login_data['csrfmiddlewaretoken'] = csrf_token
        
        headers = {
            'Referer': LOGIN_URL,  # Required by Django CSRF protection
        }
        
        response = session.post(
            LOGIN_URL,
            data=login_data,
            headers=headers,
            allow_redirects=True
        )
        
        # Check if login was successful
        # Adjust this logic based on your server's response
        if response.status_code == 200:
            # Check if we're actually logged in (you might need to adjust this)
            if 'sessionid' in session.cookies or 'login' not in response.url.lower():
                print("[Login] ✓ Login successful!")
                
                # Save cookies for the browser
                cookies = session.cookies.get_dict()
                save_cookies(cookies)
                
                return cookies
            else:
                print("[Login] ✗ Login failed - still on login page")
                return None
        else:
            print(f"[Login] ✗ Login failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[Error] Login request failed: {e}")
        return None


def save_cookies(cookies):
    """Save cookies to a file"""
    try:
        with open(COOKIE_FILE, 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f"[Cookies] Saved to {COOKIE_FILE}")
    except Exception as e:
        print(f"[Error] Failed to save cookies: {e}")


def load_cookies():
    """Load cookies from file"""
    try:
        if COOKIE_FILE.exists():
            with open(COOKIE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"[Error] Failed to load cookies: {e}")
    return None


def launch_browser_with_cookies(cookies, url, browser='firefox'):
    """
    Launch a browser with pre-loaded session cookies
    
    Args:
        cookies: Dictionary of cookies to inject
        url: URL to open
        browser: 'firefox' (default) or 'chrome'
    """
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="obi_browser_")
    
    print(f"[Browser] Launching {browser} with authenticated session...")
    print(f"[Browser] URL: {url}")
    
    try:
        from selenium import webdriver
        
        driver = None
        
        if browser.lower() == 'firefox':
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from selenium.webdriver.firefox.service import Service as FirefoxService
            
            options = FirefoxOptions()
            
            # Create a temporary Firefox profile
            options.add_argument("-profile")
            options.add_argument(temp_dir)
            
            # Optional: Run in normal window (not headless)
            # options.add_argument("--headless")  # Uncomment for headless mode
            
            # Disable some Firefox features for cleaner experience
            options.set_preference("browser.startup.homepage", "about:blank")
            options.set_preference("startup.homepage_welcome_url", "about:blank")
            options.set_preference("startup.homepage_welcome_url.additional", "about:blank")
            
            try:
                driver = webdriver.Firefox(options=options)
            except Exception as e:
                print(f"[Error] Failed to launch Firefox: {e}")
                print("[Info] Make sure geckodriver is installed:")
                print("  Ubuntu/Debian: sudo apt install firefox-geckodriver")
                print("  Or download from: https://github.com/mozilla/geckodriver/releases")
                return False
        
        elif browser.lower() == 'chrome':
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            
            options = ChromeOptions()
            options.add_argument(f"--user-data-dir={temp_dir}")
            options.add_argument("--no-first-run")
            options.add_argument("--disable-default-apps")
            
            try:
                driver = webdriver.Chrome(options=options)
            except Exception as e:
                print(f"[Error] Failed to launch Chrome: {e}")
                print("[Info] Make sure chromedriver is installed:")
                print("  Ubuntu/Debian: sudo apt install chromium-chromedriver")
                return False
        
        else:
            print(f"[Error] Unsupported browser: {browser}")
            return False
        
        # First visit the domain to set cookies
        driver.get(SERVER_URL)
        
        # Inject cookies
        for name, value in cookies.items():
            print(f"cookie: name={name} value={value}")
            driver.add_cookie({
                'name': name,
                'value': value,
                'domain': 'olimpiada.ic.unicamp.br'  # Adjust if needed
            })
        
        # Now navigate to the editor - cookies are loaded!
        driver.get(url)
        
        print(f"[Browser] ✓ {browser.capitalize()} launched successfully!")
        print("[Browser] The editor is now running with your authenticated session.")
        print("[Browser] Close the browser window when done.")
        
        # Keep the script running while browser is open
        try:
            while True:
                time.sleep(1)
                # Check if browser is still alive
                try:
                    driver.current_url
                except:
                    break
        except KeyboardInterrupt:
            print("\n[Browser] Closing browser...")
        finally:
            driver.quit()
        
        return True
        
    except ImportError:
        print("[Warning] Selenium not installed. Install with: pip install selenium")
        print("[Info] Falling back to manual cookie injection...")
        return False
    except Exception as e:
        print(f"[Error] Failed to launch browser with Selenium: {e}")
        return False


def generate_cookie_injection_script(cookies):
    """
    Generate a JavaScript snippet that can be run in the browser console
    to inject cookies manually
    """
    script = "// Run this in the browser console:\n"
    for name, value in cookies.items():
        script += f"document.cookie = '{name}={value}; path=/; domain=olimpiada.ic.unicamp.br';\n"
    script += "// Then refresh the page (press F5)\n"
    
    return script


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Auto-login to OBI Compiler and launch editor'
    )
    parser.add_argument('username', help='Your username')
    parser.add_argument('password', nargs='?', help='Your password (or use --password-file)')
    parser.add_argument('--password-file', help='Read password from file')
    parser.add_argument('--reuse-session', action='store_true', 
                       help='Reuse existing session cookies if available')
    parser.add_argument('--print-cookies', action='store_true',
                       help='Print cookie injection script for manual use')
    
    args = parser.parse_args()
    
    # Get password
    password = args.password
    if args.password_file:
        try:
            with open(args.password_file, 'r') as f:
                password = f.read().strip()
        except Exception as e:
            print(f"[Error] Failed to read password file: {e}")
            sys.exit(1)
    
    if not password:
        import getpass
        password = getpass.getpass("Password: ")
    
    # Try to reuse existing session
    cookies = None
    if args.reuse_session:
        print("[Session] Checking for existing session...")
        cookies = load_cookies()
        if cookies:
            print("[Session] ✓ Found existing session cookies")
    
    # Login if no valid session
    if not cookies:
        cookies = login(args.username, password)
        if not cookies:
            print("\n[Error] Login failed. Please check your credentials.")
            sys.exit(1)
    
    # Print cookies for manual injection if requested
    if args.print_cookies:
        print("\n" + "="*60)
        print("COOKIE INJECTION SCRIPT")
        print("="*60)
        print(generate_cookie_injection_script(cookies))
        print("="*60 + "\n")
    
    # Launch browser
    success = launch_browser_with_cookies(cookies, EDITOR_URL)
    
    if not success:
        print("failed!")


if __name__ == "__main__":
    main()
