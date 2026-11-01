import os, shutil, glob, sys

# Embedded safety scripts
AUTO_BACKUP_PY = '''import os, shutil, time, glob, json

WATCH_DIRS = []
BACKUP_DIR = r"D:\\Backup 8 17 2026\\EdithAutoBackup"
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
    try:
        size = os.path.getsize(path)
        if size < 100:
            return False
        with open(path, "rb") as f:
            f.seek(-200, 2)
            tail = f.read()
        text = tail.decode("utf-16-le", errors="replace")
        if "}" not in text:
            return False
        if size < 1000:
            return False
        return True
    except:
        return False

def backup_file(path):
    rel = os.path.relpath(path, os.path.join(os.path.dirname(path).split("Maps")[0], "Maps"))
    safe = rel.replace("\\\\", "_").replace("/", "_")
    stamp = time.strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"{safe}.{stamp}.bak")
    try:
        shutil.copy2(path, dest)
        print(f"[BACKUP] {path} -> {dest}")
        pattern = os.path.join(BACKUP_DIR, safe + ".*.bak")
        versions = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        for v in versions[MAX_VERSIONS:]:
            os.remove(v)
    except Exception as e:
        print(f"[ERR] {e}")

def save_state():
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(states, f)
    except:
        pass

maps_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Maps")
WATCH_DIRS = [os.path.join(maps_dir, "NetWare")] if os.path.exists(os.path.join(maps_dir, "NetWare")) else [maps_dir]

print("Auto-backup daemon started. Watching .edith files...")
print(f"Backup dir: {BACKUP_DIR}")
print("Press Ctrl+C to stop.\\n")

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
                    time.sleep(2)
                    try:
                        st2 = os.stat(path)
                    except FileNotFoundError:
                        continue
                    if st2.st_mtime != mtime or st2.st_size != size:
                        continue
                    if file_is_valid(path):
                        states[key] = [mtime, size]
                        backup_file(path)
                        save_state()
                    else:
                        print(f"[SKIP] {path} appears incomplete")
    time.sleep(3)
'''

CRASH_RECOVERY_PY = '''import os, time, subprocess, glob, shutil
from datetime import datetime

BACKUP_DIR = r"D:\\Backup 8 17 2026\\EdithAutoBackup"
MAPS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Maps")

def parse_ok(path):
    try:
        size = os.path.getsize(path)
        if size < 100:
            return False
        with open(path, "rb") as f:
            f.seek(-100, 2)
            tail = f.read()
        text = tail.decode("utf-16-le", errors="replace")
        return "}" in text
    except:
        return False

def latest_backup_for(rel_path):
    safe = rel_path.replace("\\\\", "_").replace("/", "_")
    pattern = os.path.join(BACKUP_DIR, safe + ".*.bak")
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    return files[0] if files else None

def edith_running():
    try:
        out = subprocess.check_output("tasklist /FI \\"IMAGENAME eq edith.exe\\" /NH", shell=True, text=True)
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
    print(f"\\n[{datetime.now().strftime('%H:%M:%S')}] Found {len(corrupted)} corrupted .edith files!")
    for path in corrupted:
        rel = os.path.relpath(path, MAPS_ROOT)
        backup = latest_backup_for(rel)
        if backup:
            print(f"  RESTORING: {rel}")
            try:
                shutil.copy2(backup, path)
                print(f"    OK")
            except Exception as e:
                print(f"    FAILED: {e}")
        else:
            print(f"  NO BACKUP: {rel}")
    print("Recovery complete.\\n")

print("Crash recovery watcher started.")
print("Monitors edith.exe. When it exits (crash), scans for corrupted .edith files.")
print("Press Ctrl+C to stop.\\n")

was_running = edith_running()
while True:
    running = edith_running()
    if was_running and not running:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Edith exited. Scanning...")
        time.sleep(2)
        scan_and_recover()
    was_running = running
    time.sleep(3)
'''

CAMERA_CONTROL_PY = '''import ctypes
import time
import sys

user32 = ctypes.windll.user32

VK_W = 0x57
VK_A = 0x41
VK_S = 0x53
VK_D = 0x44
VK_RBUTTON = 0x02

MOUSEEVENTF_WHEEL = 0x0800
WHEEL_DELTA = 120

def is_key_pressed(vk):
    return (user32.GetAsyncKeyState(vk) & 0x8000) != 0

def is_rmb_held():
    return (user32.GetAsyncKeyState(VK_RBUTTON) & 0x8000) != 0

def scroll(delta):
    user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)

def get_foreground_title():
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value

print("EML Camera Control Daemon")
print("Translates right-click + WASD into scroll wheel for Edith.")
print("Hold right-click and press W/S to move camera.")
print("Press Ctrl+C to stop.\\n")

was_w = False
was_s = False

try:
    while True:
        title = get_foreground_title()
        edith_active = "Edith" in title or "edith" in title.lower()
        
        if edith_active:
            rmb = is_rmb_held()
            w = is_key_pressed(VK_W)
            s = is_key_pressed(VK_S)
            
            if rmb:
                if w and not was_w:
                    scroll(WHEEL_DELTA)
                    was_w = True
                elif not w:
                    was_w = False
                
                if s and not was_s:
                    scroll(-WHEEL_DELTA)
                    was_s = True
                elif not s:
                    was_s = False
            else:
                was_w = False
                was_s = False
        
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\\nStopped.")
'''

print("=" * 50)
print("  EML - Edith Mod Loader")
print("  for Haydee")
print("=" * 50)
print()
print("Welcome! This installer will set up EML in your Haydee folder.")
print()

haydee_paths = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Haydee",
    r"C:\Program Files\Steam\steamapps\common\Haydee",
    r"D:\Steam\steamapps\common\Haydee",
    r"D:\SteamLibrary\steamapps\common\Haydee",
]

haydee_dir = None
for p in haydee_paths:
    if os.path.exists(os.path.join(p, "edith.exe")):
        haydee_dir = p
        break

if not haydee_dir:
    print("Could not find Haydee automatically.")
    haydee_dir = input("Enter Haydee install path: ").strip().strip('"')

if not os.path.exists(os.path.join(haydee_dir, "edith.exe")):
    print("ERROR: edith.exe not found in that folder.")
    sys.exit(1)

print(f"Found Haydee at: {haydee_dir}")
print()

resp = input("Install EML here? (y/n): ").strip().lower()
if resp != "y":
    print("Cancelled.")
    sys.exit(0)

print()
print("Installing...")

mods_dir = os.path.join(haydee_dir, "Mods")
os.makedirs(mods_dir, exist_ok=True)
print(f"  [+] Created {mods_dir}")

src_dir = os.path.dirname(os.path.abspath(__file__))
injector_src = os.path.join(src_dir, "modloader", "injector.exe")
injector_dst = os.path.join(mods_dir, "injector.exe")
if os.path.exists(injector_src):
    shutil.copy2(injector_src, injector_dst)
    print(f"  [+] Copied injector.exe")

payload_src = os.path.join(src_dir, "modloader", "payload.dll")
if not os.path.exists(payload_src):
    payload_candidates = glob.glob(os.path.join(src_dir, "modloader", "payload*.dll"))
    if payload_candidates:
        payload_src = payload_candidates[-1]
if os.path.exists(payload_src):
    payload_dst = os.path.join(mods_dir, "EML_core.dll")
    shutil.copy2(payload_src, payload_dst)
    print(f"  [+] Copied EML_core.dll")

ab_path = os.path.join(haydee_dir, "auto_backup.py")
with open(ab_path, "w") as f:
    f.write(AUTO_BACKUP_PY)
print(f"  [+] Wrote auto_backup.py")

cr_path = os.path.join(haydee_dir, "crash_recovery.py")
with open(cr_path, "w") as f:
    f.write(CRASH_RECOVERY_PY)
print(f"  [+] Wrote crash_recovery.py")

cc_path = os.path.join(haydee_dir, "camera_control.py")
with open(cc_path, "w") as f:
    f.write(CAMERA_CONTROL_PY)
print(f"  [+] Wrote camera_control.py")

bat_content = '@echo off\necho Starting Edith with EML...\nstart "" "' + os.path.join(haydee_dir, "edith.exe") + '"\ntimeout /t 3 /nobreak >nul\n"' + os.path.join(mods_dir, "injector.exe") + '" edith.exe "' + os.path.join(mods_dir, "EML_core.dll") + '"\necho EML loaded.\npause\n'
bat_path = os.path.join(haydee_dir, "launch_edith_modded.bat")
with open(bat_path, "w") as f:
    f.write(bat_content)
print(f"  [+] Created launch_edith_modded.bat")

print()
print("=" * 50)
print("  Setup complete!")
print("=" * 50)
print()
print("  To use EML:")
print("  1. Run launch_edith_modded.bat in your Haydee folder")
print("  2. Or run injector.exe manually after starting edith")
print()
print("  Place additional mod DLLs in:")
print(f"  {mods_dir}")
print()
print("  Safety scripts (auto_backup, crash_recovery, camera_control) are in:")
print(f"  {haydee_dir}")
print()
try:
    input("Press Enter to exit...")
except EOFError:
    pass
