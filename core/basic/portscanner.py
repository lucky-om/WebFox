import socket
import threading
from colorama import Fore

def scan(domain, threads, save_path):
    print(Fore.CYAN + f"[*] Scanning common ports on {domain}...")
    
    ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1433, 3306, 3389, 5900, 8000, 8080, 8443]
    results = []

    def check(p):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
            if s.connect_ex((domain, p)) == 0:
                try:
                    service = socket.getservbyport(p, 'tcp')
                except:
                    service = "Unknown Service"
                
                output_line = f"Port {p:<5} : OPEN ({service})"
                results.append(output_line)
                print(Fore.GREEN + f"    > {output_line}")
        except:
            pass
        finally:
            s.close()

    ts = [threading.Thread(target=check, args=(p,)) for p in ports]
    for t in ts: t.start()
    for t in ts: t.join()

    with open(f"{save_path}/ports.txt", "w") as f:
        f.write(f"Scan Results for {domain}\n")
        f.write("="*30 + "\n")
        f.write("\n".join(results))

    print(Fore.GREEN + f"[+] Port scan completed. Found {len(results)} open ports.")
