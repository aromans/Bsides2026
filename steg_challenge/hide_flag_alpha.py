#!/usr/bin/env python3
"""
Hide a flag in the alpha channel of an image using LSB steganography.
"""

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("[!] PIL not available, using manual PNG creation")

import sys

FLAG = "hwchall{4lph4_ch4nn3l_st3g0_1s_1nv1s1bl3}"

def hide_flag_with_pil(input_image, output_image, flag):
    """Hide flag using PIL/Pillow"""
    print(f"[*] Loading image: {input_image}")
    img = Image.open(input_image)

    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        print(f"[*] Converting {img.mode} to RGBA (adding alpha channel)")
        img = img.convert('RGBA')

    width, height = img.size
    print(f"[*] Image size: {width}x{height}")
    print(f"[*] Total pixels: {width * height}")

    # Convert flag to binary
    flag_bin = ''.join(format(ord(c), '08b') for c in flag)
    flag_bin += '00000000' * 4  # Null terminator (4 null bytes)

    print(f"[*] Flag: {flag}")
    print(f"[*] Flag length: {len(flag)} chars")
    print(f"[*] Binary length: {len(flag_bin)} bits")
    print(f"[*] Pixels needed: {len(flag_bin)} (one bit per pixel)")

    if len(flag_bin) > width * height:
        print(f"[!] Error: Flag too long for image!")
        print(f"[!] Need {len(flag_bin)} pixels, only have {width * height}")
        return False

    # Load pixel data
    pixels = img.load()

    # Hide flag in alpha channel LSBs
    print(f"[*] Hiding flag in alpha channel LSBs...")
    bit_index = 0

    for y in range(height):
        for x in range(width):
            if bit_index < len(flag_bin):
                r, g, b, a = pixels[x, y]

                # Modify LSB of alpha channel
                if flag_bin[bit_index] == '1':
                    a = a | 1  # Set LSB to 1
                else:
                    a = a & ~1  # Set LSB to 0

                pixels[x, y] = (r, g, b, a)
                bit_index += 1
            else:
                break
        if bit_index >= len(flag_bin):
            break

    print(f"[+] Hidden {bit_index} bits")
    print(f"[*] Saving to: {output_image}")
    img.save(output_image, 'PNG')
    print(f"[+] Done! Challenge image saved.")

    return True

def hide_flag_manual(input_image, output_image, flag):
    """Hide flag without PIL - read JPEG, create PNG manually"""
    print("[!] Manual PNG creation not implemented yet.")
    print("[!] Please install Pillow: pip3 install Pillow")
    return False

def main():
    input_image = 'hackerman.jpeg'
    output_image = 'hackerman_challenge.png'

    print("="*60)
    print("ALPHA CHANNEL STEGANOGRAPHY - FLAG HIDING")
    print("="*60)
    print()

    if HAS_PIL:
        success = hide_flag_with_pil(input_image, output_image, FLAG)
    else:
        success = hide_flag_manual(input_image, output_image, FLAG)

    if success:
        print()
        print("="*60)
        print("CHALLENGE CREATED!")
        print("="*60)
        print(f"File: {output_image}")
        print()
        print("The flag is hidden in the LSBs of the alpha channel.")
        print("Players need to:")
        print("  1. Recognize it's a PNG with alpha channel")
        print("  2. Extract LSBs from alpha channel")
        print("  3. Convert binary back to ASCII")
        print()
        print("Hint: 'The hackerman seems a bit transparent...'")

if __name__ == '__main__':
    main()
