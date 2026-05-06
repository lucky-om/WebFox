import dns.resolver
import dns.zone
import dns.query
import dns.exception
import socket
from colorama import Fore

RECORD_TYPES = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'CAA', 'SRV']


def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Running full DNS enumeration for {domain}...")
    lines = [f"DNS INTELLIGENCE REPORT: {domain}", "=" * 52]

    resolver = dns.resolver.Resolver()
    resolver.timeout  = 5
    resolver.lifetime = 10

    # ── All record types ───────────────────────────────────────────────────
    lines += ["", "[+] DNS RECORDS:", "-" * 44]
    for r_type in RECORD_TYPES:
        try:
            answers = resolver.resolve(domain, r_type)
            for rdata in answers:
                lines.append(f"  {r_type:<8}: {rdata.to_text()}")
        except Exception:
            pass

    # ── Zone transfer attempt (AXFR) ──────────────────────────────────────
    lines += ["", "[!] ZONE TRANSFER (AXFR) ATTEMPT:", "-" * 44]
    try:
        ns_answers = resolver.resolve(domain, 'NS')
        ns_list = [str(r.target).rstrip(".") for r in ns_answers]
    except Exception:
        ns_list = []

    if not ns_list:
        lines.append("  Could not resolve NS records — AXFR skipped.")
    else:
        for ns_host in ns_list:
            try:
                zone = dns.zone.from_xfr(
                    dns.query.xfr(ns_host, domain, timeout=5, lifetime=8)
                )
                lines.append(f"  [CRITICAL] Zone transfer SUCCEEDED on {ns_host}!")
                for name in zone.nodes.keys():
                    lines.append(f"    {name}")
            except (dns.exception.FormError, EOFError):
                lines.append(f"  [OK] Zone transfer REFUSED by {ns_host}")
            except Exception as e:
                lines.append(f"  [OK] {ns_host} refused AXFR ({type(e).__name__})")

    # ── Email security ─────────────────────────────────────────────────────
    lines += ["", "[+] EMAIL SECURITY:", "-" * 44]

    # SPF
    spf_found = False
    try:
        for rdata in resolver.resolve(domain, 'TXT'):
            txt = rdata.to_text().strip('"')
            if txt.startswith("v=spf1"):
                lines.append(f"  SPF     : FOUND — {txt}")
                spf_found = True
    except Exception:
        pass
    if not spf_found:
        lines.append("  SPF     : MISSING — Vulnerable to email spoofing")

    # DMARC
    dmarc_found = False
    try:
        for rdata in resolver.resolve(f"_dmarc.{domain}", 'TXT'):
            txt = rdata.to_text().strip('"')
            if "v=DMARC1" in txt:
                lines.append(f"  DMARC   : FOUND — {txt}")
                dmarc_found = True
    except Exception:
        pass
    if not dmarc_found:
        lines.append("  DMARC   : MISSING — No DMARC policy enforced")

    # DKIM (common selectors)
    dkim_found = False
    for sel in ["default", "google", "mail", "dkim", "k1", "s1", "s2",
                "selector1", "selector2", "mandrill", "smtp"]:
        try:
            resolver.resolve(f"{sel}._domainkey.{domain}", 'TXT')
            lines.append(f"  DKIM    : FOUND (selector: {sel})")
            dkim_found = True
            break
        except Exception:
            pass
    if not dkim_found:
        lines.append("  DKIM    : NOT found on common selectors")

    # MTA-STS
    try:
        resolver.resolve(f"_mta-sts.{domain}", 'TXT')
        lines.append("  MTA-STS : FOUND — STARTTLS downgrade protection active")
    except Exception:
        lines.append("  MTA-STS : MISSING")

    # ── DNSSEC ─────────────────────────────────────────────────────────────
    lines += ["", "[+] DNSSEC STATUS:", "-" * 44]
    try:
        dnskey = list(resolver.resolve(domain, 'DNSKEY'))
        lines.append(f"  DNSSEC  : ENABLED ({len(dnskey)} key(s) found)")
    except Exception:
        lines.append("  DNSSEC  : NOT ENABLED — Vulnerable to cache poisoning")

    # ── Common subdomain quick probe ───────────────────────────────────────
    lines += ["", "[+] QUICK SUBDOMAIN PROBE:", "-" * 44]
    common = [
        "www", "mail", "remote", "blog", "webmail", "server", "ns1", "ns2",
        "smtp", "secure", "vpn", "m", "shop", "ftp", "mx", "email", "api",
        "dev", "staging", "test", "admin", "portal", "app", "cdn", "status",
        "login", "dashboard", "git", "ci", "assets", "media",
    ]
    found_subs = []
    for sub in common:
        target_sub = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(target_sub)
            lines.append(f"  [+] {target_sub:<40} -> {ip}")
            found_subs.append(target_sub)
        except Exception:
            pass

    if not found_subs:
        lines.append("  No common subdomains resolved.")

    try:
        with open(f"{save_path}/dns.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(Fore.GREEN + f"[+] DNS scan complete. {len(found_subs)} quick subs resolved.")
    except Exception as e:
        print(Fore.RED + f"[-] DNS save error: {e}")
