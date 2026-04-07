"""
WebFox — Enhanced WHOIS Scanner
Extracts domain age, ownership, registrar details, privacy protection status,
and detects expiring domains and admin emails.

Author : Lucky | WebFox Recon Framework v4.0
"""
import whois
from datetime import datetime, timezone
from colorama import Fore
import sys
import os


def _normalize_date(dt_value):
    """Handle both single datetime and list of datetimes from whois."""
    if isinstance(dt_value, list):
        return dt_value[0] if dt_value else None
    return dt_value


def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Fetching enriched WHOIS data for {domain}...")
    output = [f"WHOIS INTELLIGENCE: {domain}", "=" * 50]

    try:
        w = whois.whois(domain)

        creation_date   = _normalize_date(w.creation_date)
        expiration_date = _normalize_date(w.expiration_date)
        updated_date    = _normalize_date(w.updated_date)

        # Domain Age
        if creation_date:
            try:
                if creation_date.tzinfo is None:
                    creation_date = creation_date.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                age_days = (now - creation_date).days
                years = age_days // 365
                months = (age_days % 365) // 30
                age_str = f"{years} years, {months} months ({age_days} days)"
            except Exception:
                age_str = str(creation_date)
        else:
            age_str = "Unknown"

        # Expiry status
        expiry_status = "Unknown"
        days_to_exp = None
        if expiration_date:
            try:
                if expiration_date.tzinfo is None:
                    expiration_date = expiration_date.replace(tzinfo=timezone.utc)
                days_to_exp = (expiration_date - datetime.now(timezone.utc)).days
                if days_to_exp < 0:
                    expiry_status = f"⚠️  EXPIRED {abs(days_to_exp)} days ago!"
                elif days_to_exp < 30:
                    expiry_status = f"⚠️  EXPIRING SOON — {days_to_exp} days left"
                elif days_to_exp < 90:
                    expiry_status = f"⚠️  Renew soon — {days_to_exp} days left"
                else:
                    expiry_status = f"Active — {days_to_exp} days left ✓"
            except Exception:
                expiry_status = str(expiration_date)

        # Privacy protection detection
        registrant_name = str(w.name or "")
        registrant_org  = str(w.org or "")
        privacy_keywords = ["privacy", "whoisguard", "domains by proxy", "perfect privacy", "redacted", "data protected", "withheld"]
        is_private = any(kw in (registrant_name + registrant_org).lower() for kw in privacy_keywords)

        output.append(f"\n[REGISTRAR & STATUS]")
        output.append(f"  Registrar    : {w.registrar or 'N/A'}")
        output.append(f"  Status       : {', '.join(w.status) if isinstance(w.status, list) else w.status or 'N/A'}")

        output.append(f"\n[DOMAIN AGE & LIFECYCLE]")
        output.append(f"  Created On   : {creation_date}")
        output.append(f"  Domain Age   : {age_str}")
        output.append(f"  Updated On   : {updated_date}")
        output.append(f"  Expires On   : {expiration_date}")
        output.append(f"  Expiry Status: {expiry_status}")

        output.append(f"\n[REGISTRANT INFO]")
        output.append(f"  Name         : {w.name or 'N/A'}")
        output.append(f"  Organization : {w.org or 'N/A'}")
        output.append(f"  Country      : {w.country or 'N/A'}")
        output.append(f"  City         : {w.city or 'N/A'}")
        output.append(f"  State        : {w.state or 'N/A'}")
        output.append(f"  Privacy Guard: {'⚠️  YES — Owner info is hidden.' if is_private else 'No — Owner info visible ✓'}")

        emails = w.emails
        if emails:
            if isinstance(emails, str):
                emails = [emails]
            output.append(f"\n[CONTACT EMAILS]")
            for em in emails:
                output.append(f"  {em}")

        output.append(f"\n[NAME SERVERS]")
        ns_list = w.name_servers
        if ns_list:
            if isinstance(ns_list, str):
                ns_list = [ns_list]
            for ns in ns_list:
                output.append(f"  {ns.lower()}")

        output.append(f"\n[RAW WHOIS]")
        output.append(str(w))

    except Exception as e:
        output.append(f"\n[-] WHOIS lookup failed: {e}")
        output.append("  This can happen for TLDs that block WHOIS, rate limits, or network issues.")
        print(Fore.YELLOW + f"  [~] WHOIS lookup failed (might be rate-limited): {e}")

    try:
        with open(f"{save_path}/whois_basic.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
    except Exception as e:
        print(Fore.RED + f"  [-] WHOIS save error: {e}")

    print(Fore.GREEN + f"  [+] WHOIS scan complete.")
