import streamlit as st
import os
import subprocess
import glob
import sys

VERSION = "v4.0.0"
AUTHOR  = "Lucky"

st.set_page_config(
    page_title=f"WEBFOX {VERSION} — RECON COMMANDER",
    layout="wide",
    page_icon="🦊"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Homenaje&family=JetBrains+Mono:wght@400;700&display=swap');

.stApp { background-color: #0d0d0d; }

h1, h2, h3, h4, p, span, div, label {
    color: #e0e0e0 !important;
    font-family: 'Homenaje', sans-serif !important;
}
h1 { color: #f97316 !important; font-size: 1.55rem !important; letter-spacing: 3px; }
h3, h4 { color: #f97316 !important; }

.stTextInput > div > div > input {
    background-color: #1a1a1a !important;
    color: #ffffff !important;
    border: 1px solid #333 !important;
    border-radius: 2px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stButton > button {
    background-color: #f97316 !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 2px !important;
    font-weight: bold !important;
    font-family: 'Homenaje', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    width: 100% !important;
    padding: 0.55rem 1rem !important;
    transition: background 0.2s;
}
.stButton > button:hover { background-color: #c2410c !important; }

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background-color: #161616;
    border-radius: 2px;
    padding: 5px;
    border: 1px solid #222;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    border: none !important;
    color: #888 !important;
    font-family: 'Homenaje', sans-serif !important;
    text-transform: uppercase !important;
    font-size: 0.78rem !important;
    padding: 5px 12px !important;
    border-radius: 2px !important;
}
.stTabs [aria-selected="true"] {
    background-color: #f97316 !important;
    color: #000 !important;
}

[data-testid="stSidebar"] {
    background-color: #111 !important;
    border-right: 1px solid #1f1f1f !important;
}

.stTextArea textarea {
    background-color: #141414 !important;
    color: #d4d4d4 !important;
    border: 1px solid #222 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
}

code, pre {
    background-color: #141414 !important;
    color: #d4d4d4 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    border: 1px solid #222 !important;
    border-radius: 2px !important;
}

.stSelectbox > div > div {
    background-color: #1a1a1a !important;
    border: 1px solid #333 !important;
    color: #e0e0e0 !important;
}

.stRadio label { color: #e0e0e0 !important; }
.stAlert { border-radius: 2px !important; }

div[data-testid="metric-container"] {
    background-color: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 2px;
    padding: 10px 14px;
}
div[data-testid="metric-container"] label { color: #f97316 !important; }
div[data-testid="metric-container"] div   { color: #ffffff !important; font-size: 1.6rem !important; }

.footer-credit {
    text-align: center;
    color: #444;
    font-size: 0.7rem;
    padding: 8px 0;
    font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ── Script directory (so subprocess can find test.py) ──────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── HEADER ─────────────────────────────────────────────────────────────────
st.title(f"⚔  WEBFOX {VERSION}  ·  ADVANCED RECON COMMANDER")
st.markdown(
    f"<div style='color:#555;font-size:0.75rem;font-family:JetBrains Mono,monospace;"
    f"margin-top:-10px;margin-bottom:10px;'>Coded by <span style='color:#f97316'>{AUTHOR}</span>"
    f" &nbsp;|&nbsp; Multi-Target Intelligence Framework</div>",
    unsafe_allow_html=True
)
st.markdown("---")

# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 🦊 WEBFOX {VERSION}")
    st.markdown(f"<div style='color:#f97316;font-size:0.7rem;margin-bottom:8px;'>Coded by {AUTHOR}</div>",
                unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("🎯 TARGET")
    target = st.text_input("Domain", placeholder="example.com", label_visibility="collapsed")

    if target and ("http" in target or "/" in target or " " in target):
        st.warning("⚠ Enter a bare domain — e.g. `example.com`")

    st.markdown("---")
    st.subheader("⚙ SCAN MODE")

    scan_mode = st.radio(
        "Mode",
        options=["🌐 Domain Only", "🔍 Subdomains Only", "🚀 Both (Full Recon)"],
        index=2,
        label_visibility="collapsed"
    )

    mode_flag_map = {
        "🌐 Domain Only"      : "-domain-only",
        "🔍 Subdomains Only"  : "-subs-only",
        "🚀 Both (Full Recon)": "-both",
    }

    st.markdown("---")
    st.subheader("🔧 OPTIONS")
    threads = st.slider("Port Scan Threads", min_value=10, max_value=300, value=100, step=10)

    st.markdown("---")

    run_btn = st.button("⚡ EXECUTE SCAN")

    if run_btn:
        if not target or "http" in target or "/" in target or " " in target:
            st.error("❌ Enter a valid domain first (e.g. example.com)")
        else:
            flag = mode_flag_map[scan_mode]
            cmd  = [
                sys.executable,
                os.path.join(SCRIPT_DIR, "test.py"),
                target,
                "-scan",
                flag,
                "-threads", str(threads),
            ]
            status_box = st.empty()
            status_box.info(f"⏳ Scanning **{target}** [{scan_mode}] — this may take several minutes...")
            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=SCRIPT_DIR,
                    timeout=1800       # 30-minute hard cap
                )
                if proc.returncode == 0:
                    status_box.success(f"✅ Scan complete for **{target}**. Scroll right to view results.")
                else:
                    err = (proc.stderr or proc.stdout or "Unknown error")[-800:]
                    status_box.error(f"❌ Scan failed:\n```\n{err}\n```")
            except subprocess.TimeoutExpired:
                status_box.error("❌ Scan timed out after 30 minutes.")
            except FileNotFoundError:
                status_box.error("❌ `test.py` not found. Make sure you run the GUI from the WebFox directory.")
            except Exception as e:
                status_box.error(f"❌ Unexpected error: {e}")

    st.markdown("---")
    st.markdown(
        f"<div class='footer-credit'>WebFox {VERSION} · Coded by {AUTHOR}</div>",
        unsafe_allow_html=True
    )

# ── Helper: safe file read ──────────────────────────────────────────────────
def _read(path, limit=8000):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read(limit)
    except Exception:
        return ""

def _count_lines(path, keyword):
    """Count lines containing keyword in a file."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return sum(1 for l in f if keyword in l)
    except Exception:
        return 0

# ── MAIN DISPLAY ────────────────────────────────────────────────────────────
if target and "http" not in target and "/" not in target and " " not in target:
    report_path = os.path.join(SCRIPT_DIR, "reports", target)
    sub_base    = os.path.join(report_path, "subdomains")

    if not os.path.exists(report_path):
        st.markdown("""
        <div style='text-align:center;padding:60px 0;'>
            <h2 style='color:#f97316!important;'>🦊 NO REPORT FOUND</h2>
            <p style='color:#555;'>Run a scan first using the sidebar, then refresh.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    st.subheader(f"📂 INTEL ARCHIVE — {target}")

    # ── Metrics bar ────────────────────────────────────────────────────────
    all_subs  = _count_lines(os.path.join(report_path, "subdomains_all.txt"),  "")  if os.path.exists(os.path.join(report_path, "subdomains_all.txt"))  else 0
    live_subs = _count_lines(os.path.join(report_path, "subdomains_live.txt"), "")  if os.path.exists(os.path.join(report_path, "subdomains_live.txt")) else 0
    open_ports= _count_lines(os.path.join(report_path, "ports.txt"),           "OPEN") if os.path.exists(os.path.join(report_path, "ports.txt"))           else 0
    secrets   = _count_lines(os.path.join(report_path, "js_analysis.txt"),     ">>")   if os.path.exists(os.path.join(report_path, "js_analysis.txt"))     else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🌐 Subdomains Found",   all_subs)
    m2.metric("✅ Live Subdomains",    live_subs)
    m3.metric("🔌 Open Ports",         open_ports)
    m4.metric("🔑 Secrets Detected",   secrets)
    st.markdown("---")

    # ── Tabs ───────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "📡 VISUALS",
        "🌐 NETWORK",
        "🔐 SECURITY",
        "🕸 CRAWLING",
        "🔥 DOS / HTTP",
        "📁 LOGS",
        "🔬 SUBDOMAIN INTEL",
    ])

    # ── TAB 0: VISUALS ─────────────────────────────────────────────────────
    with tabs[0]:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📡 GEOLOCATION & ASN")
            ip_file = os.path.join(report_path, "ip_location.txt")
            if os.path.exists(ip_file):
                st.code(_read(ip_file), language="yaml")
            else:
                st.info("No IP data. Run a Domain scan.")

        with col2:
            st.markdown("#### 👤 WHOIS / OWNER INFO")
            w_file = os.path.join(report_path, "whois_basic.txt")
            if os.path.exists(w_file):
                st.code(_read(w_file), language="yaml")
            else:
                st.info("No WHOIS data. Run a Domain scan.")

        st.markdown("#### 🖥️ SURVEILLANCE SCREENSHOTS")
        images = glob.glob(os.path.join(report_path, "*.png"))
        if images:
            cols = st.columns(min(len(images), 3))
            for i, img in enumerate(images):
                cols[i % 3].image(img, caption=os.path.basename(img), use_container_width=True)
        else:
            st.info("No screenshots captured.")

    # ── TAB 1: NETWORK ─────────────────────────────────────────────────────
    with tabs[1]:
        n1, n2, n3 = st.columns(3)

        with n1:
            st.markdown("#### 🌐 SUBDOMAINS")
            all_f  = os.path.join(report_path, "subdomains_all.txt")
            live_f = os.path.join(report_path, "subdomains_live.txt")
            if os.path.exists(all_f):
                st.text_area("All Discovered", _read(all_f, 20000), height=250)
            else:
                st.info("No subdomain data. Use Subdomains Only or Both mode.")
            if os.path.exists(live_f):
                st.text_area("✅ Live Only", _read(live_f, 10000), height=180)

        with n2:
            st.markdown("#### 🔌 OPEN PORTS")
            p_file = os.path.join(report_path, "ports.txt")
            if os.path.exists(p_file):
                st.code(_read(p_file), language="yaml")
            else:
                st.info("No port scan data.")

        with n3:
            st.markdown("#### 📒 DNS RECORDS")
            d_file = os.path.join(report_path, "dns.txt")
            if os.path.exists(d_file):
                st.code(_read(d_file))
            else:
                st.info("No DNS data.")

    # ── TAB 2: SECURITY ────────────────────────────────────────────────────
    with tabs[2]:
        s1, s2 = st.columns(2)

        with s1:
            st.markdown("#### 🔥 WAF & SECURITY HEADERS")
            waf_file = os.path.join(report_path, "waf.txt")
            if os.path.exists(waf_file):
                content = _read(waf_file, 5000)
                if "None Detected" in content:
                    st.success(content)
                else:
                    st.error(content)
            else:
                st.info("No WAF data.")

            st.markdown("#### 🛠️ TECHNOLOGY STACK")
            t_file = os.path.join(report_path, "technologies.txt")
            if os.path.exists(t_file):
                st.code(_read(t_file), language="yaml")
            else:
                st.info("No tech data.")

        with s2:
            st.markdown("#### 🔐 SSL / TLS CERTIFICATE")
            ssl_file = os.path.join(report_path, "ssl_info.txt")
            if os.path.exists(ssl_file):
                content = _read(ssl_file, 6000)
                if "EXPIRED" in content or "FAILED" in content or "VERIFICATION FAILED" in content:
                    st.error(content)
                else:
                    st.code(content, language="yaml")
            else:
                st.info("No SSL data.")

    # ── TAB 3: CRAWLING ────────────────────────────────────────────────────
    with tabs[3]:
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("#### 🕵️ JS INTELLIGENCE")
            js_file  = os.path.join(report_path, "js_analysis.txt")
            js_file2 = os.path.join(report_path, "js_urls.txt")
            if os.path.exists(js_file):
                content = _read(js_file, 8000)
                if ">>" in content:
                    st.error("⚠️ Secrets / sensitive data detected!")
                st.text_area("JS Analysis", content, height=350)
            elif os.path.exists(js_file2):
                st.text_area("JS URLs", _read(js_file2), height=350)
            else:
                st.info("No JS data.")

        with c2:
            st.markdown("#### 🤖 ROBOTS.TXT")
            r_file = os.path.join(report_path, "robots.txt")
            if os.path.exists(r_file):
                content = _read(r_file, 5000)
                if "HIGH RISK" in content:
                    st.warning("⚠️ High-risk paths exposed!")
                st.code(content)
            else:
                st.info("No robots.txt found.")

        with c3:
            st.markdown("#### 🗺️ SITEMAP")
            for fname in ["sitemap_analysis.txt", "sitemap.xml", "sitemap.txt"]:
                fpath = os.path.join(report_path, fname)
                if os.path.exists(fpath):
                    st.code(_read(fpath, 5000))
                    break
            else:
                st.info("No sitemap found.")

    # ── TAB 4: DOS / HTTP ──────────────────────────────────────────────────
    with tabs[4]:
        st.markdown("#### 🔥 DoS RESISTANCE & HTTP BEHAVIOUR")
        dos_file = os.path.join(report_path, "dos_vuln.txt")
        if os.path.exists(dos_file):
            content = _read(dos_file)
            if "VULNERABLE" in content or "ABSENT" in content:
                st.warning("⚠️ Potential vulnerabilities detected:")
            else:
                st.success("✅ No obvious DoS vulnerabilities detected.")
            st.code(content)
        else:
            st.info("No DoS data. Run a Domain scan.")

    # ── TAB 5: LOGS ────────────────────────────────────────────────────────
    with tabs[5]:
        st.markdown("#### 📁 RAW FILE BROWSER")
        all_files = sorted([
            f for f in os.listdir(report_path)
            if os.path.isfile(os.path.join(report_path, f))
        ])
        if all_files:
            selected = st.selectbox("Select file to view:", all_files)
            if selected:
                fpath = os.path.join(report_path, selected)
                if selected.lower().endswith(".png"):
                    st.image(fpath)
                else:
                    st.code(_read(fpath, 10000))
        else:
            st.info("No files yet. Run a scan first.")

    # ── TAB 6: SUBDOMAIN INTEL ─────────────────────────────────────────────
    with tabs[6]:
        st.markdown("#### 🔬 SUBDOMAIN DEEP RECON VIEWER")

        if not os.path.exists(sub_base):
            st.info(
                "No subdomain intelligence collected yet.\n\n"
                "Run a scan with **🔍 Subdomains Only** or **🚀 Both** mode."
            )
            st.stop()

        sub_dirs = sorted([
            d for d in os.listdir(sub_base)
            if os.path.isdir(os.path.join(sub_base, d))
        ])

        if not sub_dirs:
            st.warning("Subdomain folder exists but no subdomains were scanned yet.")
            st.stop()

        sel_col, stat_col = st.columns([1, 3])
        with sel_col:
            selected_sub = st.selectbox(f"🎯 {len(sub_dirs)} subdomains:", sub_dirs)

        sp = os.path.join(sub_base, selected_sub)

        sub_ports   = _count_lines(os.path.join(sp, "ports.txt"),       "OPEN") if os.path.exists(os.path.join(sp, "ports.txt"))       else 0
        sub_secrets = _count_lines(os.path.join(sp, "js_analysis.txt"), ">>")   if os.path.exists(os.path.join(sp, "js_analysis.txt")) else 0

        with stat_col:
            sc1, sc2 = st.columns(2)
            sc1.metric("🔌 Open Ports",   sub_ports)
            sc2.metric("🔑 Secrets Found", sub_secrets)

        st.markdown(f"---\n**Target:** `{selected_sub}`")

        # Row 1
        r1a, r1b, r1c = st.columns(3)
        with r1a:
            st.markdown("**📡 IP / Geolocation**")
            f = os.path.join(sp, "ip_location.txt")
            st.code(_read(f), language="yaml") if os.path.exists(f) else st.info("No data.")

        with r1b:
            st.markdown("**🔐 SSL Certificate**")
            f = os.path.join(sp, "ssl_info.txt")
            st.code(_read(f, 2500), language="yaml") if os.path.exists(f) else st.info("No data.")

        with r1c:
            st.markdown("**📒 DNS Records**")
            f = os.path.join(sp, "dns.txt")
            st.code(_read(f, 2000)) if os.path.exists(f) else st.info("No data.")

        # Row 2
        r2a, r2b, r2c = st.columns(3)
        with r2a:
            st.markdown("**🔥 WAF / Headers**")
            f = os.path.join(sp, "waf.txt")
            if os.path.exists(f):
                c = _read(f, 2500)
                if "DETECTED" in c and "None Detected" not in c:
                    st.error(c)
                else:
                    st.code(c)
            else:
                st.info("No data.")

        with r2b:
            st.markdown("**🛠️ Tech Stack**")
            f = os.path.join(sp, "technologies.txt")
            st.code(_read(f, 2000), language="yaml") if os.path.exists(f) else st.info("No data.")

        with r2c:
            st.markdown("**🔌 Open Ports**")
            f = os.path.join(sp, "ports.txt")
            st.code(_read(f, 2000)) if os.path.exists(f) else st.info("No data.")

        # Row 3
        r3a, r3b, r3c = st.columns(3)
        with r3a:
            st.markdown("**🕵️ JS Analysis**")
            found_js = False
            for fn in ["js_analysis.txt", "js_urls.txt"]:
                f = os.path.join(sp, fn)
                if os.path.exists(f):
                    c = _read(f, 3000)
                    if ">>" in c:
                        st.error("⚠️ Secrets found!")
                    st.text_area("", c, height=200, key=f"js_{selected_sub}_{fn}")
                    found_js = True
                    break
            if not found_js:
                st.info("No data.")

        with r3b:
            st.markdown("**🤖 Robots.txt**")
            f = os.path.join(sp, "robots.txt")
            st.code(_read(f, 2000)) if os.path.exists(f) else st.info("No data.")

        with r3c:
            st.markdown("**🗺️ Sitemap**")
            found_sm = False
            for fn in ["sitemap_analysis.txt", "sitemap.xml", "sitemap.txt"]:
                f = os.path.join(sp, fn)
                if os.path.exists(f):
                    st.code(_read(f, 2000))
                    found_sm = True
                    break
            if not found_sm:
                st.info("No data.")

        # Screenshots
        st.markdown("**🖥️ Screenshots**")
        imgs = glob.glob(os.path.join(sp, "*.png"))
        if imgs:
            ic = st.columns(min(len(imgs), 3))
            for i, img in enumerate(imgs):
                ic[i % 3].image(img, caption=os.path.basename(img), use_container_width=True)
        else:
            st.info("No screenshots captured.")

        # Raw file browser
        with st.expander("📁 Browse all files for this subdomain"):
            sub_files = sorted([
                f for f in os.listdir(sp)
                if os.path.isfile(os.path.join(sp, f))
            ])
            if sub_files:
                picked = st.selectbox("File:", sub_files, key=f"picker_{selected_sub}")
                fp = os.path.join(sp, picked)
                if picked.lower().endswith(".png"):
                    st.image(fp)
                else:
                    st.code(_read(fp, 6000))
            else:
                st.info("No files yet.")

else:
    # Welcome screen
    st.markdown(f"""
    <div style="text-align:center;padding:70px 0;">
        <h2 style="color:#f97316!important;font-size:2rem;letter-spacing:4px;">🦊 WEBFOX {VERSION}</h2>
        <p style="color:#555;font-size:1rem;margin-top:6px;">Advanced Multi-Target Recon Framework</p>
        <p style="color:#f97316;font-size:0.8rem;margin-top:2px;">Coded by {AUTHOR}</p>
        <hr style="border-color:#1f1f1f;margin:30px auto;width:60%;">
        <p style="color:#444;font-size:0.85rem;">
            Enter a domain in the sidebar &nbsp;→&nbsp; choose a scan mode &nbsp;→&nbsp; click <strong>EXECUTE SCAN</strong>
        </p>
        <p style="color:#333;font-size:0.75rem;margin-top:12px;">
            Reports persist between sessions. Enter a previously scanned domain to view cached results.
        </p>
    </div>
    """, unsafe_allow_html=True)
