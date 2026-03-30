#!/usr/bin/env python3
"""
Creates a PNG/ZIP polyglot file with corrupted PNG magic bytes.

Stage 1: Fix PNG header (89 50 4E 47 -> correct magic bytes)
Stage 2: Unzip the same file to get the real flag
"""

from PIL import Image, ImageDraw, ImageFont
import zipfile
import os

# Step 1: Create a PNG with a hint
print("[*] Creating hint PNG...")
img = Image.new('RGB', (800, 400), color='black')
draw = ImageDraw.Draw(img)

# Try to use a font, fall back to default if not available
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
except:
    font = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Draw hint text
draw.text((50, 100), "Nice! You fixed the header.", fill='white', font=font)
draw.text((50, 160), "But that's not the real flag...", fill='yellow', font=font)
draw.text((50, 250), "Hint: This file is more than meets the eye.", fill='green', font=font_small)
draw.text((50, 300), "flag{n0t_th3_r34l_fl4g_k33p_g01ng}", fill='red', font=font_small)

img.save('hint.png')
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
        png_data = png.read()
        polyglot.write(png_data)

    # Append ZIP data (ZIP files can have data before them!)
    with open('secret.zip', 'rb') as zf:
        zip_data = zf.read()
        polyglot.write(zip_data)

print("[+] Polyglot created: polyglot.png")

# Step 4: Corrupt the PNG magic bytes
print("[*] Corrupting PNG header...")
with open('polyglot.png', 'rb') as f:
    data = bytearray(f.read())

# PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A
# Corrupt byte 2: 50 -> 46 (P -> F)
print(f"[*] Original header: {' '.join(f'{b:02X}' for b in data[:8])}")
data[2] = 0x46  # Change 0x50 to 0x46
print(f"[*] Corrupted header: {' '.join(f'{b:02X}' for b in data[:8])}")

with open('challenge.png', 'wb') as f:
    f.write(data)

print("[+] Corrupted polyglot created: challenge.png")
print()
print("=" * 60)
print("CHALLENGE FILE READY: challenge.png")
print("=" * 60)
print()
print("Solution:")
print("  Stage 1: Fix bytes [89 46 4E 47] -> [89 50 4E 47]")
print("           (Change byte offset 0x02 from 0x46 to 0x50)")
print("  Stage 2: unzip challenge.png")
print()

# Cleanup intermediate files
os.remove('hint.png')
os.remove('secret.zip')
os.remove('polyglot.png')
print("[*] Cleaned up intermediate files")
