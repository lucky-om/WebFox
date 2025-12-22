import argparse
import os
import sys
import time
import random
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# --- MODULE IMPORTS ---
from core.basic import live_check, subdomain, portscanner, screenshot
from core.basic import ssl_scan, dns_scan, tech_detect, whois_scan, ip_info, waf
from core.crawl import robots, sitemap, js_scan, email_scan

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def type_effect(text, color=Fore.GREEN):
    for char in text:
        sys.stdout.write(color + char)
        sys.stdout.flush()
        time.sleep(0.01)
    print("")

def loading_bar(task):
    sys.stdout.write(f"{Fore.CYAN}[*] {task:<25} ")
    sys.stdout.flush()
    # Shorter animation to not waste time
    for i in range(5):
        time.sleep(0.05)
        sys.stdout.write(Fore.GREEN + "█")
        sys.stdout.flush()
    print(Fore.GREEN + " [PROCESSING]")

def banner():
    clear()
    logo = r"""
 █     █░▓█████  ▄▄▄▄    █████▒▒█████  ▒██   ██▒
▓█░ █ ░█░▓█   ▀ ▓█████▄▓██   ▒▒██▒  ██▒▒▒ █ █ ▒░
▒█░ █ ░█░▒███   ▒██▒ ▄██▒████ ░▒██░  ██▒░░  █   ░
░█░ █ ░█░▒▓█  ▄ ▒██░█▀  ░▓█▒  ░▒██   ██░ ░ █ █ ▒ 
░░██▒██▓ ░▒████▒░▓█  ▀█▓░▒█░   ░ ████▓▒░▒██▒ ▒██▒
░ ▓░▒ ▒  ░░ ▒░ ░░▒▓███▀▒ ▒ ░   ░ ▒░▒░▒░ ▒▒ ░ ░▓ ░
  ▒ ░ ░   ░ ░  ░▒░▒   ░  ░       ░ ▒ ▒░ ░░   ░▒ ░
    """
    print(Fore.RED + Style.BRIGHT + logo)
    print(f"{Fore.CYAN}    Version : {Fore.WHITE}v10.0 (NO LIMITS)")
    print(f"{Fore.CYAN}    Mode    : {Fore.WHITE}Infinite Timeout\n")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("domain", nargs="?", help="Target Domain")
    parser.add_argument("-scan", action="store_true")
    parser.add_argument("-threads", type=int, default=100)
    args = parser.parse_args()

    if not args.domain:
        banner()
        type_effect("Usage: python3 test.py <domain> -scan", Fore.YELLOW)
        sys.exit()

    banner()
    save_path = os.path.join(os.getcwd(), "reports", args.domain)
    if not os.path.exists(save_path): os.makedirs(save_path)

    type_effect(f"[*] TARGET LOCKED: {args.domain}", Fore.GREEN)
    print("-" * 50)

    loading_bar("Establishing Connection")
    if not live_check.check(args.domain): sys.exit()

    if args.scan:
        print(Fore.WHITE + "\n--- [ PHASE 1: INTELLIGENCE GATHERING ] ---")
        loading_bar("Geolocating Server")
        ip_info.scan(args.domain, save_path)
        
        loading_bar("Extracting Ownership")
        whois_scan.scan(args.domain, save_path)
        
        loading_bar("Dumping DNS Zone")
        dns_scan.scan(args.domain, save_path)

        print(Fore.WHITE + "\n--- [ PHASE 2: VULNERABILITY MATRIX ] ---")
        loading_bar("Analyzing SSL/SANs")
        ssl_scan.scan(args.domain, save_path)
        
        loading_bar("Bypassing WAF / Headers")
        waf.scan(args.domain, save_path)
        
        loading_bar("Fingerprinting Tech")
        tech_detect.scan(args.domain, save_path)

        print(Fore.WHITE + "\n--- [ PHASE 3: DEEP RECON ] ---")
        print(Fore.YELLOW + "[*] Enumerating Subdomains...")
        subdomain.enumerate(args.domain, save_path)
        
        print(Fore.YELLOW + f"[*] Scanning Ports (Threads: {args.threads})...")
        portscanner.scan(args.domain, args.threads, save_path)

        print(Fore.WHITE + "\n--- [ PHASE 4: DATA EXTRACTION ] ---")
        loading_bar("Harvesting Emails")
        email_scan.scan(args.domain, save_path)
        
        loading_bar("Robots.txt Secrets")
        robots.scan(args.domain, save_path)
        sitemap.scan(args.domain, save_path)
        js_scan.scan(args.domain, save_path)

        print(Fore.WHITE + "\n--- [ PHASE 5: VISUAL SURVEILLANCE ] ---")
        print(Fore.YELLOW + "[*] Capturing Evidence ...")
        screenshot.capture(args.domain, save_path)

        type_effect("\n[✓] MISSION ACCOMPLISHED. REPORT GENERATED.", Fore.GREEN)

if __name__ == "__main__":
    main()
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
