import requests, re
from colorama import Fore
def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Hunting SQL Injection...")
    errors = {"MySQL": "syntax", "Oracle": "ORA-", "SQL": "Unclosed"}
    vulns = []
    try:
        html = requests.get(f"http://{domain}", timeout=10).text
        links = set(re.findall(r'href=["\'](https?://' + domain + r'/[^"\']*?\?.*?)["\']', html))
        for url in list(links)[:20]: # Check first 20 param links
            try:
                if any(v in requests.get(url+"'", timeout=5).text for k,v in errors.items()):
                    print(Fore.RED + f"    [!] VULNERABLE: {url}")
                    vulns.append(url)
            except: pass
    except: pass
    if vulns:
        with open(f"{save_path}/sqli_vuln.txt", "w") as f: f.write("\n".join(vulns))
