"""
WebFox — Enhanced Technology Stack Detector
Builtwith, HTTP header analysis, HTML fingerprinting, CMS detection,
JavaScript framework detection, and CDN detection.

Author : Lucky | WebFox Recon Framework v4.0
"""
import requests
import re
import os
import subprocess
from colorama import Fore
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.stealth import get_stealth_session, jitter

# CMS/Framework fingerprints from HTML and headers
CMS_FINGERPRINTS = {
    "WordPress":      ["/wp-content/", "/wp-includes/", "wp-json", 'generator.*wordpress'],
    "Joomla":         ["/media/jui/", "joomla!", "/components/com_"],
    "Drupal":         ["/sites/default/files", "drupal", 'generator.*drupal'],
    "Magento":        ["mage/cookies.js", "/skin/frontend/", "/js/mage/"],
    "Shopify":        ["cdn.shopify.com", "shopify.com/s/files", "myshopify.com"],
    "Wix":            ["wix.com/", "static.parastorage.com"],
    "Squarespace":    ["squarespace.com", "static1.squarespace.com"],
    "Ghost":          ["ghost.io", "/ghost/api/"],
    "Django":         ["csrfmiddlewaretoken", "django"],
    "Laravel":        ["laravel_session", "csrf_token", "laravel"],
    "React":          ["react.development.js", "react.production.min.js", "__REACT_DEVTOOLS"],
    "Vue.js":         ["vue.js", "vue.min.js", "__vue__"],
    "Angular":        ["ng-version", "angular.js", "angular.min.js"],
    "Next.js":        ["_next/static", "__NEXT_DATA__"],
    "Nuxt.js":        ["_nuxt/", "__NUXT__"],
    "Gatsby":         ["gatsby", "gatsby-image"],
    "Bootstrap":      ["bootstrap.min.css", "bootstrap.css"],
    "jQuery":         ["jquery.min.js", "jquery-"],
    "Cloudflare":     ["cloudflare", "cf-ray"],
    "Google Analytics": ["google-analytics.com/analytics", "gtag/js"],
    "Google Tag Mgr": ["googletagmanager.com", "GTM-"],
    "Hotjar":         ["hotjar.com/c/hotjar"],
    "Intercom":       ["intercom.io", "widget.intercom.io"],
    "Stripe":         ["js.stripe.com/v3"],
    "Recaptcha":      ["google.com/recaptcha", "recaptcha/api"],
}

CMS_HEADER_FINGERPRINTS = {
    "WordPress":  [("x-powered-by", "php"), ("x-pingback", "")],
    "Drupal":     [("x-drupal-cache", ""), ("x-generator", "drupal")],
    "Joomla":     [("x-content-encoded-by", "joomla")],
    "SharePoint": [("microsoftsharepoint", ""), ("sprequestguid", "")],
}

def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Detecting tech stack, CMS, and frameworks for {domain}...")
    session = get_stealth_session()

    output = [f"TECHNOLOGY STACK ANALYSIS: {domain}", "=" * 50]
    all_detected = {}

    # 1. Get HTML source for fingerprinting
    html_source = ""
    response_headers = {}
    cookies_str = ""
    for proto in ["https", "http"]:
        url = f"{proto}://{domain}"
        try:
            r = session.get(url, timeout=15, verify=False)
            html_source = r.text.lower()
            response_headers = {k.lower(): v.lower() for k, v in r.headers.items()}
            cookies_str = str(r.cookies.get_dict()).lower()
            break
        except Exception:
            continue

    jitter(0.2, 0.5)

    # 2. HTML fingerprinting
    detected_from_html = []
    for tech, patterns in CMS_FINGERPRINTS.items():
        for pattern in patterns:
            if re.search(pattern, html_source, re.IGNORECASE):
                detected_from_html.append(tech)
                break
    if detected_from_html:
        all_detected["CMS / Frameworks (HTML)"] = detected_from_html

    # 3. Header fingerprinting
    detected_from_headers = []
    for tech, sig_list in CMS_HEADER_FINGERPRINTS.items():
        for (header_key, value_fragment) in sig_list:
            h_val = response_headers.get(header_key, "")
            if value_fragment == "" and h_val:
                detected_from_headers.append(tech)
                break
            elif value_fragment and value_fragment in h_val:
                detected_from_headers.append(tech)
                break
    if detected_from_headers:
        all_detected["CMS / Frameworks (Headers)"] = detected_from_headers

    # 4. Server & language from headers
    server_hdr = response_headers.get("server", "")
    powered_by  = response_headers.get("x-powered-by", "")
    if server_hdr:
        all_detected["Web Server"] = [server_hdr]
    if powered_by:
        all_detected["Backend Language / Runtime"] = [powered_by]

    # 5. Cookie-based detection
    detected_from_cookies = []
    cookie_sigs = {
        "PHP":         ["phpsessid"],
        "ASP.NET":     ["asp.net_sessionid", "aspxauth"],
        "Java/Tomcat": ["jsessionid"],
        "Ruby on Rails": ["_session_id"],
        "Django":      ["csrftoken", "sessionid"],
        "Laravel":     ["laravel_session"],
    }
    for tech, cookie_keys in cookie_sigs.items():
        for ck in cookie_keys:
            if ck in cookies_str:
                detected_from_cookies.append(tech)
                break
    if detected_from_cookies:
        all_detected["Backend (Session Cookies)"] = detected_from_cookies

    # 6. builtwith as supplementary
    try:
        import builtwith
        bw_data = builtwith.parse(f"http://{domain}")
        for category, tools in bw_data.items():
            if tools:
                cat_key = f"BuiltWith: {category}"
                all_detected[cat_key] = tools
    except Exception:
        pass

    # 7. OS Guess from TTL
    output.append(f"\n[OS FINGERPRINT via TTL]")
    try:
        param = '-n' if os.name == 'nt' else '-c'
        proc = subprocess.Popen(['ping', param, '1', domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = proc.communicate(timeout=8)
        ttl_match = re.search(r'ttl=(\d+)', out.decode('utf-8', errors='ignore'), re.IGNORECASE)
        if ttl_match:
            ttl = int(ttl_match.group(1))
            if ttl <= 64:
                os_guess = f"Linux / Unix (TTL={ttl})"
            elif ttl <= 128:
                os_guess = f"Windows Server (TTL={ttl})"
            else:
                os_guess = f"Solaris / Network Device (TTL={ttl})"
            output.append(f"  OS Guess: {os_guess}")
        else:
            output.append(f"  Could not determine OS from TTL.")
    except Exception:
        output.append(f"  Ping failed — could not determine OS.")

    # Build final output
    output.append(f"\n[DETECTED TECHNOLOGIES]")
    if all_detected:
        for category, items in all_detected.items():
            output.append(f"\n  [{category}]")
            for item in items:
                output.append(f"    - {item}")
    else:
        output.append("  No specific technologies detected.")

    # Meta tags extract
    output.append(f"\n[META TAG ANALYSIS]")
    meta_matches = re.findall(r'<meta[^>]+(name|property)=["\']([^"\']+)["\'][^>]+(content)=["\']([^"\']+)["\']', html_source[:50000])
    useful_meta_names = {'generator', 'author', 'description', 'framework', 'application-name'}
    for m in meta_matches:
        if m[1].lower() in useful_meta_names:
            output.append(f"  {m[1]}: {m[3][:100]}")

    try:
        with open(f"{save_path}/technologies.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
    except Exception as e:
        print(Fore.RED + f"  [-] Tech save error: {e}")

    count = sum(len(v) for v in all_detected.values())
    print(Fore.GREEN + f"  [+] Tech detection done. {count} technologies found across {len(all_detected)} categories.")
