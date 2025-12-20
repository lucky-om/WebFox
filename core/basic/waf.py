import requests
from colorama import Fore
def scan(domain, save_path):
    sigs = {"Cloudflare":"cf-ray", "Akamai":"akamai", "AWS":"awselb", "Imperva":"incap-ses", "F5":"bigip", "Google":"google-cloud-armor"}
    try:
        r = requests.get(f"http://{domain}")
        headers = str(r.headers).lower()
        found = [n for n,k in sigs.items() if k in headers]
        res = ", ".join(found) if found else "None Detected"
        print(Fore.GREEN + f"    > WAF  : {res}")
        with open(f"{save_path}/waf.txt", "w") as f: f.write(res)
    except: pass

