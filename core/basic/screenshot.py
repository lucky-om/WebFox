import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from colorama import Fore

def capture(domain, save_path):
    print(Fore.YELLOW + "[*] Taking Screenshot...")
    
    # 1. Configure Firefox Options
    options = Options()
    options.add_argument("--headless")  # Run without a visible window
    options.add_argument("--no-sandbox") # Required for running as root/Kali
    options.add_argument("--disable-dev-shm-usage") # Fixes memory issues on phones
    
    # 2. Try to locate geckodriver manually if it's not in PATH
    service = None
    if os.path.exists("/usr/bin/geckodriver"):
        service = Service("/usr/bin/geckodriver")
    elif os.path.exists("./geckodriver"):
        service = Service("./geckodriver")

    try:
        # 3. Initialize the Browser
        if service:
            driver = webdriver.Firefox(options=options, service=service)
        else:
            driver = webdriver.Firefox(options=options)
            
        driver.set_page_load_timeout(30) # Give it 30 seconds to load
        
        # 4. Visit and Snap
        url = f"http://{domain}"
        driver.get(url)
        time.sleep(3) # Wait for animations
        
        output_file = f"{save_path}/screenshot.png"
        driver.save_screenshot(output_file)
        driver.quit()
        
        print(Fore.GREEN + f"[✓] Screenshot saved: screenshot.png")
        
    except Exception as e:
        # 5. Print the EXACT error so we know what to fix next
        print(Fore.RED + f"[-] Screenshot failed. Error: {e}")

