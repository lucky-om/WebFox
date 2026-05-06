import whois
import requests
from datetime import datetime
from colorama import Fore

HEADERS = {'User-Agent': 'Mozilla/5.0 (WebFox/3.0)'}

def _days_until(date_val):
    """Return days until expiry from a date or list of dates."""
    try:
        if isinstance(date_val, list):
            date_val = date_val[0]
        if date_val and isinstance(date_val, datetime):
            return (date_val - datetime.utcnow()).days
    except:
        pass
    return "Unknown"

def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Fetching WHOIS & registration data for {domain}...")
    lines = [f"WHOIS REPORT: {domain}", "=" * 45]

    try:
        w = whois.whois(domain)

        def fmt(val):
            if isinstance(val, list):
                return ", ".join(str(v) for v in val[:5])
            return str(val) if val else "N/A"

        expiry = w.expiration_date
        days_left = _days_until(expiry)
        expiry_warn = ""
        if isinstance(days_left, int):
            if days_left < 0:
                expiry_warn = " [EXPIRED!]"
            elif days_left < 30:
                expiry_warn = f" [EXPIRING IN {days_left} DAYS — CRITICAL]"
            elif days_left < 90:
                expiry_warn = f" [Expiring in {days_left} days]"

        lines += [
            f"Domain Name    : {fmt(w.domain_name)}",
            f"Registrar      : {fmt(w.registrar)}",
            f"Registrar URL  : {fmt(w.registrar_url) if hasattr(w,'registrar_url') else 'N/A'}",
            f"WHOIS Server   : {fmt(w.whois_server) if hasattr(w,'whois_server') else 'N/A'}",
            f"Status         : {fmt(w.status)}",
            f"Created        : {fmt(w.creation_date)}",
            f"Updated        : {fmt(w.updated_date)}",
            f"Expires        : {fmt(expiry)}{expiry_warn}",
            f"Days to Expiry : {days_left}",
            "",
            "REGISTRANT:",
            f"  Organization : {fmt(w.org)}",
            f"  Name         : {fmt(w.name) if hasattr(w,'name') else 'N/A'}",
            f"  City         : {fmt(w.city)}",
            f"  State        : {fmt(w.state) if hasattr(w,'state') else 'N/A'}",
            f"  Country      : {fmt(w.country)}",
            f"  Emails       : {fmt(w.emails)}",
            "",
            "NAME SERVERS:",
        ]
        ns = w.name_servers
        if isinstance(ns, (list, set)):
            for n in sorted(set(str(x).lower() for x in ns)):
                lines.append(f"  {n}")
        else:
            lines.append(f"  {ns}")

        # RDAP enrichment (extra registrant data, abuse contact)
        try:
            rdap_url = f"https://rdap.org/domain/{domain}"
            rdap = requests.get(rdap_url, headers=HEADERS, timeout=10).json()
            lines += ["", "RDAP ENRICHMENT:", "-" * 30]
            for entity in rdap.get("entities", []):
                roles = entity.get("roles", [])
                vcard = entity.get("vcardArray", [[], []])[1]
                for field in vcard:
                    if field[0] == "fn":
                        lines.append(f"  {'/'.join(roles)}: {field[3]}")
                    if field[0] == "email":
                        lines.append(f"  Email: {field[3]}")
                    if field[0] == "tel":
                        lines.append(f"  Tel  : {field[3]}")
        except:
            pass

        print(Fore.GREEN + f"[+] WHOIS complete for {domain}. Expires: {fmt(expiry)}{expiry_warn}")

    except Exception as e:
        lines.append(f"WHOIS Error: {e}")
        print(Fore.RED + f"[-] WHOIS failed: {e}")

    with open(f"{save_path}/whois_basic.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
