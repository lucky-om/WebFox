import whois
from colorama import Fore
def scan(domain, save_path):
    try:
        w = whois.whois(domain)
        print(Fore.GREEN + f"    > Owner: {w.org}")
        print(Fore.GREEN + f"    > Loc  : {w.city}, {w.country}")
        with open(f"{save_path}/whois_basic.txt", "w") as f:
            f.write(f"Owner: {w.org}\nLoc: {w.city}, {w.country}\nReg: {w.registrar}")
    except: pass
