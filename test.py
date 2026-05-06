import argparse
import os
import sys
import time
from colorama import init, Fore, Style

init(autoreset=True)

# Ensure core packages are importable from any working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.basic import live_check, subdomain, portscanner, screenshot, dos_check
from core.basic import ssl_scan, dns_scan, tech_detect, whois_scan, ip_info, waf
from core.crawl  import robots, sitemap, js_scan

VERSION  = "v4.0.0"
AUTHOR   = "Lucky"

# ── Helpers ────────────────────────────────────────────────────────────────

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def loading_effect(task_name):
    label = task_name[:44]
    sys.stdout.write(f"{Fore.CYAN}[*] {label:<46} ")
    sys.stdout.flush()
    chars = ["|", "/", "-", "\\"]
    for i in range(12):
        time.sleep(0.04)
        sys.stdout.write(f"\b{chars[i % 4]}")
        sys.stdout.flush()
    sys.stdout.write(f"\b{Fore.GREEN}[DONE]{Fore.RESET}\n")
    sys.stdout.flush()


def banner():
    clear()
    print(Fore.RED + Style.BRIGHT + r"""
░██╗░░░░░░░██╗███████╗██████╗░███████╗░█████╗░██╗░░██╗
░██║░░██╗░░██║██╔════╝██╔══██╗██╔════╝██╔══██╗╚██╗██╔╝
░╚██╗████╗██╔╝█████╗░░██████╦╝█████╗░░██║░░██║░╚███╔╝░
░░████╔═████║░██╔══╝░░██╔══██╗██╔══╝░░██║░░██║░██╔██╗░
░░╚██╔╝░╚██╔╝░███████╗██████╦╝██║░░░░░╚█████╔╝██╔╝╚██╗
░░░╚═╝░░░╚═╝░░╚══════╝╚═════╝░╚═╝░░░░░░╚════╝░╚═╝░░╚═╝
    """ + Fore.RESET)
    print(f"{Fore.CYAN}    Version     : {Fore.WHITE}{VERSION}")
    print(f"{Fore.CYAN}    Coded By     : {Fore.WHITE}{AUTHOR}")
    print(f"{Fore.CYAN}    Mode        : {Fore.WHITE}Advanced Multi-Target Recon Engine\n")


def help_menu():
    banner()
    print(Fore.YELLOW + " [ COMMAND CENTER ]")
    print(Fore.WHITE  + " " + "─" * 58)
    print(f" {Fore.GREEN}python test.py <domain> -scan               {Fore.WHITE}|  Full scan (domain + subdomains)")
    print(f" {Fore.GREEN}python test.py <domain> -scan -domain-only  {Fore.WHITE}|  Domain ONLY scan")
    print(f" {Fore.GREEN}python test.py <domain> -scan -subs-only    {Fore.WHITE}|  Subdomains ONLY scan")
    print(f" {Fore.GREEN}python test.py <domain> -scan -both         {Fore.WHITE}|  Both (explicit)")
    print(f" {Fore.GREEN}python test.py -help                        {Fore.WHITE}|  Show this menu")
    print(f"\n {Fore.YELLOW} [ OPTIONS ]")
    print(f" {Fore.WHITE}  -threads <N>   Port scan threads (default: 100)")
    print(f"\n {Fore.YELLOW} [ EXAMPLES ]")
    print(f" {Fore.WHITE}  python test.py example.com -scan")
    print(f" {Fore.WHITE}  python test.py example.com -scan -domain-only")
    print(f" {Fore.WHITE}  python test.py example.com -scan -subs-only -threads 50")
    print(f"\n {Fore.CYAN}  Coded by {AUTHOR} | WebFox {VERSION}")
    sys.exit(0)


# ── Core scan runners ──────────────────────────────────────────────────────

def run_domain_scan(domain, save_path, threads):
    """Run all recon modules on a single target (domain or subdomain)."""
    print(Fore.WHITE + Style.BRIGHT + "\n[+] NETWORK INTELLIGENCE")
    print(Fore.WHITE + "─" * 48)

    loading_effect("Geolocation & ASN")
    try:
        ip_info.scan(domain, save_path)
    except Exception as e:
        print(Fore.RED + f"  [-] IP scan error: {e}")

    loading_effect("WHOIS + RDAP")
    try:
        whois_scan.scan(domain, save_path)
    except Exception as e:
        print(Fore.RED + f"  [-] WHOIS error: {e}")

    loading_effect("DNS Enumeration")
    try:
        dns_scan.scan(domain, save_path)
    except Exception as e:
        print(Fore.RED + f"  [-] DNS error: {e}")

    print(Fore.WHITE + Style.BRIGHT + "\n[+] SECURITY MATRIX")
    print(Fore.WHITE + "─" * 48)

    loading_effect("SSL/TLS Inspection")
    try:
        ssl_scan.scan(domain, save_path)
    except Exception as e:
        print(Fore.RED + f"  [-] SSL error: {e}")

    loading_effect("DoS / Rate-Limit Check")
    try:
        dos_check.scan(domain, save_path)
    except Exception as e:
        print(Fore.RED + f"  [-] DoS check error: {e}")

    loading_effect("WAF & Security Headers")
    try:
        waf.scan(domain, save_path)
    except Exception as e:
        print(Fore.RED + f"  [-] WAF error: {e}")

    loading_effect("Technology Fingerprint")
    try:
        tech_detect.scan(domain, save_path)
    except Exception as e:
        print(Fore.RED + f"  [-] Tech detect error: {e}")

    print(Fore.WHITE + Style.BRIGHT + "\n[+] PORT SCAN")
    print(Fore.WHITE + "─" * 48)
    try:
        portscanner.scan(domain, threads, save_path)
    except Exception as e:
        print(Fore.RED + f"  [-] Port scan error: {e}")

    print(Fore.WHITE + Style.BRIGHT + "\n[+] WEB CRAWLER")
    print(Fore.WHITE + "─" * 48)

    loading_effect("Robots.txt Analysis")
    try:
        robots.scan(domain, save_path)
    except Exception as e:
        print(Fore.RED + f"  [-] Robots error: {e}")

    loading_effect("Sitemap Discovery")
    try:
        sitemap.scan(domain, save_path)
    except Exception as e:
        print(Fore.RED + f"  [-] Sitemap error: {e}")

    loading_effect("JS Intelligence")
    try:
        js_scan.scan(domain, save_path)
    except Exception as e:
        print(Fore.RED + f"  [-] JS scan error: {e}")

    print(Fore.WHITE + Style.BRIGHT + "\n[+] VISUAL SURVEILLANCE")
    print(Fore.WHITE + "─" * 48)
    try:
        screenshot.capture(domain, save_path)
    except Exception as e:
        print(Fore.RED + f"  [-] Screenshot error: {e}")


def run_subdomain_recon(domain, base_save_path, threads):
    """Enumerate subdomains then run full recon on each live one."""
    print(Fore.WHITE + Style.BRIGHT + "\n[+] SUBDOMAIN ENUMERATION")
    print(Fore.WHITE + "─" * 48)
    print(Fore.YELLOW + "[*] Querying crt.sh / HackerTarget / AlienVault / RapidDNS ...")

    try:
        subdomain.enumerate(domain, base_save_path)
    except Exception as e:
        print(Fore.RED + f"[-] Subdomain enumeration error: {e}")
        return

    live_subs_file = os.path.join(base_save_path, "subdomains_live.txt")
    if not os.path.exists(live_subs_file):
        print(Fore.YELLOW + "[!] No live subdomain file produced — skipping deep recon.")
        return

    with open(live_subs_file, encoding="utf-8") as f:
        live_subs = [line.strip() for line in f if line.strip()]

    if not live_subs:
        print(Fore.YELLOW + "[!] No live subdomains found — skipping deep recon.")
        return

    print(Fore.MAGENTA + Style.BRIGHT + f"\n[+] SUBDOMAIN DEEP RECON — {len(live_subs)} live targets")
    print(Fore.WHITE + "─" * 48)

    sub_base = os.path.join(base_save_path, "subdomains")
    os.makedirs(sub_base, exist_ok=True)

    for idx, sub in enumerate(live_subs, 1):
        sub_path = os.path.join(sub_base, sub)
        os.makedirs(sub_path, exist_ok=True)
        print(Fore.CYAN + f"\n  [{idx}/{len(live_subs)}] ── Target: {sub}")

        modules = [
            ("IP/Geo",      ip_info.scan,       (sub, sub_path)),
            ("SSL/TLS",     ssl_scan.scan,       (sub, sub_path)),
            ("DNS",         dns_scan.scan,       (sub, sub_path)),
            ("WAF/Headers", waf.scan,            (sub, sub_path)),
            ("Tech Stack",  tech_detect.scan,    (sub, sub_path)),
            ("Port Scan",   portscanner.scan,    (sub, threads, sub_path)),
            ("Robots.txt",  robots.scan,         (sub, sub_path)),
            ("Sitemap",     sitemap.scan,        (sub, sub_path)),
            ("JS Analysis", js_scan.scan,        (sub, sub_path)),
            ("Screenshot",  screenshot.capture,  (sub, sub_path)),
        ]

        for name, fn, args in modules:
            try:
                loading_effect(f"  {name} ({sub[:24]})")
                fn(*args)
            except Exception as e:
                print(Fore.RED + f"  [-] {name} failed: {e}")

    print(Fore.GREEN + Style.BRIGHT + f"\n[✓] SUBDOMAIN RECON COMPLETE — {len(live_subs)} targets processed.")
    print(Fore.GREEN + f"[✓] Results saved to: {sub_base}")


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    if "-help" in sys.argv or "--help" in sys.argv:
        help_menu()

    parser = argparse.ArgumentParser(
        prog="webfox",
        add_help=False,
        description=f"WebFox {VERSION} — Advanced Recon Framework by {AUTHOR}"
    )
    parser.add_argument("domain",       nargs="?",           help="Target domain (e.g. example.com)")
    parser.add_argument("-scan",        action="store_true", help="Activate scanning")
    # NOTE: flags use unique dest names to avoid collision with positional 'domain'
    parser.add_argument("-domain-only", dest="domain_only",  action="store_true", help="Scan root domain only")
    parser.add_argument("-subs-only",   dest="subs_only",    action="store_true", help="Scan subdomains only")
    parser.add_argument("-both",        dest="both",         action="store_true", help="Scan domain + subdomains")
    parser.add_argument("-threads",     type=int, default=100)

    args = parser.parse_args()

    if not args.domain:
        help_menu()

    banner()

    # ── Determine scan mode ────────────────────────────────────────────────
    if args.domain_only and not args.subs_only:
        scan_domain, scan_subs = True, False
        mode_label = "DOMAIN ONLY"
    elif args.subs_only and not args.domain_only:
        scan_domain, scan_subs = False, True
        mode_label = "SUBDOMAINS ONLY"
    else:
        # -both, or both flags together, or neither flag = default full scan
        scan_domain, scan_subs = True, True
        mode_label = "FULL (DOMAIN + SUBDOMAINS)"

    target    = args.domain
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", target)
    os.makedirs(save_path, exist_ok=True)

    print(Fore.GREEN + f"[*] TARGET        : {target}")
    print(Fore.GREEN + f"[*] SCAN MODE     : {mode_label}")
    print(Fore.GREEN + f"[*] THREADS       : {args.threads}")
    print(Fore.GREEN + f"[*] REPORT PATH   : {save_path}\n")

    # ── Host liveness check ────────────────────────────────────────────────
    loading_effect("Host Liveness Check")
    if not live_check.check(target):
        print(Fore.RED + "[-] Target is unreachable. Check the domain and try again.")
        sys.exit(1)

    if not args.scan:
        print(Fore.YELLOW + "[!] No -scan flag provided. Use -help for usage.")
        sys.exit(0)

    # ── Execute phases ─────────────────────────────────────────────────────
    sep = "=" * 55

    if scan_domain:
        print(Fore.CYAN + Style.BRIGHT + f"\n{sep}")
        print(Fore.CYAN + Style.BRIGHT + f"  PHASE 1 — DOMAIN RECON: {target}")
        print(Fore.CYAN + Style.BRIGHT + sep)
        run_domain_scan(target, save_path, args.threads)

    if scan_subs:
        print(Fore.CYAN + Style.BRIGHT + f"\n{sep}")
        print(Fore.CYAN + Style.BRIGHT + f"  PHASE 2 — SUBDOMAIN RECON: {target}")
        print(Fore.CYAN + Style.BRIGHT + sep)
        run_subdomain_recon(target, save_path, args.threads)

    print(Fore.GREEN + Style.BRIGHT + f"\n{sep}")
    print(Fore.GREEN + Style.BRIGHT +  "  [✓] MISSION ACCOMPLISHED — ALL PHASES COMPLETE")
    print(Fore.GREEN + Style.BRIGHT + sep)
    print(Fore.GREEN + f"  Report  : {save_path}")
    print(Fore.GREEN + f"  Version : WebFox {VERSION} | Coded by {AUTHOR}")


if __name__ == "__main__":
    main()
