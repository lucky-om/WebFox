import requests, threading
from queue import Queue
from colorama import Fore
def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Hunting Admin Panels...")
    paths = ["admin/", "login/", "wp-admin/", "dashboard/", "cpanel/"]
    found = []
    def check(p):
        try:
            code = requests.get(f"http://{domain}/{p}", timeout=5).status_code
            if code in [200, 401, 403]:
                print(Fore.RED + f"    [!] FOUND: /{p} ({code})")
                found.append(f"/{p} [{code}]")
        except: pass
    
    q = Queue()
    for p in paths: q.put(p)
    def worker():
        while not q.empty():
            check(q.get())
            q.task_done()
    
    ts = [threading.Thread(target=worker) for _ in range(5)]
    for t in ts: t.start()
    for t in ts: t.join()
    
    if found:
        with open(f"{save_path}/admin_paths.txt", "w") as f: f.write("\n".join(found))
