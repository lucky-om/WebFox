#!/bin/bash

# --- NEON THEME CONFIG ---
GREEN='\033[0;32m'
NEON_GREEN='\033[1;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- MATRIX ANIMATION ---
matrix_effect() {
    clear
    echo -e "${NEON_GREEN}"
    echo " W E B F O X   P R O T O C O L   I N I T I A T E D "
    echo -e "${NC}"
    sleep 0.5
}

matrix_effect

# 1. SYSTEM UPDATE
echo -e "${CYAN}[*] Updating System Core...${NC}"
sudo apt update -qq > /dev/null 2>&1
echo -e "${GREEN}    > System Core Updated.${NC}"

# 2. INSTALL DEPENDENCIES
echo -e "\n${CYAN}[*] Installing Offensive Tools...${NC}"
sudo apt install -y python3 python3-pip git wget tar curl jq firefox-esr > /dev/null 2>&1
echo -e "${GREEN}    > Dependencies Installed.${NC}"

# 3. PYTHON LIBRARIES
echo -e "\n${CYAN}[*] Injecting Python Libraries...${NC}"
# Using --break-system-packages for modern Kali (Python 3.11+)
pip3 install builtwith --break-system-packages > /dev/null 2>&1
pip3 install -r requirements.txt --break-system-packages > /dev/null 2>&1
echo -e "${GREEN}    > Python Modules Active.${NC}"

# 4. GECKODRIVER SETUP (PC / x86_64 VERSION)
echo -e "\n${CYAN}[*] Configuring Stealth Drivers...${NC}"

# Remove any old/wrong drivers
sudo rm -f /usr/bin/geckodriver

# Download the PC Version (linux64)
wget -q -O driver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz"

if [ -f "driver.tar.gz" ]; then
    tar -xf driver.tar.gz
    chmod +x geckodriver
    sudo mv geckodriver /usr/bin/geckodriver
    rm driver.tar.gz
    echo -e "${GREEN}    > Driver Installed Successfully.${NC}"
else
    echo -e "${RED}    [!] Driver Download Failed. Check Internet.${NC}"
fi

# 5. FINAL PERMISSIONS
chmod +x test.py
echo -e "\n${NEON_GREEN}=========================================="
echo -e "   [✓] INSTALATION SUCCESSFULL. SYSTEM READY. "
echo -e "   [>] Run CLI: python3 test.py <domain> -scan"
echo -e "   [>] Run GUI: streamlit run gui.py"
echo -e "==========================================${NC}"
