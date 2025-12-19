import builtwith
from colorama import Fore

def scan(domain, save_path):
    print(Fore.YELLOW + "[*] Detecting Technologies...")
    try:
        url = f"http://{domain}"
        tech = builtwith.parse(url)
        
        with open(f"{save_path}/technologies.txt", "w") as f:
            for category, tools in tech.items():
                line = f"{category}: {', '.join(tools)}"
                print(Fore.BLUE + f"    {line}")
                f.write(line + "\n")
        print(Fore.GREEN + "[✓] Tech stack saved.")
    except:
        print(Fore.RED + "[-] Tech detection failed.")
