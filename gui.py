import streamlit as st
import os
import subprocess
import glob

# --- DARK NEON CONFIG ---
st.set_page_config(page_title="WEBFOX COMMANDER", layout="wide", page_icon="🦊")

st.markdown("""
<style>
    .stApp { background-color: #050505; }
    h1, h2, h3 { color: #00ff41 !important; text-shadow: 0 0 10px #00ff41; font-family: 'Courier New'; }
    p, label, span, div { color: #e0e0e0 !important; font-family: 'Courier New'; }
    .stTextInput input { background-color: #111; color: #00ff41; border: 1px solid #00ff41; }
    div.stButton > button { background-color: #000; color: #00ff41; border: 1px solid #00ff41; box-shadow: 0 0 15px #00ff41; font-weight: bold; width: 100%; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; }
    .stTabs [data-baseweb="tab"] { background-color: #111; border: 1px solid #333; }
    .stTabs [aria-selected="true"] { background-color: #00ff41; color: black !important; }
</style>
""", unsafe_allow_html=True)

st.title("🦊 WEBFOX Recon Tool")
st.markdown("---")

col1, col2 = st.columns([3, 1])
with col1:
    target = st.text_input("ENTER TARGET DOMAIN", placeholder="example.com")
with col2:
    st.write("")
    st.write("")
    if st.button("⚡ INITIATE ATTACK"):
        if target:
            with st.status("🚀 INFILTRATING SYSTEM (NO TIMEOUT)...", expanded=True) as status:
                subprocess.run(["python3", "test.py", target, "-scan"])
                status.update(label="✅ MISSION COMPLETE", state="complete", expanded=False)
            st.success("DATA SECURED.")

if target:
    report_path = os.path.join("reports", target)
    if os.path.exists(report_path):
        st.subheader(f"📂 INTEL: {target}")
        tabs = st.tabs(["📸 VISUALS", "🌍 NETWORK", "🛡️ SECURITY", "🕷️ CRAWL DATA", "📧 CONTACTS"])
        
        with tabs[0]:
            images = glob.glob(f"{report_path}/*.png")
            if images: st.image(images, width=400, caption=[os.path.basename(i) for i in images])
            else: st.info("No Visuals.")
            
        with tabs[1]:
            c1, c2 = st.columns(2)
            with c1:
                if os.path.exists(f"{report_path}/subdomains.txt"):
                    st.text_area("Subdomains", open(f"{report_path}/subdomains.txt").read(), height=300)
            with c2:
                if os.path.exists(f"{report_path}/ports.txt"):
                    st.text_area("Ports", open(f"{report_path}/ports.txt").read(), height=300)

        with tabs[2]:
            if os.path.exists(f"{report_path}/waf.txt"): st.code(open(f"{report_path}/waf.txt").read())
            if os.path.exists(f"{report_path}/ssl_info.txt"): st.code(open(f"{report_path}/ssl_info.txt").read())

        with tabs[3]:
            if os.path.exists(f"{report_path}/robots_secrets.txt"):
                st.warning("⚠️ SENSITIVE PATHS FOUND")
                st.code(open(f"{report_path}/robots_secrets.txt").read())
            else: st.info("No Sensitive Robots paths.")

        with tabs[4]:
            if os.path.exists(f"{report_path}/emails.txt"): st.code(open(f"{report_path}/emails.txt").read())
            else: st.info("No Emails Found.")
                
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

