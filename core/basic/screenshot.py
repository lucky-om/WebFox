import time
import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from colorama import Fore

def capture(domain, save_path):
    print(Fore.YELLOW + "[*] Taking Full-Res Screenshots (Please Wait)...")
    
    # 1. Force Headless Mode for Root User
    os.environ['MOZ_HEADLESS'] = '1'
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")            # <--- CRITICAL FOR ROOT
    options.add_argument("--disable-dev-shm-usage") # <--- Prevents memory crash
    options.add_argument("--disable-gpu")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    # 2. Force use of Firefox ESR (More stable on Kali)
    if os.path.exists("/usr/bin/firefox-esr"):
        options.binary_location = "/usr/bin/firefox-esr"
    elif os.path.exists("/usr/bin/firefox"):
        options.binary_location = "/usr/bin/firefox"

    # 3. Locate Geckodriver
    service = None
    if os.path.exists("/usr/bin/geckodriver"):
        service = Service("/usr/bin/geckodriver")
    elif os.path.exists("./geckodriver"):
        service = Service("./geckodriver")

    try:
        # 4. Initialize Driver
        if service:
            driver = webdriver.Firefox(options=options, service=service)
        else:
            driver = webdriver.Firefox(options=options)
            
        driver.set_page_load_timeout(300)

        # 5. Scan Logic
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

        print(Fore.CYAN + f"    > Target List: {len(urls)} pages")

        for i, u in enumerate(urls):
            try:
                driver.get(u)
                time.sleep(2)
                name = u.replace("http://","").replace(domain,"").replace("/","_")[:40] or "home"
                
                # Fix empty filenames
                if name == "_" or name == "": name = "homepage"
                
                filename = f"{save_path}/{name}.png"
                driver.save_screenshot(filename)
                print(Fore.BLUE + f"    > [{i+1}] Captured: {name}.png")
            except Exception as e:
                pass # Skip bad pages silently

        driver.quit()
        print(Fore.GREEN + "[✓] Screenshots saved.")

    except Exception as e:
        print(Fore.RED + f"    > Error: {e}")
        print(Fore.RED + "    > TIP: Run './install.sh' again to fix drivers.")

