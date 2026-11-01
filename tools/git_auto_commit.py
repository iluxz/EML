"""
Auto-commit script for Haydee Maps git repo.
Commits changes every 5 minutes.
Run with: python git_auto_commit.py
"""
import os
import subprocess
import time
from datetime import datetime

MAPS_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Haydee\Maps"
INTERVAL = 300  # seconds (5 minutes)


def run_git(args):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=MAPS_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def commit_changes():
    code, out, err = run_git(["status", "--porcelain"])
    if code != 0:
        print(f"[GIT] status failed: {err}")
        return

    if not out.strip():
        print(f"[GIT] {datetime.now().strftime('%H:%M:%S')} no changes")
        return

    run_git(["add", "-A"])
    msg = f"auto-commit {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    code, out, err = run_git(["commit", "-m", msg])
    if code == 0:
        print(f"[GIT] committed: {msg}")
    else:
        print(f"[GIT] commit failed: {err}")


def main():
    print(f"[GIT] Auto-commit running on {MAPS_DIR}")
    print(f"[GIT] Committing every {INTERVAL} seconds. Ctrl+C to stop.\n")

    # Initial commit
    commit_changes()

    try:
        while True:
            time.sleep(INTERVAL)
            commit_changes()
    except KeyboardInterrupt:
        print("\n[GIT] Stopped.")


if __name__ == "__main__":
    main()
