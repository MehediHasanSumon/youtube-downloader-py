#!/usr/bin/env bash
# ====================================================================
#  YouTube Downloader - Automated Launcher for Linux / Ubuntu
# ====================================================================

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Ensure script runs in its own directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo -e "${CYAN}===================================================${NC}"
echo -e "${BOLD}    YouTube Downloader (Linux / Ubuntu Launcher)    ${NC}"
echo -e "${CYAN}===================================================${NC}"
echo ""

# 1. Condition: Check if Python 3 is installed
echo -e "${BOLD}[1/5] Checking Python 3 installation...${NC}"
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}[ERROR] Python 3 is not installed or not available in PATH.${NC}"
    echo -e "Please install Python on Ubuntu by running:"
    echo -e "    ${YELLOW}sudo apt update && sudo apt install -y python3 python3-venv python3-pip${NC}"
    echo ""
    exit 1
fi
PYTHON_VER=$(python3 --version 2>&1)
echo -e "${GREEN}[OK]${NC} Found: $PYTHON_VER"

# 2. Condition: Check if Virtual Environment (venv) exists, create if missing
echo ""
echo -e "${BOLD}[2/5] Checking virtual environment...${NC}"
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${CYAN}[INFO]${NC} Virtual environment not found. Creating 'venv'..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment!${NC}"
        echo -e "On Ubuntu, you might need to install python3-venv:"
        echo -e "    ${YELLOW}sudo apt install -y python3-venv${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Virtual environment created successfully."
else
    echo -e "${GREEN}[OK]${NC} Virtual environment already exists."
fi

# 3. Condition: Activate Virtual Environment
echo ""
echo -e "${BOLD}[3/5] Activating virtual environment...${NC}"
# shellcheck disable=SC1091
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Could not activate virtual environment!${NC}"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Virtual environment activated."

# 4. Condition: Check if yt-dlp and rich are installed, install dependencies if needed
echo ""
echo -e "${BOLD}[4/5] Checking dependencies...${NC}"
python3 -c "import yt_dlp, rich" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${CYAN}[INFO]${NC} Required packages not found. Installing..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        pip install -U yt-dlp
    fi
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to install dependencies. Check your internet connection.${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Dependencies installed successfully."
else
    echo -e "${GREEN}[OK]${NC} All required packages are already installed."
fi

# 5. Condition: Check and Setup FFmpeg (Automatic download & PATH setup if missing)
echo ""
echo -e "${BOLD}[5/5] Checking FFmpeg installation...${NC}"

# If local ffmpeg/bin exists, add to PATH immediately
if [ -d "$SCRIPT_DIR/ffmpeg/bin" ]; then
    export PATH="$SCRIPT_DIR/ffmpeg/bin:$PATH"
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
    echo -e "${CYAN}[INFO]${NC} FFmpeg not found on system PATH."
    echo -e "${CYAN}[INFO]${NC} Starting automatic standalone FFmpeg setup..."
    if [ -f "setup_ffmpeg.py" ]; then
        python3 setup_ffmpeg.py
        if [ $? -eq 0 ]; then
            export PATH="$SCRIPT_DIR/ffmpeg/bin:$PATH"
            echo -e "${GREEN}[OK]${NC} FFmpeg setup completed and added to PATH."
        else
            echo -e "${YELLOW}[WARNING] Automatic FFmpeg setup could not complete.${NC}"
            echo -e "You can install it system-wide with: ${YELLOW}sudo apt install -y ffmpeg${NC}"
        fi
    else
        echo -e "${YELLOW}[WARNING] setup_ffmpeg.py not found.${NC}"
    fi
else
    FFMPEG_VER=$(ffmpeg -version 2>/dev/null | head -n 1)
    echo -e "${GREEN}[OK]${NC} FFmpeg is ready: $FFMPEG_VER"
fi

# 6. Condition: Run main.py
echo ""
echo -e "${CYAN}===================================================${NC}"
echo -e "${BOLD}               Starting Downloader                 ${NC}"
echo -e "${CYAN}===================================================${NC}"

# Brief pause so user sees all checks passed, then clear screen for clean UI
sleep 1
clear

if [ -f "main.py" ]; then
    python3 main.py "$@"
else
    echo -e "${RED}[ERROR] 'main.py' file not found in $SCRIPT_DIR!${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}===================================================${NC}"
echo -e "${GREEN}Program execution finished.${NC}"
echo -e "${CYAN}===================================================${NC}"
