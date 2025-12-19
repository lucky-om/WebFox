import requests
from colorama import Fore
def enumerate(domain, save_path):
    print(Fore.YELLOW + "[*] Fetching Subdomains...")
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        data = requests.get(url, timeout=10).json()
        subs = set(e['name_value'] for e in data)
        with open(f"{save_path}/subdomains.txt", "w") as f:
            for s in subs: f.write(s+"\n")
        print(Fore.GREEN + f"[✓] Found {len(subs)} subdomains")
    except: print(Fore.RED + "[-] Subdomain scan failed")
