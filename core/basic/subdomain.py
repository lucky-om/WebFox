import requests
from colorama import Fore
def enumerate(domain, save_path):
    try:
        # NO TIMEOUT - Will wait forever
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        data = requests.get(url).json() 
        subs = set(e['name_value'] for e in data)
        with open(f"{save_path}/subdomains.txt", "w") as f:
            for s in subs: f.write(s+"\n")
        print(Fore.GREEN + f"    > Found {len(subs)} subdomains.")
    except Exception as e:
        print(Fore.RED + f"    > Failed: {e}")

