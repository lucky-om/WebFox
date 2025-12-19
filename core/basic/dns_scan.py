import dns.resolver
from colorama import Fore
def scan(domain, save_path):
    print(Fore.YELLOW + "[*] DNS Enumeration...")
    with open(f"{save_path}/dns_records.txt", "w") as f:
        for t in ['A','MX','NS']:
            try:
                ans = dns.resolver.resolve(domain, t)
                for r in ans: f.write(f"{t}: {r.to_text()}\n")
            except: pass
    print(Fore.GREEN + "[✓] DNS saved")
  
