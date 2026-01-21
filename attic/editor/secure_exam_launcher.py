#!/usr/bin/env python3
"""
Secure Exam Launcher & Auto-Login - THREE TAB VERSION (FIXED)
Uses file:// for info page with Editor tab as controller

This script:
1. Kills all major browser processes.
2. Starts a secure, allow-list-only proxy server on 127.0.0.1:8080.
3. Logs into the exam server to get session cookies.
4. Fetches the required User-Agent string from the server.
5. Launches Firefox with THREE tabs:
   - Exam Tab (Worker 1) - reports visibility
   - Editor Tab (Controller) - coordinates locking
   - Info Tab (Worker 2) - reports visibility
6. Locks when BOTH worker tabs (exam AND info) are hidden
"""

import requests
import json
import os
import sys
import time
from pathlib import Path
import subprocess
import platform
import tempfile
import shutil
import re
import socket
import threading
import http.server
import socketserver
from urllib.parse import urlparse

# --- Configuration ---
SERVER_URL = "https://olimpiada.ic.unicamp.br"
LOGIN_URL = f"{SERVER_URL}/contas/login/"
USER_AGENT_API_URL = f"{SERVER_URL}/get_exam_ua/"

LOG_FILE = "examproxy.log"
LISTEN_ADDR = "127.0.0.1"
LISTEN_PORT = 8080
REFRESH_INTERVAL_SECONDS = 300

# URLs to open
EXAM_URL = "https://editor.provas.ic.unicamp.br/"
IDE_URL = "https://editor.provas.ic.unicamp.br/editor/"
INFO_URL = "https://editor.provas.ic.unicamp.br/info/" 

# --- Proxy Allow-List Configuration ---
ALLOWED_HOSTS = [
    "script.google.com",
    "script.googleusercontent.com",
    "olimpiada.ic.unicamp.br",
    "editor.provas.ic.unicamp.br",
    "pj.provas.ic.unicamp.br",
    "p1.provas.ic.unicamp.br",
    "p2.provas.ic.unicamp.br",
    "ps.provas.ic.unicamp.br",
    "cdn.jsdelivr.net",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "detectportal.firefox.com",
    "location.services.mozilla.com",
    "firefox.settings.services.mozilla.com",
    "firefox-settings-attachments.cdn.mozilla.net",
    "content-signature-2.cdn.mozilla.net",
    "ads.mozilla.org",
]

ALLOWED_PATH_RULES = {}

# --- Global Proxy State ---
allowed_ip_set = set()
allowed_mutex = threading.Lock()
running = True

# ==============================================================================
# BUNDLED DRIVER HELPER
# ==============================================================================

def get_driver_path(driver_name):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    path = os.path.join(base_path, driver_name)
    
    if platform.system() == "Darwin":
        log_line(f"Attempting to remove quarantine attribute from {driver_name}...")
        try:
            subprocess.run(['xattr', '-d', 'com.apple.quarantine', path], 
                           check=False, capture_output=True)
            log_line("Quarantine attribute removed (if it existed).")
        except Exception as e:
            log_line(f"[Warning] Failed to run xattr command: {e}")

    if platform.system() != "Windows":
        if not os.access(path, os.X_OK):
            try:
                os.chmod(path, 0o755)
            except Exception as e:
                log_line(f"[Error] Failed to make driver executable: {e}")
            
    return path

# ==============================================================================
# LOGGING
# ==============================================================================
log_mutex = threading.Lock()

def log_line(line):
    with log_mutex:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_msg = f"[{timestamp}] {line}"
        print(log_msg)
        try:
            with open(LOG_FILE, "a") as f:
                f.write(log_msg + "\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}")

# ==============================================================================
# PROCESS & CLEANUP
# ==============================================================================

def kill_existing_browsers():
    log_line("Checking for existing browser processes...")
    system = platform.system()
    browsers = ["firefox", "chrome", "msedge", "opera"]
    try:
        if system == "Windows":
            for browser in browsers:
                subprocess.run(["taskkill", "/F", "/IM", f"{browser}.exe"], check=False, capture_output=True)
        else:
            for browser in browsers:
                subprocess.run(["pkill", "-9", "-i", browser], check=False, capture_output=True)
            if system == "Darwin":
                subprocess.run(["killall", "-9", "Firefox"], check=False, capture_output=True)
                subprocess.run(["killall", "-9", "Google Chrome"], check=False, capture_output=True)
                subprocess.run(["killall", "-9", "Microsoft Edge"], check=False, capture_output=True)
                subprocess.run(["killall", "-9", "Opera"], check=False, capture_output=True)

        log_line("Attempted to kill all browser processes")
        time.sleep(2)
    except Exception as e:
        log_line(f"Error killing browsers: {e}")

def kill_process_on_port(port):
    log_line(f"Checking for processes using port {port}...")
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(
                f"netstat -aon | findstr :{port} | findstr LISTENING",
                shell=True, check=False, capture_output=True
            )
            log_line("Attempting to free port (Windows). Manual check may be needed.")
        elif system == "Darwin":
            cmd = f"lsof -ti tcp:{port} | xargs kill -9 2>/dev/null"
            subprocess.run(cmd, shell=True, check=False, capture_output=True)
        else:
            cmd = f"fuser -k {port}/tcp 2>/dev/null"
            subprocess.run(cmd, shell=True, check=False, capture_output=True)
        
        log_line(f"Attempted to kill process on port {port}")
        time.sleep(1)
    except Exception as e:
        log_line(f"Error killing process on port {port}: {e}")

def clean_firefox_session(profile_path):
    log_line(f"Cleaning Firefox session data in {profile_path}...")
    if not os.path.isdir(profile_path):
        return
    session_files = ["sessionstore.jsonlz4", "sessionCheckpoints.json"]
    session_dirs = ["sessionstore-backups"]
    for file in session_files:
        try: os.remove(os.path.join(profile_path, file))
        except OSError: pass
    for dir in session_dirs:
        try: shutil.rmtree(os.path.join(profile_path, dir))
        except OSError: pass
    log_line("Session data cleaned")

# ==============================================================================
# PROXY LOGIC
# ==============================================================================

def is_host_allowed(hostname):
    return hostname.lower() in [h.lower() for h in ALLOWED_HOSTS]

def is_ip_allowed(ip):
    with allowed_mutex:
        return ip in allowed_ip_set

def refresh_allowed_ips():
    log_line("Refreshing allowed IP addresses...")
    new_ips = set()
    for host in ALLOWED_HOSTS:
        try:
            addrs = socket.getaddrinfo(host, None)
            for addr in addrs:
                ip = addr[4][0]
                new_ips.add(ip)
        except Exception as e:
            log_line(f"Failed to resolve {host}: {e}")
    
    with allowed_mutex:
        allowed_ip_set.clear()
        allowed_ip_set.update(new_ips)
    
    log_line(f"Allowed IPs: {len(allowed_ip_set)} addresses")

def refresher_thread():
    global running
    while running:
        time.sleep(REFRESH_INTERVAL_SECONDS)
        if running:
            refresh_allowed_ips()

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log_line(f"[Proxy] {format % args}")
    
    def do_CONNECT(self):
        try:
            host, port = self.path.split(':')
            port = int(port)
            
            if not is_host_allowed(host):
                log_line(f"[Proxy] BLOCKED: {host}")
                self.send_error(403, "Forbidden")
                return
            
            try:
                ip = socket.gethostbyname(host)
                if not is_ip_allowed(ip):
                    log_line(f"[Proxy] BLOCKED IP: {host} ({ip})")
                    self.send_error(403, "Forbidden")
                    return
            except Exception as e:
                log_line(f"[Proxy] DNS lookup failed for {host}: {e}")
                self.send_error(502, "Bad Gateway")
                return
            
            try:
                target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                target.connect((host, port))
            except Exception as e:
                log_line(f"[Proxy] Connection failed to {host}:{port}: {e}")
                self.send_error(502, "Bad Gateway")
                return
            
            self.send_response(200, "Connection Established")
            self.end_headers()
            
            self._tunnel(target)
            
        except Exception as e:
            log_line(f"[Proxy] CONNECT error: {e}")
            self.send_error(500, "Internal Server Error")
    
    def _tunnel(self, target):
        client = self.connection
        sockets = [client, target]
        
        try:
            while True:
                import select
                readable, _, _ = select.select(sockets, [], [], 1.0)
                
                if not readable:
                    continue
                
                for sock in readable:
                    try:
                        data = sock.recv(8192)
                        if not data:
                            return
                        
                        other = target if sock is client else client
                        other.sendall(data)
                    except Exception:
                        return
        except Exception:
            pass
        finally:
            target.close()

def proxy_thread():
    global proxy_server
    try:
        proxy_server = socketserver.ThreadingTCPServer(
            (LISTEN_ADDR, LISTEN_PORT),
            ProxyHandler
        )
        proxy_server.allow_reuse_address = True
        log_line(f"[Proxy] Started on {LISTEN_ADDR}:{LISTEN_PORT}")
        proxy_server.serve_forever()
    except Exception as e:
        log_line(f"[Proxy] Error: {e}")

# ==============================================================================
# AUTO-LOGIN
# ==============================================================================

def login(username, password):
    session = requests.Session()
    log_line(f"[Login] Attempting to login as '{username}'...")
    try:
        response = session.get(LOGIN_URL, timeout=10)
        response.raise_for_status()
        csrf_token = session.cookies.get('csrftoken', '')
    except Exception as e:
        log_line(f"[Error] Failed to access login page: {e}")
        return None
    try:
        login_data = {'username': username, 'password': password}
        if csrf_token:
            login_data['csrfmiddlewaretoken'] = csrf_token
        headers = {'Referer': LOGIN_URL}
        response = session.post(
            LOGIN_URL,
            data=login_data,
            headers=headers,
            allow_redirects=True,
            timeout=10
        )
        if response.status_code == 200:
            if 'sessionid' in session.cookies or 'login' not in response.url.lower():
                log_line("[Login] ✓ Login successful!")
                return session.cookies.get_dict()
            else:
                log_line("[Login] ✗ Login failed - still on login page")
                return None
        else:
            log_line(f"[Login] ✗ Login failed with status {response.status_code}")
            return None
    except Exception as e:
        log_line(f"[Error] Login exception: {e}")
        return None

def fetch_user_agent(contestant):
    url = f"{USER_AGENT_API_URL}{contestant}"
    log_line(f"Fetching User-Agent from {url}...")
    try:
        response = requests.get(url, params={"contestant": contestant}, timeout=10)
        response.raise_for_status()
        raw = response.text.strip()
        log_line(f"Raw UA response: {raw}")
        level_pos = raw.find("level=")
        examkit_pos = raw.find("ExamKit")
        if level_pos == -1 or examkit_pos == -1:
            raise ValueError("Invalid UA string format")
        level_start = level_pos + len("level=")
        level_str = raw[level_start : examkit_pos].strip().rstrip(";")
        level = int(level_str)
        ua_string = raw[examkit_pos:]
        log_line(f"Got UA: {ua_string} (level={level})")
        return ua_string, level
    except Exception as e:
        log_line(f"Failed to fetch User-Agent: {e}")
        log_line("Falling back to default User-Agent.")
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0", 0

# ==============================================================================
# BROWSER LAUNCH
# ==============================================================================

def launch_secure_browser(cookies, user_agent_string, username):
    """
    Launch Firefox with THREE tabs:
    - Exam tab (Worker 1)
    - Editor tab (Controller)
    - Info tab (Worker 2) from local file
    """
    profile_dir = tempfile.mkdtemp(prefix="obi_browser_")
    log_line(f"Creating temporary profile at: {profile_dir}")
    clean_firefox_session(profile_dir)
    
    # Create userChrome.css
    try:
        chrome_dir = os.path.join(profile_dir, "chrome")
        os.makedirs(chrome_dir, exist_ok=True)
        css_content = """
        #nav-bar, #toolbar-menubar, #new-tab-button, #tabs-newtab-button {
            visibility: collapse !important;
        }
        #PanelUI-menu-button {
            visibility: collapse !important;
            display: none !important;
        }
        #firefox-view-button {
            visibility: collapse !important;
        }
        """
        with open(os.path.join(chrome_dir, "userChrome.css"), "w") as f:
            f.write(css_content)
        log_line("Created userChrome.css to hide UI elements.")
    except Exception as e:
        log_line(f"[Warning] Failed to create userChrome.css: {e}")
    
    log_line("[Browser] Configuring Firefox options...")
    try:
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
    except ImportError:
        log_line("[Error] Selenium not installed. Please run: pip install selenium")
        return False
        
    options = FirefoxOptions()
    
    # Kiosk mode with profile
    options.add_argument("-kiosk")
    options.add_argument("-profile")
    options.add_argument(profile_dir)
    options.add_argument("-no-remote")
    
    # Set custom User-Agent
    log_line(f"Setting User-Agent: {user_agent_string}")
    options.set_preference("general.useragent.override", user_agent_string)
    
    # Enable userChrome.css
    options.set_preference("toolkit.legacyUserProfileCustomizations.stylesheets", True)
    
    # Enable beforeunload prompts
    options.set_preference("dom.disable_beforeunload", False)
    
    # Set proxy
    log_line(f"Setting proxy to {LISTEN_ADDR}:{LISTEN_PORT}")
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.http", LISTEN_ADDR)
    options.set_preference("network.proxy.http_port", LISTEN_PORT)
    options.set_preference("network.proxy.ssl", LISTEN_ADDR)
    options.set_preference("network.proxy.ssl_port", LISTEN_PORT)
    options.set_preference("network.proxy.no_proxies_on", "localhost, 127.0.0.1")
    
    # Disable DNS-over-HTTPS and HTTP3
    options.set_preference("network.trr.mode", 5)
    options.set_preference("network.http.http3.enabled", False)
    options.set_preference("browser.tabs.firefox-view", False)

    # --- DISABLE DEV TOOLS ---
    #options.set_preference("devtools.policy.disabled", True)
    
    # JavaScript for Exam tab (Worker 1)
    js_exam_worker = f"""
    (function() {{
        if (window.obiWorkerInjected) return;
        window.obiWorkerInjected = true;
        console.log('Exam Tab (Worker 1): Script Injected');
        
        const bc = new BroadcastChannel('obi_exam_visibility');
        let isLocked = false;

        const username = {json.dumps(username)}; 

        function showLockoutScreen() {{
            if (isLocked) return;
            isLocked = true;
            window.onbeforeunload = null;
            const newHTML = `
            <style>
                body {{ background-color: #333; color: white; font-family: sans-serif; }}
                div {{ display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 100vh; font-size: 1.5rem; }}
                h1 {{ color: #FF6B6B; font-size: 3rem; }}
                p {{ padding-top: 2.0rem; }}
            </style>
            <div>
                <h1>Exame Terminado</h1>
                <p>Esta sessão foi encerrada por violar as regras do exame.</p>
                <p>Por favor, aguarde instruções de um fiscal.</p>
            </div>`;
            document.body.innerHTML = newHTML;
        }}

        bc.postMessage({{ 'id': 'exam', 'state': document.hidden ? 'hidden' : 'visible' }});
        document.addEventListener('visibilitychange', () => {{
            if (isLocked) return;
            const myState = document.hidden ? 'hidden' : 'visible';
            console.log('posting change in Exam visibility, ', myState);
            bc.postMessage({{ 'id': 'exam', 'state': document.hidden ? 'hidden' : 'visible' }});
        }});
        window.addEventListener('beforeunload', () => {{
            if (isLocked) return;
            bc.postMessage({{ 'id': 'exam', 'state': 'closed' }});
        }});

        bc.onmessage = (event) => {{
            if (event.data.command === 'LOCK') {{
                console.log('Exam Tab: Received LOCK command.');
                showLockoutScreen();
            }}
            
            if (event.data.command === 'request_username') {{
                console.log('Exam Tab: Received username request. Replying.');
                bc.postMessage({{ 'id': 'exam', 'command': 'set_username', 'value': username }});
            }}
        }};
    }})();
    """
    
    # JavaScript for Info tab (Worker 2)
    js_info_worker = """
    (function() {
        const bc = new BroadcastChannel('obi_exam_visibility');
        let isLocked = false;
        console.log('Info Tab (Worker 2): script injected.');
        function showLockoutScreen() {
            if (isLocked) return;
            isLocked = true;
            window.onbeforeunload = null;
            const newHTML = `
            <style>
                body { background-color: #333; color: white; font-family: sans-serif; }
                div { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 100vh; font-size: 1.5rem; }
                h1 { color: #FF6B6B; font-size: 3rem; }
                p { padding-top: 2.0rem; }
            </style>
            <div>
                <h1>Exame Terminado</h1>
                <p>Esta sessão foi encerrada por violar as regras do exame.</p>
                <p>Por favor, aguarde instruções de um fiscal.</p>
            </div>`;
            document.body.innerHTML = newHTML;
        }

        bc.postMessage({ 'id': 'info', 'state': document.hidden ? 'hidden' : 'visible' });
        document.addEventListener('visibilitychange', () => {
            if (isLocked) return;
            const myState = document.hidden ? 'hidden' : 'visible';
            console.log('posting change in Info visibility, ', myState);
            bc.postMessage({ 'id': 'info', 'state': myState });
            console.log('posted!');
        });
        window.addEventListener('beforeunload', () => {
            if (isLocked) return;
            bc.postMessage({ 'id': 'info', 'state': 'closed' });
        });

        bc.onmessage = (event) => {
            if (event.data.command === 'LOCK') {
                console.log('Info Tab: Received LOCK command.');
                showLockoutScreen();
            }
        };
    })();
    """

    driver = None
    try:
        log_line("[Browser] Launching Firefox...")
        
        driver_name = "geckodriver.exe" if platform.system() == "Windows" else "geckodriver"
        driver_path = get_driver_path(driver_name)
        log_line(f"[Browser] Using driver at: {driver_path}")
        service = FirefoxService(executable_path=driver_path)
        driver = webdriver.Firefox(service=service, options=options)

        # Open Info tab (Worker 2) - FIRST
        log_line(f"[Browser] Opening Info URL: {INFO_URL}")
        driver.get(INFO_URL)
        time.sleep(2)
        log_line("[Browser] Injecting visibility worker script into Info tab...")
        driver.execute_script(js_info_worker)
        log_line("[Browser] ✓ Injected worker script into Info tab.")
        
        # Open Exam tab (Worker 1)
        log_line(f"[Browser] Opening exam URL: {EXAM_URL}")
        driver.execute_script("window.open(arguments[0], '_blank');", EXAM_URL)
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[1])
        log_line("[Browser] Injecting visibility worker script into Exam tab...")
        driver.execute_script(js_exam_worker)
        log_line("[Browser] ✓ Injected worker script into Exam tab.")
        
        # Open IDE tab (Controller)
        log_line(f"[Browser] Opening IDE URL: {IDE_URL}")
        driver.execute_script("window.open(arguments[0], '_blank');", IDE_URL)
        time.sleep(1)
        
        # Stay on Info tab (switch back to first tab)
        driver.switch_to.window(driver.window_handles[0])
        log_line("[Browser] ✓ Staying on Info tab.")
        
        
        # Switch back to exam tab
        #driver.switch_to.window(driver.window_handles[0])

        log_line("[Browser] ✓ Secure browser is running with 3 tabs.")
        log_line("[Browser] Close the browser window when finished.")

        # Keep alive
        while True:
            time.sleep(1)
            try:
                driver.current_url
            except Exception:
                log_line("[Browser] Browser window closed.")
                break
    except KeyboardInterrupt:
        log_line("\n[Browser] Interrupted. Closing browser...")
    except Exception as e:
        log_line(f"[Error] Browser runtime error: {e}")
        import traceback
        log_line(f"[Error] Traceback: {traceback.format_exc()}")
        return False
    finally:
        if driver:
            driver.quit()
        log_line("[Browser] Firefox quit.")
        try:
            shutil.rmtree(profile_dir)
            log_line(f"Cleaned up profile: {profile_dir}")
        except Exception as e:
            log_line(f"Error cleaning up profile: {e}")
    
    return True

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    global running, proxy_server
    
    import argparse
    parser = argparse.ArgumentParser(description='Secure OBI Exam Launcher')
    parser.add_argument('username', help='Your contestant username')
    parser.add_argument('password', nargs='?', help='Your password (or use --password-file)')
    parser.add_argument('--password-file', help='Read password from file')
    
    args = parser.parse_args()
    
    password = args.password
    if args.password_file:
        try:
            with open(args.password_file, 'r') as f:
                password = f.read().strip()
        except Exception as e:
            log_line(f"[Error] Failed to read password file: {e}")
            sys.exit(1)
    
    if not password:
        import getpass
        password = getpass.getpass("Password: ")
    
    kill_existing_browsers()
    kill_process_on_port(LISTEN_PORT)
    
    cookies = login(args.username, password)
    if not cookies:
        log_line("\n[Error] Login failed. Please check credentials.")
        sys.exit(1)
    
    ua_string, level = fetch_user_agent(args.username)
    
    refresh_allowed_ips() 
    
    refresher = threading.Thread(target=refresher_thread, daemon=True)
    refresher.start()
    
    proxy = threading.Thread(target=proxy_thread, daemon=True)
    proxy.start()
    
    time.sleep(1) 
    
    try:
        log_line("--- Attempting to launch with Mozilla Firefox ---")
        success = launch_secure_browser(cookies, ua_string, args.username)
        if not success:
            log_line("\n[FATAL] Failed to launch Firefox. Exiting.")

    except KeyboardInterrupt:
        log_line("Main thread interrupted.")
    except Exception as e_firefox:
        log_line(f"[Error] Failed to launch Firefox: {e_firefox}")
        log_line("\n[FATAL] Browser failed to launch. Exiting.")
    finally:
        log_line("Shutting down...")
        running = False
        if 'proxy_server' in globals():
            proxy_server.shutdown()
            proxy_server.server_close()
        log_line("All processes stopped. Exiting.")

if __name__ == "__main__":
    try:
        import select
    except ImportError:
        log_line("Module 'select' not available. Proxy tunneling will fail.")
        sys.exit(1)
        
    main()
