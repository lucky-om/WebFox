"""
WebFox — Enhanced WAF & CDN Fingerprinting
More signature patterns, cookie analysis, error page analysis,
redirect chain inspection, and response timing analysis.

Author : Lucky | WebFox Recon Framework v4.0
"""
import requests
import time
from colorama import Fore
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.stealth import get_stealth_session, jitter

# Header-based WAF signatures (header key: value fragment)
HEADER_SIGS = {
    "Cloudflare":           [("cf-ray", ""), ("server", "cloudflare"), ("cf-cache-status", "")],
    "Akamai":               [("x-check-cacheable", ""), ("x-akamai-transformed", ""), ("akamai-ghost-ip", "")],
    "AWS WAF / ALB":        [("x-amzn-requestid", ""), ("x-amz-cf-id", ""), ("server", "awselb")],
    "Imperva / Incapsula":  [("x-iinfo", ""), ("set-cookie", "incap_ses"), ("set-cookie", "visid_incap")],
    "F5 BigIP":             [("server", "bigip"), ("set-cookie", "bigip"), ("x-wa-info", "")],
    "Sucuri":               [("x-sucuri-id", ""), ("server", "sucuri")],
    "Cloudfront (AWS)":     [("x-amz-cf-id", ""), ("via", "cloudfront")],
    "Google Cloud Armor":   [("server", "gws"), ("x-goog-", "")],
    "Fastly":               [("x-fastly-request-id", ""), ("fastly-io-warning", ""), ("via", "fastly")],
    "Azure Front Door":     [("x-azure-ref", ""), ("x-cache", "tcp_hit"), ("x-ms-request-id", "")],
    "Stackpath":            [("x-sp-url", ""), ("x-sp-cache-control", "")],
    "ArvanCloud":           [("ar-poweredby", ""), ("server", "arvancloud")],
    "ModSecurity":          [("server", "mod_security"), ("x-modsecurity", "")],
    "Barracuda":            [("barra_counter_session", ""), ("server", "barra")],
    "Fortinet FortiGate":   [("fortiwafsid", ""), ("server", "fortigate")],
    "Sophos UTM":           [("x-tmwd", ""), ("server", "sophos")],
    "Reblaze":              [("rbzid", ""), ("x-reblaze-protection", "")],
    "Radware AppWall":      [("x-rdwr-", ""), ("server", "appwall")],
    "Wallarm":              [("x-wallarm-node", "")],
    "Edgio / Verizon":      [("x-ec-custom-error", ""), ("x-varnish", "")],
    "Nginx":                [("server", "nginx")],
    "Apache":               [("server", "apache")],
    "LiteSpeed":            [("server", "litespeed")],
    "Microsoft IIS":        [("server", "microsoft-iis")],
    "OpenResty":            [("server", "openresty")],
}

# Body-based WAF detection (for 403/blocked pages)
BODY_SIGS = {
    "Cloudflare":       ["cloudflare", "cf-error"],
    "Imperva":          ["incapsula incident id"],
    "Sucuri":           ["sucuri cloudproxy"],
    "Barracuda":        ["barracuda web application firewall"],
    "FortiGate":        ["fortigate application control"],
    "Palo Alto":        ["pan-os", "threat id"],
    "SonicWall":        ["sonicwall network security appliance"],
    "AWS WAF":          ["aws waf"],
}


def _get_redirect_chain(url, session):
    """Follow a URL and return the full redirect chain."""
    chain = []
    try:
        history_r = session.get(url, timeout=15, allow_redirects=True, verify=False)
        for resp in history_r.history:
            chain.append(f"  {resp.status_code} -> {resp.headers.get('Location', '?')}")
        chain.append(f"  {history_r.status_code} -> (final) {history_r.url}")
    except Exception:
        pass
    return chain


def scan(domain, save_path):
    print(Fore.CYAN + f"[*] WAF / CDN / Web server fingerprinting for {domain}...")
    session = get_stealth_session()

    output = [f"WAF / CDN / SERVER FINGERPRINT: {domain}", "=" * 50]

    # Try to get both HTTP and HTTPS responses
    responses = {}
    for proto in ["https", "http"]:
        url = f"{proto}://{domain}"
        try:
            r = session.get(url, timeout=15, allow_redirects=True, verify=False)
            responses[proto] = r
        except Exception:
            pass

    if not responses:
        output.append("\n[-] Could not connect to target.")
        with open(f"{save_path}/waf.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        return

    # Use HTTPS if available, fallback HTTP
    r = responses.get("https") or responses.get("http")

    headers_lower = {k.lower(): v.lower() for k, v in r.headers.items()}
    cookies_str = str(r.cookies.get_dict()).lower()
    body_lower = r.text[:5000].lower()

    detected_waf = []
    detected_server = []

    for name, sigs in HEADER_SIGS.items():
        for (header_key, value_fragment) in sigs:
            h_val = headers_lower.get(header_key, "")
            if value_fragment == "" and h_val:
                detected_waf.append(name)
                break
            elif value_fragment and value_fragment in h_val:
                detected_waf.append(name)
                break
            elif value_fragment and value_fragment in cookies_str:
                detected_waf.append(name)
                break

    for name, patterns in BODY_SIGS.items():
        for pattern in patterns:
            if pattern in body_lower:
                if name not in detected_waf:
                    detected_waf.append(name)
                break

    detected_waf = list(dict.fromkeys(detected_waf))  # deduplicate

    output.append(f"\n[DETECTED WAF / CDN / SERVER]")
    if detected_waf:
        for d in detected_waf:
            output.append(f"  ✓ {d}")
    else:
        output.append("  None detected (may be custom or not present).")

    # --- Response Info ---
    output.append(f"\n[RESPONSE INFO]")
    output.append(f"  Final URL    : {r.url}")
    output.append(f"  Status Code  : {r.status_code}")
    output.append(f"  Response Time: {r.elapsed.total_seconds():.2f}s")
    output.append(f"  Content-Type : {r.headers.get('Content-Type', 'N/A')}")
    output.append(f"  Content-Length: {r.headers.get('Content-Length', 'N/A')}")

    # --- Redirect Chain ---
    jitter(0.2, 0.5)
    redirect_chain = _get_redirect_chain(f"http://{domain}", session)
    output.append(f"\n[HTTP->HTTPS REDIRECT CHAIN]")
    output.extend(redirect_chain if redirect_chain else ["  No redirects observed."])

    # --- Raw Headers ---
    output.append(f"\n[RAW RESPONSE HEADERS]")
    for k, v in r.headers.items():
        output.append(f"  {k}: {v}")

    try:
        with open(f"{save_path}/waf.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
    except Exception as e:
        print(Fore.RED + f"  [-] WAF save error: {e}")

    detected_str = ", ".join(detected_waf[:3]) if detected_waf else "None"
    print(Fore.GREEN + f"  [+] Fingerprint complete. Detected: {detected_str}")
