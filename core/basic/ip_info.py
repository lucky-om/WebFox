import socket, requests
from colorama import Fore
def scan(domain, save_path):
    print(Fore.YELLOW + "[*] IP Geolocation...")
    try:
        ip = socket.gethostbyname(domain)
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        with open(f"{save_path}/ip_location.txt", "w") as f: f.write(str(r))
    except: pass
      
