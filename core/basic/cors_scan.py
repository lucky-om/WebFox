import requests
from colorama import Fore
def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Checking CORS...")
    try:
        h = {'Origin': 'http://evil.com'}
        r = requests.get(f"http://{domain}", headers=h, timeout=5)
        if r.headers.get('Access-Control-Allow-Origin') == 'http://evil.com':
            msg = "VULNERABLE: Reflects arbitrary origin"
            print(Fore.RED + f"    [!] {msg}")
            with open(f"{save_path}/cors_vuln.txt", "w") as f: f.write(msg)
    except: pass
