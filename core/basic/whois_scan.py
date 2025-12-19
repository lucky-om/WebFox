import whois
from colorama import Fore
def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Whois Lookup...")
    try:
        w = whois.whois(domain)
        with open(f"{save_path}/whois.txt", "w") as f: f.write(str(w))
    except: pass
      
