# San Diego BSides2026 Hardware Hacking Challenge

## Hardware (Pico rp2040)
 
1) UART boot interrupt
	- UART will require to press enter within 5s to get flag.
	- (Representing unlocked bootloader)

2) Discover which pins are SPI
	- Requires probing pins for data (requires multimeter or logic analyzer)
	- Download firmware over SPI (saleae software, SPI analyzer + CSV download)

3) EMFI Glitch during "boot" 
	- This will be hinted in firmware
	- A successful EMFI glitch will give (password???) for a file

## Firmware

1) Firmware will be a squashfs 
	- Unsquashfs to get a rootfs

2) `/etc/shadow` will have a hash to crack
	- john, hashcat, etc
	- sha512 hash: `e553c9f0e41d7958fb5782004802970e1348620ce376ef642f2721ddf093e413bea7a3b3611d1cdbc06411fa4c904ecf397397c23d53894e3dbedb250688b75c`
	- password: 25302530

3) File can be found in `root` that is password protected
	- EMFI glitch
	- password: `el3ctr0m4gnetic_pul5es_f0r_fun_4nd_pr0f1t`

4) Simple binary found in `tmp` 
	- Buffer overflow vulnerability
    - ROP chain exploit

5) `png` file found in `home/haxor`
    	- Steganography flag 
        - flag hidden in alpha channel
        - use zsteg to get the flag



