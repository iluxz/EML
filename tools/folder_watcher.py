"""
Real-time folder watcher for Haydee .edith files.
Backs up any create/modify/rename/delete-restore event, including Explorer copy-paste overwrites.
Uses Windows ReadDirectoryChangesW (no extra deps).
Run with: python folder_watcher.py
"""
import os
import sys
import time
import shutil
import ctypes
from ctypes import wintypes
from datetime import datetime

# CONFIG
WATCH_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Haydee\Maps"
BACKUP_DIR = r"D:\Backup 8 17 2026\EdithAutoBackup"
FILE_FILTERS = [".edith", ".scene"]
KEEP_VERSIONS = 20  # keep last N backups per file

# Windows constants
FILE_LIST_DIRECTORY = 0x0001
FILE_SHARE_READ = 0x0001
FILE_SHARE_WRITE = 0x0002
FILE_SHARE_DELETE = 0x0004
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000

FILE_ACTION_ADDED = 1
FILE_ACTION_REMOVED = 2
FILE_ACTION_MODIFIED = 3
FILE_ACTION_RENAMED_OLD_NAME = 4
FILE_ACTION_RENAMED_NEW_NAME = 5

FILE_NOTIFY_CHANGE_FILE_NAME = 0x00000001
FILE_NOTIFY_CHANGE_DIR_NAME = 0x00000002
FILE_NOTIFY_CHANGE_ATTRIBUTES = 0x00000004
FILE_NOTIFY_CHANGE_SIZE = 0x00000008
FILE_NOTIFY_CHANGE_LAST_WRITE = 0x00000010
FILE_NOTIFY_CHANGE_LAST_ACCESS = 0x00000020
FILE_NOTIFY_CHANGE_CREATION = 0x00000040
FILE_NOTIFY_CHANGE_SECURITY = 0x00000100

ERROR_ACCESS_DENIED = 5


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def safe_name(path):
    """Convert a map path to a backup-safe base name."""
    rel = os.path.relpath(path, WATCH_DIR)
    return rel.replace(os.sep, "_").replace(" ", "_")


def backup_file(src_path):
    if not any(src_path.lower().endswith(ext) for ext in FILE_FILTERS):
        return
    if not os.path.isfile(src_path):
        return

    ensure_dir(BACKUP_DIR)
    base = safe_name(src_path)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"{base}.{stamp}.bak")

    try:
        shutil.copy2(src_path, dest)
        print(f"[BACKUP] {src_path} -> {dest}")
    except Exception as e:
        print(f"[ERROR] backup failed for {src_path}: {e}")
        return

    # prune old versions
    pattern = os.path.join(BACKUP_DIR, f"{base}.*.bak")
    try:
        versions = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.startswith(base + ".") and f.endswith(".bak")],
            key=lambda f: os.path.getmtime(os.path.join(BACKUP_DIR, f))
        )
        while len(versions) > KEEP_VERSIONS:
            old = versions.pop(0)
            try:
                os.remove(os.path.join(BACKUP_DIR, old))
                print(f"[PRUNE] {old}")
            except Exception as e:
                print(f"[ERROR] prune failed: {e}")
    except Exception as e:
        print(f"[ERROR] version pruning failed: {e}")


def watch_directory(path):
    ensure_dir(BACKUP_DIR)
    print(f"[WATCH] Monitoring {path}")
    print(f"[WATCH] Backups go to {BACKUP_DIR}")
    print("[WATCH] Press Ctrl+C to stop\n")

    kernel32 = ctypes.windll.kernel32

    while True:
        hDir = kernel32.CreateFileW(
            path,
            FILE_LIST_DIRECTORY,
            FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
            None,
            OPEN_EXISTING,
            FILE_FLAG_BACKUP_SEMANTICS,
            None
        )

        if hDir == wintypes.HANDLE(-1).value:
            err = kernel32.GetLastError()
            print(f"[ERROR] CreateFileW failed: {err}")
            time.sleep(5)
            continue

        try:
            buf_size = 8192
            buf = ctypes.create_string_buffer(buf_size)
            bytes_returned = wintypes.DWORD()

            while True:
                ok = kernel32.ReadDirectoryChangesW(
                    hDir,
                    buf,
                    buf_size,
                    True,  # recursive
                    FILE_NOTIFY_CHANGE_FILE_NAME |
                    FILE_NOTIFY_CHANGE_SIZE |
                    FILE_NOTIFY_CHANGE_LAST_WRITE,
                    ctypes.byref(bytes_returned),
                    None,
                    None
                )
                if not ok:
                    err = kernel32.GetLastError()
                    print(f"[ERROR] ReadDirectoryChangesW failed: {err}")
                    break

                offset = 0
                while offset < bytes_returned.value:
                    fnext = ctypes.cast(
                        ctypes.addressof(buf) + offset,
                        ctypes.POINTER(wintypes.DWORD)
                    ).contents.value

                    faction = ctypes.cast(
                        ctypes.addressof(buf) + offset + 4,
                        ctypes.POINTER(wintypes.DWORD)
                    ).contents.value

                    flen = ctypes.cast(
                        ctypes.addressof(buf) + offset + 8,
                        ctypes.POINTER(wintypes.DWORD)
                    ).contents.value

                    fname = ctypes.cast(
                        ctypes.addressof(buf) + offset + 12,
                        ctypes.c_wchar_p
                    ).value

                    full_path = os.path.join(path, fname)

                    if fname and any(fname.lower().endswith(ext) for ext in FILE_FILTERS):
                        if faction in (FILE_ACTION_ADDED, FILE_ACTION_MODIFIED, FILE_ACTION_RENAMED_NEW_NAME):
                            # Small delay to let the write finish
                            time.sleep(0.1)
                            backup_file(full_path)
                        elif faction == FILE_ACTION_REMOVED:
                            print(f"[REMOVED] {full_path}")

                    if fnext == 0:
                        break
                    offset += fnext
        finally:
            kernel32.CloseHandle(hDir)


def main():
    if not os.path.isdir(WATCH_DIR):
        print(f"[ERROR] Watch directory does not exist: {WATCH_DIR}")
        sys.exit(1)

    # Do an initial backup of all current .edith files
    print("[INIT] Taking baseline backups...")
    for root, dirs, files in os.walk(WATCH_DIR):
        for f in files:
            if any(f.lower().endswith(ext) for ext in FILE_FILTERS):
                backup_file(os.path.join(root, f))
    print("[INIT] Baseline done\n")

    try:
        watch_directory(WATCH_DIR)
    except KeyboardInterrupt:
        print("\n[WATCH] Stopped.")


if __name__ == "__main__":
    main()
