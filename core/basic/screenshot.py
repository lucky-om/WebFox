import time, os, re, requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from colorama import Fore

def capture(domain, save_path):
    os.environ['MOZ_HEADLESS'] = '1'
    opt = Options()
    opt.add_argument("--headless")
    opt.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Firefox(options=opt)
        driver.set_page_load_timeout(300) # 5 Minutes per page
        
        base = f"http://{domain}"
        urls = [base]
        try:
            html = requests.get(base).text
            links = re.findall(r'href=["\'](https?://' + domain + r'/[^"\']*|/[^"\']*)["\']', html)
            for l in links:
                full = l if l.startswith("http") else base + l
                if full not in urls: urls.append(full)
            # PC MODE: Deep Scan (Up to 100 pages)
            urls = list(set(urls))[:100]
        except: pass

        print(Fore.CYAN + f"    > Queued {len(urls)} pages for capture...")
        for i, u in enumerate(urls):
            try:
                driver.get(u)
                time.sleep(2)
                name = u.replace("http://","").replace(domain,"").replace("/","_")[:40] or "home"
                driver.save_screenshot(f"{save_path}/{name}.png")
                print(Fore.BLUE + f"    > [{i+1}] Captured: {name}.png")
            except: pass
        driver.quit()
    except Exception as e: print(Fore.RED + f"    > Error: {e}")
