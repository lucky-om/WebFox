import requests, re
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Scraping Emails...")
    try:
        
        text = requests.get(f"http://{domain}").text
        emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text, re.I))
        valid = [e for e in emails if not e.endswith(('png','jpg','js'))]
        
        if valid:
            print(Fore.GREEN + f"    > Found {len(valid)} emails.")
            with open(f"{save_path}/emails.txt", "w") as f: f.write("\n".join(valid))
        else: print(Fore.RED + "    > No emails found.")
    except: pass
