import socket, threading
from colorama import Fore

def scan(domain, threads, save_path):
    ports = [21,22,23,25,53,80,110,135,139,143,443,445,3306,3389,8080]
    results = []
    
    def check(p):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # INCREASED TIMEOUT to 5 seconds (Slow but accurate)
            s.settimeout(5.0) 
            if s.connect_ex((domain, p)) == 0:
                try:
                    s.send(b'HEAD / HTTP/1.0\r\n\r\n')
                    banner = s.recv(1024).decode().strip().split('\n')[0][:30]
                except: banner = "Unknown"
                info = f"Port {p}: Open ({banner})"
                print(Fore.GREEN + f"    > {info}")
                results.append(info)
            s.close()
        except: pass

    ts = [threading.Thread(target=check, args=(p,)) for p in ports]
    for t in ts: t.start()
    for t in ts: t.join()
    
    with open(f"{save_path}/ports.txt", "w") as f: f.write("\n".join(results))

