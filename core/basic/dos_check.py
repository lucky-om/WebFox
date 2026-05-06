import requests
import socket
import time
import os
from colorama import Fore

HEADERS = {'User-Agent': 'Mozilla/5.0 (WebFox/3.0)'}

def scan(domain, save_path):
    print(Fore.YELLOW + f"[*] HTTP response & DoS resistance check for {domain}...")
    lines = [f"HTTP RESPONSE & DOS RESISTANCE REPORT: {domain}", "=" * 55]

    # ── HTTP Response Timing ──────────────────────────────────────────────
    lines += ["", "[+] HTTP TIMING & AVAILABILITY:", "-" * 40]
    for proto in ["https", "http"]:
        for i in range(3):
            try:
                t0 = time.time()
                r = requests.get(f"{proto}://{domain}", headers=HEADERS, timeout=15)
                elapsed = round(time.time() - t0, 3)
                lines.append(f"  [{proto.upper()}] Probe {i+1}: HTTP {r.status_code} in {elapsed}s")
            except Exception as e:
                lines.append(f"  [{proto.upper()}] Probe {i+1}: FAILED ({e})")

    # ── Raw socket Slowloris-style probe ──────────────────────────────────
    lines += ["", "[+] SLOWLORIS RESISTANCE (port 80 / 443):", "-" * 40]
    for port, label in [(80, "HTTP"), (443, "HTTPS")]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(6)
            s.connect((domain, port))
            payload = f"GET / HTTP/1.1\r\nHost: {domain}\r\nX-Slowloris: test\r\n"
            s.send(payload.encode())
            try:
                s.settimeout(4)
                data = s.recv(4096)
                lines.append(f"  [{label}] Port {port}: Responsive — {len(data)} bytes received (OK)")
            except socket.timeout:
                lines.append(f"  [{label}] Port {port}: No response — Possibly vulnerable to Slowloris")
            s.close()
        except ConnectionRefusedError:
            lines.append(f"  [{label}] Port {port}: CLOSED")
        except Exception as e:
            lines.append(f"  [{label}] Port {port}: Error — {e}")

    # ── Rate limit check ──────────────────────────────────────────────────
    lines += ["", "[+] RATE LIMITING CHECK (10 rapid requests):", "-" * 40]
    try:
        status_codes = []
        for _ in range(10):
            try:
                r = requests.get(
                    f"https://{domain}",
                    headers=HEADERS,
                    timeout=5,
                    allow_redirects=False
                )
                status_codes.append(r.status_code)
            except: pass

        rate_limited = any(c in [429, 503] for c in status_codes)
        lines.append(f"  Status codes  : {status_codes}")
        if rate_limited:
            lines.append("  Rate Limiting : [ACTIVE] Server returned 429/503 — Protected")
        else:
            lines.append("  Rate Limiting : [ABSENT] No rate-limit detected — Potentially vulnerable to DDoS")
    except Exception as e:
        lines.append(f"  Rate limit test error: {e}")

    # ── Connection limit probe ─────────────────────────────────────────────
    lines += ["", "[+] TCP CONNECTION SATURATION (5 parallel):", "-" * 40]
    import threading
    results_conn = []
    def conn_test():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            r = s.connect_ex((domain, 80))
            results_conn.append("OK" if r == 0 else "REFUSED")
            s.close()
        except:
            results_conn.append("ERROR")

    threads = [threading.Thread(target=conn_test) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    lines.append(f"  Connection results: {results_conn}")

    with open(f"{save_path}/dos_vuln.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(Fore.GREEN + f"[+] DoS resistance check complete for {domain}.")
