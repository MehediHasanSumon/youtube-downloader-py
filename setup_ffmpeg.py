#!/usr/bin/env python3
"""
====================================================================
 Automatic FFmpeg Downloader & PATH Configurator
 - Supports Linux (Ubuntu / Debian / etc.) and Windows (x86_64 & ARM64)
 - Checks system & local PATH for ffmpeg
 - Downloads official static FFmpeg builds with progress tracking
 - Extracts binaries to ./ffmpeg/bin
 - Configures PATH (Registry for Windows, environment for Linux)
====================================================================
"""

import os
import sys
import shutil
import urllib.request
import zipfile
import tarfile
import time
import subprocess
import platform

# Enable UTF-8 encoding and ANSI Virtual Terminal Processing on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        h_stdout = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(h_stdout, ctypes.byref(mode)):
            kernel32.SetConsoleMode(h_stdout, mode.value | 0x0004)
    except Exception:
        pass

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def get_ffmpeg_urls() -> tuple[list[str], str]:
    """Returns the mirror URLs and archive extension appropriate for the current platform."""
    is_windows = sys.platform == "win32"
    arch = platform.machine().lower()

    if is_windows:
        urls = [
            "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
            "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
            "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
        ]
        return urls, ".zip"
    else:
        # Linux / Unix
        if "arm" in arch or "aarch64" in arch:
            urls = [
                "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz",
                "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz",
            ]
        else:
            urls = [
                "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz",
                "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",
            ]
        return urls, ".tar.xz"


def format_bytes(bytes_num: float) -> str:
    """Format bytes into readable units."""
    if not bytes_num:
        return "0.0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_num < 1024.0:
            return f"{bytes_num:3.1f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.1f} TB"


def download_with_progress(url: str, output_path: str) -> bool:
    """Downloads a file with real-time speed, percentage, and ETA progress."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=40) as response, open(output_path, "wb") as out_file:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            start_time = time.time()
            last_update = start_time
            block_size = 1024 * 256  # 256 KB blocks

            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                out_file.write(buffer)
                downloaded += len(buffer)
                now = time.time()

                # Update progress roughly every 0.1s
                if now - last_update >= 0.1 or (total_size > 0 and downloaded == total_size):
                    last_update = now
                    elapsed = max(now - start_time, 0.001)
                    speed = downloaded / elapsed

                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        remaining_bytes = total_size - downloaded
                        eta_seconds = int(remaining_bytes / speed) if speed > 0 else 0
                        eta_str = time.strftime("%M:%S", time.gmtime(eta_seconds))

                        bar_len = 25
                        filled = int(bar_len * downloaded // total_size)
                        bar = "=" * filled + "-" * (bar_len - filled)

                        status = (
                            f"\r{CYAN}[Downloading]{RESET} [{bar}] {percent:5.1f}% "
                            f"| {format_bytes(downloaded)}/{format_bytes(total_size)} "
                            f"| {format_bytes(speed)}/s | ETA: {eta_str}  "
                        )
                    else:
                        status = f"\r{CYAN}[Downloading]{RESET} {format_bytes(downloaded)} | {format_bytes(speed)}/s   "

                    sys.stdout.write(status)
                    sys.stdout.flush()

            sys.stdout.write("\n")
            return True
    except Exception as e:
        sys.stdout.write(f"\n{RED}[Error]{RESET} Download failed from {url}: {e}\n")
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except OSError:
                pass
        return False


def extract_ffmpeg(archive_path: str, destination_dir: str) -> bool:
    """Extracts ffmpeg, ffprobe, and ffplay binaries to destination_dir/bin."""
    print(f"{CYAN}[Extracting]{RESET} Unpacking FFmpeg archive...")
    bin_dir = os.path.join(destination_dir, "bin")
    os.makedirs(bin_dir, exist_ok=True)

    target_binaries = (
        {"ffmpeg.exe", "ffprobe.exe", "ffplay.exe"}
        if sys.platform == "win32"
        else {"ffmpeg", "ffprobe", "ffplay"}
    )

    extracted_count = 0

    # 1. Check if zip archive
    if zipfile.is_zipfile(archive_path):
        try:
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    filename = os.path.basename(member)
                    if filename.lower() in {b.lower() for b in target_binaries}:
                        target_file = os.path.join(bin_dir, filename)
                        with zip_ref.open(member) as source, open(target_file, "wb") as target:
                            shutil.copyfileobj(source, target)
                        if sys.platform != "win32":
                            os.chmod(target_file, 0o755)
                        extracted_count += 1
                        print(f"  {GREEN}✔{RESET} Extracted {filename} -> {target_file}")
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} Failed to extract zip archive: {e}")
            return False

    # 2. Check if tar / tar.xz / tar.gz archive
    else:
        try:
            with tarfile.open(archive_path, "r:*") as tar_ref:
                for member in tar_ref.getmembers():
                    filename = os.path.basename(member.name)
                    if filename in target_binaries:
                        target_file = os.path.join(bin_dir, filename)
                        f = tar_ref.extractfile(member)
                        if f is not None:
                            with open(target_file, "wb") as target:
                                shutil.copyfileobj(f, target)
                            if sys.platform != "win32":
                                os.chmod(target_file, 0o755)
                            extracted_count += 1
                            print(f"  {GREEN}✔{RESET} Extracted {filename} -> {target_file}")
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} Failed to extract tar archive: {e}")
            return False

    if extracted_count > 0:
        print(f"{GREEN}[OK]{RESET} Successfully extracted {extracted_count} FFmpeg binaries.")
        return True
    else:
        print(f"{RED}[ERROR]{RESET} No FFmpeg executables found in archive.")
        return False


def configure_path(directory_to_add: str) -> bool:
    """Configures system/user environment to permanently or persistently recognize FFmpeg."""
    directory_to_add = os.path.abspath(directory_to_add)

    # Windows Registry configuration
    if sys.platform == "win32":
        try:
            import winreg
            import ctypes

            reg_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0,
                winreg.KEY_READ | winreg.KEY_WRITE,
            )

            try:
                current_path, _ = winreg.QueryValueEx(reg_key, "Path")
            except FileNotFoundError:
                current_path = ""

            existing_paths = [p.strip() for p in current_path.split(";") if p.strip()]

            if any(os.path.normpath(p).lower() == os.path.normpath(directory_to_add).lower() for p in existing_paths):
                winreg.CloseKey(reg_key)
                return True

            existing_paths.append(directory_to_add)
            new_path_val = ";".join(existing_paths)

            winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path_val)
            winreg.CloseKey(reg_key)

            try:
                HWND_BROADCAST = 0xFFFF
                WM_SETTINGCHANGE = 0x001A
                SMTO_ABORTIFHUNG = 0x0002
                result = ctypes.c_long()
                ctypes.windll.user32.SendMessageTimeoutW(
                    HWND_BROADCAST,
                    WM_SETTINGCHANGE,
                    0,
                    "Environment",
                    SMTO_ABORTIFHUNG,
                    3000,
                    ctypes.byref(result),
                )
            except Exception:
                pass

            print(f"{GREEN}[OK]{RESET} Added {directory_to_add} to permanent Windows User PATH.")
            return True
        except Exception as e:
            print(f"{YELLOW}[WARNING]{RESET} Could not update Windows User PATH in registry: {e}")
            return False

    else:
        # On Linux/Ubuntu: binaries in ./ffmpeg/bin are handled dynamically by run.sh and main.py
        print(f"{GREEN}[OK]{RESET} FFmpeg available in local path: {directory_to_add}")
        print(f"{CYAN}[Tip]{RESET} You can also install system-wide via: sudo apt install ffmpeg")
        return True


def is_ffmpeg_installed() -> bool:
    """Check if ffmpeg executable is available in system PATH or can be invoked."""
    ffmpeg_cmd = shutil.which("ffmpeg")
    if ffmpeg_cmd:
        return True
    try:
        res = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        return res.returncode == 0
    except Exception:
        return False


def setup_ffmpeg(force: bool = False) -> bool:
    """Main setup procedure for FFmpeg."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    local_ffmpeg_dir = os.path.join(project_root, "ffmpeg")
    local_bin_dir = os.path.join(local_ffmpeg_dir, "bin")

    binary_name = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
    local_ffmpeg_binary = os.path.join(local_bin_dir, binary_name)

    # Add local bin dir to current process PATH
    if os.path.exists(local_bin_dir) and local_bin_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = local_bin_dir + os.pathsep + os.environ.get("PATH", "")

    # Check if already installed
    if not force:
        if os.path.isfile(local_ffmpeg_binary):
            print(f"{GREEN}[OK]{RESET} FFmpeg is already installed locally in: {local_bin_dir}")
            configure_path(local_bin_dir)
            return True

        if is_ffmpeg_installed():
            print(f"{GREEN}[OK]{RESET} FFmpeg is already installed and available on system PATH.")
            return True

    os_label = "Windows" if sys.platform == "win32" else f"Linux ({platform.machine()})"
    print(f"\n{BOLD}{YELLOW}==================================================={RESET}")
    print(f"{BOLD}{YELLOW}          FFmpeg Automatic Setup for {os_label}    {RESET}")
    print(f"{BOLD}{YELLOW}==================================================={RESET}\n")
    print(f"{CYAN}[INFO]{RESET} FFmpeg not found. Downloading static standalone build...")

    urls, ext = get_ffmpeg_urls()
    archive_temp = os.path.join(project_root, f"ffmpeg_temp{ext}")
    download_success = False

    for idx, url in enumerate(urls, 1):
        print(f"\n{CYAN}[Source {idx}/{len(urls)}]{RESET} Downloading from: {url}")
        if download_with_progress(url, archive_temp):
            download_success = True
            break
        else:
            print(f"{YELLOW}[!] Trying next mirror...{RESET}")

    if not download_success:
        print(f"\n{RED}[ERROR]{RESET} Failed to download FFmpeg from all available mirrors.")
        if sys.platform != "win32":
            print(f"{YELLOW}[Solution]{RESET} Run: sudo apt update && sudo apt install -y ffmpeg")
        else:
            print(f"Please install FFmpeg manually from: https://www.gyan.dev/ffmpeg/builds/")
        return False

    # Extract
    extract_success = extract_ffmpeg(archive_temp, local_ffmpeg_dir)

    # Clean up temporary archive
    if os.path.exists(archive_temp):
        try:
            os.remove(archive_temp)
        except OSError:
            pass

    if not extract_success:
        return False

    # Configure PATH
    configure_path(local_bin_dir)

    # Ensure current process PATH includes local_bin_dir
    os.environ["PATH"] = local_bin_dir + os.pathsep + os.environ.get("PATH", "")

    # Verify
    try:
        res = subprocess.run(
            [local_ffmpeg_binary, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            first_line = res.stdout.splitlines()[0] if res.stdout else "FFmpeg ready"
            print(f"\n{GREEN}{BOLD}✔ [Success]{RESET} {first_line}")
            print(f"{GREEN}[OK]{RESET} FFmpeg setup completed successfully!\n")
            return True
    except Exception as e:
        print(f"{RED}[ERROR]{RESET} FFmpeg execution verification failed: {e}")
        return False

    return True


if __name__ == "__main__":
    force_install = "--force" in sys.argv
    success = setup_ffmpeg(force=force_install)
    sys.exit(0 if success else 1)
