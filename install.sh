#!/bin/bash

# Define Colors for nicer output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[*] Webfox Auto-Installer v2.0${NC}"
echo -e "${YELLOW}[*] Detecting System Architecture...${NC}"

# 1. Detect Architecture (Phone vs PC)
ARCH=$(uname -m)
echo -e "${GREEN}[+] Architecture detected: $ARCH${NC}"

# 2. Update System & Install Common Tools (Firefox, Python, Git)
echo -e "${YELLOW}[*] Updating system and installing dependencies...${NC}"
sudo apt update
sudo apt install -y python3 python3-pip git wget tar firefox-esr

# 3. Select the Correct Driver based on Architecture
if [[ "$ARCH" == "aarch64" ]]; then
    echo -e "${YELLOW}[*] Android/Phone detected. Downloading ARM64 Geckodriver...${NC}"
    # Download Link for PHONES
    URL="https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux-aarch64.tar.gz"
    FILE="geckodriver-v0.33.0-linux-aarch64.tar.gz"

elif [[ "$ARCH" == "x86_64" ]]; then
    echo -e "${YELLOW}[*] PC/Desktop detected. Downloading x64 Geckodriver...${NC}"
    # Download Link for PC
    URL="https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz"
    FILE="geckodriver-v0.33.0-linux64.tar.gz"

else
    echo -e "${RED}[!] Unknown system architecture: $ARCH${NC}"
    echo "Please install geckodriver manually."
    exit 1
fi

# 4. Download, Extract, and Install the Driver
echo -e "${YELLOW}[*] Downloading...${NC}"
wget -O "$FILE" "$URL"

echo -e "${YELLOW}[*] Installing to /usr/bin/...${NC}"
tar -xvzf "$FILE"
chmod +x geckodriver
sudo mv geckodriver /usr/bin/
rm "$FILE"

# 5. Install Python Libraries
echo -e "${YELLOW}[*] Installing Python Requirements...${NC}"
# We use --break-system-packages for newer Kali versions that protect system Python
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt

echo -e "${GREEN}[✓] Installation Complete! You can now run the tool.${NC}"
echo -e "${GREEN}    Command: python3 test.py${NC}"

