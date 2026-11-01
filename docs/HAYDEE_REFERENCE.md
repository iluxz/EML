# Haydee / Edith Reference Notes

## File Formats

### .edith (Map files)
- UTF-16LE encoded text, parsed by `src/edith.js`
- Structure: `HD_DATA_TXT 300` header, `content { ... }` block with entities
- Entities have components: CSG, CSGSolid, StaticMesh, Skeleton, PlayerMesh, Ragdoll, Sound, Travel, etc.
- NavMeshes can cause crashes — remove if unstable
- Hyphens in director target names crash OG Edith (rename `Grate-2` → `Grate2`)

### .mesh (3D models)
- `HD_CHUNK` container, 60-byte vertices
- Vertex layout: position(3f), uv(2f), boneIndex(int32), normal(3f), tangent(3f), bitangent(3f)
- 32-bit unsigned indices
- Bounds: 24 bytes (min vec3 + max vec3)

### .pack (Archives)
- `HD_CHUNK` container with `desc` and `data` properties
- Desc entry: 12 bytes [dataOffset u32, dataSize u32, prior u32]
- Directories: dataSize==0 && prior==1
- Files: dataSize>0 && prior==0
- Custom packs go in `Packs\` folder

### .sound (Sound cues)
- Text file (HD_DATA_TXT 300) referencing a .wav
- Format:
```
HD_DATA_TXT 300

soundCue
{
	sound	"Sounds\Custom\name.wav";
	range	512.0;
}
```
- .wav must be: mono, 44100 Hz, 16-bit, no LIST/metadata chunks
- Must be in a .pack to load (loose files don't work)

### .scene (Compiled maps)
- Baked binary (HD_CHUNK) with embedded geometry
- Created by compiling .edith in Edith (F5 or compile button)
- Required for NEW GAME menu (needs .game file too)

### .game (Campaign config)
- Text file in `System\`
- Format:
```
HD_DATA_TXT 300
game
{
    name "CampaignName";
    default false;
    scene N_Start;
    entry E_Start;
    intro Intro;
}
```
- `scene` = first scene to load
- `entry` = entity name to spawn player at

### .skel / .skin / .doll
- .skel: bone names, parent indices, rest matrices (104 bytes per bone)
- .skin: weights (20 bytes each: 4 floats + 4 bone indices), binds (112 bytes each)
- .doll: ragdoll collision shapes (limbs + shapes)

## Edith Editor

### Controls
- Right-click drag = mouselook
- WASD = fly, Shift = 3x sprint
- Q/Ctrl = down, E/Space = up

### Compilation
- Compiling a map creates a `.scene` file in `Scenes\`
- Compiled scenes have baked CSG geometry
- Doors/triggers work after compilation (not in uncompiled .edith)

### CSG
- CSG = visual geometry (cheaper, editable)
- CSGSolid = collision geometry (blocks movement)
- Decals clip on non-continuous geometry (individual tile brushes)

### Director Graph
- Nodes can connect to multiple nodes by dragging multiple lines from same output
- Gate nodes are for branching (not strictly required)
- Nodes: Enable, Disable, Toggle, Travel, etc.

### Sound Components
- `Sound` component (not Background) for triggered SFX
- Props: is3D, start, looped, sound (path to .sound file)

## Engine Quirks
- `CreateFileA` with `CREATE_ALWAYS` truncates file immediately → crash during save = corrupted file
- `hdWAVLoad` rejects WAVs with LIST/metadata chunks
- NavMeshes can cause crashes during gameplay
- Edith crashes on large maps (stack buffer overflow in haydee.dll)
- Loose audio files don't load — must be in .pack

## Safety Tools
- `auto_backup.py` — watches .edith files, backs up on change (validates before backup)
- `crash_recovery.py` — monitors edith.exe, auto-restores corrupted files on crash
- Both in `D:\Multipurpose\other projects\edithreborn\`
- Startup bat: `edith_safety.bat` in Windows Startup folder

## Custom Packer
- `packer.py` — creates .pack files from folder structure
- Usage: `python packer.py <input_dir> <output_pack>`
- Input folder structure becomes pack's internal paths

## Ghidra RE Findings
- edith.exe: x86 PE, imports from haydee.dll
- Save map: FUN_0048e020 → hdUISaveFile → FUN_0048df80 → HDESaveJob
- Save flow: hdStreamFileWrite → HDData::SaveTxt → FUN_10102620 (writer constructor)
- hdStreamFileWrite: CreateFileA with CREATE_ALWAYS (truncates immediately!)
- haydee.dll base in edith: ~0x730D0000 (varies per run)

## Modloader
- `injector.exe` + `payload.dll` — DLL injection into edith.exe
- Hooks hdStreamFileWrite (both ANSI and wide versions)
- Successfully tested — creates .bak before every save
- Defender flags inline hooking as suspicious (add exclusion)

## Key Addresses (edith.exe)
- FUN_0048e020: map save dialog
- FUN_0048df80: map save callback (creates HDESaveJob)
- FUN_00415450: save file wrapper (hdUISaveFile)
- FUN_00415300: save selected nodes callback (hdStreamFileWrite + SaveTxt)

## Key Addresses (haydee.dll)
- hdStreamFileWrite(char*) @ +0x1aa280
- hdStreamFileWrite(wchar_t*) @ +0x1aa2d0
- HDData::SaveTxt @ +0x1006b0
- FUN_10102620: HDDataWriterWTxt constructor
- hdChunkSave @ +0x0ff700
