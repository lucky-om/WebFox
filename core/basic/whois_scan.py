import whois
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Fetching WHOIS Data...")
    try:
        w = whois.whois(domain)
        
        # Date aur List values ko clean karne ke liye helper function
        def clean(val):
            if isinstance(val, list): return str(val[0])
            if val is None: return "Unknown"
            return str(val)

        org = w.org or "Redacted"
        city = w.city or "Unknown"
        country = w.country or "Unknown"
        registrar = w.registrar or "Unknown"  # <--- YAHAN HAI REGISTRAR
        creation = clean(w.creation_date)
        expiry = clean(w.expiration_date)

        # Terminal Output
        print(Fore.GREEN + f"    > Owner   : {org}")
        print(Fore.GREEN + f"    > Provider: {registrar}") # <--- AB YE PRINT HOGA (GoDaddy etc.)
        print(Fore.GREEN + f"    > Expire  : {expiry}")

        # File Save
        with open(f"{save_path}/whois_basic.txt", "w") as f:
            f.write(f"Organization : {org}\n")
            f.write(f"Registrar    : {registrar}\n") # <--- FILE ME BHI SAVE HOGA
            f.write(f"City         : {city}\n")
            f.write(f"Country      : {country}\n")
            f.write(f"Creation Date: {creation}\n")
            f.write(f"Expiry Date  : {expiry}\n")
            
    except Exception as e:
        print(Fore.RED + f"    > Whois failed: {e}")
