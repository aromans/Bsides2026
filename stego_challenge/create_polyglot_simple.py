#!/usr/bin/env python3
"""
Creates a PNG/ZIP polyglot file with corrupted PNG magic bytes.
Uses a minimal PNG - no external dependencies needed.
"""

import zipfile
import os
import struct
import zlib

def create_minimal_png(width=400, height=200, text="Fixed! But not done yet..."):
    """Create a minimal valid PNG with red background"""

    # PNG signature
    png_sig = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk (image header)
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr = struct.pack('>I', len(ihdr_data)) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)

    # Create red image data (simple red pixels)
    scanlines = []
    for y in range(height):
        # Filter byte (0 = none) + RGB data for each pixel
        scanline = b'\x00' + (b'\xff\x00\x00' * width)  # Red pixels
        scanlines.append(scanline)

    raw_data = b''.join(scanlines)
    compressed_data = zlib.compress(raw_data, 9)

    # IDAT chunk (image data)
    idat_crc = zlib.crc32(b'IDAT' + compressed_data) & 0xffffffff
    idat = struct.pack('>I', len(compressed_data)) + b'IDAT' + compressed_data + struct.pack('>I', idat_crc)

    # tEXt chunk with hint
    text_data = b'Comment\x00' + text.encode('latin1')
    text_crc = zlib.crc32(b'tEXt' + text_data) & 0xffffffff
    text_chunk = struct.pack('>I', len(text_data)) + b'tEXt' + text_data + struct.pack('>I', text_crc)

    # IEND chunk (end of image)
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)

    # Combine all chunks
    png_data = png_sig + ihdr + text_chunk + idat + iend
    return png_data

# Step 1: Create a minimal PNG
print("[*] Creating hint PNG...")
png_data = create_minimal_png(400, 200, "You fixed the header! But this isn't the real flag... Try: unzip challenge.png")
with open('hint.png', 'wb') as f:
    f.write(png_data)
print("[+] Hint PNG created: hint.png")

# Step 2: Create ZIP file with real flag
print("[*] Creating ZIP with real flag...")
with zipfile.ZipFile('secret.zip', 'w') as zf:
    zf.write('flag.txt')
print("[+] ZIP created: secret.zip")

# Step 3: Create polyglot (PNG + ZIP)
print("[*] Creating polyglot file...")
with open('polyglot.png', 'wb') as polyglot:
    # Write PNG data
    with open('hint.png', 'rb') as png:
        polyglot.write(png.read())

    # Append ZIP data (ZIP files can have data prepended!)
    with open('secret.zip', 'rb') as zf:
        polyglot.write(zf.read())

print("[+] Polyglot created: polyglot.png")

# Step 4: Corrupt the PNG magic bytes
print("[*] Corrupting PNG header...")
with open('polyglot.png', 'rb') as f:
    data = bytearray(f.read())

# PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A
# Corrupt byte 2: 50 -> 46 (P -> F)
print(f"[*] Original header: {' '.join(f'{b:02X}' for b in data[:8])}")
data[2] = 0x46  # Change 0x50 to 0x46 (P -> F)
print(f"[*] Corrupted header: {' '.join(f'{b:02X}' for b in data[:8])}")

with open('challenge.png', 'wb') as f:
    f.write(data)

print("[+] Corrupted polyglot created: challenge.png")
print()

# Verify the challenge
print("=" * 70)
print("VERIFICATION")
print("=" * 70)

# Try to verify it's broken
import subprocess
try:
    result = subprocess.run(['file', 'challenge.png'], capture_output=True, text=True)
    print(f"file command output: {result.stdout.strip()}")
except:
    pass

# Check size
size = os.path.getsize('challenge.png')
print(f"Challenge file size: {size} bytes")
print()

print("=" * 70)
print("CHALLENGE FILE READY: challenge.png")
print("=" * 70)
print()
print("Solution:")
print("  Stage 1: Fix corrupted PNG header")
print("           Byte offset 0x02: Change 0x46 -> 0x50")
print("           [89 46 4E 47] -> [89 50 4E 47]")
print("           Command: printf '\\x50' | dd of=challenge.png bs=1 seek=2 count=1 conv=notrunc")
print()
print("  Stage 2: Unzip the fixed file")
print("           Command: unzip challenge.png")
print("           Extract: flag.txt")
print()

# Cleanup intermediate files
os.remove('hint.png')
os.remove('secret.zip')
os.remove('polyglot.png')
print("[*] Cleaned up intermediate files")
