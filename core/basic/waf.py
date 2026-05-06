import requests
import re
import subprocess
import os
from colorama import Fore

HEADERS = {'User-Agent': 'Mozilla/5.0 (WebFox/3.0)'}

# Signature database
WAF_SIGS = {
    "Cloudflare"          : ["cf-ray", "cloudflare", "__cfduid", "cf-cache-status", "cf-request-id"],
    "Akamai"              : ["akamai", "akamaighost", "x-akamai-transformed", "x-check-cacheable"],
    "AWS WAF"             : ["awselb", "awsalb", "x-amzn-requestid", "x-amzn-trace-id"],
    "Imperva Incapsula"   : ["incap-ses", "visid_incap", "incapsula", "x-iinfo"],
    "F5 BIG-IP"           : ["bigip", "f5-", "x-wa-info", "x-cnection"],
    "Google Cloud Armor"  : ["x-goog-", "google-cloud-armor"],
    "Sucuri"              : ["sucuri", "x-sucuri-id", "x-sucuri-cache"],
    "ModSecurity"         : ["mod_security", "modsecurity", "x-modsecurity"],
    "Barracuda"           : ["barracuda_", "barra"],
    "Fortinet FortiWeb"   : ["fortigate", "fortiweb", "x-fw-"],
    "SonicWall"           : ["sonicwall", "x-sonicwall"],
    "Palo Alto"           : ["pan-os", "pan-", "x-global-transaction-id"],
    "Sophos"              : ["sophos", "x-astaro-"],
    "Citrix NetScaler"    : ["ns-server", "citrix", "x-citrix-"],
    "StackPath"           : ["stackpath", "x-sp-"],
    "ArvanCloud"          : ["arvancloud", "x-arvan-"],
    "Reblaze"             : ["x-reblaze-", "rbzid"],
    "Wallarm"             : ["x-wallarm-"],
    "NAXSI"               : ["naxsi"],
    "Radware"             : ["x-rdwr-"],
    "DenyAll"             : ["x-denyall-"],
    "Alibaba Cloud WAF"   : ["ali-cdn", "eagleid"],
    "Tencent Cloud WAF"   : ["x-cache-lookup", "x-nws-log-uuid"],
}

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "X-XSS-Protection",
    "Cross-Origin-Opener-Policy",
    "Cross-Origin-Resource-Policy",
    "Cross-Origin-Embedder-Policy",
]

def scan(domain, save_path):
    print(Fore.CYAN + f"[*] WAF detection & HTTP security header audit for {domain}...")
    lines = [f"WAF & SECURITY HEADERS REPORT: {domain}", "=" * 50]

    response = None
    used_url = None
    for proto in ["https", "http"]:
        try:
            url = f"{proto}://{domain}"
            response = requests.get(
                url,
                headers={**HEADERS, "Cache-Control": "no-cache"},
                timeout=15,
                allow_redirects=True
            )
            used_url = url
            break
        except: pass

    if not response:
        lines.append("[-] Could not connect to target.")
        with open(f"{save_path}/waf.txt", "w") as f:
            f.write("\n".join(lines))
        return

    # ── WAF Detection ─────────────────────────────────────────────────────
    raw_headers = str(response.headers).lower()
    raw_cookies = str(response.cookies.get_dict()).lower()
    body_lower  = response.text[:3000].lower()
    combined    = raw_headers + raw_cookies + body_lower

    detected_wafs = []
    for waf_name, sigs in WAF_SIGS.items():
        for sig in sigs:
            if sig in combined:
                detected_wafs.append(waf_name)
                break

    waf_result = ", ".join(sorted(set(detected_wafs))) if detected_wafs else "None Detected"

    lines += [
        "",
        f"[+] WAF DETECTION:",
        "-" * 40,
        f"  Status   : {'[DETECTED] ' + waf_result if detected_wafs else '[NONE] No WAF signatures matched'}",
        f"  Endpoint : {used_url}",
        f"  HTTP Code: {response.status_code}",
        f"  Server   : {response.headers.get('Server', 'Hidden')}",
        f"  Powered By: {response.headers.get('X-Powered-By', 'Hidden')}",
    ]

    # ── Security Headers Audit ────────────────────────────────────────────
    lines += ["", "[+] SECURITY HEADERS AUDIT:", "-" * 40]
    missing = []
    for hdr in SECURITY_HEADERS:
        val = response.headers.get(hdr)
        if val:
            lines.append(f"  [+] {hdr:<40}: {val[:80]}")
        else:
            lines.append(f"  [-] {hdr:<40}: MISSING")
            missing.append(hdr)

    if missing:
        lines.append(f"\n  [!] Missing {len(missing)} security headers — Attack surface exposed.")
    else:
        lines.append("\n  [OK] All standard security headers present.")

    # ── Cookie Security Audit ─────────────────────────────────────────────
    lines += ["", "[+] COOKIE SECURITY:", "-" * 40]
    if response.cookies:
        for cookie in response.cookies:
            flags = []
            if cookie.secure:     flags.append("Secure")
            if cookie.has_nonstandard_attr("HttpOnly"): flags.append("HttpOnly")
            samesite = cookie.get_nonstandard_attr("SameSite", "Not Set")
            flags.append(f"SameSite={samesite}")
            lines.append(f"  {cookie.name:<30}: {', '.join(flags)}")
    else:
        lines.append("  No cookies set on initial response.")

    # ── Full response headers dump ────────────────────────────────────────
    lines += ["", "[+] ALL RESPONSE HEADERS:", "-" * 40]
    for k, v in response.headers.items():
        lines.append(f"  {k}: {v}")

    with open(f"{save_path}/waf.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(Fore.GREEN + f"[+] WAF scan complete. WAF: {waf_result}. Missing headers: {len(missing)}")
