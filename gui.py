"""
WebFox v4.0 — GUI Commander
Streamlit-based graphical interface for the WebFox Recon Framework.

Author  : Lucky
Project : WebFox Recon Framework v4.0
License : MIT
"""
import streamlit as st
import os
import subprocess
import glob

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WebFox v4.0 | by Lucky",
    layout="wide",
    page_icon="🦊",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

    /* ── Base ── */
    .stApp {
        background: linear-gradient(135deg, #0d0d0f 0%, #111114 100%);
        font-family: 'Inter', sans-serif;
    }

    /* ── Typography ── */
    h1, h2, h3, h4, p, span, div, label {
        color: #e5e7eb !important;
        font-family: 'Inter', sans-serif !important;
    }
    h1 { color: #f97316 !important; font-size: 1.6rem !important; font-weight: 900 !important; letter-spacing: -0.5px; }
    h2 { color: #f97316 !important; font-size: 1.1rem !important; font-weight: 700 !important; }
    h3 { color: #e5e7eb !important; font-size: 0.95rem !important; font-weight: 600 !important; }

    /* ── Inputs ── */
    .stTextInput > div > div > input {
        background-color: #1c1c22;
        color: #ffffff;
        border: 1px solid #2a2a35;
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
        padding: 10px 14px;
        transition: border-color 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #f97316 !important;
        box-shadow: 0 0 0 2px rgba(249,115,22,0.15) !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #f97316, #ea580c);
        color: #ffffff !important;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.8rem;
        padding: 10px 20px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 14px rgba(249,115,22,0.25);
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #fb923c, #f97316);
        box-shadow: 0 6px 20px rgba(249,115,22,0.4);
        transform: translateY(-1px);
        color: #ffffff !important;
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #131317;
        border-radius: 10px;
        padding: 6px;
        border: 1px solid #1e1e28;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        color: #9ca3af !important;
        font-family: 'Inter', sans-serif;
        text-transform: uppercase;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.8px;
        padding: 8px 16px;
        border-radius: 6px;
        transition: all 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(249,115,22,0.08) !important;
        color: #f97316 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f97316, #ea580c) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111114 0%, #0d0d0f 100%);
        border-right: 1px solid #1e1e28;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        color: #9ca3af !important;
        font-size: 0.8rem;
    }

    /* ── Text Areas & Code ── */
    .stTextArea textarea {
        background-color: #131317;
        color: #e5e7eb;
        border: 1px solid #1e1e28;
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
    }
    .stCode, pre {
        background-color: #131317 !important;
        border: 1px solid #1e1e28 !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important;
    }

    /* ── Selectbox ── */
    .stSelectbox > div > div {
        background-color: #1c1c22;
        border: 1px solid #2a2a35;
        border-radius: 8px;
        color: #e5e7eb;
    }

    /* ── Alerts ── */
    .stAlert {
        border-radius: 8px !important;
        border-left-width: 4px !important;
    }

    /* ── Metrics / Cards ── */
    [data-testid="metric-container"] {
        background-color: #131317;
        border: 1px solid #1e1e28;
        border-radius: 10px;
        padding: 16px;
    }

    /* ── Divider ── */
    hr { border-color: #1e1e28 !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #0d0d0f; }
    ::-webkit-scrollbar-thumb { background: #2a2a35; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #f97316; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def safe_read(path):
    """Safely read a file; return empty string on any error."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #0d0d0f 0%, #1a0a00 60%, #0d0d0f 100%);
    border-bottom: 1px solid #1e1e28;
    padding: 20px 28px 16px 28px;
    margin: -1rem -1rem 1.5rem -1rem;
    display: flex; align-items: center; justify-content: space-between;
">
    <div>
        <span style="font-family:'Inter',sans-serif; font-size:2rem; font-weight:900; color:#f97316; letter-spacing:-1px;">
            WEB<span style="color:#e5e7eb;">FOX</span>
        </span>
        <span style="font-size:0.9rem; color:#6b7280; margin-left:12px; font-family:'Inter',sans-serif;">
            v4.0 COMMANDER
        </span>
    </div>
    <div style="text-align:right;">
        <span style="display:inline-block; background:rgba(249,115,22,0.12); border:1px solid rgba(249,115,22,0.3);
            color:#f97316; border-radius:20px; padding:4px 14px; font-size:0.72rem;
            font-weight:700; letter-spacing:1px; font-family:'Inter',sans-serif;">
            ⚡ BY LUCKY
        </span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Sidebar Controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 16px 0;">
        <p style="color:#f97316 !important; font-weight:700; font-size:0.9rem; text-transform:uppercase; letter-spacing:1px;">
            🦊 WebFox Recon
        </p>
        <p style="color:#6b7280 !important; font-size:0.75rem; margin-top:-8px;">
            by Lucky · v4.0
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 Target System")

    target = st.text_input(
        "Enter Domain",
        placeholder="example.com",
        help="Enter a domain without http:// prefix"
    )

    # Input validation
    if target:
        if "http" in target or "/" in target:
            st.warning("⚠️ Enter domain only — no http:// or paths.")
        elif " " in target:
            st.warning("⚠️ Domain cannot contain spaces.")

    st.markdown("")

    col_full, col_fast = st.columns(2)
    with col_full:
        run_full = st.button("🔍 FULL SCAN", use_container_width=True)
    with col_fast:
        run_fast = st.button("⚡ FAST SCAN", use_container_width=True)

    if (run_full or run_fast) and target and " " not in target and "http" not in target:
        cmd = ["python3", "test.py", target, "-scan"]
        if run_fast:
            cmd.append("-fast")
        with st.spinner(f"🦊 Infiltrating {target}… please wait"):
            result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            st.success("✅ Scan complete! Data collected.")
        else:
            st.error("❌ Scan failed. Check the domain or logs.")
            if result.stderr:
                with st.expander("Show error output"):
                    st.code(result.stderr[:2000])

    st.markdown("---")
    st.markdown("""
    <div style="padding:12px; background:#131317; border-radius:8px; border:1px solid #1e1e28;">
        <p style="color:#6b7280 !important; font-size:0.72rem; margin:0; line-height:1.6;">
            <b style="color:#f97316 !important;">🔒 Usage</b><br>
            python3 test.py &lt;domain&gt; -scan<br>
            python3 test.py &lt;domain&gt; -scan -fast<br>
            python3 test.py -help
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("""
    <p style="color:#374151 !important; font-size:0.7rem; text-align:center;">
        © Lucky · WebFox Recon Framework
    </p>
    """, unsafe_allow_html=True)


# ── Main Display Area ─────────────────────────────────────────────────────────
if not target:
    # Landing state
    st.markdown("""
    <div style="text-align:center; padding:80px 20px;">
        <div style="font-size:4rem;">🦊</div>
        <h2 style="color:#f97316 !important; font-size:1.5rem !important; margin:16px 0 8px 0;">
            WebFox Recon Commander
        </h2>
        <p style="color:#6b7280 !important; font-size:0.95rem;">
            Enter a domain in the sidebar and run a scan to begin intelligence gathering.
        </p>
        <div style="margin-top:32px; display:flex; gap:16px; flex-wrap:wrap; justify-content:center;">
            <span style="background:#131317; border:1px solid #1e1e28; border-radius:8px; padding:10px 18px; font-size:0.8rem; color:#9ca3af;">🌐 Subdomain Enum</span>
            <span style="background:#131317; border:1px solid #1e1e28; border-radius:8px; padding:10px 18px; font-size:0.8rem; color:#9ca3af;">🔌 Port Scanning</span>
            <span style="background:#131317; border:1px solid #1e1e28; border-radius:8px; padding:10px 18px; font-size:0.8rem; color:#9ca3af;">🛡️ HTTP Headers</span>
            <span style="background:#131317; border:1px solid #1e1e28; border-radius:8px; padding:10px 18px; font-size:0.8rem; color:#9ca3af;">🔐 SSL/TLS Audit</span>
            <span style="background:#131317; border:1px solid #1e1e28; border-radius:8px; padding:10px 18px; font-size:0.8rem; color:#9ca3af;">🔑 JS Secret Hunt</span>
            <span style="background:#131317; border:1px solid #1e1e28; border-radius:8px; padding:10px 18px; font-size:0.8rem; color:#9ca3af;">📁 Dir Scanning</span>
        </div>
        <p style="color:#374151 !important; font-size:0.72rem; margin-top:48px;">
            © Lucky · WebFox Recon Framework v4.0
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    report_path = os.path.join("reports", target)

    if not os.path.exists(report_path):
        st.markdown(f"""
        <div style="text-align:center; padding:60px 20px;">
            <div style="font-size:3rem;">📡</div>
            <h3 style="color:#f97316 !important; margin-top:12px;">No Report Found for <code>{target}</code></h3>
            <p style="color:#6b7280 !important;">Run a scan from the sidebar to collect intelligence.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Report found — show it
        html_report = os.path.join(report_path, "Lucky_WebFox_Report.html")
        st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:space-between;
            background:#131317; border:1px solid #1e1e28; border-radius:10px; padding:12px 20px; margin-bottom:20px;">
            <div>
                <span style="color:#f97316 !important; font-weight:700; font-size:1rem;">🎯 {target}</span>
                <span style="color:#6b7280; font-size:0.78rem; margin-left:12px;">Intelligence Report</span>
            </div>
            {"<a href='file://" + html_report + "' target='_blank' style='background:rgba(249,115,22,0.15);color:#f97316;border:1px solid rgba(249,115,22,0.3);border-radius:6px;padding:6px 14px;text-decoration:none;font-size:0.78rem;font-weight:700;'>📄 Open Full HTML Report</a>" if os.path.exists(html_report) else ""}
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📡 VISUALS",
            "🌐 NETWORK",
            "🔐 SECURITY",
            "🕸️ CRAWLER",
            "📂 RAW LOGS"
        ])

        # ── TAB 1: Visuals ────────────────────────────────────────────────────
        with tab1:
            col1, col2 = st.columns(2, gap="medium")
            with col1:
                st.markdown("### 📍 Server Location")
                ip_data = safe_read(f"{report_path}/ip_location.txt")
                if ip_data:
                    st.code(ip_data, language="yaml")
                else:
                    st.info("No IP/Location data found.")

            with col2:
                st.markdown("### 👤 WHOIS / Owner Info")
                whois_data = safe_read(f"{report_path}/whois_basic.txt")
                if whois_data:
                    st.code(whois_data, language="yaml")
                else:
                    st.info("No WHOIS data found.")

            st.markdown("---")
            st.markdown("### 🖥️ Surveillance Snapshots")
            images = glob.glob(f"{report_path}/*.png")
            if images:
                cols = st.columns(min(len(images), 3))
                for i, img_path in enumerate(images):
                    with cols[i % 3]:
                        st.image(img_path, caption=os.path.basename(img_path), use_container_width=True)
            else:
                st.info("📷 No screenshots captured. Run without -fast flag on Linux/Kali.")

        # ── TAB 2: Network ────────────────────────────────────────────────────
        with tab2:
            c1, c2, c3 = st.columns(3, gap="medium")
            with c1:
                st.markdown("### 🌐 Subdomains")
                if os.path.exists(f"{report_path}/subdomains_all.txt"):
                    st.text_area("All Discovered", safe_read(f"{report_path}/subdomains_all.txt"), height=280)
                    live_path = f"{report_path}/subdomains_live.txt"
                    if os.path.exists(live_path):
                        st.text_area("Live Only", safe_read(live_path), height=200)
                else:
                    st.info("No subdomains found yet.")

            with c2:
                st.markdown("### 🔌 Open Ports")
                port_data = safe_read(f"{report_path}/ports.txt")
                if port_data:
                    st.text_area("Port Scan Results", port_data, height=300)
                else:
                    st.info("No open ports found.")

            with c3:
                st.markdown("### 📒 DNS Records")
                dns_data = safe_read(f"{report_path}/dns.txt")
                if dns_data:
                    st.code(dns_data)
                else:
                    st.info("No DNS data found.")

        # ── TAB 3: Security ───────────────────────────────────────────────────
        with tab3:
            c1, c2 = st.columns(2, gap="medium")
            with c1:
                st.markdown("### 🔥 WAF / CDN Fingerprint")
                waf_data = safe_read(f"{report_path}/waf.txt")
                if waf_data:
                    st.error(waf_data)
                else:
                    st.info("No WAF data found.")

                st.markdown("### ⚙️ Technology Stack")
                tech_data = safe_read(f"{report_path}/technologies.txt")
                if tech_data:
                    st.code(tech_data)
                else:
                    st.info("No tech stack data.")

                st.markdown("### 🛡️ HTTP Security Headers")
                headers_data = safe_read(f"{report_path}/http_headers.txt")
                if headers_data:
                    st.code(headers_data)
                else:
                    st.info("No headers data.")

            with c2:
                st.markdown("### 🔐 SSL / TLS Certificate")
                ssl_data = safe_read(f"{report_path}/ssl_info.txt")
                if ssl_data:
                    st.success(ssl_data)
                else:
                    st.info("No SSL data found.")

                st.markdown("### ⚠️ Subdomain Takeover")
                takeover_data = safe_read(f"{report_path}/takeover.txt")
                if takeover_data:
                    st.code(takeover_data)
                else:
                    st.info("No takeover data.")

                st.markdown("### 💣 DoS Resistance")
                dos_data = safe_read(f"{report_path}/dos_vuln.txt")
                if dos_data:
                    st.code(dos_data)
                else:
                    st.info("No DoS data found.")

        # ── TAB 4: Crawler ────────────────────────────────────────────────────
        with tab4:
            c1, c2, c3 = st.columns(3, gap="medium")
            with c1:
                st.markdown("### 🔑 JS & Secrets")
                js_data = safe_read(f"{report_path}/js_analysis.txt")
                if js_data:
                    st.text_area("JS Analysis", js_data, height=280)
                else:
                    st.info("No JS/secret data.")

                st.markdown("### 📁 Directory Scan")
                dir_data = safe_read(f"{report_path}/dir_scan.txt")
                if dir_data:
                    st.text_area("Exposed Paths", dir_data, height=200)
                else:
                    st.info("No exposed directories found.")

            with c2:
                st.markdown("### 🤖 Robots.txt")
                robots_data = safe_read(f"{report_path}/robots.txt")
                if robots_data:
                    st.code(robots_data)
                else:
                    st.info("No robots.txt data.")

                st.markdown("### ✉️ Email Intel")
                email_data = safe_read(f"{report_path}/email_intel.txt")
                if email_data:
                    st.code(email_data)
                else:
                    st.info("No email data found.")

            with c3:
                st.markdown("### 🗺️ Sitemap")
                sitemap_data = safe_read(f"{report_path}/sitemap.xml") or safe_read(f"{report_path}/sitemap.txt")
                if sitemap_data:
                    st.code(sitemap_data[:5000])
                else:
                    st.info("No sitemap data.")

        # ── TAB 5: Raw Logs ───────────────────────────────────────────────────
        with tab5:
            st.markdown("### 📂 All Generated Files")
            try:
                all_files = sorted(os.listdir(report_path))
            except Exception:
                all_files = []

            if not all_files:
                st.info("No report files found yet.")
            else:
                selected_file = st.selectbox(
                    "Select a file to view:",
                    all_files,
                    format_func=lambda x: f"📄 {x}"
                )
                if selected_file:
                    file_path = os.path.join(report_path, selected_file)
                    if selected_file.endswith(".png"):
                        st.image(file_path, use_container_width=True)
                    elif selected_file.endswith((".html", ".htm")):
                        st.markdown(f"[🔗 Open in browser (HTML report)]({file_path})")
                        st.code(safe_read(file_path)[:5000])
                    else:
                        content = safe_read(file_path)
                        if content:
                            st.code(content)
                        else:
                            st.warning("File is empty or cannot be read.")
