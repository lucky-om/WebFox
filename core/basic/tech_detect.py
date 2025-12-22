import builtwith
import subprocess
import re
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Fingerprinting OS & Technologies...")
    
    tech_data = {}
    os_guess = "Unknown"

    # --- PART 1: SOFTWARE SCAN (Basic) ---
    try:
        # Detects CMS, Web Servers, Frameworks (e.g. WordPress, Nginx, React)
        tech_data = builtwith.parse(f"http://{domain}")
    except: pass

    # --- PART 2: OS DETECTION via TTL (Advanced) ---
    try:
        # Sends a single ping packet to check 'Time To Live' (TTL)
        cmd = ['ping', '-c', '1', domain]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = proc.communicate()
        
        # Extract TTL value
        ttl_match = re.search(r'ttl=(\d+)', out.decode(), re.IGNORECASE)
        if ttl_match:
            ttl = int(ttl_match.group(1))
            # Linux usually has TTL around 64, Windows around 128
            if ttl <= 64: os_guess = "Linux / Unix"
            elif ttl <= 128: os_guess = "Windows Server"
            else: os_guess = "Solaris / Network Device"
    except: pass

    # --- PART 3: HEADER ANALYSIS (Confirmation) ---
    # Double-checks the OS by looking at server headers (e.g., "Microsoft-IIS")
    if 'web-servers' in tech_data:
        headers = str(tech_data['web-servers']).lower()
        if 'iis' in headers or 'microsoft' in headers:
            os_guess = "Windows Server (Confirmed by Headers)"
        elif 'ubuntu' in headers or 'debian' in headers:
            os_guess = "Linux (Confirmed by Headers)"

    # --- OUTPUT & SAVE ---
    print(Fore.GREEN + f"    > OS Detect : {os_guess}")
    
    # Print discovered technologies
    for cat, tools in tech_data.items():
        print(Fore.BLUE + f"    > {cat}: {', '.join(tools)}")

    # Save to file for GUI
    with open(f"{save_path}/technologies.txt", "w") as f:
        f.write(f"OPERATING SYSTEM: {os_guess}\n")
        f.write("="*30 + "\n")
        if not tech_data:
            f.write("No specific technologies detected.\n")
        for cat, tools in tech_data.items():
            f.write(f"{cat}: {', '.join(tools)}\n")
