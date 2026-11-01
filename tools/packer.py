import os, struct, sys

def create_pack(input_dir, output_path):
    # Collect all files recursively
    files = []
    dirs = set()
    for root, _, filenames in os.walk(input_dir):
        rel_root = os.path.relpath(root, input_dir)
        if rel_root != ".":
            parts = rel_root.replace("\\", "/").split("/")
            for i in range(len(parts)):
                dir_path = "\\".join(parts[:i+1])
                dirs.add(dir_path)
        for fn in filenames:
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, input_dir).replace("/", "\\")
            files.append((rel, full))
    
    all_dirs = sorted(dirs)
    all_files = sorted(files, key=lambda x: x[0])
    
    # Root dir name = first path component (e.g., "Sounds")
    root_dir = all_dirs[0].split("\\")[0] if all_dirs else ""
    
    # Build entries: dirs first (sorted), then files (sorted)
    # Each entry: (name, full_path, size, prior, is_dir)
    entries = []
    for d in all_dirs:
        # name is just the last component
        name = d.split("\\")[-1]
        entries.append((name, None, 0, 1, True, d))  # prior=1 for dir
    for rel, full in all_files:
        size = os.path.getsize(full)
        name = os.path.basename(rel)
        entries.append((name, full, size, 0, False, rel))  # prior=0 for file
    
    # Calculate desc table size: 12 bytes per entry
    num_entries = len(entries)
    desc_size = num_entries * 12
    
    # Calculate data offsets (files only, concatenated)
    # Data offsets are relative to data section start, after desc table
    data_offsets = {}
    current = desc_size  # skip desc table
    for name, full, size, prior, is_dir, path in entries:
        if not is_dir:
            data_offsets[path] = current
            current += size
    total_data_size = current - desc_size  # only file data size
    
    # Total data section size = desc_size + total_data_size
    total_section_size = desc_size + total_data_size
    
    # Build data section
    data_section = bytearray()
    # Desc table first
    for name, full, size, prior, is_dir, path in entries:
        if is_dir:
            data_section += struct.pack("<III", 0, 0, 1)  # dataOffset=0, dataSize=0, prior=1
        else:
            off = data_offsets[path]
            data_section += struct.pack("<III", off, size, 0)  # dataOffset, dataSize, prior=0
    # File data
    for name, full, size, prior, is_dir, path in entries:
        if not is_dir and full:
            with open(full, "rb") as f:
                data_section += f.read()
    
    # Build HD_CHUNK
    buf = bytearray()
    buf += b"HD_CHUNK"
    buf += struct.pack("<I", 0)  # padding
    buf += struct.pack("<I", 0)  # padding
    buf += struct.pack("<I", 100)  # version
    buf += struct.pack("<I", num_entries + 2)  # numInfo (entries + desc + data)
    buf += struct.pack("<I", total_section_size)  # dataSize
    
    # Info table: desc, data, and one per entry
    # "desc" record
    desc_name = b"desc" + b"\x00" * 28
    buf += desc_name
    buf += struct.pack("<I", desc_size)  # size
    buf += struct.pack("<I", 0)  # offset (relative to data section start)
    buf += struct.pack("<I", 0)  # padding
    buf += struct.pack("<I", 0)  # padding
    
    # "data" record
    data_name = b"data" + b"\x00" * 28
    buf += data_name
    buf += struct.pack("<I", total_data_size)  # size
    buf += struct.pack("<I", desc_size)  # offset (relative to data section start)
    buf += struct.pack("<I", 0)  # padding
    buf += struct.pack("<I", 0)  # padding
    
    # Entry records: offset points into desc table
    # First entry's desc offset = 0 (relative to descStart)
    # Each subsequent entry = previous + 12
    desc_rel = 0
    for name, full, size, prior, is_dir, path in entries:
        name_bytes = name.encode("ascii") + b"\x00" * (32 - len(name))
        if len(name_bytes) > 32:
            name_bytes = name.encode("ascii")[:32]
        buf += name_bytes
        buf += struct.pack("<I", 12)  # size = 12 (desc entry size)
        buf += struct.pack("<I", desc_rel)  # offset (relative to descStart)
        buf += struct.pack("<I", 0)  # padding
        buf += struct.pack("<I", 0)  # padding
        desc_rel += 12
    
    # Data section
    buf += data_section
    
    with open(output_path, "wb") as f:
        f.write(buf)
    
    print(f"Created pack: {output_path} ({len(buf)} bytes, {num_entries} entries)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: packer.py <input_dir> <output_pack>")
        sys.exit(1)
    create_pack(sys.argv[1], sys.argv[2])
