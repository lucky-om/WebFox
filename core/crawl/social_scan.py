import requests, re
from colorama import Fore
def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Scraping Social Links...")
    try:
        t = requests.get(f"http://{domain}", timeout=10).text
        pats = {"FB": r"facebook\.com/[\w\.]+", "Insta": r"instagram\.com/[\w\.]+", "X": r"twitter\.com/\w+"}
        found = []
        for k,v in pats.items():
            for m in set(re.findall(v, t, re.I)):
                print(Fore.BLUE + f"    > {k}: {m}")
                found.append(m)
        if found:
            with open(f"{save_path}/social_links.txt", "w") as f: f.write("\n".join(found))
    except: pass
