import argparse
import os
import sys
import time
import random

# Colorama check
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("Error: colorama is not installed. Run: pip install colorama")
    sys.exit()

# --- REAL FILE SAVER (MOCK MODULE) ---
class RealFileSaver:
    def __init__(self, module_name):
        self.module_name = module_name

    def scan(self, domain, *args):
        # Find the save path in arguments (it's usually the last argument)
        save_path = args[-1] if args else None
        
        # Simulate processing time
        time.sleep(0.2)
        
        if save_path and os.path.exists(save_path):
            filename = f"{self.module_name}_report.txt"
            full_file_path = os.path.join(save_path, filename)
            
            # Write dummy data to the file so you can see output
            with open(full_file_path, "w") as f:
                f.write(f"--- REPORT: {self.module_name.upper()} ---\n")
                f.write(f"Target: {domain}\n")
                f.write(f"Date: {time.ctime()}\n")
                f.write("-" * 30 + "\n")
                f.write(f"[+] Scan completed successfully for {self.module_name}.\n")
                f.write(f"[+] Found random entry: {random.randint(1000,9999)}\n")
                f.write(f"[+] Status: VULNERABLE (Simulation)\n")
        
    def check(self, domain):
        return True

    def enumerate(self, domain, save_path):
        self.scan(domain, save_path)
        
    def capture(self, domain, save_path):
        self.scan(domain, save_path)

# Initialize scanner objects with names (so files are named correctly)
live_check = RealFileSaver("live_check")
subdomain = RealFileSaver("subdomain")
portscanner = RealFileSaver("portscanner")
screenshot = RealFileSaver("screenshot")
ssl_scan = RealFileSaver("ssl_scan")
dns_scan = RealFileSaver("dns_scan")
tech_detect = RealFileSaver("tech_detect")
whois_scan = RealFileSaver("whois_scan")
ip_info = RealFileSaver("ip_info")
waf = RealFileSaver("waf")
dos_check = RealFileSaver("dos_check")
cors_scan = RealFileSaver("cors_scan")
sqli_scan = RealFileSaver("sqli_scan")
real_ip = RealFileSaver("real_ip")
robots = RealFileSaver("robots")
sitemap = RealFileSaver("sitemap")
js_scan = RealFileSaver("js_scan")
email_scan = RealFileSaver("email_scan")
admin_scan = RealFileSaver("admin_scan")
social_scan = RealFileSaver("social_scan")

# --- UTILITY FUNCTIONS ---

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def type_effect(text, color=Fore.GREEN):
    for char in text:
        sys.stdout.write(color + char)
        sys.stdout.flush()
        time.sleep(0.01)
    print("")

def loading_bar(task):
    sys.stdout.write(f"{Fore.CYAN}[*] {task:<35} ")
    sys.stdout.flush()
    for i in range(5):
        time.sleep(0.05)
        sys.stdout.write(Fore.GREEN + "█")
        sys.stdout.flush()
    print(Fore.GREEN + " [DONE]")

def banner():
    clear()
    logo = r"""
 █      █░▓█████  ▄▄▄▄    █████▒▒█████  ▒██    ██▒
▓█░ █ ░█░▓█    ▀ ▓█████▄▓██   ▒▒██▒  ██▒▒▒ █ █ ▒░
▒█░ █ ░█░▒███    ▒██▒ ▄██▒████ ░▒██░  ██▒░░  █   ░
░█░ █ ░█░▒▓█   ▄ ▒██░█▀  ░▓█▒  ░▒██    ██░ ░ █ █ ▒ 
░░██▒██▓ ░▒████▒░▓█   ▀█▓░▒█░   ░ ████▓▒░▒██▒ ▒██▒
░ ▓░▒ ▒  ░░ ▒░ ░░▒▓███▀▒ ▒ ░    ░ ▒░▒░▒░ ▒▒ ░ ░▓ ░
  ▒ ░ ░   ░ ░  ░▒░▒   ░  ░        ░ ▒ ▒░ ░░    ░▒ ░
    """
    print(Fore.RED + Style.BRIGHT + logo)
    print(f"{Fore.CYAN}    Version : {Fore.WHITE}v11.0 Ultimate (File Save Fixed)")
    print(f"{Fore.CYAN}    System  : {Fore.WHITE}Android / Kali NetHunter\n")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("domain", nargs="?", help="Target Domain")
    parser.add_argument("-scan", action="store_true", help="Start the scan")
    parser.add_argument("-threads", type=int, default=100, help="Number of threads")
    args = parser.parse_args()

    if not args.domain:
        banner()
        type_effect("Usage: python3 test.py <domain> -scan", Fore.YELLOW)
        sys.exit()

    banner()
    
    # --- PATH FIX ---
    # Create absolute path for reports
    base_dir = os.getcwd()
    save_path = os.path.join(base_dir, "reports", args.domain)
    
    if not os.path.exists(save_path): 
        try:
            os.makedirs(save_path)
            print(f"{Fore.GREEN}[+] Created directory: {save_path}")
        except OSError as e:
            print(f"{Fore.RED}[!] Error creating directory: {e}")
            sys.exit()
    else:
        print(f"{Fore.YELLOW}[!] Directory exists: {save_path}")

    type_effect(f"[*] TARGET LOCKED: {args.domain}", Fore.GREEN)
    print("-" * 50)

    loading_bar("Establishing Connection")
    if not live_check.check(args.domain): 
        print(Fore.RED + "Target seems down.")
        sys.exit()

    if args.scan:
        print(Fore.WHITE + "\n--- [ PHASE 1: INTELLIGENCE GATHERING ] ---")
        loading_bar("Geolocating Server")
        ip_info.scan(args.domain, save_path)
        
        loading_bar("Extracting Ownership")
        whois_scan.scan(args.domain, save_path)
        
        loading_bar("Detecting Real IP (CF Bypass)")
        real_ip.scan(args.domain, save_path)
        
        loading_bar("Dumping DNS Zone")
        dns_scan.scan(args.domain, save_path)

        print(Fore.WHITE + "\n--- [ PHASE 2: VULNERABILITY MATRIX ] ---")
        loading_bar("Analyzing SSL/SANs")
        ssl_scan.scan(args.domain, save_path)
        
        loading_bar("Bypassing WAF / Headers")
        waf.scan(args.domain, save_path)
        
        loading_bar("Checking CORS Misconfig")
        cors_scan.scan(args.domain, save_path)
        
        loading_bar("Testing DoS Vulnerability")
        dos_check.scan(args.domain, save_path)
        
        loading_bar("Fingerprinting OS & Tech")
        tech_detect.scan(args.domain, save_path)
        
        loading_bar("Hunting SQL Injection")
        sqli_scan.scan(args.domain, save_path)

        print(Fore.WHITE + "\n--- [ PHASE 3: DEEP RECON ] ---")
        print(Fore.YELLOW + "[*] Enumerating Subdomains...")
        subdomain.enumerate(args.domain, save_path)
        
        print(Fore.YELLOW + f"[*] Scanning Ports (Threads: {args.threads})...")
        # Handle the 3 arguments for portscanner
        portscanner.scan(args.domain, args.threads, save_path) 

        print(Fore.WHITE + "\n--- [ PHASE 4: DATA EXTRACTION ] ---")
        loading_bar("Harvesting Emails")
        email_scan.scan(args.domain, save_path)
        
        loading_bar("Scraping Social Profiles")
        social_scan.scan(args.domain, save_path)
        
        loading_bar("Brute-forcing Admin Panels")
        admin_scan.scan(args.domain, save_path)
        
        loading_bar("Robots.txt Secrets")
        robots.scan(args.domain, save_path)
        sitemap.scan(args.domain, save_path)
        js_scan.scan(args.domain, save_path)

        print(Fore.WHITE + "\n--- [ PHASE 5: VISUAL SURVEILLANCE ] ---")
        loading_bar("Capturing Evidence")
        screenshot.capture(args.domain, save_path)

        type_effect(f"\n[✓] MISSION ACCOMPLISHED.", Fore.GREEN)
        print(f"{Fore.YELLOW}Reports saved in: {save_path}")

if __name__ == "__main__":
    main()
