import os, subprocess, struct, sys

# Only these two directories
SOURCE_DIRS = [
    r"D:\Cube",
    r"D:\Cube\void-records",
]
OUTPUT_BASE = r"D:\Cube\pack_input\Sounds\Custom"
PACK_OUTPUT = r"D:\Cube\AllSounds.pack"

os.makedirs(OUTPUT_BASE, exist_ok=True)

# Collect audio files (only from root and void-records, not subdirs)
audio_files = []
for d in SOURCE_DIRS:
    for f in os.listdir(d):
        full = os.path.join(d, f)
        if os.path.isfile(full) and f.lower().endswith(('.ogg','.mp3','.wav','.flac')):
            audio_files.append((f, full))

# Deduplicate by filename (void-records might have same names as root)
seen = set()
unique = []
for name, full in audio_files:
    if name in seen:
        continue
    seen.add(name)
    unique.append((name, full))

print(f"Found {len(unique)} unique audio files to convert")

def sanitize_name(name):
    # Remove extension
    base = os.path.splitext(name)[0]
    # Replace spaces and special chars with underscores
    safe = ""
    for c in base:
        if c.isalnum() or c in "-_":
            safe += c
        else:
            safe += "_"
    return safe

def convert_to_wav(src, dst):
    """Convert audio to mono 16-bit 44100 Hz WAV without metadata"""
    cmd = [
        "ffmpeg", "-y", "-i", src,
        "-ar", "44100", "-ac", "1", "-sample_fmt", "s16",
        "-map_metadata", "-1", "-f", "wav", dst
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  FFMPEG ERROR: {result.stderr[-200:]}")
        return False
    return True

def strip_list_chunk(wav_path):
    """Remove LIST/metadata chunks from WAV"""
    data = open(wav_path, "rb").read()
    pos = 12
    chunks = []
    while pos < len(data) - 8:
        chunk_id = data[pos:pos+4]
        chunk_size = struct.unpack("<I", data[pos+4:pos+8])[0]
        chunks.append((pos, chunk_id, chunk_size))
        pos += 8 + chunk_size
        if chunk_size % 2 == 1:
            pos += 1
    
    # Keep RIFF header + fmt + data chunks only
    fmt_pos, fmt_id, fmt_size = chunks[0]
    data_pos, data_id, data_size = None, None, None
    for pos, cid, csize in chunks:
        if cid == b'data':
            data_pos, data_id, data_size = pos, cid, csize
            break
    
    if data_id is None:
        print("  No data chunk found!")
        return False
    
    riff_header = data[:12]
    fmt_chunk = data[fmt_pos:fmt_pos+8+fmt_size]
    data_chunk = data[data_pos:data_pos+8+data_size]
    
    clean = riff_header + fmt_chunk + data_chunk
    riff_size = len(clean) - 8
    clean = clean[:4] + struct.pack("<I", riff_size) + clean[8:]
    
    with open(wav_path, "wb") as f:
        f.write(clean)
    return True

def create_sound_file(name, wav_name, sound_path):
    content = "HD_DATA_TXT 300\r\n\r\nsoundCue\r\n{\r\n"
    content += '\tsound\t"Sounds\\Custom\\' + wav_name + '";\r\n'
    content += "\trange\t512.0;\r\n}\r\n"
    with open(sound_path, "wb") as f:
        f.write(content.encode("ascii"))

# Process each file
for i, (orig_name, src_path) in enumerate(unique):
    safe = sanitize_name(orig_name)
    wav_name = safe + ".wav"
    sound_name = safe + ".sound"
    wav_path = os.path.join(OUTPUT_BASE, wav_name)
    sound_path = os.path.join(OUTPUT_BASE, sound_name)
    
    print(f"[{i+1}/{len(unique)}] {orig_name} -> {safe}")
    
    # Convert
    if not convert_to_wav(src_path, wav_path):
        print(f"  SKIP (conversion failed)")
        continue
    
    # Strip LIST chunk
    strip_list_chunk(wav_path)
    
    # Create .sound file
    create_sound_file(safe, wav_name, sound_path)
    print(f"  OK")

print(f"\nDone. {len(unique)} files processed.")
print(f"Output: {OUTPUT_BASE}")
print(f"Run packer.py to create the pack.")
