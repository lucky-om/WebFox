import socket, threading
from colorama import Fore
def scan(domain, threads, save_path):
    print(Fore.YELLOW + "[*] Scanning Ports...")
    ports = [21,22,80,443,3306,8080]
    open_p = []
    def check(p):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        if s.connect_ex((domain, p))==0: open_p.append(str(p))
        s.close()
    ts = [threading.Thread(target=check, args=(p,)) for p in ports]
    for t in ts: t.start()
    for t in ts: t.join()
    with open(f"{save_path}/ports.txt", "w") as f: f.write("\n".join(open_p))
    print(Fore.GREEN + f"[✓] Found {len(open_p)} open ports")
  
