#!/bin/bash

# 1. Update System and Install Basic Tools
echo "[*] Updating system and installing Firefox, Git, and Python..."
sudo apt update
sudo apt install -y firefox-esr git python3 python3-pip wget tar

# 2. Fix Geckodriver for Kali on Android (ARM64)
# We download it manually because 'apt install firefox-geckodriver' often fails on phones.
echo "[*] Installing Geckodriver for ARM64..."
wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux-aarch64.tar.gz
tar -xvzf geckodriver-v0.33.0-linux-aarch64.tar.gz
chmod +x geckodriver
sudo mv geckodriver /usr/bin/
rm geckodriver-v0.33.0-linux-aarch64.tar.gz

# 3. Install Python Requirements
echo "[*] Installing Python libraries from requirements.txt..."
pip3 install -r requirements.txt --break-system-packages

echo "[✓] Installation Complete! You can now run 'python3 test.py'"
