@echo off
setlocal EnableDelayedExpansion
title YouTube Downloader Setup & Runner

echo ===================================================
echo     YouTube Downloader (Automated Launcher)
echo ===================================================
echo.

:: 1. Condition: Check if Python is installed and available in PATH
echo [1/4] Checking Python installation...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please download and install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
python --version

:: 2. Condition: Check if Virtual Environment (venv) exists, create if missing
echo.
echo [2/4] Checking virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Creating 'venv'...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully.
) else (
    echo [OK] Virtual environment already exists.
)

:: 3. Condition: Activate Virtual Environment
echo.
echo [3/4] Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    if !errorlevel! neq 0 (
        echo [ERROR] Could not activate the virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment activated.
) else (
    echo [ERROR] Activation script not found!
    pause
    exit /b 1
)

:: 4. Condition: Check if yt-dlp is installed, install dependencies if needed
echo.
echo [4/4] Checking dependencies...
python -c "import yt_dlp" >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Required packages not found. Installing...
    if exist "requirements.txt" (
        pip install -r requirements.txt
    ) else (
        pip install -U yt-dlp
    )
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install dependencies. Check your internet connection.
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed successfully.
) else (
    echo [OK] All required packages are already installed.
)

:: Optional Check: Check if FFmpeg is available on system
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [NOTE] FFmpeg was not detected in PATH.
    echo High-resolution stream merging works best when FFmpeg is installed.
)

:: 5. Condition: Check and run main.py
echo.
echo ===================================================
echo                Starting Downloader
echo ===================================================
echo.

if exist "main.py" (
    python main.py
) else (
    echo [ERROR] 'main.py' file not found in current folder!
)

echo.
echo ===================================================
echo Program execution finished.
pause
