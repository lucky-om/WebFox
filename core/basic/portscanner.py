import socket
import concurrent.futures
from colorama import Fore

# Comprehensive port list with service descriptions
TOP_PORTS = {
    21: "FTP",       22: "SSH",        23: "Telnet",     25: "SMTP",
    53: "DNS",       67: "DHCP",       69: "TFTP",       80: "HTTP",
    88: "Kerberos",  110: "POP3",      111: "RPC",       119: "NNTP",
    123: "NTP",      135: "RPC/DCOM",  137: "NetBIOS-NS",138: "NetBIOS-DGM",
    139: "NetBIOS",  143: "IMAP",      161: "SNMP",      162: "SNMP-Trap",
    179: "BGP",      389: "LDAP",      443: "HTTPS",     445: "SMB",
    465: "SMTPS",    587: "SMTP-Sub",  636: "LDAPS",     993: "IMAPS",
    995: "POP3S",    1080:"SOCKS",     1194:"OpenVPN",   1433:"MSSQL",
    1521:"Oracle",   1723:"PPTP",      2049:"NFS",       2375:"Docker",
    2376:"Docker-TLS",3306:"MySQL",    3389:"RDP",       4444:"Metasploit",
    5432:"PostgreSQL",5900:"VNC",      5901:"VNC-1",     6379:"Redis",
    6443:"K8s-API",  7001:"WebLogic",  8000:"HTTP-Alt",  8008:"HTTP-Alt",
    8080:"HTTP-Proxy",8443:"HTTPS-Alt",8888:"Jupyter",   9000:"PHP-FPM",
    9090:"Prometheus",9200:"Elasticsearch",9300:"Elasticsearch",
    10000:"Webmin",  11211:"Memcached",27017:"MongoDB",  27018:"MongoDB",
    50070:"Hadoop",  50075:"Hadoop",
}

# Ports with elevated risk when open
RISKY_PORTS = {23, 135, 137, 138, 139, 445, 1433, 2375, 3306, 3389, 4444,
               5432, 5900, 5901, 6379, 7001, 8888, 9000, 9200, 10000, 11211, 27017, 27018}

def _banner_grab(ip, port, timeout=2.0):
    """Try to grab a service banner."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.sendall(b"HEAD / HTTP/1.0\r\n\r\n" if port in (80, 8080, 8000, 8008) else b"\r\n")
        banner = s.recv(1024).decode("utf-8", errors="ignore").strip()
        s.close()
        return banner[:120] if banner else ""
    except:
        return ""

def scan(domain, threads, save_path):
    print(Fore.CYAN + f"[*] Port scanning {domain} ({len(TOP_PORTS)} ports, {threads} threads)...")

    try:
        ip = socket.gethostbyname(domain)
    except Exception as e:
        print(Fore.RED + f"[-] Could not resolve {domain}: {e}")
        return

    print(Fore.BLUE + f"    > Resolved to {ip}")

    open_ports = []

    def check(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.8)
        try:
            result = s.connect_ex((ip, port))
            if result == 0:
                service = TOP_PORTS.get(port, "Unknown")
                banner  = _banner_grab(ip, port)
                risk    = "[RISKY]" if port in RISKY_PORTS else ""
                return (port, service, banner, risk)
        except:
            pass
        finally:
            s.close()
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        futures = {ex.submit(check, p): p for p in TOP_PORTS}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)

    open_ports.sort(key=lambda x: x[0])

    lines = [
        f"PORT SCAN REPORT: {domain} ({ip})",
        "=" * 60,
        f"Scanned : {len(TOP_PORTS)} ports",
        f"Open    : {len(open_ports)} ports",
        "",
        f"{'PORT':<8}{'SERVICE':<18}{'RISK':<10}BANNER",
        "-" * 60,
    ]

    for port, service, banner, risk in open_ports:
        banner_short = f" | {banner[:60]}" if banner else ""
        lines.append(f"{port:<8}{service:<18}{risk:<10}{banner_short}")

    risky_open = [p for p, s, b, r in open_ports if p in RISKY_PORTS]
    if risky_open:
        lines += ["", f"[!] HIGH-RISK PORTS OPEN: {', '.join(str(p) for p in risky_open)}"]
        lines.append("    These ports may expose critical services. Investigate immediately.")

    with open(f"{save_path}/ports.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(Fore.GREEN + f"[+] Port scan complete. {len(open_ports)} open ports. {len(risky_open)} high-risk.")
