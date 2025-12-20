import socket, requests
from colorama import Fore
def scan(domain, save_path):
    try:
        ip = socket.gethostbyname(domain)
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        print(Fore.GREEN + f"    > IP   : {ip}")
        print(Fore.GREEN + f"    > Cloud: {r.get('isp')}")
        with open(f"{save_path}/ip_location.txt", "w") as f:
            f.write(f"IP Address  : {ip}\n")
            f.write(f"City        : {r.get('city')}\n")
            f.write(f"Region      : {r.get('regionName')}\n")
            f.write(f"Country     : {r.get('country')}\n")
            f.write(f"ISP (Cloud) : {r.get('isp')}\n")
    except: pass
