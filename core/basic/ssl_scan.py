"""
WebFox — Enhanced SSL/TLS Scanner
Certificate details, expiry, weak cipher suites, TLS protocol versions,
and certificate transparency log lookups.

Author : Lucky | WebFox Recon Framework v4.0
"""
import ssl
import socket
from datetime import datetime, timezone
from colorama import Fore
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.stealth import get_stealth_session, jitter

WEAK_PROTOCOLS = ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]
STRONG_PROTOCOLS = ["TLSv1.2", "TLSv1.3"]


def _test_protocol(domain, protocol):
    """Try to connect with a specific deprecated protocol — tests if server accepts weak ones."""
    proto_map = {
        "SSLv2":  ssl.PROTOCOL_SSLv23,
        "SSLv3":  ssl.PROTOCOL_SSLv23,
        "TLSv1":  ssl.PROTOCOL_TLSv1  if hasattr(ssl, 'PROTOCOL_TLSv1') else None,
        "TLSv1.1": ssl.PROTOCOL_TLSv1_1 if hasattr(ssl, 'PROTOCOL_TLSv1_1') else None,
        "TLSv1.2": ssl.PROTOCOL_TLSv1_2 if hasattr(ssl, 'PROTOCOL_TLSv1_2') else None,
    }
    proto = proto_map.get(protocol)
    if proto is None:
        return False
    try:
        ctx = ssl.SSLContext(proto)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain):
                return True
    except Exception:
        return False


def _get_ct_log_count(domain, session):
    """Query crt.sh for how many historical certificates exist for this domain."""
    try:
        r = session.get(f"https://crt.sh/?q={domain}&output=json", timeout=15, verify=False)
        if r.status_code == 200:
            data = r.json()
            return len(data)
    except Exception:
        pass
    return 0


def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Deep SSL/TLS analysis for {domain}...")
    session = get_stealth_session()
    output = [f"SSL/TLS SECURITY REPORT: {domain}", "=" * 50]

    cert_data = {}
    tls_version_used = "Unknown"

    # --- Main cert grab ---
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as s:
            with ctx.wrap_socket(s, server_hostname=domain) as ss:
                c = ss.getpeercert()
                tls_version_used = ss.version() or "Unknown"
                cipher = ss.cipher()
                cert_data = c
    except ssl.SSLCertVerificationError as e:
        output.append(f"\n⚠️  CERTIFICATE VERIFICATION ERROR: {e}")
        output.append("  This could indicate a self-signed or expired cert.")
    except Exception as e:
        output.append(f"\n[-] SSL Connection Failed: {e}")
        try:
            with open(f"{save_path}/ssl_info.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(output))
        except Exception:
            pass
        return

    # --- Certificate Details ---
    output.append("\n[CERTIFICATE DETAILS]")
    subject = dict(x[0] for x in cert_data.get('subject', []))
    issuer  = dict(x[0] for x in cert_data.get('issuer', []))

    cn = subject.get('commonName', 'Unknown')
    issued_to_org = subject.get('organizationName', 'N/A')
    issued_by = issuer.get('organizationName', 'Unknown')
    issued_by_cn = issuer.get('commonName', '')
    is_self_signed = cn == issued_by_cn or issued_by in ("", "Unknown")

    output.append(f"  Common Name  : {cn}")
    output.append(f"  Org          : {issued_to_org}")
    output.append(f"  Issued By    : {issued_by}")
    output.append(f"  Self-Signed  : {'⚠️  YES — Not trusted by browsers!' if is_self_signed else 'No ✓'}")
    output.append(f"  Serial No    : {cert_data.get('serialNumber', 'N/A')}")
    output.append(f"  Version      : {cert_data.get('version', 'N/A')}")

    # Expiry
    fmt = r'%b %d %H:%M:%S %Y %Z'
    not_before_str = cert_data.get('notBefore', '')
    not_after_str  = cert_data.get('notAfter', '')
    days_left = "Unknown"
    expired = False
    try:
        not_after_dt = datetime.strptime(not_after_str, fmt).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        days_left = (not_after_dt - now).days
        expired = days_left < 0
    except Exception:
        pass

    output.append(f"  Valid From   : {not_before_str}")
    output.append(f"  Valid Until  : {not_after_str}")
    if expired:
        output.append(f"  ⚠️  EXPIRED! Certificate expired {abs(days_left)} days ago.")
    elif isinstance(days_left, int) and days_left < 30:
        output.append(f"  ⚠️  EXPIRING SOON: {days_left} days remaining!")
    else:
        output.append(f"  Days Left    : {days_left} ✓")

    # SANs
    sans = [item[1] for item in cert_data.get('subjectAltName', []) if item[0] == 'DNS']
    output.append(f"\n  Subject Alt Names ({len(sans)}):")
    for san in sans[:20]:
        output.append(f"    - {san}")
    if len(sans) > 20:
        output.append(f"    ... and {len(sans) - 20} more")

    # --- TLS Protocol and Cipher ---
    output.append(f"\n[TLS PROTOCOL & CIPHER]")
    output.append(f"  Protocol     : {tls_version_used}")
    output.append(f"  Cipher Suite : {cipher[0] if cipher else 'Unknown'}")
    output.append(f"  Key Bits     : {cipher[2] if cipher else 'Unknown'}")

    # Weak protocol testing
    output.append(f"\n[WEAK PROTOCOL TESTING]")
    for proto in WEAK_PROTOCOLS:
        try:
            result = _test_protocol(domain, proto)
            if result:
                output.append(f"  ⚠️  {proto}: ACCEPTED — Server supports deprecated protocol!")
            else:
                output.append(f"  {proto}: Rejected ✓")
        except Exception:
            output.append(f"  {proto}: Could not test.")

    # --- Certificate Transparency Logs ---
    output.append(f"\n[CERTIFICATE TRANSPARENCY LOGS]")
    jitter(0.3, 0.6)
    ct_count = _get_ct_log_count(domain, session)
    output.append(f"  Total historical certs in CT logs: {ct_count}")
    if ct_count > 50:
        output.append(f"  Tip: Visit https://crt.sh/?q={domain} to review full certificate history.")

    try:
        with open(f"{save_path}/ssl_info.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
    except Exception as e:
        print(Fore.RED + f"  [-] SSL save error: {e}")

    exp_status = "EXPIRED" if expired else f"{days_left}d left"
    print(Fore.GREEN + f"  [+] SSL scan complete. Cert by '{issued_by}', TLS: {tls_version_used}, Expiry: {exp_status}")
