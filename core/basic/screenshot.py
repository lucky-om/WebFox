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
    
    # 1. Force Headless Mode
    os.environ['MOZ_HEADLESS'] = '1'
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")            # <--- CRITICAL FIX FOR ROOT USER
    options.add_argument("--disable-dev-shm-usage") # <--- Prevents memory crashes
    options.add_argument("--disable-gpu")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    # 2. Point to correct Firefox Binary (ESR is stable on Kali)
    if os.path.exists("/usr/bin/firefox-esr"):
        options.binary_location = "/usr/bin/firefox-esr"
    elif os.path.exists("/usr/bin/firefox"):
        options.binary_location = "/usr/bin/firefox"

    # 3. Locate Geckodriver (Standard Paths)
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
            
        driver.set_page_load_timeout(60)

        # 5. Simple Crawler to find pages
        base = f"http://{domain}"
        urls = [base]
        try:
            html = requests.get(base, timeout=10).text
            links = re.findall(r'href=["\'](https?://' + domain + r'/[^"\']*|/[^"\']*)["\']', html)
            for l in links:
                full = l if l.startswith("http") else base + l
                if full not in urls: urls.append(full)
            urls = list(set(urls))[:10] # Limit to 10 pages
        except: pass

        print(Fore.CYAN + f"    > Target List: {len(urls)} pages")

        for i, u in enumerate(urls):
            try:
                driver.get(u)
                time.sleep(2)
                name = u.replace("http://","").replace(domain,"").replace("/","_")[:40]
                if not name or name == "_": name = "homepage"
                
                filename = f"{save_path}/{name}.png"
                driver.save_screenshot(filename)
                print(Fore.BLUE + f"    > [{i+1}] Captured: {name}.png")
            except Exception as e:
                pass 

        driver.quit()
        print(Fore.GREEN + "[✓] Screenshots saved.")

    except Exception as e:
        print(Fore.RED + f"    > Screenshot Error: {e}")
        print(Fore.RED + "    > TIP: Run './install.sh' again to fix drivers.")
        
    finally:
        if driver:
            driver.quit()

