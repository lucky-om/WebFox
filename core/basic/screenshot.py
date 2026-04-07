"""
Screenshot Module — Auto-disabled on Termux
On real Linux: captures headless Firefox screenshots of key pages.
On Termux: skips gracefully with a warning message.
"""
import time
import os
import re
import requests
from colorama import Fore
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.stealth import is_termux, get_stealth_session


def capture(domain, save_path):
    # ── Termux Guard ─────────────────────────────────────────────────────────
    if is_termux():
        print(Fore.YELLOW + "  [~] Termux detected — Screenshot module disabled (no headless browser on Android).")
        with open(f"{save_path}/screenshots_skipped.txt", "w") as f:
            f.write("Screenshots were skipped because this scan ran on Termux (Android).\n")
            f.write("Run on Linux desktop/server to enable screenshot capture.\n")
        return
    # ─────────────────────────────────────────────────────────────────────────

    try:
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
    except ImportError:
        print(Fore.RED + "  [-] Selenium not installed. Skipping screenshots.")
        return

    print(Fore.CYAN + f"  [*] Capturing high-value visual evidence (Max 5 pages)...")
    session = get_stealth_session()
    driver = None

    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")

        # Firefox binary detection
        firefox_binaries = [
            "/usr/bin/firefox-esr",
            "/usr/bin/firefox",
            "/usr/local/bin/firefox",
        ]
        for binary in firefox_binaries:
            if os.path.exists(binary):
                options.binary_location = binary
                break

        # Geckodriver detection
        geckodriver_paths = [
            "/usr/bin/geckodriver",
            "/usr/local/bin/geckodriver",
            "./geckodriver",
        ]
        service_path = None
        for p in geckodriver_paths:
            if os.path.exists(p):
                service_path = p
                break

        if service_path:
            service = Service(service_path)
            driver = webdriver.Firefox(options=options, service=service)
        else:
            # Try webdriver-manager as fallback
            try:
                from webdriver_manager.firefox import GeckoDriverManager
                service = Service(GeckoDriverManager().install())
                driver = webdriver.Firefox(options=options, service=service)
            except Exception:
                print(Fore.RED + "  [-] Geckodriver not found. Skipping screenshots.")
                return

        driver.set_page_load_timeout(30)

        base_url = f"http://{domain}"
        candidates = {base_url}

        # Discover high-value URLs from homepage links
        try:
            r = session.get(base_url, timeout=10, verify=False)
            links = re.findall(r'href=["\\'](https?://[^"\\\']+)["\\'']', r.text)
            for link in links:
                if domain in link:
                    candidates.add(link)
        except Exception:
            pass

        # Score and rank URLs
        keywords = {
            "login": 90, "signin": 90, "sign-in": 90,
            "admin": 80, "dashboard": 80, "portal": 80,
            "register": 70, "signup": 70,
            "profile": 60, "account": 60,
            "contact": 50, "about": 40,
        }

        scored = []
        base_clean = base_url.rstrip("/")
        for url in candidates:
            score = 100 if url.rstrip("/") == base_clean else 0
            url_lower = url.lower()
            for word, pts in keywords.items():
                if word in url_lower:
                    score = pts
                    break
            if score > 0:
                scored.append((score, url))

        scored.sort(key=lambda x: x[0], reverse=True)
        final_targets = [x[1] for x in scored[:5]]

        for i, url in enumerate(final_targets):
            try:
                driver.get(url)
                time.sleep(2)

                # Determine a nice name for the screenshot file
                if url.rstrip("/") == base_clean:
                    name = "Homepage"
                else:
                    name = "Page"
                    for k in keywords:
                        if k in url.lower():
                            name = k.capitalize()
                            break

                filename = f"{save_path}/Screenshot_{i+1}_{name}.png"
                driver.save_screenshot(filename)
                print(Fore.GREEN + f"    > [{i+1}/{len(final_targets)}] Captured: {name} ({url})")
            except Exception:
                pass

        print(Fore.GREEN + f"  [+] Screenshots complete.")

    except Exception as e:
        print(Fore.RED + f"  [-] Screenshot error: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
