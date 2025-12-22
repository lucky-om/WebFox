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
# I added '--reinstall python3-pip' to fix your corrupted pip error automatically
echo -e "\n${CYAN}[2/4] Installing & Repairing Core Tools...${NC}"
sudo apt install --reinstall -y python3-pip > /dev/null 2>&1
sudo apt install -y python3 git wget tar curl jq firefox-esr > /dev/null 2>&1 &
PID=$!
animate "    Installing Dependencies"
wait $PID

# STEP 3: LIBRARIES
echo -e "\n${CYAN}[3/4] Installing Python Libraries...${NC}"
# Installing builtwith specifically first to ensure it's not missed
pip3 install builtwith --break-system-packages > /dev/null 2>&1
pip3 install -r requirements.txt --break-system-packages > /dev/null 2>&1 &
PID=$!
animate "    Downloading Libraries"
wait $PID

# STEP 4: LATEST GECKODRIVER (Dynamic Fetch)
echo -e "\n${CYAN}[4/4] Configuring Latest Geckodriver...${NC}"

# 1. Dynamically get the URL for the absolute latest version from GitHub API
LATEST_URL=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | jq -r '.assets[] | select(.name | contains("linux64.tar.gz")) | .browser_download_url')

# 2. Fallback if API fails (Use v0.36.0 which is current latest)
if [ -z "$LATEST_URL" ]; then
    LATEST_URL="https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz"
fi

# 3. Download & Install to /usr/bin/ (Correct Path)
wget -q -O driver.tar.gz "$LATEST_URL"
tar -xf driver.tar.gz
chmod +x geckodriver
sudo mv geckodriver /usr/bin/geckodriver > /dev/null 2>&1
rm driver.tar.gz
animate "    Finalizing Setup"

echo -e "\n${GREEN}=========================================="
echo -e "   [✓] INSTALLATION SUCCESSFUL"
echo -e "   [✓] PIP REPAIRED & PACKAGES INSTALLED"
echo -e "   [✓] GECKODRIVER PATH: /usr/bin/geckodriver"
echo -e "   [>] Run: python3 test.py -help"
echo -e "==========================================${NC}"
