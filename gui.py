import streamlit as st
import os
import subprocess
import glob

st.set_page_config(page_title="WEBFOX RACON TOOL", layout="wide", page_icon="🦊")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Homenaje&display=swap');
    .stApp { background-color: #1a1a1a; }
    h1, h2, h3, h4, p, span, div, label { 
        color: #fff !important; 
        font-family: 'Homenaje', sans-serif !important; 
    }
    h1 { color: #f97316 !important; font-size: 1.5rem !important; }
    .stTextInput > div > div > input {
        background-color: #2a2a2a; 
        color: #ffffff; 
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        font-family: 'Homenaje', sans-serif;
    }
    .stButton > button {
        background-color: #f97316; 
        color: #ffffff !important;
        border: none; 
        border-radius: 4px;
        font-weight: bold;
        font-family: 'Homenaje', sans-serif;
        text-transform: uppercase;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #ea580c;
        color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab-list"] { 
        gap: 15px; 
        background-color: #252525;
        border-radius: 4px;
        padding: 8px;
    }
    .stTabs [data-baseweb="tab"] { 
        background-color: transparent; 
        border: none;
        color: #ffffff !important;
        font-family: 'Homenaje', sans-serif;
        text-transform: uppercase;
        font-size: 0.85rem;
        padding-left: 10px;
        padding-right: 10px;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #f97316 !important; 
        color: #000000 !important;
        border-radius: 4px;
    }
    [data-testid="stSidebar"] { background-color: #1e1e1e; border-right: 1px solid #2a2a2a; }
    .stTextArea textarea { background-color: #2a2a2a; color: #ffffff; border: 1px solid #3a3a3a; font-family: 'Homenaje', sans-serif; }
    .stCode { font-family: 'Courier New', monospace !important; }
</style>
""", unsafe_allow_html=True)

st.title("WEBFOX v10.0")
st.markdown("---")

with st.sidebar:
    st.header("TARGET SYSTEM")
    target = st.text_input("ENTER DOMAIN URL", placeholder="example.com")
    
    if st.button("EXECUTE FULL SCAN"):
        if target:
            with st.spinner(f"INFILTRATING {target}... PLEASE WAIT"):
                try:
                    subprocess.run(["python3", "test.py", target, "-scan"], check=True)
                    st.success("MISSION COMPLETE. DATA DOWNLOADED.")
                except subprocess.CalledProcessError:
                    st.error("EXECUTION FAILED. CHECK CONSOLE LOGS.")
                except FileNotFoundError:
                    st.error("CORE SCRIPT 'test.py' NOT FOUND.")

if target:
    report_path = os.path.join("reports", target)
    
    if os.path.exists(report_path):
        st.subheader(f"INTEL FOR: {target}")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "VISUALS", 
            "NETWORK", 
            "SECURITY", 
            "CRAWLING", 
            "LOGS"
        ])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### SERVER LOCATION")
                loc_file = f"{report_path}/ip_location.txt"
                if os.path.exists(loc_file):
                    st.code(open(loc_file).read(), language="yaml")
                else:
                    st.warning("NO LOCATION DATA")
            
            with col2:
                st.markdown("### OWNER INFO")
                whois_file = f"{report_path}/whois_basic.txt"
                if os.path.exists(whois_file):
                    st.code(open(whois_file).read(), language="yaml")
                else:
                    st.warning("NO WHOIS DATA")
            
            st.markdown("### SURVEILLANCE SNAPSHOTS")
            images = glob.glob(f"{report_path}/*.png")
            if images: 
                st.image(images, width=350)
            else:
                st.info("NO VISUALS CAPTURED")

        with tab2:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("### SUBDOMAINS")
                sub_file = f"{report_path}/subdomains.txt"
                if os.path.exists(sub_file):
                    with st.expander("VIEW SUBDOMAINS", expanded=True):
                        st.text_area("List", open(sub_file).read(), height=300, label_visibility="collapsed")
                else:
                    st.warning("NO SUBDOMAINS FOUND")
            
            with c2:
                st.markdown("### OPEN PORTS")
                port_file = f"{report_path}/ports.txt"
                if os.path.exists(port_file):
                    with st.expander("VIEW PORT MAP", expanded=True):
                        st.text_area("Map", open(port_file).read(), height=300, label_visibility="collapsed")
                else:
                    st.warning("NO PORTS DETECTED")
            
            with c3:
                st.markdown("### DNS RECORDS")
                dns_file = f"{report_path}/dns.txt"
                if os.path.exists(dns_file):
                    st.code(open(dns_file).read())
                else:
                    st.warning("NO DNS RECORDS")

        with tab3:
            st.markdown("### SECURITY INTEL")
            vuln_file = f"{report_path}/vulns.txt"
            if os.path.exists(vuln_file):
                st.text_area("Vulnerability Report", open(vuln_file).read(), height=400)
            else:
                st.info("NO SECURITY VULNERABILITIES LOGGED")
        
        with tab4:
            st.markdown("### CRAWLER DATA")
            crawl_file = f"{report_path}/crawl_map.txt"
            if os.path.exists(crawl_file):
                st.code(open(crawl_file).read())
            else:
                st.info("CRAWLER MAP EMPTY")

        with tab5:
            st.markdown("### SYSTEM LOGS")
            log_file = f"{report_path}/scan.log"
            if os.path.exists(log_file):
                st.code(open(log_file).read())
            else:
                st.info("NO SYSTEM LOGS AVAILABLE")
            
    else:
        st.info(f"TARGET '{target}' QUEUED. PLEASE EXECUTE SCAN.")
else:
    st.info("ENTER A DOMAIN AND CLICK 'EXECUTE SCAN' TO START.")
            "SECURITY", 
            "CRAWLING", 
            "LOGS"
        ])
        
        # Logic for tabs remains unchanged...
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### SERVER LOCATION")
                if os.path.exists(f"{report_path}/ip_location.txt"):
                    st.code(open(f"{report_path}/ip_location.txt").read(), language="yaml")
            with col2:
                st.markdown("### OWNER INFO")
                if os.path.exists(f"{report_path}/whois_basic.txt"):
                    st.code(open(f"{report_path}/whois_basic.txt").read(), language="yaml")
            st.markdown("### SURVEILLANCE SNAPSHOTS")
            images = glob.glob(f"{report_path}/*.png")
            if images: st.image(images, width=350)

        with tab2:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("### SUBDOMAINS")
                if os.path.exists(f"{report_path}/subdomains.txt"):
                    st.text_area("Found Subdomains", open(f"{report_path}/subdomains.txt").read(), height=300)
            with c2:
                st.markdown("### OPEN PORTS")
                if os.path.exists(f"{report_path}/ports.txt"):
                    st.text_area("Port Scan", open(f"{report_path}/ports.txt").read(), height=300)
            with c3:
                st.markdown("### DNS RECORDS")
                if os.path.exists(f"{report_path}/dns.txt"):
                    st.code(open(f"{report_path}/dns.txt").read())

        with tab3:
            st.markdown("### SECURITY INTEL")
            # Security content...
        
        with tab4:
            st.markdown("### CRAWLER DATA")
            # Crawler content...

        with tab5:
            st.markdown("### SYSTEM LOGS")
            # Log content...
            
    else:
        st.info("ENTER A DOMAIN AND CLICK 'EXECUTE SCAN' TO START.")    print(f"{Fore.CYAN}    Version : {Fore.WHITE}v11.0 Ultimate (File Save Fixed)")
    print(f"{Fore.CYAN}    System  : {Fore.WHITE}Android / Kali NetHunter\n")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("domain", nargs="?", help="Target Domain")
    parser.add_argument("-scan", action="store_true", help="Start the scan")
    parser.add_argument("-threads", type=int, default=100, help="Number of threads")
    args = parser.parse_args()

    if not args.domain:
        banner()
        type_effect("Usage: python3 test.py <domain> -scan", Fore.YELLOW)
        sys.exit()

    banner()
    
    # --- PATH FIX ---
    # Create absolute path for reports
    base_dir = os.getcwd()
    save_path = os.path.join(base_dir, "reports", args.domain)
    
    if not os.path.exists(save_path): 
        try:
            os.makedirs(save_path)
            print(f"{Fore.GREEN}[+] Created directory: {save_path}")
        except OSError as e:
            print(f"{Fore.RED}[!] Error creating directory: {e}")
            sys.exit()
    else:
        print(f"{Fore.YELLOW}[!] Directory exists: {save_path}")

    type_effect(f"[*] TARGET LOCKED: {args.domain}", Fore.GREEN)
    print("-" * 50)

    loading_bar("Establishing Connection")
    if not live_check.check(args.domain): 
        print(Fore.RED + "Target seems down.")
        sys.exit()

    if args.scan:
        print(Fore.WHITE + "\n--- [ PHASE 1: INTELLIGENCE GATHERING ] ---")
        loading_bar("Geolocating Server")
        ip_info.scan(args.domain, save_path)
        
        loading_bar("Extracting Ownership")
        whois_scan.scan(args.domain, save_path)
        
        loading_bar("Detecting Real IP (CF Bypass)")
        real_ip.scan(args.domain, save_path)
        
        loading_bar("Dumping DNS Zone")
        dns_scan.scan(args.domain, save_path)

        print(Fore.WHITE + "\n--- [ PHASE 2: VULNERABILITY MATRIX ] ---")
        loading_bar("Analyzing SSL/SANs")
        ssl_scan.scan(args.domain, save_path)
        
        loading_bar("Bypassing WAF / Headers")
        waf.scan(args.domain, save_path)
        
        loading_bar("Checking CORS Misconfig")
        cors_scan.scan(args.domain, save_path)
        
        loading_bar("Testing DoS Vulnerability")
        dos_check.scan(args.domain, save_path)
        
        loading_bar("Fingerprinting OS & Tech")
        tech_detect.scan(args.domain, save_path)
        
        loading_bar("Hunting SQL Injection")
        sqli_scan.scan(args.domain, save_path)

        print(Fore.WHITE + "\n--- [ PHASE 3: DEEP RECON ] ---")
        print(Fore.YELLOW + "[*] Enumerating Subdomains...")
        subdomain.enumerate(args.domain, save_path)
        
        print(Fore.YELLOW + f"[*] Scanning Ports (Threads: {args.threads})...")
        # Handle the 3 arguments for portscanner
        portscanner.scan(args.domain, args.threads, save_path) 

        print(Fore.WHITE + "\n--- [ PHASE 4: DATA EXTRACTION ] ---")
        loading_bar("Harvesting Emails")
        email_scan.scan(args.domain, save_path)
        
        loading_bar("Scraping Social Profiles")
        social_scan.scan(args.domain, save_path)
        
        loading_bar("Brute-forcing Admin Panels")
        admin_scan.scan(args.domain, save_path)
        
        loading_bar("Robots.txt Secrets")
        robots.scan(args.domain, save_path)
        sitemap.scan(args.domain, save_path)
        js_scan.scan(args.domain, save_path)

        print(Fore.WHITE + "\n--- [ PHASE 5: VISUAL SURVEILLANCE ] ---")
        loading_bar("Capturing Evidence")
        screenshot.capture(args.domain, save_path)

        type_effect(f"\n[✓] MISSION ACCOMPLISHED.", Fore.GREEN)
        print(f"{Fore.YELLOW}Reports saved in: {save_path}")

if __name__ == "__main__":
    main()
