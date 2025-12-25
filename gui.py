import streamlit as st
import os
import subprocess
import glob

# --- UI CHANGE: Updated page config ---
st.set_page_config(page_title="WEBFOX v10.0 COMMANDER", layout="wide", page_icon="🦊")

# --- UI CHANGE: Updated CSS for Tab spacing and White Text ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Homenaje&display=swap');
    
    /* UI CHANGE: Dark gray background instead of pure black */
    .stApp { background-color: #1a1a1a; }
    
    /* UI CHANGE: Homenaje font, muted gray text */
    h1, h2, h3, h4, p, span, div, label { 
        color: #fff !important; 
        font-family: 'Homenaje', sans-serif !important; 
    }
    
    /* UI CHANGE: Orange accent for primary headings */
    h1 { color: #f97316 !important; font-size: 1.5rem !important; }
    
    /* UI CHANGE: Darker input styling */
    .stTextInput > div > div > input {
        background-color: #2a2a2a; 
        color: #ffffff; 
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        font-family: 'Homenaje', sans-serif;
    }
    
    /* UI CHANGE: Orange buttons matching screenshot */
    .stButton > button {
        background-color: #f97316; 
        color: #ffffff !important; /* CHANGE: Text on button to white */
        border: none; 
        border-radius: 4px;
        font-weight: bold;
        font-family: 'Homenaje', sans-serif;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        background-color: #ea580c;
        color: #ffffff !important;
    }
    
    /* UI CHANGE: Tab styling - White text and extra spacing */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 15px; /* CHANGE: Increased gap for equal spacing between tabs */
        background-color: #252525;
        border-radius: 4px;
        padding: 8px;
    }
    .stTabs [data-baseweb="tab"] { 
        background-color: transparent; 
        border: none;
        color: #ffffff !important; /* CHANGE: Text color to pure white */
        font-family: 'Homenaje', sans-serif;
        text-transform: uppercase;
        font-size: 0.85rem;
        padding-left: 10px; /* CHANGE: Equal inner spacing */
        padding-right: 10px;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #f97316 !important; 
        color: #000000 !important; /* Active tab keeps dark text for contrast */
        border-radius: 4px;
    }
    
    /* Sidebar and other elements preserved */
    [data-testid="stSidebar"] { background-color: #1e1e1e; border-right: 1px solid #2a2a2a; }
    .stTextArea textarea { background-color: #2a2a2a; color: #ffffff; border: 1px solid #3a3a3a; font-family: 'Homenaje', sans-serif; }
    .stSelectbox > div > div { background-color: #2a2a2a; border: 1px solid #3a3a3a; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("WEBFOX v10.0")
st.markdown("---")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("TARGET SYSTEM")
    target = st.text_input("ENTER DOMAIN URL", placeholder="example.com")
    
    if st.button("EXECUTE FULL SCAN"):
        if target:
            with st.spinner(f"INFILTRATING {target}... PLEASE WAIT"):
                subprocess.run(["python3", "test.py", target, "-scan"])
            st.success("MISSION COMPLETE. DATA DOWNLOADED.")

# --- MAIN DISPLAY AREA ---
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
        st.info("ENTER A DOMAIN AND CLICK 'EXECUTE SCAN' TO START.")