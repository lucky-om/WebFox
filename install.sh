#!/bin/bash
echo "[*] Webfox v9.0 Ultimate Installer"

# 1. Install System Tools
sudo apt update
sudo apt install -y python3 python3-pip git wget tar firefox-esr

# 2. Install Python Libraries
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt

# 3. Install Geckodriver (Linux x64)
echo "[*] Installing Geckodriver..."
wget -O driver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz"
tar -xvf driver.tar.gz
chmod +x geckodriver
sudo mv geckodriver /usr/bin/
rm driver.tar.gz

echo "[✓] Installation Complete. Run: python3 test.py -help"

