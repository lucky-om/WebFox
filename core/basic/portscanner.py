"""
WebFox — Enhanced Port Scanner with Service Banner Grabbing
Covers 50 important ports, grabs service banners and categorizes by risk level.

Author : Lucky | WebFox Recon Framework v4.0
"""
import socket
import threading
from urllib.parse import urlparse
from colorama import Fore, init

init(autoreset=True)

# Extended port list organized by risk category
PORT_LIST = {
    # Remote Access (HIGH RISK if exposed)
    22:   ("SSH",                "HIGH"),
    23:   ("Telnet",             "CRITICAL"),
    3389: ("RDP (Remote Desktop)","CRITICAL"),
    5900: ("VNC",                "CRITICAL"),
    5901: ("VNC Alt",            "HIGH"),
    512:  ("rexec",              "CRITICAL"),
    513:  ("rlogin",             "CRITICAL"),
    514:  ("rsh",                "CRITICAL"),

    # Web Servers
    80:   ("HTTP",               "LOW"),
    443:  ("HTTPS",              "LOW"),
    8000: ("HTTP Alt",           "MEDIUM"),
    8080: ("HTTP Proxy/Alt",     "MEDIUM"),
    8443: ("HTTPS Alt",          "MEDIUM"),
    8888: ("HTTP Alt 2",         "MEDIUM"),
    9000: ("PHP-FPM / Web",      "MEDIUM"),
    3000: ("Node.js / Dev",      "MEDIUM"),
    4000: ("Dev Server",         "MEDIUM"),
    5000: ("Dev / Flask",        "MEDIUM"),

    # File Transfer
    21:   ("FTP",                "HIGH"),
    20:   ("FTP Data",           "HIGH"),
    69:   ("TFTP",               "HIGH"),
    2049: ("NFS",                "HIGH"),

    # Email
    25:   ("SMTP",               "MEDIUM"),
    587:  ("SMTP Submission",    "LOW"),
    465:  ("SMTPS",              "LOW"),
    110:  ("POP3",               "MEDIUM"),
    995:  ("POP3S",              "LOW"),
    143:  ("IMAP",               "MEDIUM"),
    993:  ("IMAPS",              "LOW"),

    # DNS
    53:   ("DNS",                "MEDIUM"),

    # Databases (CRITICAL if publicly exposed)
    3306: ("MySQL",              "CRITICAL"),
    5432: ("PostgreSQL",         "CRITICAL"),
    1433: ("MSSQL",              "CRITICAL"),
    1521: ("Oracle DB",          "CRITICAL"),
    27017:("MongoDB",            "CRITICAL"),
    6379: ("Redis",              "CRITICAL"),
    11211:("Memcached",          "CRITICAL"),
    9200: ("Elasticsearch",      "CRITICAL"),
    5984: ("CouchDB",            "CRITICAL"),
    7474: ("Neo4j",              "HIGH"),

    # Message Queues / Infra
    5672: ("RabbitMQ AMQP",      "HIGH"),
    15672:("RabbitMQ Mgmt",      "HIGH"),
    9092: ("Kafka",              "HIGH"),
    2181: ("Zookeeper",          "HIGH"),
    2375: ("Docker API (HTTP!)", "CRITICAL"),
    2376: ("Docker API TLS",     "HIGH"),
    6443: ("Kubernetes API",     "HIGH"),

    # Network Services
    135:  ("MSRPC",              "HIGH"),
    139:  ("NetBIOS",            "HIGH"),
    445:  ("SMB",                "CRITICAL"),

    # Misc
    161:  ("SNMP",               "HIGH"),
    162:  ("SNMP Trap",          "MEDIUM"),
    389:  ("LDAP",               "HIGH"),
    636:  ("LDAPS",              "MEDIUM"),
    8161: ("ActiveMQ Admin",     "CRITICAL"),
}

RISK_COLOR = {
    "CRITICAL": Fore.RED,
    "HIGH":     Fore.YELLOW,
    "MEDIUM":   Fore.CYAN,
    "LOW":      Fore.GREEN,
}


def get_clean_ip(target):
    try:
        if "://" not in target:
            target = "http://" + target
        parsed = urlparse(target)
        hostname = parsed.netloc.split(":")[0]
        ip = socket.gethostbyname(hostname)
        return ip, hostname
    except Exception:
        return None, None


def grab_banner(ip, port, timeout=2):
    """Attempt to grab a service banner from an open port."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        # Send an HTTP-style request for web ports, else just wait for banner
        if port in (80, 8080, 8000, 8888, 3000, 4000, 5000, 9000):
            s.send(b"HEAD / HTTP/1.0\r\nHost: localhost\r\n\r\n")
        banner = s.recv(256).decode('utf-8', errors='ignore').strip()
        s.close()
        # Sanitize newlines
        return banner.replace("\r", " ").replace("\n", " ")[:150]
    except Exception:
        return ""


def scan(domain, threads, save_path):
    target_ip, clean_hostname = get_clean_ip(domain)

    if not target_ip:
        print(Fore.RED + f"  [-] Could not resolve: {domain}")
        return

    print(Fore.CYAN + f"  [*] Port scanning {clean_hostname} ({target_ip}) — {len(PORT_LIST)} ports...")

    results = []
    results_lock = threading.Lock()
    ports = list(PORT_LIST.keys())

    def check(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        try:
            result = s.connect_ex((target_ip, port))
            if result == 0:
                service, risk = PORT_LIST.get(port, ("Unknown", "LOW"))
                banner = grab_banner(target_ip, port)
                banner_str = f" | Banner: {banner}" if banner else ""
                line = {
                    "port": port,
                    "service": service,
                    "risk": risk,
                    "banner": banner,
                    "display": f"Port {port:<6}: OPEN | {service:<25} | Risk: {risk}{banner_str}",
                }
                with results_lock:
                    results.append(line)
        except Exception:
            pass
        finally:
            s.close()

    # Use threading to scan all ports in parallel
    thread_list = [threading.Thread(target=check, args=(p,)) for p in ports]
    for t in thread_list:
        t.daemon = True
        t.start()
    for t in thread_list:
        t.join(timeout=5)

    # Sort by risk seriousness then port number
    risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    results.sort(key=lambda x: (risk_order.get(x["risk"], 4), x["port"]))

    # Print critical ones immediately
    for r in results:
        color = RISK_COLOR.get(r["risk"], Fore.WHITE)
        print(color + f"  {r['display']}")

    # Write to file
    try:
        with open(f"{save_path}/ports.txt", "w", encoding="utf-8") as f:
            f.write(f"PORT SCAN RESULTS: {clean_hostname} ({target_ip})\n")
            f.write(f"Total ports checked: {len(PORT_LIST)}\n")
            f.write("=" * 50 + "\n\n")
            if results:
                for r in results:
                    f.write(r["display"] + "\n")
            else:
                f.write("No open ports found.\n")
    except Exception as e:
        print(Fore.RED + f"  [-] Port save error: {e}")

    critical_count = sum(1 for r in results if r["risk"] == "CRITICAL")
    print(Fore.GREEN + f"  [+] Port scan complete. {len(results)} open ({critical_count} critical) out of {len(PORT_LIST)} checked.")
