import requests
def scan(domain, save_path):
    try:
        r = requests.get(f"http://{domain}/robots.txt", timeout=10)
        if r.status_code == 200:
            with open(f"{save_path}/robots.txt", "w") as f: f.write(r.text)
    except: pass
