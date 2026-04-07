"""
WebFox — Enhanced IP Geolocation & Network Info Scanner
Multi-API fallback, ASN analysis, reverse DNS, CDN/proxy detection,
hosting provider identification, and abuse contact lookup.

Author : Lucky | WebFox Recon Framework v4.0
"""
import socket
import requests
from colorama import Fore
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.stealth import get_stealth_session, jitter

CDN_ASNS = {
    "AS13335": "Cloudflare", "AS209242": "Cloudflare",
    "AS16509": "Amazon AWS", "AS14618": "Amazon AWS",
    "AS15169": "Google Cloud", "AS396982": "Google Cloud",
    "AS8075":  "Microsoft Azure", "AS8068": "Microsoft Azure",
    "AS54113": "Fastly CDN",
    "AS60068": "CDN77",
    "AS22822": "Limelight Networks",
    "AS20940": "Akamai",
    "AS36183": "Akamai",
}

def scan(domain, save_path):
    print(Fore.CYAN + f"[*] IP geolocation and ASN analysis for {domain}...")
    session = get_stealth_session()

    output = [f"IP & NETWORK INTELLIGENCE: {domain}", "=" * 50]

    # Resolve all IP addresses for the domain
    all_ips = []
    try:
        info = socket.getaddrinfo(domain, None)
        all_ips = list({addr[4][0] for addr in info})
        output.append(f"\n[DNS RESOLUTION]")
        output.append(f"  Domain: {domain}")
        output.append(f"  Resolved IPs ({len(all_ips)}): {', '.join(all_ips)}")
    except Exception as e:
        output.append(f"\n[-] DNS resolution failed: {e}")
        with open(f"{save_path}/ip_location.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        return

    primary_ip = all_ips[0] if all_ips else None
    if not primary_ip:
        return

    # Reverse DNS
    output.append(f"\n[REVERSE DNS]")
    try:
        rdns = socket.gethostbyaddr(primary_ip)[0]
        output.append(f"  PTR Record: {rdns}")
    except Exception:
        output.append(f"  PTR Record: None")

    # Main geo/ASN lookup via ip-api.com
    geo_data = {}
    try:
        jitter(0.2, 0.4)
        r = session.get(
            f"http://ip-api.com/json/{primary_ip}?fields=status,message,continent,country,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,query,proxy,hosting",
            timeout=12
        )
        geo_data = r.json()
    except Exception:
        pass

    output.append(f"\n[GEOLOCATION (Primary IP: {primary_ip})]")
    if geo_data and geo_data.get("status") == "success":
        output.append(f"  Continent  : {geo_data.get('continent', 'N/A')}")
        output.append(f"  Country    : {geo_data.get('country', 'N/A')}")
        output.append(f"  Region     : {geo_data.get('regionName', 'N/A')}")
        output.append(f"  City       : {geo_data.get('city', 'N/A')}")
        output.append(f"  Zip Code   : {geo_data.get('zip', 'N/A')}")
        output.append(f"  Timezone   : {geo_data.get('timezone', 'N/A')}")
        output.append(f"  Lat/Lon    : {geo_data.get('lat', 'N/A')}, {geo_data.get('lon', 'N/A')}")
        output.append(f"  Maps Link  : https://maps.google.com/?q={geo_data.get('lat')},{geo_data.get('lon')}")

        output.append(f"\n[NETWORK / ASN]")
        output.append(f"  ISP        : {geo_data.get('isp', 'N/A')}")
        output.append(f"  Organization: {geo_data.get('org', 'N/A')}")
        asn_raw = geo_data.get('as', '')
        output.append(f"  ASN        : {asn_raw}")
        output.append(f"  ASN Name   : {geo_data.get('asname', 'N/A')}")

        # Check if known CDN/Cloud ASN
        for asn_code, provider in CDN_ASNS.items():
            if asn_code in asn_raw:
                output.append(f"  ⚠️  CDN/Cloud Detected: Hosted on {provider} — Real server IP may be hidden.")
                break

        output.append(f"\n[PROXY / VPN / HOSTING DETECTION]")
        is_proxy = geo_data.get('proxy', False)
        is_hosting = geo_data.get('hosting', False)
        output.append(f"  Is Proxy/VPN: {'YES ⚠️' if is_proxy else 'No ✓'}")
        output.append(f"  Is Hosting  : {'YES (Datacenter / Cloud)' if is_hosting else 'No (Residential/Business)'}")

    else:
        output.append(f"  IP-API query failed or rate-limited. Raw IP: {primary_ip}")

    # Attempt ipinfo.io as secondary source
    jitter(0.3, 0.6)
    try:
        r2 = session.get(f"https://ipinfo.io/{primary_ip}/json", timeout=10)
        ipinfo = r2.json()
        output.append(f"\n[IPINFO.IO CROSS-CHECK]")
        output.append(f"  Hostname: {ipinfo.get('hostname', 'N/A')}")
        output.append(f"  City    : {ipinfo.get('city', 'N/A')}")
        output.append(f"  Region  : {ipinfo.get('region', 'N/A')}")
        output.append(f"  Country : {ipinfo.get('country', 'N/A')}")
        output.append(f"  Org/ASN : {ipinfo.get('org', 'N/A')}")
    except Exception:
        pass

    try:
        with open(f"{save_path}/ip_location.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
    except Exception as e:
        print(Fore.RED + f"  [-] IP save error: {e}")

    city = geo_data.get('city', 'N/A')
    country = geo_data.get('country', 'N/A')
    print(Fore.GREEN + f"  [+] IP scan done. Location: {city}, {country}. ASN: {geo_data.get('asname', 'N/A')}")
