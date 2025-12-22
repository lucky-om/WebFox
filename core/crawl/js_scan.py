import requests, re
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Parsing JS Files...")
    try:
        # NO TIMEOUT
        text = requests.get(f"http://{domain}").text
        js_files = re.findall(r'src=["\'](.*?\.js)["\']', text)
        found_urls = set()
        
        for js in js_files:
            if not js.startswith("http"): js = f"http://{domain}/{js}"
            try:
                c = requests.get(js).text
                for l in re.findall(r'https?://[a-zA-Z0-9./?=&_-]+', c): found_urls.add(l)
            except: pass
            
        with open(f"{save_path}/js_urls.txt", "w") as f:
            for l in found_urls: f.write(l + "\n")
        print(Fore.GREEN + f"    > Extracted {len(found_urls)} hidden URLs.")
    except: pass
