import requests
def scan(domain, save_path):
    try:
        r = requests.get(f"http://{domain}/sitemap.xml")
        if r.status_code==200:
            with open(f"{save_path}/sitemap.xml", "w") as f: f.write(r.text)
    except: pass
      
