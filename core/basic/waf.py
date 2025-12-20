import requests
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Detecting Firewall (WAF)...")
    url = f"http://{domain}"
    waf_name = "None"
    
    # List of WAF signatures to check in Headers
    waf_signatures = {
        "Cloudflare": ["cf-ray", "cloudflare", "__cfduid", "cf-cache-status"],
        "Akamai": ["akamai", "x-akamai", "akamai-ghost", "ak_bmsc"],
        "AWS WAF": ["x-amz-cf-id", "aws-waf", "awselb"],
        "Imperva Incapsula": ["x-cdn", "incap-ses", "visid_incap"],
        "Barracuda": ["barra_counter_session", "bncookie"],
        "F5 BIG-IP": ["bigipserver", "f5_cspm"],
        "Google Cloud Armor": ["x-google-cloud-armor"],
        "Sucuri": ["x-sucuri", "sucuri_cloudproxy"],
        "StackPath": ["x-stackpath"],
        "ModSecurity": ["mod_security", "nypowermod"],
        "Fortinet": ["fortiwafsid"],
        "Citrix NetScaler": ["ns_af", "citrix_ns_id"],
        "Azure WAF": ["appgw-", "x-ms-application-gateway"]
    }

    try:
        # Send a normal request
        r = requests.get(url, timeout=10, allow_redirects=True)
        headers = str(r.headers).lower()
        cookies = str(r.cookies.get_dict()).lower()
        all_data = headers + cookies

        # Check against signatures
        detected = []
        for name, sigs in waf_signatures.items():
            for sig in sigs:
                if sig in all_data:
                    detected.append(name)
                    break
        
        if detected:
            waf_name = ", ".join(detected)
            print(Fore.RED + f"[!] WAF DETECTED: {waf_name}")
        else:
            print(Fore.GREEN + "[+] No common WAF detected.")

        # Save results
        with open(f"{save_path}/waf.txt", "w") as f:
            f.write(f"WAF: {waf_name}\n")
            f.write("-" * 20 + "\n")
            f.write("Raw Headers:\n")
            f.write(str(r.headers))

    except Exception as e:
        print(Fore.RED + f"[-] WAF Check failed: {e}")
