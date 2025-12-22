import requests
import json
from colorama import Fore

def enumerate(domain, save_path):
    print(Fore.YELLOW + "[*] Fetching Subdomains (Infinite Wait Mode)...")
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        
        # 1. Check if crt.sh is actually working
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=45)
        
        if r.status_code != 200:
            print(Fore.RED + f"    > crt.sh is down (Status {r.status_code}). Skipping.")
            return

        # 2. Try to parse JSON safely
        try:
            data = r.json()
        except json.JSONDecodeError:
            print(Fore.RED + "    > crt.sh returned Invalid Data (API Error). Skipping.")
            return

        subs = set()
        for entry in data:
            subs.add(entry['name_value'])
        
        with open(f"{save_path}/subdomains.txt", "w") as f:
            for s in subs: f.write(s + "\n")
            
        print(Fore.GREEN + f"    > Found {len(subs)} subdomains.")
        
    except Exception as e:
        print(Fore.RED + f"    > Subdomain Error: {e}")
