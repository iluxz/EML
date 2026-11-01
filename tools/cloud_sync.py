"""
Cloud sync: copies new .bak files to OneDrive backup folder.
Run periodically or alongside other watchers.
"""
import os
import shutil
import time
from datetime import datetime

BACKUP_DIR = r"D:\Backup 8 17 2026\EdithAutoBackup"
CLOUD_DIR = r"C:\Users\Can\OneDrive\EML_Backups"
INTERVAL = 300  # 5 minutes


def sync():
    os.makedirs(CLOUD_DIR, exist_ok=True)
    copied = 0
    for f in os.listdir(BACKUP_DIR):
        if not f.endswith(".bak"):
            continue
        src = os.path.join(BACKUP_DIR, f)
        dst = os.path.join(CLOUD_DIR, f)
        if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
            try:
                shutil.copy2(src, dst)
                copied += 1
            except Exception as e:
                print(f"[CLOUD] failed to copy {f}: {e}")
    if copied:
        print(f"[CLOUD] {datetime.now().strftime('%H:%M:%S')} synced {copied} new files")


def main():
    print(f"[CLOUD] Syncing backups to {CLOUD_DIR}")
    print(f"[CLOUD] Every {INTERVAL} seconds. Ctrl+C to stop.\n")
    try:
        while True:
            sync()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n[CLOUD] Stopped.")


if __name__ == "__main__":
    main()
