#!/usr/bin/env python3
"""
====================================================================
 YouTube & Media Downloader (Single Video / Full Playlist)
 Interactive Arrow Key Navigation (↑ / ↓, Enter)
 Maximum Quality 8K / 4K / 1440p / 1080p60 + FFmpeg Lossless Merge
 Optimized for Windows & English Interface
====================================================================
"""

import os
import sys
import ctypes

# Enable UTF-8 and ANSI colors / Virtual Terminal Processing on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    try:
        kernel32 = ctypes.windll.kernel32
        h_stdout = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(h_stdout, ctypes.byref(mode)):
            kernel32.SetConsoleMode(h_stdout, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass

# Ensure local ./ffmpeg/bin is added to PATH if present
_LOCAL_FFMPEG_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg", "bin")
if os.path.isdir(_LOCAL_FFMPEG_BIN) and _LOCAL_FFMPEG_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _LOCAL_FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")

try:
    import yt_dlp
except ImportError:
    print("\n\033[91m[ERROR] 'yt-dlp' package is missing!\033[0m")
    print("Please run 'run.bat' or install it using: pip install -U yt-dlp\n")
    sys.exit(1)


# Check if msvcrt (Windows keyboard input) is available
try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


def format_bytes(bytes_num):
    """Format bytes into a readable string (KB, MB, GB)."""
    if not bytes_num:
        return "N/A"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_num < 1024.0:
            return f"{bytes_num:3.1f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.1f} PB"


def progress_hook(d):
    """Display real-time download progress."""
    status = d.get("status")
    if status == "downloading":
        percent = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        downloaded = format_bytes(d.get("downloaded_bytes", 0))
        total = format_bytes(d.get("total_bytes") or d.get("total_bytes_estimate", 0))

        sys.stdout.write(f"\r\033[96m[Downloading]\033[0m {percent} | {downloaded}/{total} | Speed: {speed} | ETA: {eta}   ")
        sys.stdout.flush()
    elif status == "finished":
        print("\n\033[93m[Processing] Download completed! Merging with FFmpeg...\033[0m")


def interactive_menu(prompt: str, options: list[str], default_index: int = 0) -> int:
    """
    Renders an interactive CLI menu controlled via Keyboard Arrow Keys (Up/Down) & Enter.
    """
    selected = default_index
    num_options = len(options)

    if not HAS_MSVCRT:
        # Fallback for environments without msvcrt
        print(f"\n{prompt}")
        for idx, opt in enumerate(options, 1):
            print(f"  [{idx}] {opt}")
        while True:
            choice = input(f"Select option (1-{num_options}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= num_options:
                return int(choice) - 1

    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    def render(first_time: bool = False):
        if not first_time:
            # Move cursor up by the number of option lines
            sys.stdout.write(f"\033[{num_options}A")

        for idx, option in enumerate(options):
            if idx == selected:
                # Highlight active option with cyan color & indicator
                sys.stdout.write(f"\033[2K\r  \033[96m\033[1m❯ [●] {option}\033[0m\n")
            else:
                # Dim inactive options
                sys.stdout.write(f"\033[2K\r    \033[90m[ ]\033[0m {option}\n")
        sys.stdout.flush()

    print(f"\n\033[1m{prompt}\033[0m")
    print("\033[90m(Use ↑ / ↓ arrow keys to move, Enter to confirm)\033[0m")
    render(first_time=True)

    try:
        while True:
            key = msvcrt.getch()

            # Arrow keys or special keys on Windows
            if key in (b'\x00', b'\xe0'):
                sub_key = msvcrt.getch()
                if sub_key == b'H':  # Up Arrow
                    selected = (selected - 1) % num_options
                    render()
                elif sub_key == b'P':  # Down Arrow
                    selected = (selected + 1) % num_options
                    render()
            # Enter key
            elif key in (b'\r', b'\n'):
                break
            # Ctrl + C
            elif key == b'\x03':
                sys.stdout.write("\033[?25h\n")
                sys.stdout.flush()
                raise KeyboardInterrupt
            # Direct number key shortcuts (1-9)
            elif key.isdigit():
                num = int(key.decode("ascii", errors="ignore"))
                if 1 <= num <= num_options:
                    selected = num - 1
                    render()
                    break
    finally:
        # Restore terminal cursor
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    print(f"\033[92m✔ Selected:\033[0m {options[selected]}\n")
    return selected


def get_download_options(save_path: str, format_choice: int, is_playlist: bool = False) -> dict:
    """Constructs yt-dlp configuration options based on user's interactive selection."""
    os.makedirs(save_path, exist_ok=True)

    if is_playlist:
        out_template = os.path.join(
            save_path,
            "%(playlist_title|Playlist)s",
            "%(playlist_index&{:02d} - |)s%(title)s.%(ext)s",
        )
    else:
        out_template = os.path.join(save_path, "%(title)s.%(ext)s")

    ydl_opts = {
        "outtmpl": {"default": out_template},
        "windowsfilenames": True,  # Safe Windows file names
        "ignoreerrors": True,      # Continue if one video in playlist has issues
        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 5,
        "progress_hooks": [progress_hook],
    }

    # Format choices mapping:
    # 0 -> Maximum Quality (8K/4K/1440p/1080p60 MP4)
    # 1 -> 1080p Full HD Video (MP4)
    # 2 -> 720p HD Video (MP4)
    # 3 -> Audio Only (320kbps MP3)
    # 4 -> Audio Only (Best Original / M4A)

    if format_choice == 0:
        # Absolute best video + best audio
        ydl_opts.update({
            "format": "bestvideo+bestaudio/best",
            "format_sort": ["res", "fps", "hdr:12", "vcodec", "channels", "br", "asr"],
            "merge_output_format": "mp4",
        })
    elif format_choice == 1:
        # Up to 1080p
        ydl_opts.update({
            "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "merge_output_format": "mp4",
        })
    elif format_choice == 2:
        # Up to 720p
        ydl_opts.update({
            "format": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "merge_output_format": "mp4",
        })
    elif format_choice == 3:
        # 320 kbps MP3
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
        })
    elif format_choice == 4:
        # Original Best Audio (M4A/AAC/Opus)
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }
            ],
        })

    return ydl_opts


def download(url: str, save_path: str = "downloads", format_choice: int = 0):
    """Downloads media from URL with the selected configuration."""
    is_playlist = "list=" in url
    if is_playlist:
        print("\033[94m[Info] Playlist detected. Videos will be organized into a dedicated playlist folder.\033[0m")

    ydl_opts = get_download_options(save_path, format_choice=format_choice, is_playlist=is_playlist)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main():
    print("\033[95m=====================================================\033[0m")
    print("\033[97m\033[1m      YouTube / Universal Video & Audio Downloader   \033[0m")
    print("\033[90m          (Interactive Arrow Key Navigation)         \033[0m")
    print("\033[95m=====================================================\033[0m\n")

    url = input("\033[1mEnter Video or Playlist URL:\033[0m ").strip()
    if not url:
        print("\033[91m[!] No URL provided. Exiting.\033[0m")
        sys.exit(1)

    # Interactive Arrow Key Menu
    menu_options = [
        "Maximum Quality Video (8K / 4K / 1440p / 1080p MP4 + Best Audio)",
        "1080p Full HD Video (Standard MP4)",
        "720p HD Video (Fast Download / Smaller Size)",
        "Audio Only - Ultra Quality (320kbps MP3)",
        "Audio Only - Original Quality (M4A)",
    ]

    selected_format = interactive_menu("Select Quality & Format:", menu_options, default_index=0)

    # Destination folder
    folder_input = input("Enter destination folder (Press Enter for 'downloads'): ").strip()
    folder = folder_input if folder_input else "downloads"
    full_path = os.path.abspath(folder)

    print(f"\n\033[94m[Destination]\033[0m {full_path}")
    print("\033[90m" + "-" * 55 + "\033[0m")

    try:
        download(url, folder, format_choice=selected_format)
        print("\033[90m" + "-" * 55 + "\033[0m")
        print("\n\033[92m\033[1m✔ [Success] Download completed successfully!\033[0m")
        print(f"\033[94m[Saved In]\033[0m {full_path}\n")
    except KeyboardInterrupt:
        print("\n\n\033[93m[!] Download canceled by user.\033[0m\n")
    except Exception as e:
        print(f"\n\n\033[91m[Error] An unexpected error occurred: {e}\033[0m\n")


if __name__ == "__main__":
    main()