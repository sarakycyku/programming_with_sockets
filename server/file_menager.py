"""
File system operations for admin clients.

Every function is sandboxed to SERVER_FILES_DIR -- path-traversal attempts
(e.g. "../etc/passwd") are rejected by _safe_path() before any I/O occurs.
File content is base64-encoded on the wire so binary files transfer safely.
"""
import base64
import os
import time
from pathlib import Path
from typing import Tuple

from server.config import SERVER_FILES_DIR


# -- Path safety ---------------------------------------------------------------

def _safe_path(filename: str) -> Tuple[bool, str]:
    """
    Resolve *filename* relative to SERVER_FILES_DIR and confirm it stays inside.
    Returns (True, absolute_path) or (False, "") on traversal attempt.
    """
    base   = Path(SERVER_FILES_DIR).resolve()
    target = (base / filename).resolve()
    try:
        target.relative_to(base)   # raises ValueError if outside base
    except ValueError:
        return False, ""
    return True, str(target)


def _ensure_dir() -> None:
    os.makedirs(SERVER_FILES_DIR, exist_ok=True)


# -- Public API ----------------------------------------------------------------

def list_files() -> dict:
    _ensure_dir()
    files = [
        name
        for name in os.listdir(SERVER_FILES_DIR)
        if os.path.isfile(os.path.join(SERVER_FILES_DIR, name))
    ]
    return {"files": sorted(files), "count": len(files)}


def read_file(filename: str) -> dict:
    ok, path = _safe_path(filename)
    if not ok:
        return {"error": "Path traversal attempt blocked"}
    if not os.path.isfile(path):
        return {"error": f"File not found: {filename}"}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return {"filename": filename, "content": fh.read()}
    except OSError as exc:
        return {"error": str(exc)}


def write_file(filename: str, content_b64: str) -> dict:
    """Upload: client supplies base64-encoded file content."""
    ok, path = _safe_path(filename)
    if not ok:
        return {"error": "Path traversal attempt blocked"}
    _ensure_dir()
    try:
        data = base64.b64decode(content_b64)
    except Exception:
        return {"error": "Invalid base64 content"}
    try:
        with open(path, "wb") as fh:
            fh.write(data)
        return {"message": f"Uploaded '{filename}' ({len(data):,} bytes)"}
    except OSError as exc:
        return {"error": str(exc)}


def download_file(filename: str) -> dict:
    """Download: server returns base64-encoded file content."""
    ok, path = _safe_path(filename)
    if not ok:
        return {"error": "Path traversal attempt blocked"}
    if not os.path.isfile(path):
        return {"error": f"File not found: {filename}"}
    try:
        with open(path, "rb") as fh:
            content_b64 = base64.b64encode(fh.read()).decode("ascii")
        return {"filename": filename, "content_b64": content_b64}
    except OSError as exc:
        return {"error": str(exc)}


def delete_file(filename: str) -> dict:
    ok, path = _safe_path(filename)
    if not ok:
        return {"error": "Path traversal attempt blocked"}
    if not os.path.isfile(path):
        return {"error": f"File not found: {filename}"}
    try:
        os.remove(path)
        return {"message": f"Deleted '{filename}'"}
    except OSError as exc:
        return {"error": str(exc)}


def search_files(keyword: str) -> dict:
    """Case-insensitive keyword search across all text files."""
    _ensure_dir()
    kw = keyword.lower()
    matches = []
    for name in os.listdir(SERVER_FILES_DIR):
        path = os.path.join(SERVER_FILES_DIR, name)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                if kw in fh.read().lower():
                    matches.append(name)
        except OSError:
            pass
    return {"keyword": keyword, "matches": sorted(matches), "count": len(matches)}


def file_info(filename: str) -> dict:
    ok, path = _safe_path(filename)
    if not ok:
        return {"error": "Path traversal attempt blocked"}
    if not os.path.isfile(path):
        return {"error": f"File not found: {filename}"}
    st = os.stat(path)
    return {
        "filename": filename,
        "size_bytes": st.st_size,
        "created":  time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(st.st_ctime)),
        "modified": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(st.st_mtime)),
    }
