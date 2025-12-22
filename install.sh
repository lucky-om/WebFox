#!/bin/bash

# NEON COLORS
GREEN='\033[0;32m'
NEON_GREEN='\033[1;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# MATRIX ANIMATION
matrix_effect() {
    clear
    echo -e "${NEON_GREEN}"
    echo " W E B F O X   P R O T O C O L   I N I T I A T E D "
    echo -e "${NC}"
    sleep 0.5
}

# PROGRESS BAR
progress() {
    echo -ne "${CYAN}[*] $1... "
    for i in {1..20}; do
        echo -ne "█"
        sleep 0.02
    done
    echo -e " ${NEON_GREEN}[DONE]${NC}"
}

matrix_effect

echo -e "${NEON_GREEN}[1/5] Updating System Core...${NC}"
sudo apt update -qq > /dev/null 2>&1 &
wait $!
progress "System Update"

echo -e "\n${NEON_GREEN}[2/5] Repairing Python Environment...${NC}"
sudo apt install --reinstall -y python3-pip > /dev/null 2>&1
progress "PIP Repair"

echo -e "\n${NEON_GREEN}[3/5] Installing Offensive Tools...${NC}"
sudo apt install -y python3 git wget tar curl jq firefox-esr > /dev/null 2>&1 &
wait $!
progress "Installing Dependencies"

echo -e "\n${NEON_GREEN}[4/5] Injecting Python Libraries...${NC}"
pip3 install builtwith --break-system-packages > /dev/null 2>&1
pip3 install -r requirements.txt --break-system-packages > /dev/null 2>&1 &
wait $!
progress "Library Injection"

echo -e "\n${NEON_GREEN}[5/5] Configuring Stealth Drivers...${NC}"
# DIRECT LINK (Stable)
URL="https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz"
wget -q -O driver.tar.gz "$URL"
tar -xf driver.tar.gz
chmod +x geckodriver
sudo mv geckodriver /usr/bin/geckodriver > /dev/null 2>&1
rm driver.tar.gz
progress "Driver Setup"

echo -e "\n${NEON_GREEN}=========================================="
echo -e "   [✓] INSTALLATION SUCCESSFULLY! SYSTEM READY."
echo -e "   [>] Run CLI: python3 test.py example.com -scan"
echo -e "   [>] Run GUI: streamlit run gui.py"
echo -e "==========================================${NC}"

