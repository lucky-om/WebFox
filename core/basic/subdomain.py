import requests
from colorama import Fore

def enumerate(domain, save_path):
    print(Fore.YELLOW + "[*] Fetching Subdomains (crt.sh)...")
    try:
        # Changed timeout from 10 to 30 seconds
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        data = requests.get(url, timeout=30).json()
        
        subs = set()
        for entry in data:
            subs.add(entry['name_value'])
        
        with open(f"{save_path}/subdomains.txt", "w") as f:
            for s in subs:
                f.write(s + "\n")
                # Optional: Print each one if you want to see them live
                # print(Fore.CYAN + f"    {s}")
                
        print(Fore.GREEN + f"[✓] Found {len(subs)} subdomains.")
        
    except requests.exceptions.Timeout:
        print(Fore.RED + "[-] Subdomain scan timed out (Try increasing timeout in code).")
    except Exception as e:
        print(Fore.RED + f"[-] Subdomain scan failed: {e}")

