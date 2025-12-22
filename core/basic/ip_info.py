import socket
import requests
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Geolocating Server...")
    try:
        ip = socket.gethostbyname(domain)
        # Added timeout to prevent hanging
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10).json()
        
        city = r.get('city', 'Unknown')
        country = r.get('country', 'Unknown')
        isp = r.get('isp', 'Unknown')
        
        print(Fore.GREEN + f"    > IP Address: {ip}")
        print(Fore.GREEN + f"    > Location  : {city}, {country}")
        print(Fore.GREEN + f"    > Provider  : {isp}")
        
        with open(f"{save_path}/ip_location.txt", "w") as f:
            f.write(f"IP Address  : {ip}\n")
            f.write(f"City        : {city}\n")
            f.write(f"Country     : {country}\n")
            f.write(f"ISP         : {isp}\n")
            
    except Exception as e:
        print(Fore.RED + f"    > IP Scan Error: {e}")
