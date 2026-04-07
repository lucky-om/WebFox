"""
WebFox — HTTP Security Headers Scanner
Checks response headers for missing or misconfigured security settings.
Detects Click-jacking, CORS, HSTS, CSP, XSS issues.

Author : Lucky | WebFox Recon Framework v4.0
"""
import requests
from colorama import Fore
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.stealth import get_stealth_session, jitter

# Headers we need to check, what to look for, and what it means if missing
SECURITY_HEADERS = {
    "Strict-Transport-Security": {
        "check": lambda v: len(v) > 0,
        "severity": "HIGH",
        "desc": "HSTS missing. Browser may downgrade to HTTP — enables MITM attacks."
    },
    "Content-Security-Policy": {
        "check": lambda v: len(v) > 0,
        "severity": "HIGH",
        "desc": "CSP missing. XSS attacks are not mitigated."
    },
    "X-Frame-Options": {
        "check": lambda v: v.upper() in ("DENY", "SAMEORIGIN"),
        "severity": "MEDIUM",
        "desc": "Clickjacking protection missing. Attackers can embed the site in an iframe."
    },
    "X-Content-Type-Options": {
        "check": lambda v: v.lower() == "nosniff",
        "severity": "MEDIUM",
        "desc": "MIME-type sniffing not blocked. Enables content injection attacks."
    },
    "Referrer-Policy": {
        "check": lambda v: len(v) > 0,
        "severity": "LOW",
        "desc": "Referrer-Policy missing. Internal URLs may leak to external sites."
    },
    "Permissions-Policy": {
        "check": lambda v: len(v) > 0,
        "severity": "LOW",
        "desc": "Permissions-Policy missing. Site may have unnecessary access to camera/mic/geo."
    },
    "Access-Control-Allow-Origin": {
        "check": lambda v: v != "*",
        "severity": "HIGH",
        "desc": "CORS wildcard (*) detected! Any origin can read responses from this server."
    },
    "X-XSS-Protection": {
        "check": lambda v: "1" in v,
        "severity": "LOW",
        "desc": "Browser-level XSS filter not enabled (legacy header, but still useful)."
    },
    "Cross-Origin-Opener-Policy": {
        "check": lambda v: len(v) > 0,
        "severity": "MEDIUM",
        "desc": "COOP missing. Cross-origin attacks like Spectre may leak memory."
    },
}

def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Scanning HTTP Security Headers for {domain}...")
    session = get_stealth_session()

    result_lines = [f"HTTP SECURITY HEADER AUDIT: {domain}\n{'='*50}\n"]
    
    findings = {"PASS": [], "WARN": [], "FAIL": [], "INFO": []}
    response_headers_raw = ""

    urls_to_try = [f"https://{domain}", f"http://{domain}"]
    r = None
    for url in urls_to_try:
        try:
            r = session.get(url, timeout=15, allow_redirects=True, verify=False)
            break
        except Exception:
            continue

    if not r:
        print(Fore.RED + f"  [-] Could not connect to {domain} for header scan.")
        return

    jitter()
    response_headers_raw = "\n".join(f"  {k}: {v}" for k, v in r.headers.items())
    
    # Check each security header
    for header, config in SECURITY_HEADERS.items():
        val = r.headers.get(header, "")
        if val:
            try:
                ok = config["check"](val)
            except Exception:
                ok = False
            
            if ok:
                findings["PASS"].append(f"[✓] {header}: {val}")
            else:
                findings["WARN"].append(
                    f"[!] {header}: MISCONFIGURED (value={val}) | {config['severity']} | {config['desc']}"
                )
        else:
            sev = config["severity"]
            if sev == "HIGH":
                findings["FAIL"].append(f"[✗] {header}: MISSING | {sev} | {config['desc']}")
            else:
                findings["WARN"].append(f"[~] {header}: MISSING | {sev} | {config['desc']}")

    # Server version disclosure detection
    server_header = r.headers.get("Server", "")
    if server_header:
        findings["INFO"].append(f"[i] Server Disclosure: {server_header}")
        print(Fore.YELLOW + f"  [!] Server Version Exposed: {server_header}")

    x_powered = r.headers.get("X-Powered-By", "")
    if x_powered:
        findings["INFO"].append(f"[i] X-Powered-By Disclosure: {x_powered}")
        print(Fore.YELLOW + f"  [!] Tech Disclosure: X-Powered-By: {x_powered}")

    # Write to file  
    result_lines.append(f"\n--- FAILED (HIGH RISK) ({len(findings['FAIL'])}) ---\n")
    result_lines.extend(findings["FAIL"] or ["  None. ✓"])
    result_lines.append(f"\n--- WARNINGS ({len(findings['WARN'])}) ---\n")
    result_lines.extend(findings["WARN"] or ["  None. ✓"])
    result_lines.append(f"\n--- PASSED ({len(findings['PASS'])}) ---\n")
    result_lines.extend(findings["PASS"] or ["  None."])
    result_lines.append(f"\n--- INFO ---\n")
    result_lines.extend(findings["INFO"] or ["  None."])
    result_lines.append(f"\n\n--- RAW RESPONSE HEADERS ---\n{response_headers_raw}\n")

    fail_count = len(findings["FAIL"])
    warn_count = len(findings["WARN"])
    
    score = 100 - (fail_count * 15) - (warn_count * 5)
    score = max(score, 0)
    result_lines.append(f"\nSECURITY SCORE: {score}/100 ({fail_count} critical, {warn_count} warnings)\n")

    try:
        with open(f"{save_path}/http_headers.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(result_lines))
    except Exception as e:
        print(Fore.RED + f"  [-] Error saving header report: {e}")

    print(Fore.GREEN + f"  [+] Header scan done. Score: {score}/100 — {fail_count} failures, {warn_count} warnings.")
