import requests
from colorama import Fore
def check(domain):
    print(Fore.YELLOW + f"[*] Checking {domain}...")
    try:
        r = requests.get(f"http://{domain}", timeout=5)
        if r.status_code < 500:
            print(Fore.GREEN + "[+] Target is LIVE")
            return True
    except: pass
    print(Fore.RED + "[-] Target seems DOWN")
    return False
  
