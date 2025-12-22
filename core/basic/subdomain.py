import requests, json, socket, threading
from queue import Queue
from colorama import Fore

def enumerate(domain, save_path):
    print(Fore.YELLOW + "[*] Fetching & Verifying Subdomains...")
    found = set()
    live = []
    
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        # NO TIMEOUT on requests
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        for e in r: found.add(e['name_value'])
    except: pass
    
    def check(sub):
        try:
            # Standard socket timeout (not strict)
            ip = socket.gethostbyname(sub)
            live.append(f"{sub} ({ip})")
            print(Fore.GREEN + f"    [+] Alive: {sub}")
        except: pass

    q = Queue()
    for s in found: q.put(s)
    
    def worker():
        while not q.empty():
            check(q.get())
            q.task_done()

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    with open(f"{save_path}/subdomains.txt", "w") as f:
        f.write(f"Total Found: {len(found)}\n")
        f.write(f"Active Found: {len(live)}\n\n")
        f.write("\n".join(live))

