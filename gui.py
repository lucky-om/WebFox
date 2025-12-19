import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Webfox v6.0", layout="wide")
st.markdown("<style>.stApp{background-color:#0e1117;color:#00ff41;}</style>", unsafe_allow_html=True)

st.title("🦊 WEBFOX DASHBOARD v6.0")

with st.sidebar:
    st.header("Controls")
    target = st.text_input("Target Domain", "example.com")
    if st.button("🚀 START SCAN"):
        if target:
            with st.spinner("Scanning target..."):
                subprocess.run(["python3", "test.py", target, "-scan"])
            st.success("Scan Finished!")

if target:
    path = os.path.join("reports", target)
    if os.path.exists(path):
        t1, t2, t3, t4 = st.tabs(["📸 Visuals", "🌐 Network", "🛡️ Security", "🕷️ Crawl"])
        
        with t1:
            if os.path.exists(f"{path}/screenshot.png"):
                st.image(f"{path}/screenshot.png", caption="Live Screenshot")
        
        with t2:
            c1, c2 = st.columns(2)
            with c1:
                st.write("**IP Address**")
                if os.path.exists(f"{path}/ip_location.txt"): st.code(open(f"{path}/ip_location.txt").read())
            with c2:
                st.write("**DNS Records**")
                if os.path.exists(f"{path}/dns_records.txt"): st.code(open(f"{path}/dns_records.txt").read())

        with t3:
            c1, c2 = st.columns(2)
            with c1:
                st.write("**SSL Certificate**")
                if os.path.exists(f"{path}/ssl_info.txt"): st.code(open(f"{path}/ssl_info.txt").read())
            with c2:
                st.write("**Firewall (WAF)**")
                if os.path.exists(f"{path}/waf.txt"): st.code(open(f"{path}/waf.txt").read())

        with t4:
            st.write("**JS Hidden URLs**")
            if os.path.exists(f"{path}/js_urls.txt"): st.text(open(f"{path}/js_urls.txt").read())

