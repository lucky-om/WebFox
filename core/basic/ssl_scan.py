import ssl
import socket
import datetime
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Checking SSL Certificate...")
    hostname = domain
    context = ssl.create_default_context()
    
    try:
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Get expiry date
                not_after = cert['notAfter']
                
                # Calculate days remaining (optional but nice to have)
                # expiry_date = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                # days_left = (expiry_date - datetime.datetime.now()).days
                
                print(Fore.GREEN + f"[+] SSL Expires: {not_after}")
                
                # Save to file
                with open(f"{save_path}/ssl_info.txt", "w") as f:
                    f.write(f"Issuer: {cert['issuer']}\nExpiry: {not_after}\n")
                    
    except Exception as e:
        print(Fore.RED + f"[-] SSL Check Failed: {e}")

