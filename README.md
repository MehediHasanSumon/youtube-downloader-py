# YouTube & Media Downloader Pro (Next-Level Terminal TUI)

A state-of-the-art, interactive command-line YouTube video and playlist downloader with automated dependency setup, real-time metadata preview, lossless FFmpeg merging, and an ultra-modern Terminal User Interface (TUI).

Supports up to **8K, 4K, 1440p, 1080p60 MP4 video** and **320kbps MP3 audio**.

Works seamlessly on **Linux (Ubuntu / Debian / Mint)** and **Windows**.

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
> - Installs `yt-dlp` and `rich` from `requirements.txt`.
> - Checks for FFmpeg (and automatically downloads a standalone static Linux build if missing — **no root/sudo password required!**).
> - Launches `main.py`.

---

### 🪟 Windows

1. Double-click `run.bat` or run in CMD / PowerShell:
   ```cmd
   run.bat
   ```

---

## 💎 Next-Level UI/UX Features

- **Visual Hero Header & Status Badges**: Clean, branded dashboard displaying engine, FFmpeg, and OS status.
- **Instant Media Information Card**: Fetches video metadata with a live spinner and displays title, channel/artist, duration, view count, and content type before downloading.
- **Interactive Keyboard Navigation**: Smoothly navigate format options using keyboard arrow keys (`↑` / `↓`) and `Enter`, or press number keys (`1`–`5`) directly.
- **Maximum Quality (8K / 4K / 1080p60)**: Downloads the best video stream and best audio stream, then losslessly merges them into MP4 via FFmpeg.
- **Smart Disk Check & Auto-Resume**: Checks your destination folder directly before downloading. Files already on disk are skipped automatically. Incomplete downloads (`.part`) automatically resume from where they stopped.
- **Live Real-Time Rich Progress Engine**: Real-time progress bar tracking stream download, percentage, MB downloaded / total, speed in MB/s, and ETA. Separate status indicators for video download, audio download, and FFmpeg stream merging.
- **Playlist Dual-Tracking**: Shows overall playlist progress alongside the active video's download progress.
- **Completed Items Dashboard**: Displays real-time `✓ Completed` notifications for each video along with a structured summary table showing download status and file size.
- **Dedicated Log File (`youtube_downloader.log`)**: Automatically logs all downloads, skips, errors, and yt-dlp diagnostic messages. You can inspect logs directly from the interactive post-download menu.
- **Clean Terminal Experience**: Automatically clears terminal setup checks before launching the interactive dashboard.
- **Post-Download Action Dashboard**: Upon completion, view the download summary with an option to open the downloads folder directly in your system file manager (`xdg-open` on Linux, `File Explorer` on Windows).

---

## 🇧🇩 বাংলা নির্দেশিকা (Quick Guide in Bengali)

### লিনাক্স উবুন্টু / ডেবিয়ানে চালানো:
টার্মিনালে প্রজেক্ট ফোল্ডারে গিয়ে রান করুন:
```bash
chmod +x run.sh
./run.sh
```
`run.sh` স্বয়ংক্রিয়ভাবে Python ভার্চুয়াল এনভায়রনমেন্ট তৈরি করবে, `yt-dlp` ও `rich` ইন্সটল করবে এবং FFmpeg না থাকলে স্বয়ংক্রিয়ভাবে ডাউনলোড ও কনফিগার করে নেবে (কোনো root/sudo পাসওয়ার্ড লাগবে না)। চেক শেষ হওয়ার পর টার্মিনাল স্বয়ংক্রিয়ভাবে ক্লিয়ার হয়ে ফ্রেশ ইন্টারফেস ওপেন হবে।

### নতুন আকর্ষণীয় ফিচারসমূহ:
1. **লাইভ মিডিয়া কার্ড**: লিঙ্ক পেস্ট করতেই স্বয়ংক্রিয়ভাবে ভিডিওর নাম, চ্যানেল, ভিউ ও সময়সীমা প্রিভিউ আকারে দেখাবে।
2. **অ্যারো কি দিয়ে সিলেক্ট**: কীবোর্ডের `↑` / `↓` অ্যারো কি দিয়ে সহজেই কোয়ালিটি বেছে নেওয়া যাবে, কিংবা সরাসরি `1` থেকে `5` চাপলেও সিলেক্ট হয়ে যাবে।
3. **রিয়েলটাইম প্রগ্রেস ও কমপ্লিট স্ট্যাটাস**: প্রতিটি ভিডিও ডাউনলোড শেষে `✓ Completed` স্ট্যাটাস, ফাইল সাইজ ও সামারি টেবিলে সম্পূর্ণ রিপোর্ট দেখাবে।
4. **স্মার্ট অটো-রিজিউম ও স্কিপ**: আগে থেকে ডাউনলোড করা থাকলে স্বয়ংক্রিয়ভাবে স্কিপ করবে, আর অসম্পূর্ণ থাকলে সেখান থেকেই রিজুউম করবে।
5. **লগ ফাইল (`youtube_downloader.log`)**: প্রতিটি ডাউনলোডের সময়, গতি, সম্পন্ন হওয়া ফাইল এবং ত্রুটি স্বয়ংক্রিয়ভাবে লগ ফাইলে সেভ হবে এবং মেনু থেকেও দেখা যাবে।
6. **এক ক্লিকে ফোল্ডার ওপেন**: ডাউনলোড শেষে অপশন থেকে সরাসরি ফাইল ম্যানেজারে ফোল্ডার খুলে দেখার সুবিধা।
