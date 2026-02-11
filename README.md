# San Diego BSides2026 Hardware Hacking Challenge

## Hardware (Pico rp2040)
 
1) Discover which pins are UART
	- Discover unique baud rate (requires logic analyzer)

2) UART boot glitch
	- UART will require to press enter within 5s to get flag.
	- (Representing unlocked bootloader)

3) Discover which pins are SPI
	- Requires probing pins for data (requires multimeter or logic analyzer)
	- Download firmware over SPI (saleae software, SPI analyzer + CSV download)

4) EMFI Glitch during "boot" 
	- This will be hinted in firmware
	- A successful EMFI glitch will give (password???) for a file

## Firmware

1) Firmware will be a squashfs 
	- Unsquashfs to get a rootfs

2) `/etc/shadow` will have a hash to crack
	- john, hashcat, etc
	- bcrypt hash: `$2a$12$iDuorex.9pY48VmlT16rLejDZcQ3/zW4Ah6oDfNeFcs9QCUdF5X.q`
	- password: 25302530

3) File can be found in `root` that is password protected
	- EMFI glitch
	- password: `el3ctr0m4gnetic_pul5es_f0r_fun_4nd_pr0f1t`

4) Simple binary found `???` 
	- Buffer overflow vulnerability

5) `.ssh` will have a private key (??? Maybe something else, since standing up a Linode server could cause difficulties with other players ???)
	- `/home/hwh4ck3r` will have a `note.txt` with a server IP address. 
	- Using that private key, same user name, and server IP will allow someone to log into the server and get a flag. 

6) Maybe a `jpg` could be found in `tmp`
    	- Steganography flag 



