import time, os, re, requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from colorama import Fore

def capture(domain, save_path):
    print(Fore.YELLOW + "[*] Starting Visual Surveillance (High Timeout)...")
    os.environ['MOZ_HEADLESS'] = '1'
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    
    if os.path.exists("/usr/bin/firefox-esr"): opts.binary_location = "/usr/bin/firefox-esr"

    driver = None
    try:
        driver = webdriver.Firefox(options=opts)
        # 120 SECONDS PAGE LOAD TIMEOUT
        driver.set_page_load_timeout(120)
        
        urls = [f"http://{domain}"]
        try:
            # NO TIMEOUT ON REQUESTS
            html = requests.get(urls[0]).text
            links = re.findall(r'href=["\'](https?://' + domain + r'/[^"\']*)["\']', html)
            urls += list(set(links))[:8]
        except: pass

        for i, u in enumerate(urls):
            try:
                driver.get(u)
                time.sleep(2)
                name = u.split("/")[-1] or "home"
                driver.save_screenshot(f"{save_path}/{name[:20]}.png")
                print(Fore.BLUE + f"    > Captured: {name}.png")
            except: pass
            
    except Exception as e: print(Fore.RED + f"    > Error: {e}")
    finally: 
        if driver: driver.quit()
