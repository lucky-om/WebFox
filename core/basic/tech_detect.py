import builtwith
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Detecting Technologies...")
    try:
        tech = builtwith.parse(f"http://{domain}")
        with open(f"{save_path}/technologies.txt", "w") as f:
            for cat, tools in tech.items():
                line = f"{cat}: {', '.join(tools)}"
                print(Fore.BLUE + f"    {line}")
                f.write(line + "\n")
    except: print(Fore.RED + "[-] Tech detection failed.")

