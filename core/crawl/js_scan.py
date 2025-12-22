import requests
import re
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Parsing JS Files for hidden URLs...")
    try:
        text = requests.get(f"http://{domain}", timeout=10).text
        js_files = re.findall(r'src=["\'](.*?\.js)["\']', text)
        print(Fore.BLUE + f"    Found {len(js_files)} JS files. Scanning content...")
        
        found_urls = set()
        
        for js in js_files:
            if js.startswith("//"): js_url = "http:" + js
            elif js.startswith("/"): js_url = f"http://{domain}{js}"
            elif not js.startswith("http"): js_url = f"http://{domain}/{js}"
            else: js_url = js
            
            try:
                content = requests.get(js_url, timeout=5).text
                links = re.findall(r'https?://[a-zA-Z0-9./?=&_-]+', content)
                for l in links: found_urls.add(l)
            except: pass
            
        with open(f"{save_path}/js_urls.txt", "w") as f:
            for link in found_urls: f.write(link + "\n")
            
        print(Fore.GREEN + f"[✓] Found {len(found_urls)} hidden URLs in JS.")
    except Exception as e:
        print(Fore.RED + f"[-] JS Scan failed: {e}")
