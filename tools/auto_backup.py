import os, shutil, time, glob, json

WATCH_DIRS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Haydee\Maps\NetWare",
]
BACKUP_DIR = r"D:\Backup 8 17 2026\EdithAutoBackup"
MAX_VERSIONS = 50
STATE_FILE = os.path.join(BACKUP_DIR, "state.json")

os.makedirs(BACKUP_DIR, exist_ok=True)

states = {}
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r") as f:
            states = json.load(f)
    except:
        states = {}

def file_is_valid(path):
    """Check if .edith file is complete (not mid-write/corrupt)"""
    try:
        size = os.path.getsize(path)
        if size < 100:
            return False
        with open(path, "rb") as f:
            f.seek(-200, 2)
            tail = f.read()
        text = tail.decode("utf-16-le", errors="replace")
        # Must end with closing brace
        if "}" not in text:
            return False
        # Must not have truncated content
        if size < 1000:
            return False
        return True
    except:
        return False

def backup_file(path):
    rel = os.path.relpath(path, "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Haydee\\Maps")
    safe = rel.replace("\\", "_").replace("/", "_")
    stamp = time.strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"{safe}.{stamp}.bak")
    try:
        shutil.copy2(path, dest)
        print(f"[BACKUP] {path} -> {dest}")
        pattern = os.path.join(BACKUP_DIR, safe + ".*.bak")
        versions = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        for v in versions[MAX_VERSIONS:]:
            os.remove(v)
            print(f"[PRUNE] {v}")
    except Exception as e:
        print(f"[ERR] {e}")

def save_state():
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(states, f)
    except:
        pass

print("Auto-backup daemon started (validates files before backup).")
print(f"Backup dir: {BACKUP_DIR}")
print("Press Ctrl+C to stop.\n")

while True:
    for d in WATCH_DIRS:
        for root, dirs, files in os.walk(d):
            for f in files:
                if not f.endswith(".edith"):
                    continue
                path = os.path.join(root, f)
                try:
                    st = os.stat(path)
                except FileNotFoundError:
                    continue
                key = path
                mtime = st.st_mtime
                size = st.st_size
                prev = states.get(key)
                if prev is None or prev != [mtime, size]:
                    # File changed - wait 2 seconds and check again (debounce)
                    time.sleep(2)
                    try:
                        st2 = os.stat(path)
                    except FileNotFoundError:
                        continue
                    if st2.st_mtime != mtime or st2.st_size != size:
                        # Still changing, skip this cycle
                        continue
                    # Stable - validate before backup
                    if file_is_valid(path):
                        states[key] = [mtime, size]
                        backup_file(path)
                        save_state()
                    else:
                        print(f"[SKIP] {path} appears incomplete/corrupt, not backing up")
    time.sleep(3)
