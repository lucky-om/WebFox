import whois
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Fetching WHOIS Data...")
    try:
        w = whois.whois(domain)
        def clean_date(d):
            if isinstance(d, list): return str(d[0])
            return str(d)

        org = w.org or "Redacted"
        city = w.city or "Unknown"
        country = w.country or "Unknown"
        creation = clean_date(w.creation_date)
        expiry = clean_date(w.expiration_date)

        print(Fore.GREEN + f"    > Owner : {org}")
        print(Fore.GREEN + f"    > Expire: {expiry}")

        with open(f"{save_path}/whois_basic.txt", "w") as f:
            f.write(f"Organization : {org}\n")
            f.write(f"City         : {city}\n")
            f.write(f"Country      : {country}\n")
            f.write(f"Creation Date: {creation}\n")
            f.write(f"Expiry Date  : {expiry}\n")
    except Exception as e:
        print(Fore.RED + f"    > Whois failed: {e}")

