import whois
from colorama import Fore
def scan(domain, save_path):
    try:
        w = whois.whois(domain)
        print(Fore.GREEN + f"    > Owner: {w.org}")
        print(Fore.GREEN + f"    > Loc  : {w.city}, {w.country}")
        with open(f"{save_path}/whois_basic.txt", "w") as f:
            f.write(f"Organization: {w.org}\n")
            f.write(f"City        : {w.city}\n")
            f.write(f"Country     : {w.country}\n")
            f.write(f"Registrar   : {w.registrar}\n")
            f.write(f"Creation Date: {w.creation_date}\n")
    except: pass
