"""Saving files the user can see (backups, PDFs).

On Android, Flet 0.28's save dialog hands back a virtual path Python cannot write to (the file ends up 0 bytes),
so files are written straight into the public Download/Masarif folder instead (needs the "all files access"
permission, switched on once by the user). Every write is verified by size so an empty file is never reported as saved.
"""
import os

FOLDER = "Masarif"
ANDROID_ROOTS = ["/storage/emulated/0/Download", "/sdcard/Download"]


def is_android() -> bool:
    return "ANDROID_ROOT" in os.environ or "ANDROID_DATA" in os.environ


def write_verified(path: str, data: bytes) -> str:
    """Write `data` to `path` and make sure all bytes arrived. Returns the path or raises OSError."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    if os.path.getsize(path) != len(data):
        raise OSError("الملف انكتب ناقص")
    return path


def public_dir_candidates() -> list:
    return [os.path.join(root, FOLDER) for root in ANDROID_ROOTS]


def save_public(name: str, data: bytes, roots=None):
    """Save into Download/Masarif. Returns (path, None) or (None, error text)."""
    err = "ما في صلاحية للكتابة بمجلد التنزيلات"
    for folder in (roots if roots is not None else public_dir_candidates()):
        try:
            return write_verified(os.path.join(folder, name), data), None
        except OSError as e:
            err = f"{type(e).__name__}: {e}"
    return None, err


def mirror_backup(path: str, roots=None, keep: int = 5):
    """Best-effort copy of a backup file into Download/Masarif/auto (kept after uninstall). Silent on failure."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    for folder in (roots if roots is not None else public_dir_candidates()):
        target = os.path.join(folder, "auto")
        try:
            out = write_verified(os.path.join(target, os.path.basename(path)), data)
            old = sorted((os.path.join(target, n) for n in os.listdir(target) if n.endswith(".json")), key=os.path.getmtime)
            for p in old[:-keep]:
                os.remove(p)
            return out
        except OSError:
            continue
    return None
