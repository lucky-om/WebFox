import ssl, socket
from colorama import Fore

def scan(domain, save_path):
    try:
        ctx = ssl.create_default_context()
        # Increased Timeout
        with socket.create_connection((domain, 443), timeout=30) as s:
            with ctx.wrap_socket(s, server_hostname=domain) as ss:
                c = ss.getpeercert()
                issuer = dict(x[0] for x in c['issuer']).get('organizationName', 'Unknown')
                sans = [i[1] for i in c.get('subjectAltName', []) if i[0] == 'DNS']
                
                print(Fore.GREEN + f"    > Issuer: {issuer}")
                print(Fore.CYAN + f"    > SANs: Found {len(sans)} linked domains")
                
                with open(f"{save_path}/ssl_info.txt", "w") as f:
                    f.write(f"Issuer: {issuer}\nExpiry: {c['notAfter']}\n\n[SANs]\n")
                    f.write("\n".join(sans))
    except: pass

