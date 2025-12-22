import dns.resolver, dns.zone, dns.query
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Dumping DNS Records...")
    results = []
    
    for r in ['A', 'MX', 'NS', 'TXT']:
        try:
            answers = dns.resolver.resolve(domain, r)
            for data in answers:
                line = f"{r}: {data}"
                print(Fore.GREEN + f"    > {line}")
                results.append(line)
        except: pass

    print(Fore.YELLOW + "[*] Checking Zone Transfer (AXFR)...")
    try:
        ns_records = dns.resolver.resolve(domain, 'NS')
        for ns in ns_records:
            target_ns = str(ns)
            try:
                ns_ip = dns.resolver.resolve(target_ns, 'A')[0].to_text()
                # Increased timeout to 60s for slow servers
                zone = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, timeout=60))
                if zone:
                    print(Fore.RED + f" [!!!] VULNERABLE: {target_ns}")
                    results.append(f"\n[!!!] AXFR SUCCESS: {target_ns}")
                    for n, node in zone.nodes.items(): results.append(f"{n} {node.to_text(n)}")
                    break
            except: pass
    except: pass

    with open(f"{save_path}/dns.txt", "w") as f: f.write("\n".join(results))

