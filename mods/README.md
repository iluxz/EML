# EML Mods

Place mod DLLs here. The EML launcher will inject all `.dll` files in this folder into edith.exe.

## Included Mods

### EML_core.dll
- **90-degree rotation snap** — snaps rotations to 90° increments (CSGs + meshes)
- **Auto-backup hook** — creates `.bak` copies before file writes
- **Crash protection** — prevents file corruption on crash

## Creating Your Own Mod

1. Write a C/C++ DLL that hooks functions in edith.exe or haydee.dll
2. Use the injector: `injector.exe edith.exe your_mod.dll`
3. Place the DLL in this folder for auto-loading

See `modloader/payload.c` for an example of how hooks work.
