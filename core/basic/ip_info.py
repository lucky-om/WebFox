import socket, requests
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Geolocating Server...")
    try:
        ip = socket.gethostbyname(domain)
        # NO TIMEOUT
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        
        city = r.get('city', 'Unknown')
        country = r.get('country', 'Unknown')
        isp = r.get('isp', 'Unknown')
        
        print(Fore.GREEN + f"    > Server IP : {ip}")
        print(Fore.GREEN + f"    > Hosted In : {city}, {country}")
        print(Fore.GREEN + f"    > Provider  : {isp}")
        
        with open(f"{save_path}/ip_location.txt", "w") as f:
            f.write(f"IP: {ip}\nLocation: {city}, {country}\nISP: {isp}")
    except Exception as e:
        print(Fore.RED + f"    > IP Scan Error: {e}")

