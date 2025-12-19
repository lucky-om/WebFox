import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from colorama import Fore
def capture(domain, save_path):
    print(Fore.YELLOW + "[*] Taking Screenshot...")
    opt = Options()
    opt.add_argument("--headless")
    try:
        d = webdriver.Firefox(options=opt)
        d.get(f"http://{domain}")
        time.sleep(2)
        d.save_screenshot(f"{save_path}/screenshot.png")
        d.quit()
        print(Fore.GREEN + "[✓] Screenshot saved")
    except: print(Fore.RED + "[-] Screenshot failed")
