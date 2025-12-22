import socket
import requests
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Performing Deep IP Reconnaissance...")
    
    main_ip = "Unknown"
    
    # --- PART 1: ADVANCED GEOLOCATION & NETWORK INFO ---
    try:
        main_ip = socket.gethostbyname(domain)
        
        # Query API for ALL fields
        url = f"http://ip-api.com/json/{main_ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        data = requests.get(url, timeout=10).json()
        
        if data.get('status') == 'success':
            # Extract details
            country = f"{data.get('city')}, {data.get('regionName')} ({data.get('country')})"
            zip_code = data.get('zip', 'N/A')
            coords = f"{data.get('lat')}, {data.get('lon')}"
            timezone = data.get('timezone', 'Unknown')
            isp = data.get('isp', 'Unknown')
            org = data.get('org', 'Unknown')
            asn = data.get('as', 'Unknown') # Autonomous System Number
            
            # Print Rich Info
            print(Fore.GREEN + f"    > Target IP : {main_ip}")
            print(Fore.GREEN + f"    > Location  : {country} [Zip: {zip_code}]")
            print(Fore.GREEN + f"    > Coords    : {coords}")
            print(Fore.GREEN + f"    > Timezone  : {timezone}")
            print(Fore.CYAN  + f"    > ISP       : {isp}")
            print(Fore.CYAN  + f"    > Org       : {org}")
            print(Fore.CYAN  + f"    > ASN       : {asn}")
            
            # Save Full Report
            with open(f"{save_path}/ip_location.txt", "w") as f:
                f.write("[MAIN SERVER INTELLIGENCE]\n")
                f.write(f"IP Address  : {main_ip}\n")
                f.write(f"Location    : {country}\n")
                f.write(f"Zip Code    : {zip_code}\n")
                f.write(f"Coordinates : {coords}\n")
                f.write(f"Timezone    : {timezone}\n")
                f.write("-" * 30 + "\n")
                f.write(f"ISP         : {isp}\n")
                f.write(f"Organization: {org}\n")
                f.write(f"ASN         : {asn}\n")
                f.write("=" * 30 + "\n")
        else:
            print(Fore.RED + "    > IP Lookup Failed: API Error")

    except Exception as e:
        print(Fore.RED + f"    > IP Scan Error: {e}")

    # --- PART 2: REAL IP LEAK DETECTION (Cloudflare Bypass) ---
    print(Fore.YELLOW + "[*] Hunting for Real IP Leaks (Cloudflare Bypass)...")
    
    bypass_subs = ["ftp", "cpanel", "webmail", "direct", "mail", "dev", "test", "autodiscover", "whm"]
    leaks = []

    for sub in bypass_subs:
        subdomain = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(subdomain)
            
            # If sub IP != Main IP, it's a potential leak
            if ip != main_ip and main_ip != "Unknown":
                print(Fore.RED + f"    [!] LEAK FOUND: {subdomain} -> {ip}")
                leaks.append(f"{subdomain} : {ip}")
                
        except: pass 

    # Save Leaks
    with open(f"{save_path}/ip_location.txt", "a") as f:
        if leaks:
            f.write("\n[POTENTIAL REAL IPs / BYPASS]\n")
            f.write("These IPs differ from the main domain (Potential Real Server).\n")
            f.write("-" * 30 + "\n")
            f.write("\n".join(leaks))
        else:
            f.write("\n[REAL IP CHECK]\nNo direct IP leaks found via common subdomains.\n")
