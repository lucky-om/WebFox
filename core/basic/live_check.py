import requests
from colorama import Fore
def check(domain):
    try:
        requests.get(f"http://{domain}", timeout=15)
        return True
    except:
        print(Fore.RED + f"[-] {domain} is DOWN.")
        return False
