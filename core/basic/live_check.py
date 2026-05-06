import requests
import socket
from colorama import Fore

HEADERS = {'User-Agent': 'Mozilla/5.0 (WebFox/4.0)'}


def check(domain):
    """
    Returns True if the domain is reachable via HTTPS, HTTP, or DNS resolution.
    Tries multiple methods so a single firewall rule doesn't cause false-negatives.
    """
    print(Fore.CYAN + f"[*] Checking liveness for {domain}...")

    # 1. DNS resolution (fastest check)
    try:
        ip = socket.gethostbyname(domain)
        print(Fore.BLUE + f"    > DNS resolved: {domain} -> {ip}")
    except Exception:
        print(Fore.RED + f"[-] {domain} — DNS resolution FAILED. Not a valid domain.")
        return False

    # 2. HTTP/HTTPS connectivity
    for proto in ["https", "http"]:
        try:
            r = requests.get(
                f"{proto}://{domain}",
                headers=HEADERS,
                timeout=12,
                allow_redirects=True
            )
            print(Fore.GREEN + (
                f"[+] {domain} is ONLINE "
                f"(HTTP {r.status_code} via {proto.upper()}, "
                f"latency: {r.elapsed.total_seconds():.2f}s)"
            ))
            return True
        except requests.exceptions.SSLError:
            # SSL error means the server IS reachable, just cert issue
            print(Fore.YELLOW + f"    > {proto.upper()} SSL error — server is up but cert untrusted")
            return True
        except Exception:
            continue

    # 3. Raw TCP socket fallback (port 80 / 443)
    for port in (443, 80, 8080, 8443):
        try:
            s = socket.create_connection((domain, port), timeout=5)
            s.close()
            print(Fore.YELLOW + f"[+] {domain} — TCP port {port} open (HTTP unavailable but host is live)")
            return True
        except Exception:
            continue

    print(Fore.RED + f"[-] {domain} is UNREACHABLE on all protocols.")
    return False
