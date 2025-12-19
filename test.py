import argparse
import os
import sys
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    # Import 11 Modules
    from core.basic import live_check, subdomain, portscanner, screenshot
    from core.basic import ssl_scan, dns_scan, tech_detect, whois_scan, ip_info, waf
    from core.crawl import robots, sitemap, js_scan
except ImportError:
    pass

def banner():
    print(Fore.RED + Style.BRIGHT + r"""
 __      __      ___.   ___________             
/  \    /  \ ____\_ |__ \_   _____/__________  ___ 
\   \/\/   // __ \| __ \ |    __)/  _ \_  __ \/   \
 \        /\  ___/| \_\ \|     \(  <_> )  | \/ /_\ \
  \__/\  /  \___  >___  /\___  / \____/|__| /____  /
       \/       \/    \/     \/                  \/ 
      -- v6.0 Hunter Edition --
    """ + Fore.RESET)
    print(Fore.YELLOW + "      Created By : " + Fore.WHITE + "Lucky")
    print(Fore.YELLOW + "      Features   : " + Fore.WHITE + "11 Modules (All-in-One)\n")

def main():
    banner()
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", help="Target Domain", nargs='?')
    parser.add_argument("-scan", help="Run All 11 Features", action="store_true")
    parser.add_argument("-output", help="Output directory", default="reports")
    parser.add_argument("-threads", help="Threads for port scan", type=int, default=20)
    args = parser.parse_args()

    if not args.domain:
        print(Fore.RED + "[!] Please provide a domain name (e.g., python3 test.py google.com -scan)")
        sys.exit()

    save_path = os.path.join(os.getcwd(), args.output, args.domain)
    if not os.path.exists(save_path): os.makedirs(save_path)

    if args.scan:
        print(Fore.GREEN + f"[*] Starting Full Scan on {args.domain}...\n")

        # 1. Live Check
        if not live_check.check(args.domain): sys.exit()

        # 2. Network & Info
        ip_info.scan(args.domain, save_path)
        whois_scan.scan(args.domain, save_path)
        dns_scan.scan(args.domain, save_path)
        ssl_scan.scan(args.domain, save_path)
        waf.scan(args.domain, save_path)
        tech_detect.scan(args.domain, save_path)

        # 3. Standard Recon
        subdomain.enumerate(args.domain, save_path)
        portscanner.scan(args.domain, args.threads, save_path)

        # 4. Crawling
        robots.scan(args.domain, save_path)
        sitemap.scan(args.domain, save_path)
        js_scan.scan(args.domain, save_path)

        # 5. Visuals
        screenshot.capture(args.domain, save_path)

        print(Fore.GREEN + f"\n[✓] Scan Completed. Results saved in: {save_path}")

    else:
        print(Fore.YELLOW + "[!] Usage: python3 test.py <domain> -scan")

if __name__ == "__main__":
    main()

