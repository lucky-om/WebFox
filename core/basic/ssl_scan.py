import ssl
import socket
import datetime
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Checking SSL Certificate...")
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                not_after = cert['notAfter']
                print(Fore.GREEN + f"[+] SSL Expires: {not_after}")
                
                with open(f"{save_path}/ssl_info.txt", "w") as f:
                    f.write(f"Issuer: {cert['issuer']}\nExpiry: {not_after}")
    except Exception as e:
        print(Fore.RED + f"[-] SSL Check Failed: {e}")
