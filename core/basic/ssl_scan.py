import ssl
import socket
import hashlib
import requests
from datetime import datetime
from colorama import Fore

HEADERS = {'User-Agent': 'Mozilla/5.0 (WebFox/4.0)'}


def _days_left(date_str):
    """Return integer days until expiry, or string 'Unknown'."""
    try:
        dt = datetime.strptime(date_str, r'%b %d %H:%M:%S %Y %Z')
        return (dt - datetime.utcnow()).days
    except Exception:
        return "Unknown"


def _fetch_cert(domain, port=443):
    """
    Returns (cert_dict, cert_bytes, cipher_tuple, tls_version_str) or raises.
    Tries strict verification first; if that fails, retries without verification
    so we can still report cert details even for broken chains.
    """
    for verify in (True, False):
        try:
            ctx = ssl.create_default_context()
            if not verify:
                ctx.check_hostname = False
                ctx.verify_mode    = ssl.CERT_NONE
            with socket.create_connection((domain, port), timeout=10) as raw:
                with ctx.wrap_socket(raw, server_hostname=domain) as s:
                    return (
                        s.getpeercert(),
                        s.getpeercert(binary_form=True),
                        s.cipher(),
                        s.version(),
                        verify,          # True = verified OK
                    )
        except Exception:
            continue
    raise RuntimeError("Could not establish TLS connection on port 443 or 8443")


def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Running SSL/TLS deep inspection for {domain}...")
    lines = [f"SSL/TLS INSPECTION REPORT: {domain}", "=" * 52]

    # ── Connect ────────────────────────────────────────────────────────────
    try:
        cert, cert_bin, cipher, tls_ver, verified = _fetch_cert(domain)
    except Exception as e:
        lines.append(f"\n[-] Could not establish TLS connection: {e}")
        with open(f"{save_path}/ssl_info.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(Fore.RED + f"[-] SSL scan failed for {domain}: {e}")
        return

    if not verified:
        lines.append("\n[!] CERTIFICATE CHAIN VERIFICATION FAILED — untrusted / self-signed")

    # ── Certificate details ────────────────────────────────────────────────
    subject = dict(x[0] for x in cert.get('subject', []))
    issuer  = dict(x[0] for x in cert.get('issuer', []))
    not_before = cert.get('notBefore', 'N/A')
    not_after  = cert.get('notAfter',  'N/A')
    days       = _days_left(not_after)

    expiry_note = ""
    if isinstance(days, int):
        if days < 0:
            expiry_note = "  [CERTIFICATE EXPIRED!]"
        elif days < 14:
            expiry_note = f"  [CRITICAL: only {days} days remaining!]"
        elif days < 30:
            expiry_note = f"  [WARNING: {days} days remaining]"

    # SHA-256 fingerprint
    fp = "N/A"
    try:
        raw = hashlib.sha256(cert_bin).hexdigest().upper()
        fp  = ":".join(raw[i:i+2] for i in range(0, len(raw), 2))
    except Exception:
        pass

    lines += [
        "",
        "[+] CERTIFICATE DETAILS:",
        "-" * 44,
        f"  Issued To      : {subject.get('commonName', 'N/A')}",
        f"  Organization   : {subject.get('organizationName', 'N/A')}",
        f"  Country        : {subject.get('countryName', 'N/A')}",
        f"  Issued By      : {issuer.get('commonName', 'N/A')} ({issuer.get('organizationName', 'N/A')})",
        f"  Valid From     : {not_before}",
        f"  Valid Until    : {not_after}{expiry_note}",
        f"  Days Remaining : {days}",
        f"  Serial Number  : {cert.get('serialNumber', 'N/A')}",
        f"  Version        : {cert.get('version', 'N/A')}",
        f"  SHA-256 FP     : {fp}",
    ]

    # ── TLS handshake info ─────────────────────────────────────────────────
    lines += [
        "",
        "[+] TLS HANDSHAKE:",
        "-" * 44,
        f"  Protocol       : {tls_ver}",
        f"  Cipher Suite   : {cipher[0] if cipher else 'N/A'}",
        f"  Key Bits       : {cipher[2] if cipher and len(cipher) > 2 else 'N/A'}",
    ]

    # Weak protocol probe (TLS 1.0 / 1.1)
    weak = []
    for min_v, max_v, label in [
        (ssl.TLSVersion.TLSv1,   ssl.TLSVersion.TLSv1,   "TLS 1.0"),
        (ssl.TLSVersion.TLSv1_1, ssl.TLSVersion.TLSv1_1, "TLS 1.1"),
    ]:
        try:
            ctx_w = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx_w.check_hostname  = False
            ctx_w.verify_mode     = ssl.CERT_NONE
            ctx_w.minimum_version = min_v
            ctx_w.maximum_version = max_v
            with socket.create_connection((domain, 443), timeout=5) as raw:
                with ctx_w.wrap_socket(raw, server_hostname=domain):
                    weak.append(label)
        except Exception:
            pass

    if weak:
        lines.append(f"  Weak Protocols : [VULNERABLE] Accepts {', '.join(weak)}")
    else:
        lines.append("  Weak Protocols : [OK] TLS 1.0 / 1.1 not accepted")

    # ── Subject Alt Names ──────────────────────────────────────────────────
    sans = [v for t, v in cert.get('subjectAltName', []) if t == 'DNS']
    lines += ["", f"[+] SUBJECT ALT NAMES ({len(sans)}):", "-" * 44]
    for san in sorted(sans):
        lines.append(f"  - {san}")

    # ── CT logs via crt.sh ─────────────────────────────────────────────────
    lines += ["", "[+] CERTIFICATE TRANSPARENCY (crt.sh):", "-" * 44]
    try:
        r = requests.get(
            f"https://crt.sh/?q={domain}&output=json",
            timeout=12,
            headers=HEADERS
        )
        if r.status_code == 200:
            seen  = set()
            count = 0
            for entry in r.json()[:200]:
                name = entry.get('name_value', '').strip()
                if name and name not in seen:
                    seen.add(name)
                    exp   = entry.get('not_after', '')[:10]
                    issn  = entry.get('issuer_name', '')[:50]
                    lines.append(f"  [{exp}] {name:<40} via {issn}")
                    count += 1
                    if count >= 20:
                        lines.append("  ... (truncated, see crt.sh for full list)")
                        break
            if count == 0:
                lines.append("  No CT entries found.")
        else:
            lines.append(f"  crt.sh returned HTTP {r.status_code}")
    except Exception as e:
        lines.append(f"  CT lookup failed: {e}")

    with open(f"{save_path}/ssl_info.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    status = (f"EXPIRED" if isinstance(days, int) and days < 0
              else f"{days} days left" if isinstance(days, int)
              else "unknown expiry")
    print(Fore.GREEN + f"[+] SSL scan complete: {tls_ver}, {status}, {len(sans)} SANs")
