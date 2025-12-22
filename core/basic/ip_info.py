import socket
import requests
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Analyzing Server IP & Geolocation...")
    
    main_ip = "Unknown"
    
    # --- PART 1: BASIC GEOLOCATION ---
    try:
        main_ip = socket.gethostbyname(domain)
        # Use a free API to get location data
        r = requests.get(f"http://ip-api.com/json/{main_ip}").json()
        
        city = r.get('city', 'Unknown')
        country = r.get('country', 'Unknown')
        isp = r.get('isp', 'Unknown')
        
        print(Fore.GREEN + f"    > Main IP   : {main_ip}")
        print(Fore.GREEN + f"    > Location  : {city}, {country}")
        print(Fore.GREEN + f"    > Provider  : {isp}")
        
        # Save Basic Info
        with open(f"{save_path}/ip_location.txt", "w") as f:
            f.write(f"MAIN SERVER INFO\n")
            f.write(f"IP Address: {main_ip}\n")
            f.write(f"Location  : {city}, {country}\n")
            f.write(f"ISP       : {isp}\n")
            f.write("="*30 + "\n")
            
    except Exception as e:
        print(Fore.RED + f"    > IP Scan Error: {e}")

    # --- PART 2: REAL IP DETECTION (Cloudflare Bypass) ---
    print(Fore.YELLOW + "[*] Hunting for Real IP Leaks (Cloudflare Bypass)...")
    
    bypass_subs = ["ftp", "cpanel", "webmail", "direct", "mail", "dev", "test", "autodiscover"]
    leaks = []

    for sub in bypass_subs:
        subdomain = f"{sub}.{domain}"
        try:
            # Resolve Subdomain IP
            ip = socket.gethostbyname(subdomain)
            
            # If this IP is DIFFERENT from the Main IP, it might be the Real Server!
            if ip != main_ip and main_ip != "Unknown":
                print(Fore.RED + f"    [!] LEAK FOUND: {subdomain} -> {ip}")
                leaks.append(f"{subdomain} : {ip}")
            # Optional: Uncomment to see protected ones
            # else: print(Fore.GREEN + f"    > {subdomain}: Protected ({ip})")
                
        except:
            pass # Subdomain doesn't exist

    # Append Leaks to the same file
    with open(f"{save_path}/ip_location.txt", "a") as f:
        if leaks:
            f.write("\n[POTENTIAL REAL IPs / LEAKS]\n")
            f.write("These IPs are different from the main domain.\n")
            f.write("They might bypass the WAF (Cloudflare).\n")
            f.write("-" * 30 + "\n")
            f.write("\n".join(leaks))
            print(Fore.CYAN + f"    > Found {len(leaks)} potential direct IPs.")
        else:
            f.write("\n[REAL IP CHECK]\nNo direct IP leaks found via common subdomains.\n")
            print(Fore.GREEN + "    > No direct IP leaks found.")
