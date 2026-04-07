"""
WebFox — Enhanced JavaScript & Secret Scanner
Secret patterns, endpoint extraction, API key detection and source map discovery.

Author : Lucky | WebFox Recon Framework v4.0
"""
import requests
import re
from colorama import Fore
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.stealth import get_stealth_session, jitter

# Comprehensive secret / sensitive data patterns
SECRET_PATTERNS = {
    "Google API Key":         r"AIza[0-9A-Za-z\-_]{35}",
    "Google OAuth ID":        r"[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com",
    "AWS Access Key ID":      r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
    "AWS Secret Key":         r"(?i)aws.{0,20}(?:secret|key|token).{0,20}['\"][0-9a-zA-Z\/+]{40}['\"]",
    "Stripe Live Key":        r"sk_live_[0-9a-zA-Z]{24,34}",
    "Stripe Publishable Key": r"pk_live_[0-9a-zA-Z]{24,34}",
    "Stripe Test Key":        r"sk_test_[0-9a-zA-Z]{24,34}",
    "GitHub Token":           r"ghp_[0-9A-Za-z]{36}",
    "GitHub OAuth":           r"gho_[0-9A-Za-z]{36}",
    "Slack Token":            r"xox[baprs]\-[0-9]{12}\-[0-9]{12}\-[0-9a-zA-Z]{24}",
    "Slack Webhook":          r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}",
    "Mailchimp API":          r"[0-9a-f]{32}-us[0-9]{1,2}",
    "Twilio Auth Token":      r"SK[0-9a-fA-F]{32}",
    "SendGrid API Key":       r"SG\.[a-zA-Z0-9\-_]{22}\.[a-zA-Z0-9\-_]{43}",
    "Firebase URL":           r"https://[a-z0-9-]+\.firebaseio\.com",
    "Firebase Key":           r"AAAA[A-Za-z0-9_-]{7}:[A-Za-z0-9_-]{140}",
    "Heroku API Key":         r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
    "JWT Token":              r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
    "RSA Private Key":        r"-----BEGIN RSA PRIVATE KEY-----",
    "Private Key (Generic)":  r"-----BEGIN PRIVATE KEY-----",
    "Generic API Key":        r"(?i)(?:api[_\-]?key|apikey|api_token|access_token|auth_token|secret_key|secret_token)\s*[:=]\s*['\"]([a-zA-Z0-9\-_\.]{20,})['\"]",
    "Generic Password":       r"(?i)(?:password|passwd|pwd)\s*[:=]\s*['\"]([^'\"]{8,})['\"]",
    "MongoDB URI":            r"mongodb(?:\+srv)?://[a-zA-Z0-9_\-:@./]{20,}",
    "PostgreSQL URI":         r"postgres(?:ql)?://[a-zA-Z0-9_\-:@./]{20,}",
    "MySQL URI":              r"mysql://[a-zA-Z0-9_\-:@./]{20,}",
    "Cloudinary URL":         r"cloudinary://[0-9]+:[A-Za-z0-9_]+@[a-z]+",
    "Mapbox Token":           r"pk\.eyJ1IjoiW2EtejAtOV8tXSsiLCJhIjoiW2EtekEtWjAtOV8tXSJ9[.][a-zA-Z0-9_-]+",
    "Shopify Token":          r"shpss_[a-fA-F0-9]{32}",
    "Discord Token":          r"(?:N[a-zA-Z0-9]{23}\.|M[a-zA-Z0-9]{23}\.)[a-zA-Z0-9-_]{27}",
    "Telegram Bot Token":     r"[0-9]{8,10}:[a-zA-Z0-9_-]{35}",
    "Source Map":             r"//# sourceMappingURL=(.+\.map)",
}

ENDPOINT_PATTERNS = [
    r'["\'](/api/[^\s"\'?<>]{2,80})["\']',
    r'["\'](/v[0-9]+/[^\s"\'?<>]{2,80})["\']',
    r'["\'](/[a-z][a-z0-9\-_/]{5,60}\.(?:json|xml|php|asp|aspx|jsp|do|action))["\']',
    r'fetch\(["\']([^"\'?<>]{5,80})["\']',
    r'axios\.(?:get|post|put|delete|patch)\(["\']([^"\'?<>]{5,80})["\']',
    r'(?:url|endpoint|api_url|apiUrl|baseUrl|base_url)\s*[:=]\s*["\']([^"\']{5,80})["\']',
]


def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Deep JS analysis and secret hunting for {domain}...")
    session = get_stealth_session()

    output = [f"JAVASCRIPT & SECRET ANALYSIS: {domain}", "=" * 50]

    # Get homepage to find JS files
    js_files = []
    base_url = f"https://{domain}"
    homepage_text = ""

    for proto in ["https", "http"]:
        base_url = f"{proto}://{domain}"
        try:
            r = session.get(base_url, timeout=15, verify=False)
            homepage_text = r.text
            break
        except Exception:
            continue

    if not homepage_text:
        output.append("[-] Could not fetch homepage for JS analysis.")
        with open(f"{save_path}/js_analysis.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        return

    # Find all JS files in page source
    js_refs = re.findall(r'src=["\'](.*?\.js(?:\?[^"\']*)?)["\']', homepage_text, re.IGNORECASE)
    js_refs += re.findall(r'(https?://[^\s"\'<>]+?\.js(?:\?[^\s"\'<>]*)?)', homepage_text)
    unique_js = list(set(js_refs))

    # Normalize JS URLs
    normalized_js = []
    for js in unique_js:
        js = js.split("?")[0]  # strip query params for dedup
        if js.startswith("//"):
            normalized_js.append("https:" + js)
        elif js.startswith("/"):
            normalized_js.append(base_url + js)
        elif js.startswith("http"):
            normalized_js.append(js)
        else:
            normalized_js.append(base_url + "/" + js)

    # Deduplicate
    normalized_js = list(set(normalized_js))
    print(Fore.BLUE + f"  > Found {len(normalized_js)} unique JS files. Deep scanning...")

    found_secrets = []
    found_endpoints = set()
    found_source_maps = []
    scanned_count = 0

    for js_url in normalized_js[:30]:  # cap at 30 files to avoid being noisy
        try:
            jitter(0.1, 0.4)
            content = session.get(js_url, timeout=12, verify=False).text
            js_name = js_url.split("/")[-1][:50]
            scanned_count += 1

            # Secret patterns
            for name, pattern in SECRET_PATTERNS.items():
                if name == "Source Map":
                    maps = re.findall(pattern, content)
                    for m in maps:
                        found_source_maps.append(f"{js_url} -> {m}")
                    continue
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    if len(match) > 8:  # Skip very short false positives
                        info = f"  TYPE: {name}\n  KEY : {match[:120]}\n  SRC : {js_name}"
                        found_secrets.append(info)
                        print(Fore.RED + f"  [!!!] SECRET: {name} in {js_name}")

            # Endpoint patterns
            for ep_pattern in ENDPOINT_PATTERNS:
                matches = re.findall(ep_pattern, content)
                for m in matches:
                    if isinstance(m, tuple):
                        m = m[0]
                    found_endpoints.add(m)

        except Exception:
            continue

    # Build output
    output.append(f"\n  JS Files Found  : {len(normalized_js)}")
    output.append(f"  JS Files Scanned: {scanned_count}")

    output.append(f"\n\n{'⚠️  SECRETS FOUND' if found_secrets else '[SECRETS]'} ({len(found_secrets)}):")
    output.append("-" * 30)
    if found_secrets:
        for s in found_secrets:
            output.append(s)
            output.append("")
    else:
        output.append("  No secrets found in scanned JS files.")

    output.append(f"\n[SOURCE MAPS FOUND] ({len(found_source_maps)})")
    output.append("-" * 30)
    if found_source_maps:
        output.append("  ⚠️  Source maps expose original source code!")
        for sm in found_source_maps:
            output.append(f"  {sm}")
    else:
        output.append("  None found.")

    output.append(f"\n[EXTRACTED API ENDPOINTS] ({len(found_endpoints)})")
    output.append("-" * 30)
    sorted_endpoints = sorted(found_endpoints)
    for ep in sorted_endpoints[:100]:
        output.append(f"  {ep}")
    if len(sorted_endpoints) > 100:
        output.append(f"  ... and {len(sorted_endpoints) - 100} more.")

    try:
        with open(f"{save_path}/js_analysis.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
    except Exception as e:
        print(Fore.RED + f"  [-] JS analysis save error: {e}")

    print(Fore.GREEN + f"  [+] JS scan done. {len(found_secrets)} secrets, {len(found_endpoints)} endpoints, {len(found_source_maps)} source maps.")
