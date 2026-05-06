import requests
from colorama import Fore

HEADERS = {'User-Agent': 'Mozilla/5.0 (WebFox/3.0)'}

DISALLOW_RISK = [
    "/admin", "/administrator", "/wp-admin", "/phpmyadmin",
    "/login", "/signin", "/dashboard", "/panel", "/cpanel",
    "/backup", "/uploads", "/private", "/secret", "/config",
    "/db", "/database", "/sql", "/api", "/internal",
]

def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Fetching and analysing robots.txt for {domain}...")
    lines = [f"ROBOTS.TXT ANALYSIS: {domain}", "=" * 50]

    content = None
    for proto in ["https", "http"]:
        try:
            url = f"{proto}://{domain}/robots.txt"
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200 and ("User-agent" in r.text or "user-agent" in r.text.lower()):
                content = r.text
                lines.append(f"\n[+] Found: {url}")
                break
        except: pass

    if not content:
        lines.append("\n[-] robots.txt not found or empty.")
        with open(f"{save_path}/robots.txt", "w") as f:
            f.write("\n".join(lines))
        print(Fore.YELLOW + "[-] robots.txt not found.")
        return

    # Raw content
    lines += ["", "[+] RAW CONTENT:", "-" * 40, content, ""]

    # Parse disallowed paths
    lines += ["[+] DISALLOW ANALYSIS:", "-" * 40]
    disallowed = []
    allowed = []
    sitemaps = []
    crawl_delay = None
    user_agents = []

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("disallow:"):
            path = stripped[9:].strip()
            if path:
                disallowed.append(path)
        elif stripped.lower().startswith("allow:"):
            path = stripped[6:].strip()
            if path:
                allowed.append(path)
        elif stripped.lower().startswith("user-agent:"):
            ua = stripped[11:].strip()
            user_agents.append(ua)
        elif stripped.lower().startswith("sitemap:"):
            sitemaps.append(stripped[8:].strip())
        elif stripped.lower().startswith("crawl-delay:"):
            crawl_delay = stripped[12:].strip()

    lines.append(f"  User-Agents   : {', '.join(set(user_agents)) or 'None'}")
    lines.append(f"  Crawl-Delay   : {crawl_delay or 'Not set'}")
    lines.append(f"  Disallowed    : {len(disallowed)} paths")
    lines.append(f"  Allowed       : {len(allowed)} paths")
    lines.append(f"  Sitemaps      : {', '.join(sitemaps) or 'None declared'}")

    # Flag interesting disallowed paths
    lines += ["", "[!] INTERESTING DISALLOWED PATHS:", "-" * 40]
    flagged = []
    for path in disallowed:
        risk_match = any(risk.lower() in path.lower() for risk in DISALLOW_RISK)
        if risk_match:
            flagged.append(path)
            lines.append(f"  [HIGH RISK] {path}")
    if not flagged:
        lines.append("  No high-risk paths found in Disallow rules.")

    # Full disallow list
    lines += ["", "[+] ALL DISALLOWED PATHS:", "-" * 40]
    for p in disallowed:
        lines.append(f"  {p}")

    with open(f"{save_path}/robots.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(Fore.GREEN + f"[+] robots.txt parsed. {len(disallowed)} disallowed paths, {len(flagged)} flagged as high-risk.")
