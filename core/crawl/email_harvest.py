"""
Email Intelligence & Social Profile Harvester
Scrapes the target website, crt.sh, and common pages to find email addresses
and tries to locate associated social media accounts and linked domains.
"""
import requests
import re
from colorama import Fore
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.stealth import get_stealth_session, jitter

# Pages most likely to contain contact info
CONTACT_PAGES = [
    "/", "/contact", "/contact-us", "/about", "/about-us",
    "/team", "/company", "/support", "/help", "/staff",
    "/people", "/leadership", "/careers", "/jobs",
]

# Social media patterns to detect in HTML
SOCIAL_PATTERNS = {
    "Twitter / X":     r'(?:twitter\.com|x\.com)/([A-Za-z0-9_]{1,50})',
    "LinkedIn":        r'linkedin\.com/(?:in|company)/([A-Za-z0-9_\-\.]{1,80})',
    "GitHub":          r'github\.com/([A-Za-z0-9_\-]{1,50})',
    "Facebook":        r'facebook\.com/([A-Za-z0-9_\-\.]{1,80})',
    "Instagram":       r'instagram\.com/([A-Za-z0-9_.]{1,50})',
    "YouTube":         r'youtube\.com/(?:channel|user|@)([A-Za-z0-9_\-\.]{1,80})',
    "TikTok":          r'tiktok\.com/@([A-Za-z0-9_.]{1,50})',
    "Telegram":        r't\.me/([A-Za-z0-9_]{1,50})',
}

EMAIL_PATTERN = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,8}'
PHONE_PATTERN = r'(?:\+?\d[\d\s\-\(\)]{7,18}\d)'


def _extract_from_text(text):
    emails = set(re.findall(EMAIL_PATTERN, text))
    # Filter garbage like w3.org, schema.org style false positives
    emails = {e for e in emails if not any(junk in e for junk in ['schema.org', 'w3.org', 'example.com', '.png', '.jpg', '.gif', '.svg'])}
    
    socials = {}
    for platform, pattern in SOCIAL_PATTERNS.items():
        found = set(re.findall(pattern, text, re.IGNORECASE))
        if found:
            socials[platform] = found

    phones = set(re.findall(PHONE_PATTERN, text))
    phones = {p.strip() for p in phones if len(p.strip()) >= 10}
    return emails, socials, phones


def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Harvesting emails, phones, and social accounts for {domain}...")
    session = get_stealth_session()

    all_emails = set()
    all_socials = {}
    all_phones = set()
    scraped_pages = []

    # 1. Crawl known contact pages
    for page in CONTACT_PAGES:
        for proto in ["https", "http"]:
            url = f"{proto}://{domain}{page}"
            try:
                r = session.get(url, timeout=12, allow_redirects=True, verify=False)
                if r.status_code == 200:
                    emails, socials, phones = _extract_from_text(r.text)
                    all_emails.update(emails)
                    all_phones.update(phones)
                    for platform, accounts in socials.items():
                        all_socials.setdefault(platform, set()).update(accounts)
                    if emails or socials:
                        scraped_pages.append(url)
                    jitter(0.3, 0.7)
                    break
            except Exception:
                continue

    # 2. Check crt.sh for email in certificate metadata
    try:
        r = session.get(f"https://crt.sh/?q={domain}&output=json", timeout=20, verify=False)
        if r.status_code == 200:
            text = r.text
            emails, _, _ = _extract_from_text(text)
            all_emails.update(emails)
    except Exception:
        pass

    # 3. Check meta tags and page source of homepage more thoroughly
    try:
        for proto in ["https", "http"]:
            try:
                r = session.get(f"{proto}://{domain}", timeout=15, verify=False)
                emails, socials, phones = _extract_from_text(r.text)
                all_emails.update(emails)
                all_phones.update(phones)
                for p, a in socials.items():
                    all_socials.setdefault(p, set()).update(a)
                break
            except Exception:
                continue
    except Exception:
        pass

    # Save results
    try:
        with open(f"{save_path}/email_intel.txt", "w", encoding="utf-8") as f:
            f.write(f"EMAIL & SOCIAL INTELLIGENCE: {domain}\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"EMAILS FOUND ({len(all_emails)}):\n")
            f.write("-" * 30 + "\n")
            for e in sorted(all_emails):
                f.write(f"  {e}\n")
            if not all_emails:
                f.write("  No emails found.\n")

            f.write(f"\nPHONE NUMBERS ({len(all_phones)}):\n")
            f.write("-" * 30 + "\n")
            for p in sorted(all_phones):
                f.write(f"  {p}\n")
            if not all_phones:
                f.write("  No phone numbers found.\n")

            f.write(f"\nSOCIAL MEDIA ACCOUNTS:\n")
            f.write("-" * 30 + "\n")
            for platform, accounts in sorted(all_socials.items()):
                f.write(f"  {platform}:\n")
                for acc in sorted(accounts):
                    f.write(f"    - {acc}\n")
            if not all_socials:
                f.write("  No social accounts found.\n")

            f.write(f"\nPAGES SCRAPED:\n")
            for p in scraped_pages:
                f.write(f"  {p}\n")

    except Exception as e:
        print(Fore.RED + f"  [-] Error saving email intel: {e}")

    print(Fore.GREEN + f"  [+] Email intel done: {len(all_emails)} emails, {len(all_phones)} phones, {len(all_socials)} social platforms.")
