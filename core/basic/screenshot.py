import time
import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from colorama import Fore

def capture(domain, save_path):
    print(Fore.YELLOW + "[*] Taking Full-Res Screenshots...")
    
    # --- KALI LINUX ROOT FIX ---
    os.environ['MOZ_HEADLESS'] = '1'
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")            # <--- FIXES ROOT CRASH
    options.add_argument("--disable-dev-shm-usage") # <--- PREVENTS MEMORY CRASH
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Point to correct Firefox binary
    if os.path.exists("/usr/bin/firefox-esr"):
        options.binary_location = "/usr/bin/firefox-esr"
    elif os.path.exists("/usr/bin/firefox"):
        options.binary_location = "/usr/bin/firefox"

    try:
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(60)

        # Crawler
        base = f"http://{domain}"
        urls = [base]
        try:
            html = requests.get(base, timeout=10).text
            links = re.findall(r'href=["\'](https?://' + domain + r'/[^"\']*|/[^"\']*)["\']', html)
            for l in links:
                full = l if l.startswith("http") else base + l
                if full not in urls: urls.append(full)
            urls = list(set(urls))[:20]
        except: pass

        for i, u in enumerate(urls):
            try:
                driver.get(u)
                time.sleep(2)
                name = u.replace("http://","").replace(domain,"").replace("/","_")[:40]
                if not name or name == "_": name = "homepage"
                
                driver.save_screenshot(f"{save_path}/{name}.png")
                print(Fore.BLUE + f"    > [{i+1}] Captured: {name}.png")
            except: pass

        driver.quit()
        print(Fore.GREEN + "[✓] Screenshots saved.")

    except Exception as e:
        print(Fore.RED + f"    > Screenshot Error: {e}")
