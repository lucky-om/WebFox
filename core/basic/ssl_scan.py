
import ssl, socket, datetime
from colorama import Fore
def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Checking SSL...")
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as s:
            with ctx.wrap_socket(s, server_hostname=domain) as ss:
                cert = ss.getpeercert()
                with open(f"{save_path}/ssl_info.txt", "w") as f:
                    f.write(str(cert['notAfter']))
        print(Fore.GREEN + "[✓] SSL Valid")
    except: pass
      
