import os
import re
import sys
import ctypes
import requests
from ctypes import wintypes
from pathlib import Path
import xml.etree.ElementTree as ET

UPDATE_FEED = "https://notepad-plus-plus.org/update/getDownloadUrl.php?version=8&param={arch}"

# --------------------------
# Helpers
# --------------------------

def parse_version(s: str):
    """Turn '8.7.6' or '8.7' into a tuple of ints for comparison."""
    nums = re.findall(r"\d+", s)
    return tuple(int(n) for n in nums)

def normalize_version_tuple(t, length=4):
    """Pad or trim version tuple to a fixed length for safe comparison."""
    t = tuple(t[:length]) + (0,)*(length - len(t))
    return t

def compare_versions(a: str, b: str) -> int:
    """Return -1 if a<b, 0 if equal, +1 if a>b."""
    ta = normalize_version_tuple(parse_version(a))
    tb = normalize_version_tuple(parse_version(b))
    return (ta > tb) - (ta < tb)

def find_notepadpp_exe() -> Path | None:
    """Try common install locations for Notepad++."""
    candidates = [
        Path(r"C:\Program Files\Notepad++\notepad++.exe"),
        Path(r"C:\Program Files (x86)\Notepad++\notepad++.exe"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

def get_file_version_windows(path: Path) -> str | None:
    """Read Windows file ProductVersion/FileVersion via WinAPI."""
    # WinAPI calls
    GetFileVersionInfoSizeW = ctypes.windll.version.GetFileVersionInfoSizeW
    GetFileVersionInfoW = ctypes.windll.version.GetFileVersionInfoW
    VerQueryValueW = ctypes.windll.version.VerQueryValueW

    GetFileVersionInfoSizeW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.DWORD)]
    GetFileVersionInfoSizeW.restype = wintypes.DWORD
    GetFileVersionInfoW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID]
    GetFileVersionInfoW.restype = wintypes.BOOL
    VerQueryValueW.argtypes = [wintypes.LPCVOID, wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(wintypes.UINT)]
    VerQueryValueW.restype = wintypes.BOOL

    dummy = wintypes.DWORD(0)
    size = GetFileVersionInfoSizeW(str(path), ctypes.byref(dummy))
    if size == 0:
        return None

    data = ctypes.create_string_buffer(size)
    ok = GetFileVersionInfoW(str(path), 0, size, data)
    if not ok:
        return None

    # Query the \StringFileInfo\#######\ProductVersion or FileVersion
    # First get the translation table to build the correct sub-block
    lptr = ctypes.c_void_p()
    ulen = wintypes.UINT(0)
    if not VerQueryValueW(data, r"\\VarFileInfo\\Translation", ctypes.byref(lptr), ctypes.byref(ulen)):
        return None
    # translation is array of LANGANDCODEPAGE structures (2 WORDs)
    # We’ll just use the first one
    lang, codepage = ctypes.c_ushort.from_address(lptr.value).value, ctypes.c_ushort.from_address(lptr.value + 2).value

    def query_string(name: str) -> str | None:
        sub_block = f"\\StringFileInfo\\{lang:04x}{codepage:04x}\\{name}"
        ptr = ctypes.c_void_p()
        length = wintypes.UINT(0)
        if VerQueryValueW(data, sub_block, ctypes.byref(ptr), ctypes.byref(length)):
            # ptr is LPWSTR
            return ctypes.wstring_at(ptr, length.value - 1)  # drop trailing null
        return None

    ver = query_string("ProductVersion") or query_string("FileVersion")
    if not ver:
        return None
    # ProductVersion might include extra text; keep only digits and dots
    m = re.search(r"\d+(?:\.\d+){0,3}", ver)
    return m.group(0) if m else ver

def get_latest_notepadpp_version_and_url(arch: str = "x64") -> tuple[str, str]:
    """Use the official update feed to get latest version + download URL."""
    url = UPDATE_FEED.format(arch=arch)
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    version = root.findtext("Version")
    location = root.findtext("Location")
    if not version or not location:
        raise RuntimeError("Failed to parse update feed: missing Version/Location")
    return version.strip(), location.strip()

def detect_arch_from_install_path(path: Path | None) -> str:
    """Pick x64 if 64-bit Program Files path is used, else x86; default x64."""
    if path and "Program Files (x86)" in str(path):
        return "x86"
    return "x64"

def download(url: str, out_path: Path):
    with requests.get(url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)

# --------------------------
# Main flow Function
# --------------------------


def get_notepadpp_version_info():
    exe = find_notepadpp_exe()
    installed_version = get_file_version_windows(exe) if exe else None
    arch = detect_arch_from_install_path(exe)
    latest_version, latest_url = get_latest_notepadpp_version_and_url(arch=arch)
    needs_download = (installed_version is None) or (compare_versions(installed_version, latest_version) != 0)
    return {
        "arch": arch,
        "installed_version": installed_version,
        "latest_version": latest_version,
        "latest_url": latest_url,
        "needs_download": needs_download,
        "exe_path": str(exe) if exe else None
    }


