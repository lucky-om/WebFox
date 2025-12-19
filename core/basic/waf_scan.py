import requests
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Checking Firewall (WAF)...")
    try:
        url = f"http://{domain}"
        r = requests.get(url, timeout=5)
        headers = str(r.headers).lower()
        
        waf_name = "None"
        if "cloudflare" in headers: waf_name = "Cloudflare"
        elif "akamai" in headers: waf_name = "Akamai"
        elif "awselb" in headers: waf_name = "AWS ELB"
        elif "x-powered-by" in headers and "aws" in headers: waf_name = "AWS"
        
        if waf_name != "None":
            print(Fore.RED + f"[!] WAF DETECTED: {waf_name}")
        else:
            print(Fore.GREEN + "[+] No common WAF detected.")
            
        with open(f"{save_path}/waf.txt", "w") as f:
            f.write(f"WAF: {waf_name}\nHeaders: {r.headers}")
    except:
        print(Fore.RED + "[-] WAF Check failed (Connection Issue)")
