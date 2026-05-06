import requests
import re
import os
import subprocess
from colorama import Fore

HEADERS = {'User-Agent': 'Mozilla/5.0 (WebFox/4.0)'}

TECH_SIGS = {
    # CMS
    "WordPress"       : [r'wp-content', r'wp-includes', r'wordpress'],
    "Joomla"          : [r'joomla', r'/components/com_'],
    "Drupal"          : [r'drupal', r'/sites/default/files'],
    "Magento"         : [r'magento', r'Mage\.Cookies'],
    "Shopify"         : [r'cdn\.shopify\.com', r'Shopify\.theme'],
    "Ghost"           : [r'ghost\.org', r'/ghost/api/'],
    "Wix"             : [r'wix\.com', r'wixstatic\.com'],
    "Squarespace"     : [r'squarespace\.com', r'static\.squarespace\.com'],
    "OpenCart"        : [r'route=common', r'OpenCart'],
    "PrestaShop"      : [r'prestashop', r'/modules/'],
    # Frameworks / Languages
    "React"           : [r'react-dom', r'__reactFiber', r'data-reactroot'],
    "Vue.js"          : [r'vue\.min\.js', r'__vue__'],
    "Angular"         : [r'ng-version', r'angular\.min\.js'],
    "Next.js"         : [r'_next/static', r'__NEXT_DATA__'],
    "Nuxt.js"         : [r'__nuxt', r'_nuxt/'],
    "Laravel"         : [r'laravel_session'],
    "Django"          : [r'csrfmiddlewaretoken', r'django'],
    "Rails"           : [r'authenticity_token', r'rails'],
    "Express"         : [r'X-Powered-By.*Express'],
    # Web servers
    "Nginx"           : [r'nginx'],
    "Apache"          : [r'apache'],
    "IIS"             : [r'microsoft-iis', r'iis'],
    "Caddy"           : [r'caddy'],
    "LiteSpeed"       : [r'litespeed', r'lsphp'],
    # CDN / Cloud
    "Cloudflare"      : [r'cloudflare', r'cf-ray'],
    "Fastly"          : [r'fastly'],
    "Varnish"         : [r'x-varnish'],
    "AWS CloudFront"  : [r'x-amz-cf-id'],
    "Vercel"          : [r'x-vercel'],
    "Netlify"         : [r'netlify'],
    # Analytics
    "Google Analytics": [r'google-analytics\.com', r'gtag\(', r'UA-\d+'],
    "Google Tag Manager": [r'googletagmanager\.com', r'GTM-'],
    "Facebook Pixel"  : [r'connect\.facebook\.net', r'fbq\('],
    # JS Libraries
    "jQuery"          : [r'jquery[\.\-]', r'jQuery'],
    "Bootstrap"       : [r'bootstrap\.min\.js', r'bootstrap\.min\.css'],
    "Tailwind"        : [r'tailwindcss', r'tailwind\.config'],
    # Payments
    "Stripe"          : [r'stripe\.com/v\d', r'pk_live_', r'pk_test_'],
    "PayPal"          : [r'paypalobjects\.com'],
}

INTERESTING_PATHS = [
    "/robots.txt", "/sitemap.xml", "/.git/HEAD", "/.env",
    "/wp-login.php", "/admin", "/phpmyadmin", "/login",
    "/.htaccess", "/config.php", "/api/v1", "/graphql",
    "/swagger.json", "/openapi.json", "/.well-known/security.txt",
    "/actuator/health", "/server-status", "/.DS_Store",
    "/backup.zip", "/dump.sql", "/web.config",
]


def _ttl_to_os(ttl):
    if ttl <= 64:  return "Linux / Unix / macOS"
    if ttl <= 128: return "Windows Server"
    return "Cisco / Solaris / Network Device"


def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Tech stack & OS fingerprinting for {domain}...")

    detected = {}
    server       = "Hidden"
    powered      = "Hidden"
    content_type = "N/A"
    x_aspnet     = "N/A"
    x_aspnetmvc  = "N/A"
    generator_val= "N/A"
    response     = None

    # ── HTTP fingerprinting ────────────────────────────────────────────────
    for proto in ["https", "http"]:
        try:
            response = requests.get(
                f"{proto}://{domain}",
                headers=HEADERS,
                timeout=15,
                allow_redirects=True
            )
            break
        except Exception:
            response = None

    if response is not None:
        body     = response.text[:60000]
        combined = body + str(response.headers).lower()

        for tech, patterns in TECH_SIGS.items():
            for pattern in patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    detected[tech] = True
                    break

        server        = response.headers.get("Server",          "Hidden")
        powered       = response.headers.get("X-Powered-By",    "Hidden")
        content_type  = response.headers.get("Content-Type",    "N/A")
        x_aspnet      = response.headers.get("X-AspNet-Version",    "N/A")
        x_aspnetmvc   = response.headers.get("X-AspNetMvc-Version", "N/A")

        gen_match = re.search(
            r'<meta[^>]+name=["\']generator["\'][^>]+content=["\'](.*?)["\']',
            body, re.IGNORECASE
        )
        generator_val = gen_match.group(1) if gen_match else "N/A"

    # ── OS detection via TTL ──────────────────────────────────────────────
    os_guess = "Unknown"
    try:
        param = '-n' if os.name == 'nt' else '-c'
        result = subprocess.run(
            ['ping', param, '1', domain],
            capture_output=True, text=True, timeout=8
        )
        ttl_match = re.search(r'ttl=(\d+)', result.stdout, re.IGNORECASE)
        if ttl_match:
            os_guess = _ttl_to_os(int(ttl_match.group(1)))
    except Exception:
        pass

    # Refine with Server header
    srv_lower = server.lower()
    if any(x in srv_lower for x in ["ubuntu", "debian", "centos", "fedora", "linux"]):
        os_guess = f"Linux ({server})"
    elif any(x in srv_lower for x in ["win", "iis", "microsoft"]):
        os_guess = f"Windows Server ({server})"

    # ── builtwith (optional) ──────────────────────────────────────────────
    bw_data = {}
    try:
        import builtwith
        bw_data = builtwith.parse(f"https://{domain}")
    except Exception:
        pass

    # ── Build report ──────────────────────────────────────────────────────
    lines = [
        f"TECHNOLOGY STACK REPORT: {domain}",
        "=" * 50,
        "",
        "[+] SERVER INFO:",
        "-" * 44,
        f"  Server Header  : {server}",
        f"  X-Powered-By   : {powered}",
        f"  Content-Type   : {content_type}",
        f"  ASP.NET Version: {x_aspnet}",
        f"  ASP.NET MVC    : {x_aspnetmvc}",
        f"  Meta Generator : {generator_val}",
        f"  OS Fingerprint : {os_guess}",
        "",
        "[+] DETECTED TECHNOLOGIES:",
        "-" * 44,
    ]

    if detected:
        for tech in sorted(detected.keys()):
            lines.append(f"  [+] {tech}")
    else:
        lines.append("  No specific technologies matched.")

    if bw_data:
        lines += ["", "[+] BUILTWITH ANALYSIS:", "-" * 44]
        for cat, tools in bw_data.items():
            lines.append(f"  {cat}: {', '.join(tools)}")

    # ── Interesting paths probe ────────────────────────────────────────────
    lines += ["", "[+] INTERESTING PATHS PROBE:", "-" * 44]
    exposed_count = 0
    for path in INTERESTING_PATHS:
        for proto in ["https", "http"]:
            try:
                r = requests.get(
                    f"{proto}://{domain}{path}",
                    headers=HEADERS,
                    timeout=6,
                    allow_redirects=False
                )
                code = r.status_code
                if code == 200:
                    lines.append(f"  [EXPOSED] {proto}://{domain}{path} — HTTP {code}")
                    exposed_count += 1
                elif code in (301, 302, 403):
                    lines.append(f"  [{code}]     {proto}://{domain}{path}")
                break
            except Exception:
                continue

    if exposed_count == 0:
        lines.append("  No obviously exposed paths found.")

    with open(f"{save_path}/technologies.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(Fore.GREEN + f"[+] Tech detection complete. {len(detected)} technologies, {exposed_count} exposed paths.")
