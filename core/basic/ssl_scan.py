import ssl, socket
from colorama import Fore
def scan(domain, save_path):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as s:
            with ctx.wrap_socket(s, server_hostname=domain) as ss:
                c = ss.getpeercert()
                issuer = dict(x[0] for x in c['issuer']).get('organizationName', 'Unknown')
                print(Fore.GREEN + f"    > SSL  : Issued by {issuer}")
                with open(f"{save_path}/ssl_info.txt", "w") as f:
                    f.write(f"Issuer: {issuer}\nExpiry: {c['notAfter']}")
    except: pass
