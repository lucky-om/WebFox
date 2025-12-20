import argparse
import os
import sys
import time
import random
from colorama import init, Fore, Style
from tqdm import tqdm

init(autoreset=True)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.basic import live_check, subdomain, portscanner, screenshot
    from core.basic import ssl_scan, dns_scan, tech_detect, whois_scan, ip_info, waf
    from core.crawl import robots, sitemap, js_scan
except ImportError:
    pass

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_effect(task_name):
    # Simulates a "Hacker" loading bar
    sys.stdout.write(f"{Fore.CYAN}[*] {task_name:<20} ")
    sys.stdout.flush()
    chars = ["|", "/", "-", "\\"]
    for i in range(15):
        time.sleep(0.05)
        sys.stdout.write(f"\b{chars[i % 4]}")
        sys.stdout.flush()
    sys.stdout.write(f"\b{Fore.GREEN}[DONE]{Fore.RESET}\n")

def banner():
    clear()
    print(Fore.RED + Style.BRIGHT + r"""
 █     █░▓█████  ▄▄▄▄    █████▒▒█████  ▒██   ██▒
▓█░ █ ░█░▓█   ▀ ▓█████▄▓██   ▒▒██▒  ██▒▒▒ █ █ ▒░
▒█░ █ ░█░▒███   ▒██▒ ▄██▒████ ░▒██░  ██▒░░  █   ░
░█░ █ ░█░▒▓█  ▄ ▒██░█▀  ░▓█▒  ░▒██   ██░ ░ █ █ ▒ 
░░██▒██▓ ░▒████▒░▓█  ▀█▓░▒█░   ░ ████▓▒░▒██▒ ▒██▒
░ ▓░▒ ▒  ░░ ▒░ ░░▒▓███▀▒ ▒ ░   ░ ▒░▒░▒░ ▒▒ ░ ░▓ ░
  ▒ ░ ░   ░ ░  ░▒░▒   ░  ░       ░ ▒ ▒░ ░░   ░▒ ░
    ░       ░    ░    ░          ░ ░ ░   ░    ░  
               ░                     ░           
    """ + Fore.RESET)
    print(f"{Fore.CYAN}    Version   : {Fore.WHITE}v10.0 (Ultimate Edition)")
    print(f"{Fore.CYAN}    Dev       : {Fore.WHITE}Lucky")
    print(f"{Fore.CYAN}    System    : {Fore.WHITE}Kali Linux (x64) - No Limit Mode\n")

def help_menu():
    banner()
    print(Fore.YELLOW + " [ COMMAND CENTER ]")
    print(Fore.WHITE + " ------------------------------------------------")
    print(f" {Fore.GREEN}python3 test.py <domain> -scan   {Fore.WHITE}|  Full Recon (12 Modules)")
    print(f" {Fore.GREEN}python3 test.py -help            {Fore.WHITE}|  Show Help Menu")
    print(f"\n {Fore.YELLOW} [ EXAMPLES ]")
    print(f" {Fore.WHITE} python3 test.py google.com -scan")
    sys.exit()

def main():
    if "-help" in sys.argv: help_menu()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("domain", nargs="?", help="Target")
    parser.add_argument("-scan", action="store_true")
    parser.add_argument("-threads", type=int, default=100)
    args = parser.parse_args()

    if not args.domain: help_menu()

    banner()
    save_path = os.path.join(os.getcwd(), "reports", args.domain)
    if not os.path.exists(save_path): os.makedirs(save_path)

    print(Fore.GREEN + f"[*] TARGET LOCKED: {args.domain}")
    print(Fore.GREEN + f"[*] DATA STORAGE : {save_path}\n")

    # 1. Live Check
    loading_effect("Checking Host")
    if not live_check.check(args.domain): sys.exit()

    if args.scan:
        print(Fore.WHITE + "\n--- [ NETWORK INTELLIGENCE ] ---")
        loading_effect("Geolocation")
        ip_info.scan(args.domain, save_path)
        
        loading_effect("Whois Database")
        whois_scan.scan(args.domain, save_path)
        
        loading_effect("DNS Enumeration")
        dns_scan.scan(args.domain, save_path)

        print(Fore.WHITE + "\n--- [ SECURITY MATRIX ] ---")
        loading_effect("SSL Verification")
        ssl_scan.scan(args.domain, save_path)
        
        loading_effect("Firewall (WAF)")
        waf.scan(args.domain, save_path)
        
        loading_effect("Tech Stack")
        tech_detect.scan(args.domain, save_path)

        print(Fore.WHITE + "\n--- [ DEEP RECONNAISSANCE ] ---")
        # Subdomain - Infinite Wait
        print(Fore.YELLOW + "[*] Fetching Subdomains (Infinite Wait Mode)...")
        subdomain.enumerate(args.domain, save_path)
        
        # Ports - 100 Threads
        print(Fore.YELLOW + f"[*] Scanning Ports (Threads: {args.threads})...")
        portscanner.scan(args.domain, args.threads, save_path)

        print(Fore.WHITE + "\n--- [ WEB CRAWLER ] ---")
        loading_effect("Robots.txt")
        robots.scan(args.domain, save_path)
        sitemap.scan(args.domain, save_path)
        
        loading_effect("JS Analysis")
        js_scan.scan(args.domain, save_path)

        print(Fore.WHITE + "\n--- [ VISUAL SURVEILLANCE ] ---")
        print(Fore.YELLOW + "[*] Taking Full-Res Screenshots (Please Wait)...")
        screenshot.capture(args.domain, save_path)

        print(Fore.GREEN + Style.BRIGHT + f"\n[✓] MISSION ACCOMPLISHED. REPORT GENERATED.")

if __name__ == "__main__":
    main()

