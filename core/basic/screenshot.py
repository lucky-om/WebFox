import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from colorama import Fore

def capture(domain, save_path):
    print(Fore.YELLOW + "[*] Taking Screenshot...")
    
    # 1. Force Headless Environment Variables
    os.environ['MOZ_HEADLESS'] = '1'
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage") # Critical for Android
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # 2. Explicitly tell Python where Firefox is
    # On Kali, it is usually here:
    if os.path.exists("/usr/bin/firefox-esr"):
        options.binary_location = "/usr/bin/firefox-esr"
    elif os.path.exists("/usr/bin/firefox"):
        options.binary_location = "/usr/bin/firefox"

    # 3. Locate the Driver
    service = None
    if os.path.exists("/usr/bin/geckodriver"):
        service = Service("/usr/bin/geckodriver")
    elif os.path.exists("./geckodriver"):
        service = Service("./geckodriver")

    try:
        # Initialize Driver
        if service:
            driver = webdriver.Firefox(options=options, service=service)
        else:
            driver = webdriver.Firefox(options=options)
            
        driver.set_page_load_timeout(45)
        
        # Go to URL
        url = f"http://{domain}"
        driver.get(url)
        time.sleep(5) # Wait longer for phone CPUs
        
        output_file = f"{save_path}/screenshot.png"
        driver.save_screenshot(output_file)
        driver.quit()
        
        print(Fore.GREEN + f"[✓] Screenshot saved: screenshot.png")
        
    except Exception as e:
        # If it still fails, it prints a cleaner error
        print(Fore.RED + f"[-] Screenshot failed: {e}")

