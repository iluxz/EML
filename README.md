# EML - Edith Mod Loader

Mod loader and tools for **Haydee** (the game), built by reverse engineering `edith.exe` and `haydee.dll`.

## Features

- **DLL injection** — injects mod DLLs into edith.exe at runtime
- **Auto-backup hook** — backs up files before saving (prevents crash corruption)
- **90-degree rotation snap** — patches rotation to snap to 90° increments
- **Crash recovery** — auto-restores corrupted .edith files after a crash
- **Custom packer** — create .pack files from folder structures
- **Audio converter** — convert .ogg/.mp3 to Haydee .sound format
- **Haydee format reference** — documented file formats (.edith, .mesh, .pack, .sound, .scene, .game, etc.)

## Installation

```bash
python eml_installer.py
```

The installer will:
1. Find your Haydee install
2. Create a `Mods\` folder
3. Copy injector + EML_core.dll
4. Write safety scripts (auto_backup, crash_recovery)
5. Create a launcher bat

## Usage

1. Run `launch_edith_modded.bat` in your Haydee folder
2. Or manually: start edith.exe, then run `injector.exe edith.exe <mod.dll>`

Place additional mod DLLs in `Haydee\Mods\`.

## Tools

| Tool | Description |
|------|-------------|
| `eml_installer.py` | One-click installer |
| `injector.exe` | DLL injector for edith.exe |
| `auto_backup.py` | Watches .edith files, backs up on change |
| `crash_recovery.py` | Auto-restores corrupted files after crash |
| `packer.py` | Creates .pack files from folders |
| `convert_all.py` | Batch converts audio to Haydee format |

## Documentation

- [Haydee Format Reference](docs/HAYDEE_REFERENCE.md) — file formats, engine quirks, RE findings
- [Mod Plan](docs/EDITH_MOD_PLAN.md) — roadmap and feature tiers

## Disclaimer

This project reverse-engineers Haydee's engine for modding purposes. All decompiled code and extracted assets are kept private. Only original code and documentation are published.

Haydee is developed by Haydee Interactive. This is an unofficial modding tool.
