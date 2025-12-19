import requests, re
from colorama import Fore
def scan(domain, save_path):
    print(Fore.YELLOW + "[*] JS Parsing...")
    try:
        t = requests.get(f"http://{domain}").text
        js = re.findall(r'src=["\'](.*?\.js)["\']', t)
        with open(f"{save_path}/js_urls.txt", "w") as f:
            for j in js: f.write(j+"\n")
    except: pass
      
