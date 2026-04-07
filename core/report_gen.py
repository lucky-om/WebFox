"""
WebFox HTML Report Generator — by Lucky
Reads all scan output files and bundles them into a single,
beautifully formatted interactive HTML report.

Author  : Lucky
Project : WebFox Recon Framework v4.0
"""
import os
import glob
from datetime import datetime


def _read_file(path):
    """Safely read a text file, return empty string on failure."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception:
        return ""


def _escape(text):
    """HTML-escape text to prevent XSS in report."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _colorize_lines(text):
    """Apply per-line severity coloring based on keywords."""
    lines = []
    for line in text.split("\n"):
        l = line.lower()
        if any(k in l for k in ["critical", "⚠️", "vulnerable", "exposed", "⚠", "missing", "error", "fail", "expired", "illegal"]):
            lines.append(f'<span class="line-critical">{_escape(line)}</span>')
        elif any(k in l for k in ["high", "warning", "warn", "potential", "weak", "soon"]):
            lines.append(f'<span class="line-high">{_escape(line)}</span>')
        elif any(k in l for k in ["open", "found", "detected", "live", "✓", "pass", "success"]):
            lines.append(f'<span class="line-good">{_escape(line)}</span>')
        elif any(k in l for k in ["medium", "info", "note"]):
            lines.append(f'<span class="line-medium">{_escape(line)}</span>')
        else:
            lines.append(_escape(line))
    return "\n".join(lines)


def _section(title, icon, content, section_id):
    if not content:
        content = "No data collected for this module."
    return f"""
    <div class="section" id="{section_id}">
        <div class="section-header">
            <span class="section-icon">{icon}</span>
            <h2>{_escape(title)}</h2>
        </div>
        <div class="section-body">
            <pre class="code-block">{_colorize_lines(content)}</pre>
        </div>
    </div>
"""


def generate(domain, save_path):
    """Generate the all-in-one HTML report for a completed scan."""
    print(f"  [*] Generating HTML report for {domain}...")

    # Load all collected data
    data = {
        "ip_location":   _read_file(f"{save_path}/ip_location.txt"),
        "whois":         _read_file(f"{save_path}/whois_basic.txt"),
        "dns":           _read_file(f"{save_path}/dns.txt"),
        "ssl":           _read_file(f"{save_path}/ssl_info.txt"),
        "waf":           _read_file(f"{save_path}/waf.txt"),
        "tech":          _read_file(f"{save_path}/technologies.txt"),
        "headers":       _read_file(f"{save_path}/http_headers.txt"),
        "dos":           _read_file(f"{save_path}/dos_vuln.txt"),
        "ports":         _read_file(f"{save_path}/ports.txt"),
        "subdomains_all":_read_file(f"{save_path}/subdomains_all.txt"),
        "subdomains_live":_read_file(f"{save_path}/subdomains_live.txt"),
        "takeover":      _read_file(f"{save_path}/takeover.txt"),
        "dir_scan":      _read_file(f"{save_path}/dir_scan.txt"),
        "js":            _read_file(f"{save_path}/js_analysis.txt"),
        "robots":        _read_file(f"{save_path}/robots.txt"),
        "sitemap":       _read_file(f"{save_path}/sitemap.xml") or _read_file(f"{save_path}/sitemap.txt"),
        "email_intel":   _read_file(f"{save_path}/email_intel.txt"),
    }

    # Screenshots
    screenshot_html = ""
    screenshots = glob.glob(f"{save_path}/*.png")
    if screenshots:
        screenshot_html = '<div class="screenshot-grid">'
        for img_path in screenshots:
            img_name = os.path.basename(img_path)
            # Encode image as base64 for self-contained HTML
            try:
                import base64
                with open(img_path, "rb") as img_f:
                    b64 = base64.b64encode(img_f.read()).decode("utf-8")
                screenshot_html += f'''
                <div class="screenshot-item">
                    <img src="data:image/png;base64,{b64}" alt="{_escape(img_name)}" />
                    <p>{_escape(img_name)}</p>
                </div>'''
            except Exception:
                screenshot_html += f'<div class="screenshot-item"><p>Could not embed: {_escape(img_name)}</p></div>'
        screenshot_html += "</div>"
    else:
        screenshot_html = '<p class="no-data">No screenshots captured.</p>'

    # Timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Count findings
    critical_count = sum(
        1 for k, v in data.items()
        if any(word in v.lower() for word in ["critical", "vulnerable", "⚠️", "exposed"])
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebFox Report — {_escape(domain)}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;500;700;900&display=swap');

        :root {{
            --bg-primary: #0d0d0f;
            --bg-card: #131317;
            --bg-section: #18181d;
            --accent: #f97316;
            --accent-dim: rgba(249,115,22,0.12);
            --green: #22c55e;
            --yellow: #fbbf24;
            --red: #ef4444;
            --cyan: #22d3ee;
            --text-primary: #e5e7eb;
            --text-muted: #6b7280;
            --border: #252532;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
        }}

        /* ── Header ───────────────────────────────── */
        .header {{
            background: linear-gradient(135deg, #0d0d0f 0%, #1a0a00 60%, #0d0d0f 100%);
            border-bottom: 1px solid var(--border);
            padding: 40px 60px;
            position: relative;
            overflow: hidden;
        }}
        .header::before {{
            content: '';
            position: absolute;
            top: -50%; left: -20%;
            width: 600px; height: 600px;
            background: radial-gradient(circle, rgba(249,115,22,0.08) 0%, transparent 70%);
            pointer-events: none;
        }}
        .header-inner {{
            max-width: 1400px;
            margin: 0 auto;
            position: relative;
        }}
        .logo {{
            font-size: 3rem;
            font-weight: 900;
            color: var(--accent);
            letter-spacing: -2px;
            font-family: 'Inter', sans-serif;
            text-shadow: 0 0 40px rgba(249,115,22,0.4);
        }}
        .logo span {{ color: var(--text-primary); }}
        .header-meta {{
            margin-top: 16px;
            display: flex;
            gap: 32px;
            flex-wrap: wrap;
        }}
        .meta-item {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .meta-label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--text-muted);
        }}
        .meta-value {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-primary);
        }}
        .meta-value.target {{
            color: var(--accent);
            font-size: 1.1rem;
        }}
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .badge-critical {{ background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }}
        .badge-safe {{ background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }}

        /* ── Navigation ───────────────────────────── */
        .nav {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(13,13,15,0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 0 60px;
            overflow-x: auto;
        }}
        .nav-inner {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            gap: 0;
        }}
        .nav a {{
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 14px 18px;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .nav a:hover {{
            color: var(--accent);
            border-bottom-color: var(--accent);
        }}

        /* ── Main Layout ──────────────────────────── */
        .main {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 60px;
        }}

        /* ── Summary Cards ────────────────────────── */
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 48px;
        }}
        .summary-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px 24px;
            transition: border-color 0.2s;
        }}
        .summary-card:hover {{ border-color: var(--accent); }}
        .summary-card .card-icon {{ font-size: 1.5rem; margin-bottom: 8px; }}
        .summary-card .card-label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-muted);
        }}
        .summary-card .card-value {{
            font-size: 1.4rem;
            font-weight: 800;
            color: var(--text-primary);
            margin-top: 4px;
        }}
        .summary-card .card-value.accent {{ color: var(--accent); }}
        .summary-card .card-value.danger {{ color: var(--red); }}
        .summary-card .card-value.safe {{ color: var(--green); }}

        /* ── Section ──────────────────────────────── */
        .section {{
            background: var(--bg-section);
            border: 1px solid var(--border);
            border-radius: 16px;
            margin-bottom: 24px;
            overflow: hidden;
            transition: border-color 0.2s;
        }}
        .section:hover {{ border-color: rgba(249,115,22,0.3); }}
        .section-header {{
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 20px 28px;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            user-select: none;
        }}
        .section-icon {{ font-size: 1.4rem; }}
        .section-header h2 {{
            font-size: 1rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .section-body {{ padding: 0; }}
        .code-block {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            line-height: 1.7;
            padding: 24px 28px;
            white-space: pre-wrap;
            word-break: break-word;
            background: transparent;
            border: none;
            outline: none;
            width: 100%;
            overflow-x: auto;
        }}

        /* Line colors */
        .line-critical {{ color: #ef4444; font-weight: 700; }}
        .line-high {{ color: #fbbf24; }}
        .line-good {{ color: #22c55e; }}
        .line-medium {{ color: #22d3ee; }}

        /* ── Screenshots ──────────────────────────── */
        .screenshot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 20px;
            padding: 24px 28px;
        }}
        .screenshot-item {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
        }}
        .screenshot-item img {{
            width: 100%;
            display: block;
        }}
        .screenshot-item p {{
            padding: 10px 14px;
            font-size: 0.75rem;
            color: var(--text-muted);
        }}
        .no-data {{
            padding: 24px 28px;
            color: var(--text-muted);
            font-style: italic;
        }}

        /* ── Footer ───────────────────────────────── */
        .footer {{
            text-align: center;
            padding: 40px 60px;
            border-top: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 0.75rem;
            margin-top: 40px;
        }}
        .footer strong {{ color: var(--accent); }}

        /* ── Scrollbar ────────────────────────────── */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg-primary); }}
        ::-webkit-scrollbar-thumb {{ background: #333; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}

        /* ── Toggle animation ─────────────────────── */
        .section.collapsed .section-body {{ display: none; }}

        @media (max-width: 768px) {{
            .header, .main {{ padding: 24px 20px; }}
            .nav {{ padding: 0 20px; }}
        }}
    </style>
</head>
<body>

<!-- HEADER -->
<div class="header">
    <div class="header-inner">
        <div class="logo">WEB<span>FOX</span> <span style="font-size:1.2rem;color:var(--text-muted);font-weight:400;">by Lucky</span></div>
        <div class="header-meta">
            <div class="meta-item">
                <span class="meta-label">Target</span>
                <span class="meta-value target">{_escape(domain)}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Scan Date</span>
                <span class="meta-value">{now}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Modules Run</span>
                <span class="meta-value">{sum(1 for v in data.values() if v)} / {len(data)}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Risk Level</span>
                <span class="meta-value">
                    {'<span class="badge badge-critical">⚠ HIGH RISK</span>' if critical_count > 2 else '<span class="badge badge-safe">✓ LOW RISK</span>'}
                </span>
            </div>
        </div>
    </div>
</div>

<!-- NAV -->
<nav class="nav">
    <div class="nav-inner">
        <a href="#ip">IP/Geo</a>
        <a href="#whois">WHOIS</a>
        <a href="#dns">DNS</a>
        <a href="#ssl">SSL</a>
        <a href="#waf">WAF/CDN</a>
        <a href="#headers">Headers</a>
        <a href="#tech">Tech</a>
        <a href="#ports">Ports</a>
        <a href="#subdomains">Subdomains</a>
        <a href="#takeover">Takeover</a>
        <a href="#dir">Dir Scan</a>
        <a href="#js">JS/Secrets</a>
        <a href="#email">Emails</a>
        <a href="#crawl">Crawl</a>
        <a href="#viz">Screenshots</a>
    </div>
</nav>

<!-- MAIN -->
<div class="main">

    <!-- Summary Cards -->
    <div class="summary-grid">
        <div class="summary-card">
            <div class="card-icon">🎯</div>
            <div class="card-label">Target Domain</div>
            <div class="card-value accent">{_escape(domain)}</div>
        </div>
        <div class="summary-card">
            <div class="card-icon">🌐</div>
            <div class="card-label">Live Subdomains</div>
            <div class="card-value">{len([l for l in data['subdomains_live'].split(chr(10)) if l.strip() and '|' in l])}</div>
        </div>
        <div class="summary-card">
            <div class="card-icon">💥</div>
            <div class="card-label">Critical Alerts</div>
            <div class="card-value danger">{critical_count}</div>
        </div>
        <div class="summary-card">
            <div class="card-icon">📁</div>
            <div class="card-label">Exposed Paths</div>
            <div class="card-value danger">{len([l for l in data['dir_scan'].split(chr(10)) if '[200]' in l or '[301]' in l])}</div>
        </div>
        <div class="summary-card">
            <div class="card-icon">🔑</div>
            <div class="card-label">Secrets Found</div>
            <div class="card-value danger">{len([l for l in data['js'].split(chr(10)) if 'TYPE:' in l])}</div>
        </div>
        <div class="summary-card">
            <div class="card-icon">✉️</div>
            <div class="card-label">Emails Found</div>
            <div class="card-value">{len([l for l in data['email_intel'].split(chr(10)) if '@' in l and l.strip().startswith(tuple('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))])}</div>
        </div>
    </div>

    <!-- Sections -->
    {_section("IP Geolocation & Network", "📍", data['ip_location'], "ip")}
    {_section("WHOIS Intelligence", "👤", data['whois'], "whois")}
    {_section("DNS Enumeration & Email Security", "🗄️", data['dns'], "dns")}
    {_section("SSL / TLS Certificate Analysis", "🔐", data['ssl'], "ssl")}
    {_section("WAF / CDN / Server Fingerprint", "🔥", data['waf'], "waf")}
    {_section("HTTP Security Headers Audit", "🛡️", data['headers'], "headers")}
    {_section("Technology Stack & CMS", "⚙️", data['tech'], "tech")}
    {_section("Port Scan & Banner Grabbing", "🔌", data['ports'], "ports")}
    {_section("Subdomain Enumeration (All)", "🌐", data['subdomains_all'], "subdomains")}
    {_section("Subdomain Takeover Analysis", "⚠️", data['takeover'], "takeover")}
    {_section("Directory & Sensitive File Scan", "📁", data['dir_scan'], "dir")}
    {_section("JavaScript & Secret Analysis", "🔑", data['js'], "js")}
    {_section("Email, Phone & Social Intel", "✉️", data['email_intel'], "email")}
    {_section("Robots.txt", "🤖", data['robots'], "crawl")}
    {_section("Sitemap", "🗺️", data['sitemap'], "sitemap")}
    {_section("DoS Resistance Check", "💣", data['dos'], "dos")}

    <!-- Screenshots -->
    <div class="section" id="viz">
        <div class="section-header">
            <span class="section-icon">📸</span>
            <h2>Visual Surveillance (Screenshots)</h2>
        </div>
        <div class="section-body">
            {screenshot_html}
        </div>
    </div>
</div>

<!-- FOOTER -->
<div class="footer">
    <p>Generated by <strong>WebFox v4.0</strong> — by <strong>Lucky</strong> | Target: <strong>{_escape(domain)}</strong> | {now}</p>
    <p style="margin-top:6px;">⚠️ For authorized security testing only. Do not scan systems without permission.</p>
    <p style="margin-top:4px;color:#f97316;">© Lucky — WebFox Recon Framework</p>
</div>

<script>
    // Toggle sections on header click
    document.querySelectorAll('.section-header').forEach(header => {{
        header.addEventListener('click', () => {{
            header.closest('.section').classList.toggle('collapsed');
        }});
    }});
</script>

</body>
</html>"""

    output_path = f"{save_path}/WebFox_Report.html"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  [+] HTML Report saved: {output_path}")
    except Exception as e:
        print(f"  [-] Failed to save HTML report: {e}")

    return output_path
