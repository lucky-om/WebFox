import requests
import re
import json
from colorama import Fore

HEADERS = {'User-Agent': 'Mozilla/5.0 (WebFox/3.0)'}

SECRET_PATTERNS = {
    "Google API Key"        : r'AIza[0-9A-Za-z\-_]{35}',
    "AWS Access Key ID"     : r'AKIA[0-9A-Z]{16}',
    "AWS Secret Key"        : r'(?i)aws.{0,20}secret.{0,20}["\']([A-Za-z0-9/+]{40})["\']',
    "Stripe Live Key"       : r'sk_live_[0-9a-zA-Z]{24,}',
    "Stripe Public Key"     : r'pk_live_[0-9a-zA-Z]{24,}',
    "Stripe Test Key"       : r'sk_test_[0-9a-zA-Z]{24,}',
    "SendGrid API Key"      : r'SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43}',
    "Twilio SID"            : r'AC[a-zA-Z0-9]{32}',
    "Twilio Auth Token"     : r'(?i)twilio.{0,20}["\']([a-f0-9]{32})["\']',
    "Mailchimp API"         : r'[0-9a-f]{32}-us[0-9]{1,2}',
    "GitHub Token"          : r'ghp_[a-zA-Z0-9]{36}',
    "GitLab Token"          : r'glpat-[a-zA-Z0-9\-_]{20}',
    "Slack Bot Token"       : r'xoxb-[0-9]+-[a-zA-Z0-9]+',
    "Slack Webhook"         : r'https://hooks\.slack\.com/services/[A-Z0-9/]+',
    "Firebase Config"       : r'firebaseapp\.com',
    "JWT Token"             : r'eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_.+/=]*',
    "Private Key Block"     : r'-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----',
    "Hardcoded Password"    : r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\']{6,})["\']',
    "Generic API Key"       : r'(?i)(api[_-]?key|apikey|api_secret)\s*[:=]\s*["\']([a-zA-Z0-9\-_]{20,})["\']',
    "MongoDB URI"           : r'mongodb(\+srv)?://[^"\'\s]{10,}',
    "Database URL"          : r'(?i)(mysql|postgres|postgresql|sqlite|mssql)://[^"\'\s]{10,}',
    "Google OAuth"          : r'[0-9]+-[a-z0-9_]+\.apps\.googleusercontent\.com',
    "reCAPTCHA Key"         : r'6L[a-zA-Z0-9_\-]{36,}',
    "Mailgun API"           : r'key-[a-zA-Z0-9]{32}',
    "Dropbox Token"         : r'sl\.[a-zA-Z0-9_\-]{130,}',
    "Shopify Token"         : r'shpss_[a-zA-Z0-9]{32}',
}

ENDPOINT_PATTERNS = [
    r'(?:"|\'|`)(/(?:api|v\d|graphql|admin|user|auth|login|upload|search|config|internal|private)[^"\'\s`<>]{0,100})(?:"|\'|`)',
    r'(?:"|\'|`)(/[a-zA-Z0-9_\-/]{2,80}\.(php|asp|aspx|cfm|do|action))(?:"|\'|`)',
    r'fetch\(["\']([^"\']{5,})["\']',
    r'axios\.(get|post|put|delete)\(["\']([^"\']{5,})["\']',
    r'\.ajax\(\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
    r'XMLHttpRequest.*?open\(["\'](?:GET|POST)["\'],\s*["\']([^"\']+)["\']',
]

def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Analysing JS files for endpoints & secrets on {domain}...")
    lines = [f"JAVASCRIPT INTELLIGENCE REPORT: {domain}", "=" * 55]

    # Collect JS file sources
    base_responses = []
    js_files_found = set()

    for proto in ["https", "http"]:
        try:
            r = requests.get(f"{proto}://{domain}", headers=HEADERS, timeout=15)
            base_responses.append(r)
            # Find inline + external JS
            for js in re.findall(r'src=["\']([^"\']*?\.js[^"\']*)["\']', r.text):
                js_files_found.add(js)
            break
        except: pass

    # Normalize JS URLs
    js_urls = set()
    for js in js_files_found:
        if js.startswith("//"):
            js_urls.add("https:" + js)
        elif js.startswith("/"):
            js_urls.add(f"https://{domain}{js}")
        elif js.startswith("http"):
            js_urls.add(js)
        else:
            js_urls.add(f"https://{domain}/{js}")

    # Also probe common chunk paths
    for common in ["/static/js/main.js", "/assets/index.js", "/app.js",
                   "/bundle.js", "/dist/app.js", "/js/app.js"]:
        for proto in ["https", "http"]:
            try:
                url = f"{proto}://{domain}{common}"
                r = requests.head(url, headers=HEADERS, timeout=5)
                if r.status_code == 200:
                    js_urls.add(url)
            except: pass

    lines.append(f"\n[+] JS files discovered: {len(js_urls)}")

    found_secrets = []
    found_endpoints = set()
    found_external_urls = set()
    total_size = 0

    for js_url in list(js_urls)[:30]:  # cap at 30 files
        try:
            r = requests.get(js_url, headers=HEADERS, timeout=10)
            content = r.text
            total_size += len(content)
            src_name = js_url.split("/")[-1][:50]

            # Secret scanning
            for name, pattern in SECRET_PATTERNS.items():
                for match in re.finditer(pattern, content):
                    val = match.group(0)[:120]
                    entry = f"TYPE: {name} | VALUE: {val} | FILE: {src_name}"
                    if entry not in found_secrets:
                        found_secrets.append(entry)
                        print(Fore.RED + f"    [!] SECRET FOUND: {name} in {src_name}")

            # Endpoint extraction
            for pattern in ENDPOINT_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    ep = match.group(1) if match.lastindex and match.group(1) else match.group(0)
                    ep = ep.strip("\"'`")
                    if ep and len(ep) > 2 and not ep.endswith(('.png','.jpg','.css','.ico','.svg','.woff')):
                        found_endpoints.add(ep[:200])

            # External URLs
            for url in re.findall(r'https?://[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}[^\s"\'<>]{0,150}', content):
                if domain not in url:
                    found_external_urls.add(url[:200])

        except: pass

    # ── Write report ──────────────────────────────────────────────────────
    lines += ["", f"[!] SECRETS / SENSITIVE DATA ({len(found_secrets)} found):", "-" * 50]
    if found_secrets:
        for s in found_secrets:
            lines.append(f"  >> {s}")
    else:
        lines.append("  No secrets detected.")

    lines += ["", f"[+] API ENDPOINTS / PATHS ({len(found_endpoints)} found):", "-" * 50]
    for ep in sorted(found_endpoints)[:200]:
        lines.append(f"  {ep}")

    lines += ["", f"[+] EXTERNAL URLS ({len(found_external_urls)} found):", "-" * 50]
    for url in sorted(found_external_urls)[:150]:
        lines.append(f"  {url}")

    lines += ["", f"[i] STATS:", f"  JS files analysed : {len(js_urls)}",
              f"  Total JS size     : {total_size // 1024} KB"]

    with open(f"{save_path}/js_analysis.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(Fore.GREEN + f"[+] JS scan complete. {len(found_secrets)} secrets, {len(found_endpoints)} endpoints found.")
