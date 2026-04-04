#!/usr/bin/env python3

with open('spi_dump.csv', 'r') as f:
    content = f.readlines()[1:]  # strip header

# First 4 rows are command (0x03) + 3 address bytes on MOSI — skip them
# Remaining rows are master dummy bytes (MOSI) with rootfs data clocked back on MISO
v = b''
for c in content[4:]:
    miso = c.split(',')[3].strip()
    v += int(miso, 16).to_bytes(1, 'big')

with open('spi_dump.bin', 'wb') as f:
    f.write(v)