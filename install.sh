#!/bin/bash

# COLORS
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# ANIMATION FUNCTION
animate() {
    echo -ne "$1 "
    for i in {1..20}; do
        echo -ne "█"
        sleep 0.1
    done
    echo -e " ${GREEN}[DONE]${NC}"
}

clear
echo -e "${CYAN}"
echo "██╗    ██╗███████╗██████╗ ███████╗ ██████╗ ██╗  ██╗"
echo "██║    ██║██╔════╝██╔══██╗██╔════╝██╔═══██╗╚██╗██╔╝"
echo "██║ █╗ ██║█████╗  ██████╔╝█████╗  ██║   ██║ ╚███╔╝ "
echo "██║███╗██║██╔══╝  ██╔══██╗██╔══╝  ██║   ██║ ██╔██╗ "
echo "╚███╔███╔╝███████╗██████╔╝██║     ╚██████╔╝ ██╔╝ ██╗"
echo " ╚══╝╚══╝ ╚══════╝╚═════╝ ╚═╝      ╚═════╝ ╚═╝  ╚═╝"
echo -e "          -- INSTALLATION WIZARD v10.0 --${NC}\n"

echo -e "${GREEN}[*] Initializing Environment...${NC}"
sleep 1

# STEP 1: REPOSITORIES
echo -e "\n${CYAN}[1/4] Updating System Repositories...${NC}"
sudo apt update -qq > /dev/null 2>&1 &
PID=$!
animate "    Loading Repos"
wait $PID

# STEP 2: REPAIR PIP & INSTALL TOOLS
echo -e "\n${CYAN}[2/4] Installing & Repairing Core Tools...${NC}"
sudo apt install --reinstall -y python3-pip > /dev/null 2>&1
sudo apt install -y python3 git wget tar curl jq firefox-esr > /dev/null 2>&1 &
PID=$!
animate "    Installing Dependencies"
wait $PID

# STEP 3: LIBRARIES
echo -e "\n${CYAN}[3/4] Installing Python Libraries...${NC}"
pip3 install builtwith --break-system-packages > /dev/null 2>&1
pip3 install -r requirements.txt --break-system-packages > /dev/null 2>&1 &
PID=$!
animate "    Downloading Libraries"
wait $PID

# STEP 4: INSTALL GECKODRIVER (DIRECT LINK)
echo -e "\n${CYAN}[4/4] Configuring Geckodriver (v0.36.0)...${NC}"

# DIRECT LINK - No API calls to fail
DOWNLOAD_URL="https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz"

# Force remove old driver to prevent conflicts
sudo rm -f /usr/bin/geckodriver
rm -f driver.tar.gz

# Download with verbose off (-q) but show errors
wget -O driver.tar.gz "$DOWNLOAD_URL"

if [ -f "driver.tar.gz" ]; then
    # Extract
    tar -xf driver.tar.gz
    
    # Install
    chmod +x geckodriver
    sudo mv geckodriver /usr/bin/geckodriver
    rm driver.tar.gz
    
    animate "    Finalizing Setup"
else
    echo -e "${RED}[!] Download Failed. Check Internet Connection.${NC}"
    exit 1
fi

echo -e "\n${GREEN}=========================================="
echo -e "   [✓] INSTALLATION SUCCESSFUL"
echo -e "   [✓] PIP REPAIRED & PACKAGES INSTALLED"
echo -e "   [✓] GECKODRIVER INSTALLED"
echo -e "   [>] Run: python3 test.py -help"
echo -e "==========================================${NC}"
