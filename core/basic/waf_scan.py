import requests
from colorama import Fore
def scan(domain, save_path):
    print(Fore.YELLOW + "[*] WAF Detection...")
    try:
        r = requests.get(f"http://{domain}")
        waf = "Cloudflare" if "cloudflare" in str(r.headers).lower() else "None"
        with open(f"{save_path}/waf.txt", "w") as f: f.write(waf)
    except: pass
      
