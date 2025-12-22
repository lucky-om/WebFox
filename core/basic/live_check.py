import requests
from colorama import Fore
def check(domain):
    try:
    
        requests.get(f"http://{domain}")
        return True
    except:
        print(Fore.RED + f"[-] {domain} is DOWN.")
        return False

