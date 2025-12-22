import socket
import requests
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Geolocating Server...")
    try:
        # 1. Get IP
        ip = socket.gethostbyname(domain)
        
        # 2. Get Data (with 10s timeout)
        url = f"http://ip-api.com/json/{ip}"
        r = requests.get(url, timeout=10).json()
        
        # 3. Extract Details safely
        city = r.get('city', 'Unknown')
        country = r.get('country', 'Unknown')
        isp = r.get('isp', 'Unknown')
        region = r.get('regionName', 'Unknown')
        
        # 4. Print to Terminal
        print(Fore.GREEN + f"    > IP Address: {ip}")
        print(Fore.GREEN + f"    > Location  : {city}, {region}, {country}")
        print(Fore.GREEN + f"    > Provider  : {isp}")
        
        # 5. Save Formatted Report (Best for GUI)
        with open(f"{save_path}/ip_location.txt", "w") as f:
            f.write(f"IP Address  : {ip}\n")
            f.write(f"City        : {city}\n")
            f.write(f"Region      : {region}\n")
            f.write(f"Country     : {country}\n")
            f.write(f"ISP (Cloud) : {isp}\n")
            
    except Exception as e:
        print(Fore.RED + f"    > IP Scan Failed: {e}")
