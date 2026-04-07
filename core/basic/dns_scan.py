"""
WebFox — Enhanced DNS Scanner
More record types, Zone Transfer, Security checks, Cloud provider detection,
and DNS propagation validation.

Author : Lucky | WebFox Recon Framework v4.0
"""
import dns.resolver
import dns.zone
import dns.query
import dns.exception
import socket
from colorama import Fore
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Known Cloud/CDN IP ranges (simplified prefix checks)
CLOUD_INDICATORS = {
    "104.16.": "Cloudflare",
    "104.17.": "Cloudflare",
    "172.67.": "Cloudflare",
    "192.0.": "Cloudflare",
    "13.": "AWS",
    "52.": "AWS",
    "54.": "AWS",
    "34.": "Google Cloud",
    "35.": "Google Cloud",
    "20.": "Azure",
    "40.": "Azure",
    "51.": "Azure",
}

def detect_cloud(ip):
    for prefix, provider in CLOUD_INDICATORS.items():
        if ip.startswith(prefix):
            return provider
    return None

def try_zone_transfer(domain, nameserver, output_lines):
    """Attempt DNS Zone Transfer (AXFR). This is a major misconfiguration if it succeeds."""
    try:
        z = dns.zone.from_xfr(dns.query.xfr(nameserver, domain, timeout=8))
        output_lines.append(f"\n⚠️  ZONE TRANSFER SUCCESSFUL FOR NS: {nameserver}")
        output_lines.append("  THIS IS A CRITICAL MISCONFIGURATION — ALL DNS records are exposed!\n")
        for name, node in z.nodes.items():
            output_lines.append(f"  {name.to_text()}.{domain}")
        return True
    except Exception:
        return False

def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Deep DNS enumeration for {domain}...")

    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'PTR', 'SRV', 'CAA', 'LOC']
    output_lines = [f"DEEP DNS SCAN: {domain}", "=" * 50]

    resolver = dns.resolver.Resolver()
    resolver.timeout = 5
    resolver.lifetime = 8

    all_a_records = []
    nameservers = []

    for r_type in record_types:
        try:
            answers = resolver.resolve(domain, r_type)
            output_lines.append(f"\n[{r_type}] Records:")
            for rdata in answers:
                line = f"  {rdata.to_text()}"

                # Cloud detection for A records
                if r_type == 'A':
                    ip = rdata.to_text()
                    all_a_records.append(ip)
                    cloud = detect_cloud(ip)
                    if cloud:
                        line += f"  <- Hosted on {cloud}"

                # Collect NS for zone transfer attempt
                if r_type == 'NS':
                    ns_host = rdata.to_text().rstrip('.')
                    try:
                        ns_ip = socket.gethostbyname(ns_host)
                        nameservers.append(ns_ip)
                        line += f"  (IP: {ns_ip})"
                    except Exception:
                        nameservers.append(ns_host)

                output_lines.append(line)
        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            output_lines.append(f"\n[{r_type}] NXDOMAIN — domain does not exist.")
        except Exception:
            pass

    # Wildcard DNS detection
    output_lines.append("\n\n[WILDCARD DNS CHECK]")
    try:
        fake_sub = f"randomnonexistent12345xyz.{domain}"
        wild_answers = resolver.resolve(fake_sub, 'A')
        ips = [r.to_text() for r in wild_answers]
        output_lines.append(f"  ⚠️  WILDCARD DNS DETECTED — {fake_sub} resolves to {ips}")
        output_lines.append("  All non-existent subdomains may appear alive — subdomain enum may be unreliable.")
    except Exception:
        output_lines.append("  No wildcard DNS detected. ✓")

    # Email Security
    output_lines.append("\n\n[EMAIL SECURITY (SPF / DKIM / DMARC)]")

    # SPF
    try:
        answers = resolver.resolve(domain, 'TXT')
        spf_record = None
        for rdata in answers:
            txt = rdata.to_text().strip('"')
            if "v=spf1" in txt:
                spf_record = txt
                break
        if spf_record:
            output_lines.append(f"  SPF  : FOUND — {spf_record}")
            if "-all" in spf_record:
                output_lines.append("         -> Strict enforcement (-all). ✓")
            elif "~all" in spf_record:
                output_lines.append("         -> Soft fail (~all). Moderate risk.")
            elif "?all" in spf_record or "+all" in spf_record:
                output_lines.append("         -> ⚠️  PERMISSIVE (+all / ?all). Anyone can send as this domain!")
        else:
            output_lines.append("  SPF  : MISSING — Vulnerable to email spoofing!")
    except Exception:
        output_lines.append("  SPF  : ERROR — Could not query TXT records.")

    # DMARC
    try:
        answers = resolver.resolve(f"_dmarc.{domain}", 'TXT')
        for rdata in answers:
            txt = rdata.to_text().strip('"')
            if "v=DMARC1" in txt:
                output_lines.append(f"  DMARC: FOUND — {txt}")
                if "p=reject" in txt:
                    output_lines.append("         -> Policy: reject. ✓")
                elif "p=quarantine" in txt:
                    output_lines.append("         -> Policy: quarantine. Moderate protection.")
                elif "p=none" in txt:
                    output_lines.append("         -> ⚠️  Policy: none. No enforcement — monitoring only!")
    except Exception:
        output_lines.append("  DMARC: MISSING — Vulnerable to email spoofing!")

    # DKIM (check common selectors)
    dkim_found = False
    for selector in ["default", "google", "mail", "dkim", "email", "s1", "s2", "k1"]:
        try:
            dkim_host = f"{selector}._domainkey.{domain}"
            resolver.resolve(dkim_host, 'TXT')
            output_lines.append(f"  DKIM : FOUND (selector='{selector}') ✓")
            dkim_found = True
            break
        except Exception:
            continue
    if not dkim_found:
        output_lines.append("  DKIM : Not found for common selectors. May still exist with custom selector.")

    # Zone Transfer attempts
    if nameservers:
        output_lines.append(f"\n\n[ZONE TRANSFER ATTEMPTS ({len(nameservers)} nameservers)]")
        zt_found = False
        for ns in nameservers:
            if try_zone_transfer(domain, ns, output_lines):
                zt_found = True
        if not zt_found:
            output_lines.append("  No nameservers allowed zone transfer. ✓")

    try:
        with open(f"{save_path}/dns.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
    except Exception as e:
        print(Fore.RED + f"  [-] DNS save error: {e}")

    print(Fore.GREEN + f"  [+] DNS scan complete. {len(all_a_records)} A records, zone transfer tested on {len(nameservers)} NS.")
