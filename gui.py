import streamlit as st
import os
import subprocess
import glob

st.set_page_config(page_title="WEBFOX COMMANDER", layout="wide", page_icon="🦊")
st.markdown("""
<style>
    .stApp { background-color: #050505; }
    h1, h2, h3 { color: #00ff41 !important; font-family: 'Courier New'; }
    p, label, span, div { color: #e0e0e0 !important; font-family: 'Courier New'; }
    .stTextInput input { background-color: #111; color: #00ff41; border: 1px solid #00ff41; }
    div.stButton > button { background-color: #000; color: #00ff41; border: 1px solid #00ff41; font-weight: bold; width: 100%; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; }
    .stTabs [data-baseweb="tab"] { background-color: #111; border: 1px solid #333; }
    .stTabs [aria-selected="true"] { background-color: #00ff41; color: black !important; }
</style>
""", unsafe_allow_html=True)

st.title("🦊 WEBFOX // ULTIMATE DASHBOARD")
st.markdown("---")

col1, col2 = st.columns([3, 1])
with col1:
    target = st.text_input("TARGET DOMAIN", placeholder="example.com")
with col2:
    st.write("")
    st.write("")
    if st.button("⚡ INITIATE ATTACK"):
        if target:
            with st.status("🚀 INFILTRATING...", expanded=True) as status:
                subprocess.run(["python3", "test.py", target, "-scan"])
                status.update(label="✅ COMPLETE", state="complete", expanded=False)

if target:
    report_path = os.path.join("reports", target)
    if os.path.exists(report_path):
        st.subheader(f"📂 INTEL: {target}")
        
        tabs = st.tabs(["📸 VISUALS", "🌍 NETWORK", "🛡️ VULNS", "🕷️ CRAWL", "💀 HACKS"])
        
        with tabs[0]:
            st.markdown("### 🖥️ SCREENSHOTS")
            images = glob.glob(f"{report_path}/*.png")
            if images: st.image(images, width=400)
            
            st.markdown("### 📡 GEOLOCATION")
            if os.path.exists(f"{report_path}/ip_location.txt"):
                st.code(open(f"{report_path}/ip_location.txt").read())

        with tabs[1]:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 🔍 REAL IP DETECT")
                if os.path.exists(f"{report_path}/real_ip.txt"): st.code(open(f"{report_path}/real_ip.txt").read())
                
                st.markdown("### 🌐 SUBDOMAINS")
                if os.path.exists(f"{report_path}/subdomains.txt"): st.text_area("Subs", open(f"{report_path}/subdomains.txt").read(), height=200)
            
            with c2:
                st.markdown("### 🔌 PORTS")
                if os.path.exists(f"{report_path}/ports.txt"): st.text_area("Ports", open(f"{report_path}/ports.txt").read(), height=200)

        with tabs[2]:
            st.markdown("### 🔥 VULNERABILITY SCAN")
            if os.path.exists(f"{report_path}/sqli_vuln.txt"): 
                st.error("SQL INJECTION FOUND")
                st.code(open(f"{report_path}/sqli_vuln.txt").read())
            
            if os.path.exists(f"{report_path}/cors_vuln.txt"): st.code(open(f"{report_path}/cors_vuln.txt").read())
            if os.path.exists(f"{report_path}/dos_vuln.txt"): st.code(open(f"{report_path}/dos_vuln.txt").read())

        with tabs[3]:
            if os.path.exists(f"{report_path}/social_links.txt"): 
                st.markdown("### 👥 SOCIAL PROFILES")
                st.code(open(f"{report_path}/social_links.txt").read())
            
            if os.path.exists(f"{report_path}/emails.txt"): 
                st.markdown("### 📧 EMAILS")
                st.code(open(f"{report_path}/emails.txt").read())

        with tabs[4]:
            if os.path.exists(f"{report_path}/admin_paths.txt"):
                st.error("👹 ADMIN PANELS FOUND")
                st.code(open(f"{report_path}/admin_paths.txt").read())
