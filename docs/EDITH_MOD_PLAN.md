# EDITH MOD PLAN

## Goal
Reverse-engineer and modify `edith.exe` to add stability, QoL, and editor features.

## Target
- `C:\Program Files (x86)\Steam\steamapps\common\Haydee\edith.exe` (x86 PE, 2018)
- Dependencies: `haydee.dll`, `game.dll`

## Tier 1 (immediate)
1. Auto-backup before every save
2. Crash protection / auto-recovery
3. 90-degree rotation snap
4. Right-click + WASD camera (ditch scroll wheel)

## Tier 2 (hard but possible)
5. Better director graph (groups, comments)
6. Decal clipping fix
7. Auto-compound for meshes

## Tier 3 (long-term)
8. Multiplayer collaborative editing
9. Plugin system

## RE Strategy
1. Find save/load functions in edith.exe / haydee.dll
2. Find UI/input handling (rotation, camera, WASD)
3. Hook/patch these functions
4. Test in isolated copy

## Tools
- Ghidra (headless mode available)
- strings, hex dumps
- Existing .edith parser/baker code

## Future: EML for Haydee 2 & 3
- Port injector + hook framework to Haydee 2/3 binaries
- Adapt to different engine versions (Haydee 2 is a different engine)
- Reuse auto-backup + crash recovery (engine-agnostic)
- Haydee 3 may have different file formats
