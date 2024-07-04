# FIRMWARE NOTES
This is a collection of notes made when building
the ardangelo 'beepberry-rp2040' firmware.

Flashloader is from:
https://github.com/rhulme/pico-flashloader

ardangelo has package documentation here:
https://ardangelo.github.io/beepy-ppa/#package-documentation

# GOALS
Get the ardangelo firmware to build on the glowfire system.
Enable in-circuit flash over SWD.

# TOOLS
  * objcopy
  * xxd

# LINKS
https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf

UF2 format: https://microsoft.github.io/uf2/

# NOTES
Targets build into: beepy-sdk/src/beepberry-rp2040/build/app

For pico_add_extra_outputs function, see:
beepy-sdk/src/beepberry-rp2040/3rdparty/pico-sdk/src/rp2_common.cmake, line 20
This file contains specifics on each output format in the first few lines.

pico_add_hex_output
pico_add_bin_output
pico_add_dis_output


# TESTING WITH RASPBERRY PI PICO BOARD
Build the pico flashloader.

cd beepy-sdk/src
git clone https://github.com/rhulme/pico-flashloader
cd pico-flashloader
cp -r ../beepberry-rp2040/3rdparty/pico-sdk/ ./
mkdir build
cd build
cmake -DPICO_SDK_PATH=../pico-sdk ..
make -j4



# ARDANGELO FIRMWARE UPDATER
Add ardangelo's beepy ppa package source:
$ sudo curl -s --compressed -o /etc/apt/sources.list.d/beepy.list "https://ardangelo.github.io/beepy-ppa/beepy.list"
$ curl -s --compressed "https://ardangelo.github.io/beepy-ppa/KEY.gpg" | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/beepy.gpg >/dev/null
$ sudo apt update

Install beepy-kbd, a dependency for beepy-fw:
$ sudo apt install -y beepy-kbd

Install beepy-fw:
$ sudo apt install -y beepy-fw
$ sudo update-beepy-fw



# INSPECTION
Examine the file, view in hex format, little endian:
$ xxd -e FLASH_ME.uf2

offset 12: address in flash where data should be written: 0x10000000
offset 16: number of bytes used in data: 

Seek to offset 12, length 4 bytes:
$ xxd -e -s 12 -l 4 FLASH_ME.uf2

Show total number of blocks in file:
$ xxd -e -s 24 -l 4 FLASH_ME.uf2
Take the number and multiply it by 512 bytes:
36 * 512 = 18432

Final magic number, located at offset 508 (should be 0x0ab16f30):
$ xxd -e -s 508 -l 4 FLASH_ME.uf2

Show flags:
xxd -e -s 8 -l 4 FLASH_ME.uf2




pico-flashloader/memmap_default.ld


# TEST BREADBOARD
Build and install firmware onto stock Raspi Pico board.
Attach SWD debugger and download image of flash memory.

Using with a J-Link and Pico board:
```
$ sudo openocd -f interface/jlink.cfg -c 'transport select swd' -c 'adapter_khz 6000' -f target/rp2040.cfg
```
Note: The config directories for OpenOCD are in: /usr/share/openocd/scripts/ (e.g. "target," "interface," etc.)

In another session, open a telnet connection to the OpenOCD server:
```
$ telnet localhost 4444
```

> halt;reset init
> halt;flash probe 0
> halt;flash info 0
> halt;dump_image flashdump.bin 0x00000000 

## References
  * Flashing the RP2040 with a J-Link and OpenOCD, https://machinehum.medium.com/flashing-the-rp2040-with-a-jlink-and-openocd-b5c6806d51c2
  * HW 101 JTAG Part 3, https://riverloopsecurity.com/blog/2021/07/hw-101-jtag-part3/
  * Developer explanation of RP2040 boot sequence:
    https://vanhunteradams.com/Pico/Bootloader/Boot_sequence.html
  * Bootloader project notes from the same developer:
    https://vanhunteradams.com/Pico/Bootloader/Bootloader.html



# SWD with onboard RP2040
```
$ sudo openocd -f interface/raspberrypi-native.cfg -f target/rp2040.cfg -c 'transport select swd' -c 'adapter gpio swdio 24' -c 'adapter gpio swclk 25'

> halt; dump_image onboard-dump.bin 0x10000000 0x200000
dumped 2097152 bytes in 141.406281s (14.483 KiB/s)

> quit
```

On the beepy:
```
$ sudo openocd -f interface/raspberrypi-native.cfg -f target/rp2040.cfg -c 'transport select swd' -c 'adapter gpio swdio 24' -c 'adapter gpio swclk 25' -c 'program onboard-dump.bin verify reset exit'
```


# Manually building pico-flashloader
cd /home/pi/glowfire/beepy-sdk/src
git clone https://github.com/rhulme/pico-flashloader
cd pico-flashloader;mkdir build;cd build
cmake -DPICO_SDK_PATH=/home/pi/glowfire/beepy-sdk/src/beepberry-rp2040/3rdparty/pico-sdk/ ..
make

It will build targets directly into the 'build' directory.
Program the device with the app250 demo:
```
$ sudo openocd -f interface/raspberrypi-native.cfg -f target/rp2040.cfg -c 'transport select swd' -c 'adapter gpio swdio 24' -c 'adapter gpio swclk 25' -c 'program app250.elf verify reset exit'
```
It will appear to do nothing on the beepy.


# w4ilun firmware
cd src/i2c_puppet
git submodule update --init
cd 3rdparty/pico-sdk
git submodule update --init
cd ../../
mkdir build;cd build
cmake ..


# Customizing ardangelo rp2040 firmware for glowfire
Goals:
  * build ELF file for flashing over SWD
  * enable touchpad by default
  * disable keyboard backlight by default
  * remap 4 hardware button strip for the GUI
  * remap keys, shift functions, etc. as needed

## Key functions
  * left button (left outer button) - has u-shaped glyph
  * menu button (left inner button) - a small group of dots in a rough circle
  * skip over touchpad and its button for now
  * esc button (right inner button) - arrow curving back on itself
  * right button (right outer button) - the u-shaped glyph, upside down, with a bar beneath it

$ echo always | sudo tee /sys/module/beepy_kbd/parameters/touch_act
$ echo mouse | sudo tee /sys/module/beepy_kbd/parameters/touch_as