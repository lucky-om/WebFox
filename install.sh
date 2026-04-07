#!/bin/bash
# ============================================================
#   WebFox v4.0 — Smart Installer
#   Supports: Termux (Android), Kali, Ubuntu, Debian, Parrot
#   Author: Lucky
# ============================================================

GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while ps -p $pid > /dev/null 2>&1; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
    echo -e "${GREEN}[DONE]${NC}"
}

clear
echo -e "${CYAN}"
echo "
░░██╗░░░░░░░██╗███████╗██████╗░███████╗░█████╗░██╗░░██╗
░░██║░░██╗░░██║██╔════╝██╔══██╗██╔════╝██╔══██╗╚██╗██╔╝
░░╚██╗████╗██╔╝█████╗░░██████╦╝█████╗░░██║░░██║░╚███╔╝░
░░░████╔═████║░██╔══╝░░██╔══██╗██╔══╝░░██║░░██║░██╔██╗░
░░░╚██╔╝░╚██╔╝░███████╗██████╦╝██║░░░░░╚█████╔╝██╔╝╚██╗
░░░░╚═╝░░░╚═╝░░╚══════╝╚═════╝░╚═╝░░░░░░╚════╝░╚═╝░░╚═╝
"
echo -e "${BOLD}-- WEBFOX RECON SETUP WIZARD v4.0 --${NC}\n"
echo -e "${GREEN}Author : Lucky${NC}\n"

# ── Environment Detection ────────────────────────────────────────────────────
IS_TERMUX=false
IS_ROOT=false
ARCH=$(uname -m)

if [ -n "$PREFIX" ] && echo "$PREFIX" | grep -q "com.termux"; then
    IS_TERMUX=true
    echo -e "${YELLOW}[!] Termux (Android) detected. Adjusting installation...${NC}"
fi

if [ "$EUID" -eq 0 ]; then
    IS_ROOT=true
fi

if [ "$IS_TERMUX" = false ] && [ "$IS_ROOT" = false ]; then
    echo -e "${RED}[!] On Linux, please run as root: sudo ./install.sh${NC}"
    exit 1
fi

echo -e "${CYAN}[*] Architecture : ${NC}$ARCH"
echo -e "${CYAN}[*] Termux Mode  : ${NC}$IS_TERMUX"
echo -e "${CYAN}[*] Root         : ${NC}$IS_ROOT"
echo ""

# ── Step 1: Package Installation ─────────────────────────────────────────────
echo -e "${CYAN}[1/4] Installing System Packages...${NC}"

if [ "$IS_TERMUX" = true ]; then
    echo -ne "  > Updating Termux packages"
    pkg update -y -q > /dev/null 2>&1 &
    spinner $!

    echo -ne "  > Installing Python, Git, Curl, OpenSSL"
    pkg install -y python git curl openssl-tool wget > /dev/null 2>&1 &
    spinner $!
else
    echo -ne "  > Updating apt repositories"
    apt-get update -qq > /dev/null 2>&1 &
    spinner $!

    echo -ne "  > Installing Python3, Pip, Git, Curl"
    apt-get install -y python3 python3-pip python3-venv git wget curl unzip > /dev/null 2>&1 &
    spinner $!
fi

# ── Step 2: Python Dependencies ──────────────────────────────────────────────
echo -e "\n${CYAN}[2/4] Installing Python Libraries...${NC}"
echo -ne "  > Installing from requirements.txt"

if [ "$IS_TERMUX" = true ]; then
    pip install -r requirements.txt --quiet 2>&1 &
else
    pip3 install -r requirements.txt --break-system-packages --quiet 2>&1 &
fi
spinner $!

# ── Step 3: Geckodriver / Firefox (Linux only) ───────────────────────────────
echo -e "\n${CYAN}[3/4] Browser Setup...${NC}"

if [ "$IS_TERMUX" = true ]; then
    echo -e "${YELLOW}  > Termux: Skipping Firefox and Geckodriver (not supported on Android).${NC}"
    echo -e "${YELLOW}  > Screenshots will be automatically disabled for Termux.${NC}"
else
    # Install Firefox
    echo -ne "  > Installing Firefox ESR"
    apt-get install -y firefox-esr > /dev/null 2>&1 &
    spinner $!

    # Detect architecture for correct geckodriver binary
    echo -ne "  > Detecting CPU architecture: $ARCH"
    echo ""

    GK_VERSION="0.36.0"

    case "$ARCH" in
        x86_64)
            GK_FILE="geckodriver-v${GK_VERSION}-linux64.tar.gz"
            ;;
        aarch64 | arm64)
            GK_FILE="geckodriver-v${GK_VERSION}-linux-aarch64.tar.gz"
            ;;
        armv7l | armhf)
            GK_FILE="geckodriver-v${GK_VERSION}-linux32.tar.gz"
            ;;
        i686 | i386)
            GK_FILE="geckodriver-v${GK_VERSION}-linux32.tar.gz"
            ;;
        *)
            echo -e "${RED}  [!] Unsupported architecture: $ARCH. Skipping geckodriver.${NC}"
            GK_FILE=""
            ;;
    esac

    if [ -n "$GK_FILE" ]; then
        GK_URL="https://github.com/mozilla/geckodriver/releases/download/v${GK_VERSION}/${GK_FILE}"
        echo -ne "  > Downloading geckodriver for $ARCH"

        rm -f /tmp/geckodriver.tar.gz /usr/bin/geckodriver
        wget -q -O /tmp/geckodriver.tar.gz "$GK_URL"

        if [ -f "/tmp/geckodriver.tar.gz" ]; then
            tar -xf /tmp/geckodriver.tar.gz -C /tmp/
            chmod +x /tmp/geckodriver
            mv /tmp/geckodriver /usr/bin/geckodriver
            rm /tmp/geckodriver.tar.gz
            echo -e "${GREEN}  > Geckodriver installed at /usr/bin/geckodriver${NC}"
        else
            echo -e "${RED}  [!] Download failed. Check internet connection. Skipping.${NC}"
        fi
    fi
fi

# ── Step 4: Permissions ──────────────────────────────────────────────────────
echo -e "\n${CYAN}[4/4] Setting Permissions...${NC}"
echo -ne "  > Setting execute permissions"
chmod +x test.py 2>/dev/null
echo -e "${GREEN}[DONE]${NC}"

# ── Complete ─────────────────────────────────────────────────────────────────
echo -e "\n${GREEN}================================================"
echo -e "   [✓] SYSTEM UPDATE COMPLETE"
echo -e "   [✓] DEPENDENCIES INSTALLED"
echo -e "   [✓] ENVIRONMENT READY"
if [ "$IS_TERMUX" = true ]; then
echo -e "   [~] Screenshots: DISABLED (Termux)"
else
echo -e "   [✓] Geckodriver: INSTALLED"
fi
echo -e "   [★] WebFox Recon Framework v4.0 by Lucky"
echo -e "================================================${NC}"
echo -e "${YELLOW}"
echo -e "   ╔═══════════════════════════════════════════╗"
echo -e "   ║         STARTUP QUICK REFERENCE           ║"
echo -e "   ║───────────────────────────────────────────║"
echo -e "   ║  FULL SCAN  : python3 test.py <dom> -scan ║"
echo -e "   ║  FAST SCAN  : python3 test.py <dom> -fast ║"
echo -e "   ║  GUI        : streamlit run gui.py         ║"
echo -e "   ║  HELP       : python3 test.py -help        ║"
echo -e "   ║───────────────────────────────────────────║"
echo -e "   ║  Author : Lucky  |  WebFox v4.0           ║"
echo -e "   ╚═══════════════════════════════════════════╝"
echo -e "${NC}"
