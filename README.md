# YouTube & Media Downloader (CLI)

A powerful, interactive command-line YouTube video and playlist downloader with automated dependency setup and lossless FFmpeg merging. Supports up to 8K, 4K, 1440p, 1080p60 video and 320kbps MP3 audio.

Works seamlessly on **Linux (Ubuntu / Debian)** and **Windows**.

---

## 🚀 How to Run

### 🐧 Linux (Ubuntu / Debian / Mint)

1. Open your terminal in this project folder:
   ```bash
   cd /path/to/youtube-downloader
   ```

2. Make `run.sh` executable (if not already):
   ```bash
   chmod +x run.sh
   ```

3. Launch the downloader:
   ```bash
   ./run.sh
   ```

> [!NOTE]
> The launcher (`./run.sh`) automatically:
> - Verifies Python 3 is installed.
> - Creates and activates a virtual environment (`venv`).
> - Installs `yt-dlp` from `requirements.txt`.
> - Checks for FFmpeg (and automatically downloads a standalone static Linux build if FFmpeg is missing from your system — **no root/sudo password required!**).
> - Launches `main.py`.

If you prefer installing FFmpeg system-wide on Ubuntu, you can optionally run:
```bash
sudo apt update && sudo apt install -y ffmpeg
```

---

### 🪟 Windows

1. Double-click `run.bat` or run in CMD / PowerShell:
   ```cmd
   run.bat
   ```

---

## 🎮 Features

- **Interactive Arrow-Key Menu**: Use `↑` / `↓` arrow keys and `Enter` to select quality format directly in your terminal (or press number keys `1`–`5`).
- **Maximum Quality**: Downloads best video + best audio and merges them losslessly into MP4 via FFmpeg (8K / 4K / 1440p / 1080p).
- **Playlist Support**: Automatically detects playlist links and organizes all videos into a dedicated folder with numbered order (`01 - Title.mp4`).
- **Audio Extraction**: High-quality 320kbps MP3 and original quality M4A.
- **Zero Configuration**: Fully automated setup script for both Ubuntu and Windows.

---

## 🇧🇩 বাংলা নির্দেশিকা (Quick Guide in Bengali)

### লিনাক্স উবুন্টুতে চালানো:
টার্মিনালে প্রজেক্ট ফোল্ডারে গিয়ে রান করুন:
```bash
chmod +x run.sh
./run.sh
```
`run.sh` স্বয়ংক্রিয়ভাবে Python এনভায়রনমেন্ট তৈরি করবে, `yt-dlp` ইন্সটল করবে এবং FFmpeg না থাকলে নিজে থেকেই ডাউনলোড করে কনফিগার করে নেবে (রুট/sudo পাসওয়ার্ড লাগবে না)।

মেনুতে কিবোর্ডের `↑` / `↓` অ্যারো কি দিয়ে কোয়ালিটি বেছে নিয়ে `Enter` চাপুন।
