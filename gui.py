import streamlit as st
import os
import subprocess
import glob

# --- DARK NEON THEME CONFIGURATION ---
st.set_page_config(page_title="WEBFOX COMMANDER", layout="wide", page_icon="🦊")

st.markdown("""
<style>
    /* MAIN BACKGROUND - Pitch Black */
    .stApp { background-color: #050505; }
    
    /* NEON GREEN TEXT STYLING */
    h1, h2, h3 { 
        color: #00ff41 !important; 
        text-shadow: 0 0 10px #00ff41; 
        font-family: 'Courier New', monospace;
    }
    
    /* GENERAL TEXT */
    p, label, span, div { 
        color: #e0e0e0 !important; 
        font-family: 'Courier New', monospace; 
    }
    
    /* INPUT FIELDS */
    .stTextInput input {
        background-color: #111; 
        color: #00ff41; 
        border: 1px solid #00ff41;
        box-shadow: 0 0 5px #00ff41;
    }
    
    /* ATTACK BUTTON */
    div.stButton > button {
        background-color: #000;
        color: #00ff41;
        border: 1px solid #00ff41;
        box-shadow: 0 0 15px #00ff41;
        font-weight: bold;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #00ff41;
        color: #000;
        box-shadow: 0 0 25px #00ff41;
        transform: scale(1.02);
    }

    /* TABS DESIGN */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #111; 
        border: 1px solid #333; 
        color: #fff;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #00ff41; 
        color: #000 !important; 
        font-weight: bold;
        box-shadow: 0 0 10px #00ff41;
    }
    
    /* CODE BLOCKS */
    .stCodeBlock { border: 1px solid #003300; }
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.title("🦊 WEBFOX // ULTIMATE DASHBOARD")
st.markdown("---")

# --- CONTROL PANEL ---
col1, col2 = st.columns([3, 1])
with col1:
    target = st.text_input("ENTER TARGET DOMAIN (e.g. example.com)", placeholder="target.com")
with col2:
    st.write("") # Spacer
    st.write("")
    if st.button("⚡ INITIATE ATTACK"):
        if target:
            with st.status("🚀 INFILTRATING TARGET... (NO TIMEOUT MODE)", expanded=True) as status:
                st.write("Initializing WebFox Protocol...")
                # Running the scanner script
                subprocess.run(["python3", "test.py", target, "-scan"])
                status.update(label="✅ DATA EXTRACTION COMPLETE", state="complete", expanded=False)
            st.success("TARGET COMPROMISED. DATA READY.")

# --- REPORT VIEWER ENGINE ---
if target:
    report_path = os.path.join("reports", target)
    
    if os.path.exists(report_path):
        st.subheader(f"📂 INTEL REPORT: {target}")
        
        # 5 MAIN TABS FOR ORGANIZED DATA
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📸 DASHBOARD", 
            "🌍 NETWORK MAP", 
            "🛡️ VULNERABILITIES", 
            "🕷️ CRAWL DATA", 
            "📧 CONTACTS & LEAKS"
        ])
        
        # TAB 1: DASHBOARD (Visuals + Basic Info)
        with tab1:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("### 📡 SERVER GEOLOCATION")
                if os.path.exists(f"{report_path}/ip_location.txt"):
                    st.code(open(f"{report_path}/ip_location.txt").read())
                else: st.info("No IP Data.")
            
            with col_b:
                st.markdown("### 👤 WHOIS OWNERSHIP")
                # Ye file ab Provider/Registrar/Dates sab dikhayegi
                if os.path.exists(f"{report_path}/whois_basic.txt"):
                    st.code(open(f"{report_path}/whois_basic.txt").read())
                else: st.info("No Whois Data.")

            st.markdown("### 🖥️ SURVEILLANCE SNAPSHOTS")
            images = glob.glob(f"{report_path}/*.png")
            if images:
                st.image(images, width=400, caption=[os.path.basename(i) for i in images])
            else:
                st.warning("No Screenshots Captured.")

        # TAB 2: NETWORK (Subdomains, Ports, DNS)
        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 🌐 ACTIVE SUBDOMAINS")
                if os.path.exists(f"{report_path}/subdomains.txt"):
                    st.text_area("Live Hosts & IPs", open(f"{report_path}/subdomains.txt").read(), height=400)
                else: st.info("No Subdomains Found.")
            
            with c2:
                st.markdown("### 🔌 OPEN PORTS & SERVICES")
                if os.path.exists(f"{report_path}/ports.txt"):
                    st.text_area("Port Banners", open(f"{report_path}/ports.txt").read(), height=400)
                else: st.info("No Open Ports Found.")
                
            st.markdown("### 📒 DNS RECORDS & ZONE TRANSFER")
            if os.path.exists(f"{report_path}/dns.txt"):
                st.code(open(f"{report_path}/dns.txt").read())

        # TAB 3: SECURITY (SSL, WAF, Tech)
        with tab3:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 🔥 WAF & HEADERS")
                if os.path.exists(f"{report_path}/waf.txt"):
                    st.error("Firewall Analysis")
                    st.code(open(f"{report_path}/waf.txt").read())
                
                st.markdown("### 🛠️ TECH STACK")
                if os.path.exists(f"{report_path}/technologies.txt"):
                    st.code(open(f"{report_path}/technologies.txt").read())
                
            with c2:
                st.markdown("### 🔐 SSL & SANs (Hidden Domains)")
                if os.path.exists(f"{report_path}/ssl_info.txt"):
                    st.success("Certificate Details")
                    st.code(open(f"{report_path}/ssl_info.txt").read())

        # TAB 4: CRAWL DATA (Robots, JS)
        with tab4:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### ⚠️ SENSITIVE PATHS (Robots.txt)")
                if os.path.exists(f"{report_path}/robots_secrets.txt"):
                    st.error("Admin/Backup Paths Found!")
                    st.code(open(f"{report_path}/robots_secrets.txt").read())
                elif os.path.exists(f"{report_path}/robots.txt"):
                    st.code(open(f"{report_path}/robots.txt").read())
                else: st.info("No Robots.txt.")
            
            with c2:
                st.markdown("### 🕸️ HIDDEN JS URLs")
                if os.path.exists(f"{report_path}/js_urls.txt"):
                    st.text_area("Extracted Links", open(f"{report_path}/js_urls.txt").read(), height=300)

        # TAB 5: LEAKS (Emails)
        with tab5:
            st.markdown("### 📧 SCRAPED EMAILS")
            if os.path.exists(f"{report_path}/emails.txt"):
                st.success(f"Emails Extracted from {target}")
                st.code(open(f"{report_path}/emails.txt").read())
            else:
                st.info("No Emails Found on Homepage.")

    else:
        st.info("👈 ENTER DOMAIN & CLICK 'INITIATE ATTACK' TO START RECON.")
