import dns.resolver
from colorama import Fore
def scan(domain, save_path):
    print(Fore.GREEN + "    > DNS Records Saved.")
    try:
        with open(f"{save_path}/dns.txt", "w") as f:
            for r in ['A', 'MX', 'NS', 'TXT']:
                try:
                    ans = dns.resolver.resolve(domain, r)
                    for d in ans: f.write(f"{r}: {d}\n")
                except: pass
    except: pass

    print(Fore.GREEN + "[✓] DNS saved")
  
