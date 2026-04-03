#!/usr/bin/env python3

with open('spi_dump.csv', 'r') as f:
    content = f.readlines()[1:]

v = b''
for c in content[1::2]: # Every other row
    mosi = c.split(',')[2].strip()
    v += int(mosi, 16).to_bytes(1, 'big')

with open('spi_dump.bin', 'wb') as f:
    f.write(v)