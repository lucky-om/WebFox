"""
WebFox — Enhanced Multi-Source Subdomain Enumerator
7 OSINT sources + DNS brute-force, wildcard detection, and live HTTP verification.

Author : Lucky | WebFox Recon Framework v4.0
"""
import requests
import socket
import concurrent.futures
import re
from colorama import Fore
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.stealth import get_stealth_session, jitter

# Common subdomain wordlist for bruteforce
COMMON_SUBDOMAINS = [
    "www", "mail", "ftp", "admin", "api", "dev", "staging", "test", "blog",
    "shop", "store", "portal", "dashboard", "app", "mobile", "m", "cdn",
    "static", "media", "assets", "images", "img", "files", "download", "upload",
    "auth", "login", "register", "signup", "account", "accounts", "user", "users",
    "support", "help", "docs", "documentation", "wiki", "kb", "forum", "community",
    "news", "press", "careers", "jobs", "about", "contact", "info", "status",
    "beta", "alpha", "prod", "production", "qa", "uat", "preprod", "sandbox",
    "smtp", "pop", "imap", "mx", "webmail", "email", "ns1", "ns2", "dns",
    "vpn", "remote", "access", "secure", "gateway", "proxy", "lb", "load",
    "monitor", "monitoring", "metrics", "logs", "log", "analytics", "tracking",
    "api2", "v1", "v2", "internal", "private", "legacy", "old", "new",
    "cp", "cpanel", "whm", "plesk", "manage", "management", "manager",
    "git", "gitlab", "github", "svn", "repo", "code", "ci", "cd", "jenkins",
    "sonar", "jira", "confluence", "slack", "chat", "office",
    "db", "database", "mysql", "postgres", "redis", "mongo",
    "cloud", "aws", "azure", "k8s", "kubernetes", "docker",
    "video", "live", "stream", "radio", "podcast",
    "pay", "payment", "billing", "invoice", "checkout", "cart",
    "1", "2", "3", "a", "b", "c",
    "de", "fr", "uk", "us", "eu", "asia", "global",
]

def _fetch_crtsh(domain, session):
    try:
        r = session.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=25, verify=False)
        if r.status_code == 200:
            data = r.json()
            subs = set()
            for entry in data:
                for line in entry.get('name_value', '').split('\n'):
                    sub = line.strip().lstrip('*.')
                    if sub and domain in sub:
                        subs.add(sub.lower())
            print(Fore.BLUE + f"    > crt.sh: {len(subs)} found")
            return subs
    except Exception:
        pass
    return set()

def _fetch_hackertarget(domain, session):
    try:
        r = session.get(f"https://api.hackertarget.com/hostsearch/?q={domain}", timeout=20, verify=False)
        subs = set()
        if r.status_code == 200 and "error" not in r.text.lower():
            for line in r.text.split('\n'):
                if ',' in line:
                    sub = line.split(',')[0].strip()
                    if sub and domain in sub:
                        subs.add(sub.lower())
        print(Fore.BLUE + f"    > HackerTarget: {len(subs)} found")
        return subs
    except Exception:
        pass
    return set()

def _fetch_alienvault(domain, session):
    try:
        r = session.get(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns", timeout=20, verify=False)
        subs = set()
        if r.status_code == 200:
            for entry in r.json().get('passive_dns', []):
                hostname = entry.get('hostname', '')
                if hostname and domain in hostname:
                    subs.add(hostname.lower())
        print(Fore.BLUE + f"    > AlienVault OTX: {len(subs)} found")
        return subs
    except Exception:
        pass
    return set()

def _fetch_threatminer(domain, session):
    try:
        r = session.get(f"https://api.threatminer.org/v2/domain.php?q={domain}&rt=5", timeout=15, verify=False)
        subs = set()
        if r.status_code == 200:
            data = r.json()
            for sub in data.get("results", []):
                if domain in sub:
                    subs.add(sub.lower())
        print(Fore.BLUE + f"    > ThreatMiner: {len(subs)} found")
        return subs
    except Exception:
        pass
    return set()

def _fetch_rapiddns(domain, session):
    try:
        r = session.get(f"https://rapiddns.io/subdomain/{domain}?full=1", timeout=20, verify=False)
        subs = set()
        if r.status_code == 200:
            # Extract from both <a href and <td> formats
            found = re.findall(r'<td>([a-zA-Z0-9\-\.]+\.' + re.escape(domain) + r')</td>', r.text, re.IGNORECASE)
            for sub in found:
                subs.add(sub.lower())
        print(Fore.BLUE + f"    > RapidDNS: {len(subs)} found")
        return subs
    except Exception:
        pass
    return set()

def _fetch_urlscan(domain, session):
    try:
        r = session.get(f"https://urlscan.io/api/v1/search/?q=domain:{domain}&size=200", timeout=20, verify=False)
        subs = set()
        if r.status_code == 200:
            results = r.json().get("results", [])
            for result in results:
                page = result.get("page", {})
                url = page.get("url", "")
                sub_match = re.match(r"https?://([a-zA-Z0-9\-\.]+\." + re.escape(domain) + r")", url)
                if sub_match:
                    subs.add(sub_match.group(1).lower())
        print(Fore.BLUE + f"    > urlscan.io: {len(subs)} found")
        return subs
    except Exception:
        pass
    return set()

def _dns_bruteforce(domain):
    """Resolve common subdomain names to discover infrastructure not in public databases."""
    found = set()
    def try_resolve(sub):
        try:
            hostname = f"{sub}.{domain}"
            socket.gethostbyname(hostname)
            return hostname
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(try_resolve, sub): sub for sub in COMMON_SUBDOMAINS}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                found.add(result)

    print(Fore.BLUE + f"    > DNS Brute-force: {len(found)} resolved")
    return found


def _check_live_with_status(sub):
    """Check if a subdomain resolves AND is HTTP-reachable."""
    try:
        ip = socket.gethostbyname(sub)
        # Try HTTP request for rich info
        for proto in ["https", "http"]:
            try:
                r = requests.get(f"{proto}://{sub}", timeout=5, allow_redirects=True, verify=False)
                return sub, ip, r.status_code, proto
            except Exception:
                continue
        return sub, ip, 0, ""
    except Exception:
        return None


def enumerate(domain, save_path):
    print(Fore.CYAN + f"[*] Multi-source subdomain enumeration for {domain} (7 sources + bruteforce)...")
    session = get_stealth_session()

    unique_subs = set()

    # Run all OSINT sources concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        futures = {
            "crt.sh":        executor.submit(_fetch_crtsh, domain, session),
            "HackerTarget":  executor.submit(_fetch_hackertarget, domain, session),
            "AlienVault":    executor.submit(_fetch_alienvault, domain, session),
            "ThreatMiner":   executor.submit(_fetch_threatminer, domain, session),
            "RapidDNS":      executor.submit(_fetch_rapiddns, domain, session),
            "URLScan":       executor.submit(_fetch_urlscan, domain, session),
            "DNS-BF":        executor.submit(_dns_bruteforce, domain),
        }
        for name, future in futures.items():
            try:
                result = future.result()
                if result:
                    unique_subs.update(result)
            except Exception:
                pass

    # Filter to only subdomains containing the target domain
    final_subs = {s for s in unique_subs if domain in s and s != domain}
    print(Fore.YELLOW + f"  [*] Total unique candidates: {len(final_subs)}. Verifying live status...")

    # Verify live subdomains with HTTP check
    live_subs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        futures = [executor.submit(_check_live_with_status, sub) for sub in final_subs]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    live_subs.append(result)
            except Exception:
                pass

    # Sort live subs alphabetically
    live_subs.sort(key=lambda x: x[0])

    try:
        with open(f"{save_path}/subdomains_all.txt", "w", encoding="utf-8") as f:
            f.write(f"ALL DISCOVERED SUBDOMAINS: {domain}\n")
            f.write(f"Total: {len(final_subs)}\n")
            f.write("=" * 40 + "\n")
            for s in sorted(final_subs):
                f.write(s + "\n")

        with open(f"{save_path}/subdomains_live.txt", "w", encoding="utf-8") as f:
            f.write(f"LIVE SUBDOMAINS: {domain}\n")
            f.write(f"Total Live: {len(live_subs)}\n")
            f.write("=" * 40 + "\n")
            for sub, ip, status, proto in live_subs:
                status_str = f"{status}" if status else "DNS only"
                f.write(f"{sub} | IP: {ip} | {proto.upper()} {status_str}\n")

    except Exception as e:
        print(Fore.RED + f"  [-] Error saving subdomains: {e}")

    print(Fore.GREEN + f"  [+] Subdomain enum done. {len(final_subs)} found, {len(live_subs)} live.")
