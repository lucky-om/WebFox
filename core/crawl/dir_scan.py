"""
WebFox — Stealthy Directory & Sensitive File Scanner
Checks critical paths for exposed files and sensitive directories using stealth delays.

Author : Lucky | WebFox Recon Framework v4.0
"""
import requests
from colorama import Fore
import sys
import os
import time
import random
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.stealth import get_stealth_session

# Prioritized list of high-value paths to check
SENSITIVE_PATHS = [
    # Config & Secrets
    "/.env",
    "/.env.backup",
    "/.env.local",
    "/.env.production",
    "/config.php",
    "/config.json",
    "/configuration.php",
    "/settings.py",
    "/database.yml",
    "/wp-config.php",
    "/.aws/credentials",

    # Admin Panels
    "/admin",
    "/admin/",
    "/admin/login",
    "/administrator",
    "/wp-admin",
    "/wp-login.php",
    "/phpmyadmin",
    "/cpanel",
    "/panel",
    "/dashboard",
    "/manager",
    "/console",

    # Sensitive Files / Backups
    "/.git/HEAD",
    "/.git/config",
    "/.svn/entries",
    "/backup.zip",
    "/backup.tar.gz",
    "/db.sql",
    "/database.sql",
    "/dump.sql",
    "/robots.txt",

    # Security Testing Paths
    "/server-status",
    "/server-info",
    "/.htaccess",
    "/web.config",
    "/crossdomain.xml",
    "/clientaccesspolicy.xml",
    "/api/v1",
    "/api/v2",
    "/api/users",
    "/api/docs",
    "/swagger",
    "/swagger-ui.html",
    "/openapi.json",
    "/graphql",

    # Log & Debug Files
    "/error.log",
    "/access.log",
    "/debug.log",
    "/laravel.log",
    "/storage/logs/laravel.log",
    "/application.log",
    "/app/logs/application.log",
]

FOUND_STATUS_CODES = {200, 301, 302, 403}
CRITICAL_CODES = {200, 301, 302}

def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Stealthy directory & file scan for {domain} ({len(SENSITIVE_PATHS)} paths)...")
    session = get_stealth_session()

    found = []
    base_url = f"https://{domain}"

    # Quick connectivity check — prefer HTTPS, fallback to HTTP
    try:
        session.get(base_url, timeout=8, verify=False)
    except Exception:
        base_url = f"http://{domain}"

    for path in SENSITIVE_PATHS:
        url = base_url + path
        try:
            # Use HEAD first (minimal footprint), fall back to GET if needed
            r = session.head(url, timeout=8, allow_redirects=False, verify=False)
            status = r.status_code
            
            if status not in FOUND_STATUS_CODES:
                # Some servers reject HEAD — try GET only for likely hits
                r = session.get(url, timeout=8, allow_redirects=False, verify=False)
                status = r.status_code

            if status in FOUND_STATUS_CODES:
                content_length = r.headers.get("Content-Length", "?")
                content_type = r.headers.get("Content-Type", "?").split(";")[0]
                risk = "CRITICAL" if ".env" in path or ".git" in path or ".sql" in path or "backup" in path else "HIGH" if status in CRITICAL_CODES else "INFO"
                
                result = f"[{status}] {url} | {content_type} | Size: {content_length} | Risk: {risk}"
                found.append(result)
                
                if risk == "CRITICAL":
                    print(Fore.RED + f"  [!!!] EXPOSED: {url} ({status})")
                elif status == 403:
                    print(Fore.YELLOW + f"  [~] Protected: {url} (403 - Exists but restricted)")
                else:
                    print(Fore.YELLOW + f"  [!] Found: {url} ({status})")

        except requests.exceptions.SSLError:
            pass  # SSL issues are expected — silently skip
        except Exception:
            pass

        # Brief stealthy delay between requests (0.3 - 0.9s) — reduces WAF trigger risk
        time.sleep(random.uniform(0.3, 0.9))

    try:
        with open(f"{save_path}/dir_scan.txt", "w", encoding="utf-8") as f:
            f.write(f"DIRECTORY/FILE SCAN RESULTS: {domain}\n")
            f.write(f"Total paths checked: {len(SENSITIVE_PATHS)}\n")
            f.write("=" * 50 + "\n\n")
            if found:
                f.write(f"FOUND ({len(found)}):\n")
                for line in found:
                    f.write(line + "\n")
            else:
                f.write("No sensitive paths were accessible.\n")
    except Exception as e:
        print(Fore.RED + f"  [-] Error saving dir scan: {e}")

    crit = [x for x in found if "CRITICAL" in x]
    print(Fore.GREEN + f"  [+] Dir scan complete. {len(found)} paths found ({len(crit)} critical).")
