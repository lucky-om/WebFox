#!/usr/bin/env python3
"""
WebFox v4.0 — Automated Web Reconnaissance Framework
Parallel execution engine with stealth support and Termux compatibility.

Author  : Lucky
Project : WebFox Recon Framework v4.0
License : MIT
"""
import argparse
import os
import sys
import time
import concurrent.futures
from colorama import init, Fore, Style
import warnings
warnings.filterwarnings("ignore")  # Suppress SSL warnings globally

init(autoreset=True)
sys.path.append(os.path.dirname(__file__))

# ── Core modules ──────────────────────────────────────────────────────────────
from core.basic import (
    live_check, subdomain, portscanner, screenshot, dos_check,
    ssl_scan, dns_scan, tech_detect, whois_scan, ip_info, waf, headers_scan, takeover
)
from core.crawl import robots, sitemap, js_scan, dir_scan, email_harvest
from core.report_gen import generate as generate_html_report
from core.stealth import is_termux


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def loading_effect(task_name, status="RUNNING"):
    if status == "RUNNING":
        sys.stdout.write(f"{Fore.CYAN}[*] {task_name:<30} ")
        sys.stdout.flush()
        chars = ["|", "/", "-", "\\"]
        for i in range(12):
            time.sleep(0.04)
            sys.stdout.write(f"\b{chars[i % 4]}")
            sys.stdout.flush()
        sys.stdout.write(f"\b{Fore.GREEN}[DONE]{Fore.RESET}\n")
    elif status == "SKIP":
        print(f"{Fore.YELLOW}[~] {task_name:<30} [SKIPPED]")
    elif status == "FAIL":
        print(f"{Fore.RED}[-] {task_name:<30} [FAILED]")


def banner():
    clear()
    is_mobile = is_termux()
    platform_str = "Termux (Android)" if is_mobile else "Linux / Kali"

    print(Fore.RED + Style.BRIGHT + r"""
░██╗░░░░░░░██╗███████╗██████╗░███████╗░█████╗░██╗░░██╗
░██║░░██╗░░██║██╔════╝██╔══██╗██╔════╝██╔══██╗╚██╗██╔╝
░╚██╗████╗██╔╝█████╗░░██████╦╝█████╗░░██║░░██║░╚███╔╝░
░░████╔═████║░██╔══╝░░██╔══██╗██╔══╝░░██║░░██║░██╔██╗░
░░╚██╔╝░╚██╔╝░███████╗██████╦╝██║░░░░░╚█████╔╝██╔╝╚██╗
░░░╚═╝░░░╚═╝░░╚══════╝╚═════╝░╚═╝░░░░░░╚════╝░╚═╝░░╚═╝
    """ + Fore.RESET)
    print(f"{Fore.CYAN}    Version    : {Fore.WHITE}v4.0")
    print(f"{Fore.CYAN}    Framework  : {Fore.WHITE}WebFox Recon Suite")
    print(f"{Fore.CYAN}    Platform   : {Fore.WHITE}{platform_str}")
    print(f"{Fore.CYAN}    Modules    : {Fore.WHITE}17 Recon Modules")
    print(f"{Fore.CYAN}    Mode       : {Fore.WHITE}Stealth + Parallel Execution\n")


def help_menu():
    banner()
    print(Fore.YELLOW + " [ COMMAND CENTER ]")
    print(Fore.WHITE + " " + "-" * 60)
    print(f" {Fore.GREEN}python3 test.py <domain> -scan         {Fore.WHITE}| Full Recon (17 Modules)")
    print(f" {Fore.GREEN}python3 test.py <domain> -scan -fast   {Fore.WHITE}| Fast mode (skip slow modules)")
    print(f" {Fore.GREEN}python3 test.py -help                  {Fore.WHITE}| Show this menu")
    print(f"\n {Fore.YELLOW}[ EXAMPLES ]")
    print(f" {Fore.WHITE}  python3 test.py example.com -scan")
    print(f" {Fore.WHITE}  python3 test.py hackerone.com -scan -fast")
    print(f"\n {Fore.YELLOW}[ MODULES ]")
    modules = [
        ("IP Geolocation & ASN",       "Dual-API IP lookup with CDN detection"),
        ("WHOIS Intelligence",          "Domain age, expiry, privacy, contacts"),
        ("DNS Enumeration",             "11 record types, zone transfer, wildcard"),
        ("SSL/TLS Audit",               "Cert details, weak protocols, CT logs"),
        ("WAF/CDN Fingerprint",         "25+ WAF/CDN/server signatures"),
        ("HTTP Security Headers",       "HSTS, CSP, CORS, X-Frame-Options audit"),
        ("Tech Stack Detection",        "CMS, JS frameworks, cookies, headers"),
        ("Port Scanner",               "55 ports with banner grabbing + risk levels"),
        ("Subdomain Enum",              "7 OSINT sources + DNS bruteforce"),
        ("Subdomain Takeover",          "25 vulnerable service fingerprints"),
        ("Directory Scanner",          "55 sensitive paths — stealthy HEAD requests"),
        ("JS & Secret Hunter",          "30+ secret patterns, endpoints, source maps"),
        ("Email / Social Intel",        "Emails, phones, 8 social platforms"),
        ("Robots.txt",                  "Hidden disallowed paths"),
        ("Sitemap",                     "URL discovery from sitemap"),
        ("DoS Resistance Check",        "Slowloris-style response test"),
        ("Screenshots",                 "Visual capture of key pages (Linux only)"),
    ]
    for name, desc in modules:
        print(f"   {Fore.CYAN}{name:<30}{Fore.WHITE}  {desc}")
    sys.exit()


def run_safe(func, *args):
    """Safely execute a module. Returns True on success, False on failure."""
    try:
        func(*args)
        return True
    except Exception as e:
        print(Fore.RED + f"  [-] Module error in {func.__module__}: {e}")
        return False


def main():
    if "-help" in sys.argv or "--help" in sys.argv:
        help_menu()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("domain", nargs="?", help="Target domain")
    parser.add_argument("-scan",    action="store_true")
    parser.add_argument("-fast",    action="store_true", help="Skip slow modules (screenshots, dir scan)")
    parser.add_argument("-threads", type=int, default=100)
    args = parser.parse_args()

    if not args.domain:
        help_menu()

    banner()

    # Sanitize domain input
    domain = args.domain.replace("https://", "").replace("http://", "").rstrip("/").split("/")[0]

    save_path = os.path.join(os.getcwd(), "reports", domain)
    os.makedirs(save_path, exist_ok=True)

    print(Fore.GREEN + f"[✓] TARGET  : {domain}")
    print(Fore.GREEN + f"[✓] REPORTS : {save_path}")
    print(Fore.GREEN + f"[✓] MODE    : {'Fast (reduced modules)' if args.fast else 'Full Recon'}")
    if is_termux():
        print(Fore.YELLOW + "[~] Termux detected — Screenshots disabled, headless browser skipped.")
    print()

    # ── Phase 0: Live Check ────────────────────────────────────────────────────
    loading_effect("Checking Host Status")
    if not live_check.check(domain):
        print(Fore.RED + f"  [-] {domain} is DOWN or unreachable. Aborting.")
        sys.exit(1)

    if args.scan:
        scan_start = time.time()

        # ── Phase 1: PASSIVE (Safe) — All run in parallel ─────────────────────
        print(Fore.WHITE + Style.BRIGHT + "\n[+] PHASE 1: PASSIVE INTELLIGENCE (Parallel)\n" + "-" * 50)

        passive_tasks = {
            "IP Geolocation":      (ip_info.scan,      domain, save_path),
            "WHOIS Lookup":        (whois_scan.scan,   domain, save_path),
            "DNS Enumeration":     (dns_scan.scan,     domain, save_path),
            "SSL/TLS Audit":       (ssl_scan.scan,     domain, save_path),
            "Subdomain Hunt":      (subdomain.enumerate, domain, save_path),
            "Email Harvesting":    (email_harvest.scan, domain, save_path),
        }

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            future_map = {
                executor.submit(run_safe, fn, *fn_args): name
                for name, (fn, *fn_args) in passive_tasks.items()
            }
            for future in concurrent.futures.as_completed(future_map):
                name = future_map[future]
                ok = future.result()
                loading_effect(name, "RUNNING" if ok else "FAIL")

        # ── Phase 2: ACTIVE (Stealthy HTTP) ───────────────────────────────────
        print(Fore.WHITE + Style.BRIGHT + "\n[+] PHASE 2: ACTIVE WEB ANALYSIS\n" + "-" * 50)

        active_tasks = {
            "WAF/CDN Fingerprint":     (waf.scan,          domain, save_path),
            "HTTP Headers Audit":      (headers_scan.scan, domain, save_path),
            "Tech Stack Detection":    (tech_detect.scan,  domain, save_path),
            "Robots.txt":              (robots.scan,       domain, save_path),
            "Sitemap Discovery":       (sitemap.scan,      domain, save_path),
            "JS & Secret Analysis":    (js_scan.scan,      domain, save_path),
            "DoS Resistance":          (dos_check.scan,    domain, save_path),
        }

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_map = {
                executor.submit(run_safe, fn, *fn_args): name
                for name, (fn, *fn_args) in active_tasks.items()
            }
            for future in concurrent.futures.as_completed(future_map):
                name = future_map[future]
                ok = future.result()
                loading_effect(name, "RUNNING" if ok else "FAIL")

        # ── Phase 3: DEEP — Port scan + Post-subdomain modules ────────────────
        print(Fore.WHITE + Style.BRIGHT + "\n[+] PHASE 3: DEEP INTELLIGENCE\n" + "-" * 50)

        loading_effect("Port Scanner")
        run_safe(portscanner.scan, domain, args.threads, save_path)

        loading_effect("Subdomain Takeover Check")
        run_safe(takeover.scan, domain, save_path)

        if not args.fast:
            loading_effect("Directory/File Scanner")
            run_safe(dir_scan.scan, domain, save_path)

            # ── Phase 4: VISUAL ───────────────────────────────────────────────
            print(Fore.WHITE + Style.BRIGHT + "\n[+] PHASE 4: VISUAL SURVEILLANCE\n" + "-" * 50)
            loading_effect("Screenshot Capture")
            run_safe(screenshot.capture, domain, save_path)
        else:
            loading_effect("Directory Scan", "SKIP")
            loading_effect("Screenshots", "SKIP")

        # ── Phase 5: REPORT ───────────────────────────────────────────────────
        elapsed = time.time() - scan_start
        print(Fore.WHITE + Style.BRIGHT + "\n[+] PHASE 5: GENERATING REPORT\n" + "-" * 50)
        loading_effect("HTML Report Generator")
        report_path = generate_html_report(domain, save_path)

        # ── Final Summary ──────────────────────────────────────────────────────
        print(Fore.GREEN + Style.BRIGHT + "\n" + "=" * 60)
        print(Fore.GREEN + f"  [✓] SCAN COMPLETE IN {elapsed:.1f}s")
        print(Fore.GREEN + f"  [✓] Report Directory : {save_path}")
        print(Fore.GREEN + f"  [✓] HTML Report      : {report_path}")
        print(Fore.CYAN  + f"  [★] WebFox v4.0 by Lucky")
        print(Fore.GREEN + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
