import os, time, subprocess, glob, shutil, json
from datetime import datetime

EDITH = r"C:\Program Files (x86)\Steam\steamapps\common\Haydee\edith.exe"
BACKUP_DIR = r"D:\Backup 8 17 2026\EdithAutoBackup"
MAPS_ROOT = r"C:\Program Files (x86)\Steam\steamapps\common\Haydee\Maps"
STATE_FILE = os.path.join(BACKUP_DIR, "recovery_state.json")

def parse_ok(path):
    """Quick check if .edith file is valid (ends with proper brace, non-zero size)"""
    try:
        size = os.path.getsize(path)
        if size < 100:
            return False
        with open(path, "rb") as f:
            f.seek(-100, 2)
            tail = f.read()
        # Check for closing brace
        text = tail.decode("utf-16-le", errors="replace")
        return "}" in text
    except:
        return False

def latest_backup_for(rel_path):
    safe = rel_path.replace("\\", "_").replace("/", "_")
    pattern = os.path.join(BACKUP_DIR, safe + ".*.bak")
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    return files[0] if files else None

def edith_running():
    try:
        out = subprocess.check_output("tasklist /FI \"IMAGENAME eq edith.exe\" /NH", shell=True, text=True)
        return "edith.exe" in out
    except:
        return False

def scan_and_recover():
    corrupted = []
    for root, dirs, files in os.walk(MAPS_ROOT):
        for f in files:
            if not f.endswith(".edith"):
                continue
            path = os.path.join(root, f)
            if not parse_ok(path):
                corrupted.append(path)
    if not corrupted:
        return
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Found {len(corrupted)} corrupted .edith files!")
    for path in corrupted:
        rel = os.path.relpath(path, MAPS_ROOT)
        backup = latest_backup_for(rel)
        if backup:
            print(f"  RESTORING: {rel}")
            print(f"    from: {backup}")
            try:
                shutil.copy2(backup, path)
                print(f"    OK")
            except Exception as e:
                print(f"    FAILED: {e}")
        else:
            print(f"  NO BACKUP: {rel}")
    print("Recovery complete.\n")

print("Crash recovery watcher started.")
print("Monitors edith.exe. When it exits (crash), scans for corrupted .edith files and restores from backup.")
print("Press Ctrl+C to stop.\n")

was_running = edith_running()
while True:
    running = edith_running()
    if was_running and not running:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Edith exited. Scanning for corruption...")
        time.sleep(2)  # wait for file handles to release
        scan_and_recover()
    was_running = running
    time.sleep(3)
