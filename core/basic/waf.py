import requests
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Checking Firewall & Security Headers...")
    sigs = {"Cloudflare": "cf-ray", "Akamai": "akamai", "AWS": "awselb"}
    
    try:
        # NO TIMEOUT
        r = requests.get(f"http://{domain}")
        headers = r.headers
        
        h_str = str(headers).lower()
        waf = ", ".join([n for n, k in sigs.items() if k in h_str]) or "None"
        print(Fore.GREEN + f"    > WAF: {waf}")
        
        report = [f"WAF: {waf}\n", "\n[MISSING HEADERS]"]
        for h in ["X-Frame-Options", "X-XSS-Protection", "Strict-Transport-Security"]:
            if h not in headers:
                print(Fore.RED + f"    [-] Missing: {h}")
                report.append(h)
        
        with open(f"{save_path}/waf.txt", "w") as f: f.write("\n".join(report))
    except: pass
