import requests
from colorama import Fore

def scan(domain, save_path):
    try:
        # NO TIMEOUT
        r = requests.get(f"http://{domain}/robots.txt")
        if r.status_code == 200:
            with open(f"{save_path}/robots.txt", "w") as f: f.write(r.text)
            secrets = [line for line in r.text.split('\n') if any(k in line for k in ['admin','login','backup'])]
            if secrets:
                print(Fore.RED + f"    [!] FOUND {len(secrets)} SENSITIVE PATHS")
                with open(f"{save_path}/robots_secrets.txt", "w") as f: f.write("\n".join(secrets))
    except: pass
