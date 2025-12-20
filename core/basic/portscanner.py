import socket, threading
from colorama import Fore
def scan(domain, threads, save_path):
    ports = [21,22,23,25,53,80,110,135,139,143,443,445,993,995,1433,3306,3389,8080,8443]
    open_p = []
    def check(p):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        if s.connect_ex((domain, p)) == 0: open_p.append(str(p))
        s.close()
    
    ts = [threading.Thread(target=check, args=(p,)) for p in ports]
    for t in ts: t.start()
    for t in ts: t.join()
    
    with open(f"{save_path}/ports.txt", "w") as f: f.write("\n".join(open_p))
    print(Fore.GREEN + f"    > Open Ports: {', '.join(open_p)}")
