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
import urllib.parse

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
    launcher = "run.bat" if sys.platform == "win32" else "./run.sh"
    print(f"Please run '{launcher}' or install it using: pip install -U yt-dlp\n")
    sys.exit(1)


def read_key() -> str:
    """
    Reads a single keypress or key event across Windows and Linux/Unix.
    Returns: 'UP', 'DOWN', 'LEFT', 'RIGHT', 'ENTER', 'SPACE', 'CTRL_C', or character string (e.g. '1', '2').
    """
    if sys.platform == "win32":
        try:
            import msvcrt
            key = msvcrt.getch()
            if key in (b'\x00', b'\xe0'):
                sub_key = msvcrt.getch()
                if sub_key in (b'H', b'\x48'):
                    return "UP"
                elif sub_key in (b'P', b'\x50'):
                    return "DOWN"
                elif sub_key in (b'K', b'\x4b'):
                    return "LEFT"
                elif sub_key in (b'M', b'\x4d'):
                    return "RIGHT"
                return ""
            elif key == b'\x1b':
                # Escape sequence in modern Windows terminals
                if msvcrt.kbhit():
                    ch2 = msvcrt.getch()
                    if ch2 in (b'[', b'O'):
                        if msvcrt.kbhit():
                            ch3 = msvcrt.getch()
                            if ch3 == b'A':
                                return "UP"
                            elif ch3 == b'B':
                                return "DOWN"
                            elif ch3 == b'C':
                                return "RIGHT"
                            elif ch3 == b'D':
                                return "LEFT"
                return "ESC"
            elif key in (b'\r', b'\n'):
                return "ENTER"
            elif key == b' ':
                return "SPACE"
            elif key == b'\x03':
                return "CTRL_C"
            else:
                return key.decode("utf-8", errors="ignore")
        except Exception:
            return ""
    else:
        try:
            import tty
            import termios
            import select

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                # Read raw bytes directly from fd to avoid Python's TextIOWrapper buffering
                ch = os.read(fd, 1)
                if not ch:
                    return ""
                if ch == b'\x1b':
                    # Escape sequence (e.g. arrow keys \x1b[A, \x1bOA, etc.)
                    rlist, _, _ = select.select([fd], [], [], 0.05)
                    if rlist:
                        seq = os.read(fd, 8)
                        if not seq:
                            return "ESC"
                        if seq in (b'[', b'O'):
                            rlist2, _, _ = select.select([fd], [], [], 0.05)
                            if rlist2:
                                seq += os.read(fd, 8)
                        if seq.endswith(b'A') and (b'[' in seq or b'O' in seq):
                            return "UP"
                        elif seq.endswith(b'B') and (b'[' in seq or b'O' in seq):
                            return "DOWN"
                        elif seq.endswith(b'C') and (b'[' in seq or b'O' in seq):
                            return "RIGHT"
                        elif seq.endswith(b'D') and (b'[' in seq or b'O' in seq):
                            return "LEFT"
                        return ""
                    return "ESC"
                elif ch in (b'\r', b'\n'):
                    return "ENTER"
                elif ch == b' ':
                    return "SPACE"
                elif ch == b'\x03':
                    return "CTRL_C"
                else:
                    return ch.decode("utf-8", errors="ignore")
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            return ""


# ====================================================================
#  Modern CLI Design System (Zero Emoji, Clean Typography & Badges)
# ====================================================================

class Style:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[90m"
    UNDER   = "\033[4m"

    # Foreground Colors
    WHITE   = "\033[97m"
    CYAN    = "\033[96m"
    BLUE    = "\033[94m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    MAGENTA = "\033[95m"


def render_box(lines: list[tuple[str, str]], width: int = 68, border_color: str = Style.CYAN) -> str:
    """
    Renders a modern terminal box with curved border corners and clean alignment.
    lines: list of (text, ansi_style) tuples.
    """
    max_len = max((len(text) for text, _ in lines), default=0)
    box_width = max(width, max_len + 6)
    inner = box_width - 4
    out = [f"  {border_color}╭" + "─" * inner + f"╮{Style.RESET}"]
    for text, style in lines:
        padded = text.ljust(inner - 2)
        out.append(f"  {border_color}│{Style.RESET} {style}{padded}{Style.RESET} {border_color}│{Style.RESET}")
    out.append(f"  {border_color}╰" + "─" * inner + f"╯{Style.RESET}")
    return "\n".join(out)


def print_header():
    """Prints the modern CLI application banner."""
    print()
    print(render_box([
        ("YOUTUBE & MEDIA DOWNLOADER CLI", Style.BOLD + Style.WHITE),
        ("High-speed downloads, lossless FFmpeg merge & smart disk resume", Style.DIM),
    ], border_color=Style.CYAN))
    print()


def format_bytes(bytes_num):
    """Format bytes into a readable string (KB, MB, GB)."""
    if not bytes_num:
        return "0.0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_num < 1024.0:
            return f"{bytes_num:3.1f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.1f} PB"


def make_progress_bar(percent_float: float, width: int = 20) -> str:
    """Constructs a smooth text progress bar."""
    filled = max(0, min(width, int(width * (percent_float / 100.0))))
    return "█" * filled + "░" * (width - filled)


def progress_hook(d):
    """Displays real-time modern CLI download progress."""
    status = d.get("status")
    if status == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)

        if total > 0:
            percent_num = (downloaded / total) * 100.0
        else:
            raw_p = d.get("_percent_str", "").replace("%", "").strip()
            try:
                percent_num = float(raw_p)
            except ValueError:
                percent_num = 0.0

        bar = make_progress_bar(percent_num, width=18)
        dl_str = format_bytes(downloaded)
        tot_str = format_bytes(total) if total > 0 else "N/A"
        speed = d.get("_speed_str", "N/A").strip()
        eta = d.get("_eta_str", "N/A").strip()

        line = (
            f"\r  \033[96;1m[DOWNLOAD]\033[0m "
            f"\033[96m[{bar}]\033[0m "
            f"\033[97;1m{percent_num:5.1f}%\033[0m "
            f"\033[90m|\033[0m {dl_str}/{tot_str} "
            f"\033[90m|\033[0m \033[93m{speed}\033[0m "
            f"\033[90m|\033[0m \033[90mETA\033[0m \033[97m{eta}\033[0m   "
        )
        sys.stdout.write(line)
        sys.stdout.flush()
    elif status == "finished":
        sys.stdout.write("\n  \033[93m[MERGE]\033[0m Processing streams and merging with FFmpeg...\n")
        sys.stdout.flush()


def interactive_menu(prompt: str, options: list[str], default_index: int = 0) -> int:
    """
    Renders an interactive CLI menu controlled via Keyboard Arrow Keys (Up/Down) & Enter.
    Falls back to numeric choice if stdin is non-interactive.
    """
    selected = default_index
    num_options = len(options)

    if not sys.stdin.isatty():
        # Fallback for non-interactive environments
        print(f"\n  {prompt}")
        for idx, opt in enumerate(options, 1):
            print(f"    [{idx}] {opt}")
        while True:
            choice = input(f"  Select option (1-{num_options}): ").strip()
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
            num = idx + 1
            if idx == selected:
                # Active selection: bold cyan arrow, highlight tag
                sys.stdout.write(f"\033[2K\r    \033[96;1m> [{num}] {option}\033[0m\n")
            else:
                # Inactive selection: dim tag, clean text
                sys.stdout.write(f"\033[2K\r      \033[90m[{num}]\033[0m {option}\n")
        sys.stdout.flush()

    print(f"  \033[1m{prompt}\033[0m")
    print(f"  \033[90m(Use Up / Down arrow keys or 1-{num_options} to select, Enter to confirm)\033[0m\n")
    render(first_time=True)

    try:
        while True:
            key = read_key()

            if key in ("UP", "k", "K", "w", "W"):
                selected = (selected - 1) % num_options
                render()
            elif key in ("DOWN", "j", "J", "s", "S"):
                selected = (selected + 1) % num_options
                render()
            elif key in ("ENTER", "SPACE"):
                break
            elif key == "CTRL_C":
                sys.stdout.write("\033[?25h\n")
                sys.stdout.flush()
                raise KeyboardInterrupt
            elif key.isdigit():
                num = int(key)
                if 1 <= num <= num_options:
                    selected = num - 1
                    render()
                    break
    finally:
        # Restore terminal cursor
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        # Flush any pending terminal input on Unix
        if sys.platform != "win32":
            try:
                import termios
                termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
            except Exception:
                pass

    print(f"  \033[92m[OK] Selected:\033[0m {options[selected]}\n")
    return selected


def extract_playlist_id(url: str) -> str | None:
    """Extracts playlist ID from a YouTube URL if present."""
    try:
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        if "list" in qs and qs["list"]:
            return qs["list"][0]
    except Exception:
        pass
    return None


def make_disk_check_filter(ydl, format_choice: int, is_playlist: bool = False):
    """
    Inspects the disk directly before downloading:
    - If the video/audio file is already on disk (> 1KB, not a temporary .part), skips download.
    - If missing or incomplete (.part), proceeds to download or resume.
    """
    if format_choice in (3, 4):
        # Audio formats
        valid_exts = {".mp3", ".m4a", ".opus", ".aac", ".flac", ".wav", ".ogg"}
    else:
        # Video formats
        valid_exts = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".ts"}

    def disk_check_filter(info_dict, *, incomplete=False):
        try:
            target = ydl.prepare_filename(info_dict)
            dir_name = os.path.dirname(target)
            if not os.path.isdir(dir_name):
                return None

            base, _ = os.path.splitext(target)

            # 1. Check exact base filename with valid media extensions
            for ext in valid_exts:
                cand = base + ext
                if os.path.isfile(cand) and os.path.getsize(cand) > 1024 and not cand.endswith(".part") and not cand.endswith(".ytdl"):
                    fname = os.path.basename(cand)
                    return f"\033[93m[SKIP]\033[0m '{fname}' already exists on disk. Skipping."

            # 2. For playlist videos, also check by numbered index prefix (e.g. '01 - ')
            index = info_dict.get("playlist_index")
            if is_playlist and index is not None:
                try:
                    prefix = f"{int(index):02d} - "
                    for f in os.listdir(dir_name):
                        if f.startswith(prefix) and any(f.endswith(e) for e in valid_exts):
                            full = os.path.join(dir_name, f)
                            if os.path.isfile(full) and os.path.getsize(full) > 1024 and not f.endswith(".part") and not f.endswith(".ytdl"):
                                return f"\033[93m[SKIP]\033[0m '{f}' already exists on disk. Skipping."
                except Exception:
                    pass
        except Exception:
            pass

        return None

    return disk_check_filter


def get_download_options(
    save_path: str,
    format_choice: int,
    is_playlist: bool = False,
) -> dict:
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
        "windowsfilenames": sys.platform == "win32",  # Safe Windows file names on Windows
        "ignoreerrors": True,      # Continue if one video in playlist has issues
        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 5,
        "progress_hooks": [progress_hook],
        "continuedl": True,        # Resume partially downloaded files (.part)
        "nooverwrites": True,      # Never overwrite existing files
        "noplaylist": not is_playlist,
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
            "final_ext": "mp4",
        })
    elif format_choice == 1:
        # Up to 1080p
        ydl_opts.update({
            "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "merge_output_format": "mp4",
            "final_ext": "mp4",
        })
    elif format_choice == 2:
        # Up to 720p
        ydl_opts.update({
            "format": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "merge_output_format": "mp4",
            "final_ext": "mp4",
        })
    elif format_choice == 3:
        # 320 kbps MP3
        ydl_opts.update({
            "format": "bestaudio/best",
            "final_ext": "mp3",
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
            "final_ext": "m4a",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }
            ],
        })

    return ydl_opts


def download(
    url: str,
    save_path: str = "downloads",
    format_choice: int = 0,
    is_playlist: bool = False,
):
    """Downloads media from URL with the selected configuration."""
    ydl_opts = get_download_options(
        save_path,
        format_choice=format_choice,
        is_playlist=is_playlist,
    )

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Attach disk checker filter to skip files already on disk
        ydl.params["match_filter"] = make_disk_check_filter(
            ydl, format_choice=format_choice, is_playlist=is_playlist
        )
        ydl.download([url])


def main():
    print_header()

    print(f"  \033[96;1m[INPUT]\033[0m Enter Video or Playlist URL:")
    url = input("  > ").strip()
    if not url:
        print(f"\n  \033[91m[ERROR] No URL provided. Aborting.\033[0m\n")
        sys.exit(1)

    playlist_id = extract_playlist_id(url)
    is_playlist = playlist_id is not None or "list=" in url

    # If URL contains both a video and playlist parameter
    if is_playlist and ("v=" in url or "youtu.be/" in url):
        print()
        print(render_box([
            ("NOTICE: Video in Playlist Detected", Style.BOLD + Style.YELLOW),
            ("This link points to an individual video that belongs to a playlist.", Style.DIM),
        ], border_color=Style.YELLOW))
        print(f"    [1] Download Entire Playlist (Auto-skips existing files)")
        print(f"    [2] Download Only This Single Video")
        choice = input("    Selection [1-2, default: 1]: ").strip()
        if choice == "2":
            is_playlist = False

    print()
    # Interactive Arrow Key Menu
    menu_options = [
        "Maximum Quality Video  (8K / 4K / 1440p / 1080p MP4 + Best Audio)",
        "1080p Full HD Video    (Standard MP4)",
        "720p HD Video          (Fast Download / Smaller Size)",
        "Audio Only             (Ultra Quality 320kbps MP3)",
        "Audio Only             (Original Quality M4A)",
    ]

    selected_format = interactive_menu("Select Quality & Format:", menu_options, default_index=0)

    # Destination folder
    print(f"  \033[96;1m[INPUT]\033[0m Destination folder [Press Enter for 'downloads']:")
    folder_input = input("  > ").strip()
    folder = folder_input if folder_input else "downloads"
    full_path = os.path.abspath(folder)

    print()
    if is_playlist:
        print(f"  \033[94m[INFO]\033[0m Playlist detected. Videos will be organized into a dedicated playlist folder.")
        print(f"  \033[92m[INFO]\033[0m Smart Disk Check active: existing files will be skipped automatically.")
        print(f"  \033[90m[INFO] Incomplete (.part) files will resume from where they stopped.\033[0m")
    print(f"  \033[94m[PATH]\033[0m Output Directory: {full_path}")
    print(f"  \033[90m" + "─" * 64 + "\033[0m\n")

    try:
        download(
            url,
            folder,
            format_choice=selected_format,
            is_playlist=is_playlist,
        )
        print(f"\n  \033[90m" + "─" * 64 + "\033[0m")
        print()
        print(render_box([
            ("[SUCCESS] Download completed successfully!", Style.BOLD + Style.GREEN),
            (f"Saved in: {full_path}", Style.WHITE),
        ], border_color=Style.GREEN))
        print()
    except KeyboardInterrupt:
        print(f"\n\n  \033[93m[ABORT] Download canceled by user.\033[0m\n")
    except Exception as e:
        print(f"\n\n  \033[91m[ERROR] An unexpected error occurred: {e}\033[0m\n")


if __name__ == "__main__":
    main()