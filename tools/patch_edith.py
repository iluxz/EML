#!/usr/bin/env python3
"""Patch edith.exe for 90-degree rotation snap.

Patches:
1. Rotation step: 15.0 -> 90.0
2. Always snap: je -> jmp (3 instances)

Usage: python patch_edith.py [edith_path]
"""

import struct, os, sys, shutil

def find_edith():
    paths = [
        r"C:\Program Files (x86)\Steam\steamapps\common\Haydee\edith.exe",
        r"C:\Program Files\Steam\steamapps\common\Haydee\edith.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def main():
    edith_path = sys.argv[1] if len(sys.argv) > 1 else find_edith()
    if not edith_path or not os.path.exists(edith_path):
        print("ERROR: edith.exe not found")
        sys.exit(1)

    print(f"Patching: {edith_path}")

    # Backup
    backup = edith_path + ".pre_patch"
    if not os.path.exists(backup):
        shutil.copy2(edith_path, backup)
        print(f"  Backup: {backup}")

    data = bytearray(open(edith_path, "rb").read())

    # Patch 1: 15.0 -> 90.0
    old_val = struct.pack("<f", 15.0)
    new_val = struct.pack("<f", 90.0)
    pos = data.find(old_val)
    if pos < 0:
        print("  WARNING: 15.0 constant not found (already patched?)")
    else:
        data[pos:pos+4] = new_val
        print(f"  Patched 15.0 -> 90.0 at offset 0x{pos:08X}")

    # Patch 2: je -> jmp (3 instances of cmp [ebp+0x14], 0 ; je)
    pattern = b'\x83\x7D\x14\x00\x74'
    pos = 0
    count = 0
    while True:
        idx = data.find(pattern, pos)
        if idx < 0:
            break
        data[idx+4] = 0xEB  # je (0x74) -> jmp (0xEB)
        count += 1
        pos = idx + 5
    print(f"  Patched {count} snap conditions (je -> jmp)")

    with open(edith_path, "wb") as f:
        f.write(data)
    print("Done. Restart Edith to apply.")

if __name__ == "__main__":
    main()
