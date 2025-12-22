import time
import os
import re
import requests
import platform
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from colorama import Fore

def capture(domain, save_path):
    # --- SMART DETECTION ---
    # Check if running on Phone (ARM) or PC (x86)
    arch = platform.machine().lower()
    is_phone = "aarch64" in arch or "arm" in arch or os.path.exists("/data/data/com.termux")
    
    if is_phone:
        MAX_PAGES = 5
        print(Fore.YELLOW + f"[*] Phone Detected ({arch}): Limiting to {MAX_PAGES} pages to prevent crash.")
    else:
        MAX_PAGES = 1000
        print(Fore.GREEN + f"[*] Laptop/PC Detected ({arch}): NO LIMIT set (Max 1000).")
    # -----------------------

    print(Fore.YELLOW + "[*] Starting Multi-Page Screenshot...")
    
    # 1. Setup Robust Firefox Options
    os.environ['MOZ_HEADLESS'] = '1'
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Locate Firefox Binary
    if os.path.exists("/usr/bin/firefox-esr"):
        options.binary_location = "/usr/bin/firefox-esr"
    elif os.path.exists("/usr/bin/firefox"):
        options.binary_location = "/usr/bin/firefox"

    # Locate Geckodriver
    service = None
    if os.path.exists("/usr/bin/geckodriver"):
        service = Service("/usr/bin/geckodriver")
    elif os.path.exists("./geckodriver"):
        service = Service("./geckodriver")

    driver = None
    try:
        # 2. Initialize Driver
        if service:
            driver = webdriver.Firefox(options=options, service=service)
        else:
            driver = webdriver.Firefox(options=options)
        
        driver.set_page_load_timeout(45)

        # 3. Find Pages to Screenshot
        base_url = f"http://{domain}"
        target_urls = [base_url]
        
        try:
            print(Fore.CYAN + "    Fetching internal links...")
            html = requests.get(base_url, timeout=10).text
            links = re.findall(r'href=["\'](https?://' + domain + r'/[^"\']*|/[^"\']*)["\']', html)
            
            for link in links:
                full_url = link if link.startswith("http") else f"http://{domain}{link}"
                if full_url not in target_urls and domain in full_url:
                    target_urls.append(full_url)
            
            # Apply the Dynamic Limit
            count_found = len(target_urls)
            target_urls = list(set(target_urls))[:MAX_PAGES]
            
            print(Fore.CYAN + f"    Found {count_found} pages. Snapshotting {len(target_urls)} pages...")
            
        except Exception as e:
            print(Fore.RED + f"[-] Crawl error: {e}. Defaulting to homepage.")
            target_urls = [base_url]

        # 4. Loop and Screenshot
        for i, url in enumerate(target_urls):
            try:
                print(Fore.BLUE + f"    [{i+1}/{len(target_urls)}] Snapping: {url}")
                driver.get(url)
                time.sleep(3)
                
                # Naming
                safe_name = url.replace(f"http://{domain}", "").replace("/", "_").strip("_")
                if not safe_name: safe_name = "homepage"
                # Shorten filename if too long
                safe_name = safe_name[:50] 
                
                driver.save_screenshot(f"{save_path}/screen_{safe_name}.png")
                
            except Exception as e:
                print(Fore.RED + f"    Failed to snap {url}")

        print(Fore.GREEN + f"[✓] Screenshots saved in {save_path}")

    except Exception as e:
        print(Fore.RED + f"[-] Screenshot Engine Failed: {e}")
        
    finally:
        if driver:
            driver.quit()

