import socket
import requests
from colorama import Fore

HEADERS = {'User-Agent': 'Mozilla/5.0 (WebFox/4.0)'}


def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Fetching IP geolocation & network intelligence for {domain}...")

    # ── Resolve IPs ────────────────────────────────────────────────────────
    ipv4 = None
    ipv6 = None

    try:
        ipv4 = socket.gethostbyname(domain)
    except Exception:
        pass

    try:
        info = socket.getaddrinfo(domain, None, socket.AF_INET6)
        if info:
            ipv6 = info[0][4][0]
    except Exception:
        pass

    ip = ipv4 or ipv6
    if not ip:
        print(Fore.RED + f"[-] Could not resolve IP for {domain}")
        with open(f"{save_path}/ip_location.txt", "w", encoding="utf-8") as f:
            f.write(f"IP resolution failed for {domain}\n")
        return

    # ── PTR (reverse DNS) ──────────────────────────────────────────────────
    ptr = "N/A"
    try:
        ptr = socket.gethostbyaddr(ip)[0]
    except Exception:
        pass

    # ── Primary geo: ip-api.com ────────────────────────────────────────────
    data = {}
    try:
        fields = ("status,message,continent,country,regionName,city,zip,"
                  "lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query")
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields={fields}",
            headers=HEADERS,
            timeout=10
        ).json()
        if r.get("status") == "success":
            data = r
    except Exception:
        pass

    # ── Fallback geo: ipinfo.io ────────────────────────────────────────────
    if not data:
        try:
            r2 = requests.get(
                f"https://ipinfo.io/{ip}/json",
                headers=HEADERS,
                timeout=10
            ).json()
            loc = r2.get("loc", "0,0").split(",")
            data = {
                "query"     : ip,
                "continent" : "",
                "country"   : r2.get("country",  "Unknown"),
                "regionName": r2.get("region",   "Unknown"),
                "city"      : r2.get("city",     "Unknown"),
                "zip"       : r2.get("postal",   "Unknown"),
                "lat"       : loc[0] if len(loc) > 0 else "Unknown",
                "lon"       : loc[1] if len(loc) > 1 else "Unknown",
                "timezone"  : r2.get("timezone", "Unknown"),
                "isp"       : r2.get("org",      "Unknown"),
                "org"       : r2.get("org",      "Unknown"),
                "as"        : r2.get("org",      "Unknown"),
                "asname"    : "",
                "reverse"   : r2.get("hostname", ""),
                "mobile"    : False,
                "proxy"     : False,
                "hosting"   : False,
            }
        except Exception:
            pass

    # ── Shodan InternetDB (no API key) ────────────────────────────────────
    shodan_lines = []
    try:
        sd = requests.get(
            f"https://internetdb.shodan.io/{ip}",
            headers=HEADERS,
            timeout=8
        ).json()
        open_ports  = ", ".join(str(p) for p in sd.get("ports",     [])) or "None"
        cpes        = ", ".join(sd.get("cpes",      [])) or "None"
        vulns       = ", ".join(sd.get("vulns",     [])) or "None"
        hostnames   = ", ".join(sd.get("hostnames", [])) or "None"
        shodan_lines = [
            "",
            "[+] SHODAN INTERNETDB:",
            "-" * 44,
            f"  Open Ports  : {open_ports}",
            f"  CPE Fingerp : {cpes}",
            f"  Known CVEs  : {vulns}",
            f"  Hostnames   : {hostnames}",
        ]
    except Exception:
        pass

    # ── Build report ──────────────────────────────────────────────────────
    def g(key): return data.get(key, "Unknown")

    lines = [
        f"GEOLOCATION & NETWORK REPORT: {domain}",
        "=" * 47,
        f"IPv4 Address  : {ipv4 or 'N/A'}",
        f"IPv6 Address  : {ipv6 or 'N/A'}",
        f"PTR (rDNS)    : {ptr}",
        f"Continent     : {g('continent')}",
        f"Country       : {g('country')}",
        f"Region        : {g('regionName')}",
        f"City          : {g('city')}",
        f"Zip Code      : {g('zip')}",
        f"Latitude      : {g('lat')}",
        f"Longitude     : {g('lon')}",
        f"Timezone      : {g('timezone')}",
        f"ISP           : {g('isp')}",
        f"Organization  : {g('org')}",
        f"ASN           : {g('as')}",
        f"ASN Name      : {g('asname')}",
        f"Mobile Network: {'Yes' if data.get('mobile') else 'No'}",
        f"Proxy / VPN   : {'Yes' if data.get('proxy') else 'No'}",
        f"Hosting / DC  : {'Yes' if data.get('hosting') else 'No'}",
    ] + shodan_lines

    with open(f"{save_path}/ip_location.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    city    = g('city')
    country = g('country')
    asn     = g('as')
    print(Fore.GREEN + f"[+] IP scan complete: {city}, {country} | {asn}")
