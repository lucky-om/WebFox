"""
WebFox — Subdomain Takeover Detector
For every live subdomain, checks if it resolves to a CNAME pointing
to an unclaimed service (Heroku, GitHub Pages, AWS S3, etc.).

Author : Lucky | WebFox Recon Framework v4.0
"""
import requests
import socket
import concurrent.futures
from colorama import Fore
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.stealth import get_stealth_session

# CNAME fingerprints for known takeover-vulnerable services
# Format: (CNAME keyword, fingerprint in HTTP body response, service name)
TAKEOVER_FINGERPRINTS = [
    ("github.io",           "There isn't a GitHub Pages site here",     "GitHub Pages"),
    ("heroku.com",          "No such app",                              "Heroku"),
    ("herokussl.com",       "No such app",                              "Heroku"),
    ("amazonaws.com",       "NoSuchBucket",                             "AWS S3"),
    ("s3.amazonaws.com",    "NoSuchBucket",                             "AWS S3"),
    ("cloudfront.net",      "ERROR: The request could not be satisfied","CloudFront"),
    ("azurewebsites.net",   "404 Web Site not found",                  "Azure"),
    ("netlify.com",         "Not Found",                                "Netlify"),
    ("netlify.app",         "Not Found",                                "Netlify"),
    ("readthedocs.io",      "unknown to Read the Docs",                 "ReadTheDocs"),
    ("wpengine.com",        "The site you were looking for",            "WP Engine"),
    ("zendesk.com",         "Help Center Closed",                       "Zendesk"),
    ("ghost.io",            "The thing you were looking",               "Ghost"),
    ("launchrock.com",      "It looks like you may have taken",         "LaunchRock"),
    ("myshopify.com",       "Sorry, this shop is currently unavailable","Shopify"),
    ("smartling.com",       "Domain is not configured",                 "Smartling"),
    ("desk.com",            "Please try again or try",                  "Desk.com"),
    ("campaignmonitor.com", "Double check the URL",                     "Campaign Monitor"),
    ("cargo.site",          "If you're moving your domain away",        "Cargo"),
    ("bitbucket.io",        "Repository not found",                     "Bitbucket"),
    ("surge.sh",            "project not found",                        "Surge.sh"),
    ("fastly.io",           "Fastly error: unknown domain",             "Fastly"),
    ("fly.dev",             "404 Not Found",                            "Fly.io"),
    ("vercel.app",          "The deployment you're looking for",        "Vercel"),
    ("pages.dev",           "There isn't a Cloudflare Pages site here", "Cloudflare Pages"),
]


def _check_cname(subdomain):
    """Return the CNAME chain for a subdomain if it exists."""
    try:
        import dns.resolver
        answers = dns.resolver.resolve(subdomain, 'CNAME')
        return [str(r.target).lower().rstrip('.') for r in answers]
    except Exception:
        return []


def _check_takeover(subdomain, session):
    """Returns a finding dict if subdomain appears vulnerable."""
    cnames = _check_cname(subdomain)
    if not cnames:
        return None

    for cname in cnames:
        for (pattern, fingerprint, service) in TAKEOVER_FINGERPRINTS:
            if pattern in cname:
                # The CNAME matches a vulnerable service — now check if body shows unclaimed
                for proto in ["https", "http"]:
                    url = f"{proto}://{subdomain}"
                    try:
                        r = session.get(url, timeout=10, verify=False)
                        body = r.text[:3000]
                        if fingerprint.lower() in body.lower():
                            return {
                                "subdomain": subdomain,
                                "cname": cname,
                                "service": service,
                                "status": r.status_code,
                                "url": url,
                                "verdict": "VULNERABLE",
                            }
                    except Exception:
                        pass

                # Even if body check fails, flag as "potential" since CNAME points to vulnerable service
                return {
                    "subdomain": subdomain,
                    "cname": cname,
                    "service": service,
                    "status": "N/A",
                    "url": f"http://{subdomain}",
                    "verdict": "POTENTIAL",
                }
    return None


def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Checking subdomains for takeover vulnerabilities...")
    session = get_stealth_session()

    live_file = f"{save_path}/subdomains_live.txt"
    if not os.path.exists(live_file):
        print(Fore.YELLOW + "  [~] Subdomain scan results not found. Run subdomain scan first.")
        return

    with open(live_file, "r") as f:
        live_subs = [line.strip() for line in f if line.strip()]

    if not live_subs:
        print(Fore.YELLOW + "  [~] No live subdomains to check.")
        return

    print(Fore.BLUE + f"  > Checking {len(live_subs)} live subdomains against {len(TAKEOVER_FINGERPRINTS)} service fingerprints...")

    vulnerable = []
    potential = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(_check_takeover, sub, session): sub for sub in live_subs}
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    if result["verdict"] == "VULNERABLE":
                        vulnerable.append(result)
                        print(Fore.RED + f"  [!!!] VULNERABLE: {result['subdomain']} -> {result['cname']} ({result['service']})")
                    else:
                        potential.append(result)
                        print(Fore.YELLOW + f"  [!] POTENTIAL: {result['subdomain']} -> {result['service']}")
            except Exception:
                pass

    try:
        with open(f"{save_path}/takeover.txt", "w", encoding="utf-8") as f:
            f.write(f"SUBDOMAIN TAKEOVER ANALYSIS: {domain}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Subdomains checked: {len(live_subs)}\n\n")

            f.write(f"CONFIRMED VULNERABLE ({len(vulnerable)}):\n")
            f.write("-" * 30 + "\n")
            for r in vulnerable:
                f.write(f"  Subdomain : {r['subdomain']}\n")
                f.write(f"  CNAME     : {r['cname']}\n")
                f.write(f"  Service   : {r['service']}\n")
                f.write(f"  URL       : {r['url']}\n")
                f.write(f"  Status    : {r['status']}\n\n")
            if not vulnerable:
                f.write("  None found.\n\n")

            f.write(f"POTENTIAL VULNERABILITIES ({len(potential)}):\n")
            f.write("-" * 30 + "\n")
            for r in potential:
                f.write(f"  Subdomain : {r['subdomain']}\n")
                f.write(f"  CNAME     : {r['cname']}\n")
                f.write(f"  Service   : {r['service']}\n\n")
            if not potential:
                f.write("  None found.\n")

    except Exception as e:
        print(Fore.RED + f"  [-] Error saving takeover report: {e}")

    print(Fore.GREEN + f"  [+] Takeover scan done. {len(vulnerable)} confirmed, {len(potential)} potential.")
