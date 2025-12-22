import builtwith
import subprocess
import re
import platform
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Detecting Technologies & OS...")
    
    tech_data = {}
    os_guess = "Unknown (Firewall blocked ping)"

    # 1. BuiltWith Scan (Software)
    try:
        tech = builtwith.parse(f"http://{domain}")
        tech_data = tech
    except: pass

    # 2. OS Detection via TTL (Ping Fingerprinting)
    try:
        # Command depends on system, but you are on Linux/Android so we use 'ping -c 1'
        cmd = ['ping', '-c', '1', domain]
        
        # Run Ping
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        output = out.decode()

        # Find TTL value in output (e.g., "ttl=53")
        ttl_match = re.search(r'ttl=(\d+)', output, re.IGNORECASE)
        
        if ttl_match:
            ttl = int(ttl_match.group(1))
            
            # Logic: Linux starts at 64, Windows at 128
            if ttl <= 64:
                os_guess = "Linux / Unix (TTL < 64)"
            elif ttl <= 128:
                os_guess = "Windows Server (TTL > 64)"
            else:
                os_guess = "Network Device / Solaris"
    except Exception as e:
        pass

    # 3. Header Analysis (Double Check)
    # Sometimes headers say "Apache/2.4 (Ubuntu)" or "Microsoft-IIS"
    if 'web-servers' in tech_data:
        server_str = str(tech_data['web-servers']).lower()
        if 'iis' in server_str or 'microsoft' in server_str:
            os_guess = "Windows Server (Confirmed by Headers)"
        elif 'ubuntu' in server_str:
            os_guess = "Ubuntu Linux (Confirmed by Headers)"
        elif 'centos' in server_str:
            os_guess = "CentOS Linux (Confirmed by Headers)"

    # Print Results
    print(Fore.GREEN + f"    > OS Detect : {os_guess}")
    
    for cat, tools in tech_data.items():
        tool_str = ', '.join(tools)
        print(Fore.BLUE + f"    > {cat}: {tool_str}")

    # Save to file
    with open(f"{save_path}/technologies.txt", "w") as f:
        f.write(f"TARGET OS GUESS: {os_guess}\n")
        f.write("="*30 + "\n")
        for cat, tools in tech_data.items():
            f.write(f"{cat}: {', '.join(tools)}\n")
