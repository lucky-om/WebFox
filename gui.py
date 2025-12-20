import streamlit as st
import os
import subprocess
import glob

# --- NEON HACKER THEME ---
st.set_page_config(page_title="WEBFOX v10.0 COMMANDER", layout="wide", page_icon="🦊")
st.markdown("""
<style>
    /* Global Black Background */
    .stApp { background-color: #000000; }
    
    /* Neon Green Text & Headers */
    h1, h2, h3, h4, p, span, div { 
        color: #00ff41 !important; 
        font-family: 'Courier New', monospace; 
        text-shadow: 0 0 5px #004411;
    }
    
    /* Neon Inputs */
    .stTextInput > div > div > input {
        background-color: #0a0a0a; 
        color: #00ff41; 
        border: 1px solid #00ff41;
        box-shadow: 0 0 5px #00ff41;
    }
    
    /* Neon Buttons */
    .stButton > button {
        background-color: #000000; 
        color: #00ff41; 
        border: 1px solid #00ff41; 
        box-shadow: 0 0 8px #00ff41;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #00ff41;
        color: #000000;
    }
    
    /* Code Blocks (Report Readers) */
    .stCodeBlock { border: 1px solid #003300; box-shadow: 0 0 5px #003300; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #111; border: 1px solid #333; }
    .stTabs [aria-selected="true"] { background-color: #00ff41; color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🦊 WEBFOX v10.0 // ULTIMATE DASHBOARD")
st.markdown("---")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🎯 TARGET SYSTEM")
    target = st.text_input("ENTER DOMAIN URL", placeholder="example.com")
    
    if st.button("⚡ EXECUTE FULL SCAN"):
        if target:
            with st.spinner(f"🚀 INFILTRATING {target}... PLEASE WAIT"):
                # Run the scan script in background
                subprocess.run(["python3", "test.py", target, "-scan"])
            st.success("✅ MISSION COMPLETE. DATA DOWNLOADED.")

# --- MAIN DISPLAY AREA ---
if target:
    report_path = os.path.join("reports", target)
    
    if os.path.exists(report_path):
        st.subheader(f"📂 INTEL FOR: {target}")
        
        # 5 TABS FOR ALL DATA
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📸 VISUALS", 
            "🌍 NETWORK RECON", 
            "🛡️ SECURITY & WAF", 
            "🕷️ CRAWL DATA", 
            "📝 FULL LOGS"
        ])
        
        # TAB 1: SCREENSHOTS & LOCATION
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📡 SERVER LOCATION")
                if os.path.exists(f"{report_path}/ip_location.txt"):
                    st.code(open(f"{report_path}/ip_location.txt").read(), language="yaml")
                else: st.warning("No IP Data Found.")
            
            with col2:
                st.markdown("### 👤 OWNER INFO")
                if os.path.exists(f"{report_path}/whois_basic.txt"):
                    st.code(open(f"{report_path}/whois_basic.txt").read(), language="yaml")
                else: st.warning("No Whois Data Found.")

            st.markdown("### 🖥️ SURVEILLANCE SNAPSHOTS")
            images = glob.glob(f"{report_path}/*.png")
            if images:
                st.image(images, width=350, caption=[os.path.basename(i) for i in images])
            else:
                st.info("No Screenshots Captured.")

        # TAB 2: NETWORK (Subdomains, Ports, DNS)
        with tab2:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("### 🌐 SUBDOMAINS")
                if os.path.exists(f"{report_path}/subdomains.txt"):
                    st.text_area("Found Subdomains", open(f"{report_path}/subdomains.txt").read(), height=300)
                else: st.info("No Subdomains.")
            
            with c2:
                st.markdown("### 🔌 OPEN PORTS")
                if os.path.exists(f"{report_path}/ports.txt"):
                    st.text_area("Port Scan", open(f"{report_path}/ports.txt").read(), height=300)
                else: st.info("No Open Ports Found.")
                
            with c3:
                st.markdown("### 📒 DNS RECORDS")
                if os.path.exists(f"{report_path}/dns.txt"):
                    st.code(open(f"{report_path}/dns.txt").read())
                else: st.info("No DNS Info.")

        # TAB 3: SECURITY (SSL, WAF, TECH)
        with tab3:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 🔥 FIREWALL (WAF)")
                if os.path.exists(f"{report_path}/waf.txt"):
                    st.error(open(f"{report_path}/waf.txt").read()) # Red text for WAF
                else: st.info("No WAF Data.")
                
                st.markdown("### 🛠️ TECHNOLOGY STACK")
                if os.path.exists(f"{report_path}/technologies.txt"):
                    st.code(open(f"{report_path}/technologies.txt").read())
                else: st.info("No Tech Data.")
                
            with c2:
                st.markdown("### 🔐 SSL CERTIFICATE")
                if os.path.exists(f"{report_path}/ssl_info.txt"):
                    st.success(open(f"{report_path}/ssl_info.txt").read())
                else: st.info("No SSL Data.")

        # TAB 4: CRAWLER (JS, Robots, Sitemap)
        with tab4:
            st.markdown("### 🕸️ HIDDEN JS URLs")
            if os.path.exists(f"{report_path}/js_urls.txt"):
                st.text_area("Extracted URLs from JS", open(f"{report_path}/js_urls.txt").read(), height=200)
            else: st.info("No JS URLs.")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 🤖 ROBOTS.TXT")
                if os.path.exists(f"{report_path}/robots.txt"):
                    st.code(open(f"{report_path}/robots.txt").read())
            with c2:
                st.markdown("### 🗺️ SITEMAP.XML")
                if os.path.exists(f"{report_path}/sitemap.xml"):
                    st.code(open(f"{report_path}/sitemap.xml").read())

        # TAB 5: RAW FILE VIEWER (Fallback)
        with tab5:
            st.markdown("### 📂 ALL GENERATED FILES")
            all_files = os.listdir(report_path)
            selected_file = st.selectbox("Select a file to view content:", all_files)
            
            if selected_file:
                file_path = os.path.join(report_path, selected_file)
                try:
                    if selected_file.endswith(".png"):
                        st.image(file_path)
                    else:
                        st.code(open(file_path, errors='ignore').read())
                except:
                    st.error("Cannot display this file type.")
                    
    else:
        st.info("👈 ENTER A DOMAIN AND CLICK 'EXECUTE SCAN' TO START.")

