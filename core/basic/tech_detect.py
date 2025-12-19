import builtwith
from colorama import Fore
def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Detecting Tech...")
    try:
        r = builtwith.parse(f"http://{domain}")
        with open(f"{save_path}/technologies.txt", "w") as f: f.write(str(r))
    except: pass
      
