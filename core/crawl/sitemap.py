import requests
import re
from colorama import Fore

HEADERS = {'User-Agent': 'Mozilla/5.0 (WebFox/3.0)'}

SITEMAP_CANDIDATES = [
    "sitemap.xml",
    "sitemap_index.xml",
    "sitemap-index.xml",
    "wp-sitemap.xml",
    "sitemap.txt",
    "sitemap.php",
    "sitemap1.xml",
    "news-sitemap.xml",
    "video-sitemap.xml",
    "image-sitemap.xml",
    "post-sitemap.xml",
    "page-sitemap.xml",
    "category-sitemap.xml",
]

def _extract_urls(xml_text):
    return re.findall(r'<loc>(.*?)</loc>', xml_text, re.IGNORECASE | re.DOTALL)

def _extract_nested_sitemaps(xml_text):
    return re.findall(r'<sitemap>\s*<loc>(.*?)</loc>', xml_text, re.IGNORECASE | re.DOTALL)

def scan(domain, save_path):
    print(Fore.CYAN + f"[*] Discovering and parsing sitemap for {domain}...")
    lines = [f"SITEMAP ANALYSIS: {domain}", "=" * 50]

    found_url = None
    raw_content = None

    # 1. Check robots.txt for Sitemap directive first
    for proto in ["https", "http"]:
        try:
            r = requests.get(f"{proto}://{domain}/robots.txt", headers=HEADERS, timeout=8)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    if line.strip().lower().startswith("sitemap:"):
                        sitemap_url = line.strip()[8:].strip()
                        lines.append(f"\n[+] Discovered via robots.txt: {sitemap_url}")
                        sr = requests.get(sitemap_url, headers=HEADERS, timeout=10)
                        if sr.status_code == 200:
                            found_url = sitemap_url
                            raw_content = sr.text
                        break
        except: pass
        if found_url:
            break

    # 2. Brute-force common names
    if not found_url:
        for name in SITEMAP_CANDIDATES:
            for proto in ["https", "http"]:
                try:
                    url = f"{proto}://{domain}/{name}"
                    r = requests.get(url, headers=HEADERS, timeout=8)
                    if r.status_code == 200 and len(r.content) > 50:
                        found_url = url
                        raw_content = r.text
                        lines.append(f"\n[+] Found: {url}")
                        break
                except: pass
            if found_url:
                break

    if not found_url or not raw_content:
        lines.append("\n[-] No sitemap found.")
        with open(f"{save_path}/sitemap.txt", "w") as f:
            f.write("\n".join(lines))
        print(Fore.YELLOW + "[-] No sitemap discovered.")
        return

    # ── Parse sitemap ─────────────────────────────────────────────────────
    all_urls = _extract_urls(raw_content)
    nested   = _extract_nested_sitemaps(raw_content)

    lines += [
        f"  Source        : {found_url}",
        f"  Direct URLs   : {len(all_urls)}",
        f"  Nested sitemaps: {len(nested)}",
    ]

    # Recurse nested sitemaps (max 5)
    for ns_url in nested[:5]:
        try:
            ns_r = requests.get(ns_url.strip(), headers=HEADERS, timeout=8)
            if ns_r.status_code == 200:
                sub_urls = _extract_urls(ns_r.text)
                all_urls.extend(sub_urls)
                lines.append(f"  [+] Nested {ns_url.strip()[:60]} → {len(sub_urls)} URLs")
        except: pass

    # Categorise URLs
    lines += ["", f"[+] ALL URLS ({len(all_urls)} total):", "-" * 40]

    categories = {"admin": [], "api": [], "auth": [], "other": []}
    for url in all_urls:
        u = url.strip().lower()
        if any(k in u for k in ["/admin", "/dashboard", "/panel"]):
            categories["admin"].append(url)
        elif any(k in u for k in ["/api/", "/v1/", "/v2/", "/graphql"]):
            categories["api"].append(url)
        elif any(k in u for k in ["/login", "/auth", "/signin", "/register"]):
            categories["auth"].append(url)
        else:
            categories["other"].append(url)

    for cat, urls in categories.items():
        if urls:
            lines.append(f"\n  [{cat.upper()}] ({len(urls)} URLs):")
            for u in urls[:50]:
                lines.append(f"    {u.strip()}")

    # Raw content saved separately
    ext = "xml" if "xml" in found_url else "txt"
    with open(f"{save_path}/sitemap.{ext}", "w", encoding="utf-8") as f:
        f.write(raw_content)

    with open(f"{save_path}/sitemap_analysis.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(Fore.GREEN + f"[+] Sitemap parsed. {len(all_urls)} total URLs across {1+len(nested)} sitemaps.")
