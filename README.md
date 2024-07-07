![glowfire examples](data/glowfire.gif)

Release video: https://youtu.be/QseUhKPJywU

# Description
glowfire: graphical low-fidelity REPL environment  
Python for pocket computers. Designed for creative programming.  
glowfire is a fork of [snakeware](https://github.com/joshiemoore/snakeware) for the Raspberry Pi and Memory LCD.  
Reference hardware is the [SQFMI beepy (2023)](https://github.com/sqfmi/beepy-hardware).  

# Features
  * pygame on the SQFMI beepy
  * Self-hosted: builds its own software development kit on the beepy itself
  * Includes a Python userland, Snakeware Window Manager
  * Sound using USB audio dongle or Bluetooth (experimental)
  * Localized for English, French, and Japanese

# Requirements
  * SQFMI beepy (2023)
  * Raspberry Pi Zero 2 W
  * microUSB data cable
  * host computer for installation

# Install
These instructions assume a Raspberry Pi Zero 2 W is installed in the SQFMI beepy.  

## Flash MicroSD card
Download latest Raspberry Pi Imager. It does not self update.  
  * Device > Raspberry Pi Zero 2 W
  * Operating System > scroll down > Raspberry Pi OS (other) >
    Raspberry Pi OS Lite (64-bit) - "A port of Debian Bookworm with no desktop environment."
  * Storage > choose microSD drive
Custom OS options appear. Click "Edit Settings."  
  * Customize: To join wifi network. Assign SSID, username, and hostname.
  * Save.
Customization window appears. Click Yes.  
It applies the settings.  
MicroSD copies data to microSD card.  
Do not eject microSD card.  
After copy is complete:
```
desktop:$ touch /Volumes/bootfs/ssh  <- enable SSH to automatically start
desktop:$ vi /Volumes/bootfs/config.txt  <- add new line to bottom and write: dtoverlay=dwc2
desktop:$ vi /Volumes/bootfs/cmdline.txt  <- insert after text "rootwait": modules-load=dwc2,g_ether
```

## Connect to Raspberry Pi
Eject microSD. Install microSD card into Raspberry Pi Zero 2.  
Disconnect all cables from the beepy. Disconnect the USB-C connector from the beepy.  
Power off the beepy. Slide power switch to the left.  
Disconnect all cables from the beepy.  
Connect host computer to Raspberry Pi center connector. Only connect 1 MicroUSB data cable.  
The beepy powers on.  
Wait 5 minutes for automatic configuration of Raspberry Pi OS.  
It resizes the main partition, enables SSH, etc.  
Memory LCD remains blank.  
It reboots when complete.  
Because dwc2 is enabled, Raspberry Pi tunnels Ethernet over USB.  
Host computer detects Pi as USB network adapter.  
Wait for automatic setup of Raspberry Pi OS to complete.  
You should be able to ping Pi at its hostname.local.  

## Copy your SSH key to Pi
In this example, Pi admin user is named "pi."  
Copy your public SSH key to the Pi:
```
desktop:$ ssh-copy-id pi@beepy.local  <-- use Pi username@hostname
```
If your host computer mentions a key mismatch ("something nasty"), delete Pi host key:
```
desktop:$ ssh-keygen -R beepy.local  <-- use Pi hostname or IP
```
After old key is removed, retry ssh-copy-id.

## Mount NFS server automatically (optional)
For owners with NFS Git repos. (If you have an internal version of glowfire.)  
Assume a ZFS based NFS at 192.168.1.1, holding your local Git repo. Create a mountpoint for it:
```
beepy:$ sudo mkdir /mnt/git
```
Open /etc/fstab and insert this line, changing IP and zpool name as needed:
```
192.168.1.1:/mnt/zpool/git /mnt/git nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0
```
Reboot.

## Install glowfire
SSH to Pi. Install glowfire.
```
beepy:$ sudo apt install -y git
beepy:$ cd ~
beepy:$ git clone https://github.com/hack-shack/glowfire
beepy:$ cd ~/glowfire
beepy:$ python make-glowfire.py
```

It builds a custom toolchain for pygame on the Memory LCD.  
It takes about 2 hours to build on a Class 10 U1 microSD.  
There will be no LCD image during this time.  
It configures systemd to automatically start snakewm at boot.  

After make-glowfire.py finishes, the Pi will reboot into snakewm.
This is the snakeware window manager.  
To show the app menu, press space key or right click mouse.  

The touchpad will not work until you flash RP2040 firmware.  

# Flash firmware
To enable touchpad, install firmware.  

SSH into Pi and copy file to your host computer:  
~/glowfire/beepy-sdk/src/rp2040-firmware.uf2

This file contains detailed instructions on flashing the firmware:  
~/glowfire/beepy-sdk/src/rp2040-instructions.txt

Remove all cables from the beepy.  
Turn the beepy off. Slide beepy power switch to left.  
Connect your host computer to bottom USB-C port on beepy.  
Turn on in DFU mode. While holding End Call button, slide beepy power switch to right.  
Continue to hold End Call for 1 second, then release.  
On host computer, drag rp2040-firmware.uf2 file onto mounted RPI_RP2 disk. It should copy the file.  
On host computer, eject RPI-RP2 disk.  
Power cycle beepy. On beepy, slide power switch to left OFF, then right ON. It should boot.  
When beepy turns on, its LED is red. When glowfire starts, its LED turns off.  

# Set language
glowfire is localized for English, French, and Japanese.  
SSH into the beepy.  
Open ~/glowfire/snakewm/wm.py.  
Search for "Language" and uncomment the language you wish to use.  

# Use glowfire
Use the spacebar or right click to show the app menu.  
If SnakeWM crashes or exits, systemd automatically relaunches it.  
To disable auto relaunch, "sudo service snakewm disable"  

Shutdown system with system > shutdown, or holding End Call button (rightmost) for 5 seconds.  

Mouse pointer has no right or bottom limits.  
If you lose the pointer, move it to the upper left.

## Keyboard Shortcuts
  * Invert screen: Press berry key. A tiny asterisk in a box will appear in the upper right of the screen. Press 0 ("microphone") key. Screen colors will invert.

## Known Issues + TODO
This is an experimental system.
  * Many apps are incomplete, including most games and image/dither.
  * Any app which uses sound will crash if no audio output device is detected.
  * Connect USB audio dongles with a USB OTG hub or OTG adapter, to the Pi Zero center USB-Data port.
  * Bluetooth headset pairing is possible, but experimental. It must be done manually. See beepy-sdk/scripts/experimental/BT-NOTES.md and bt-robot.py.

# Take apart example apps
Examine the snakeware apps in ~/glowfire/snakewm/apps/

Read the pygame-gui Quick Start page:  
https://pygame-gui.readthedocs.io/en/latest/quick_start.html

Begin by taking apart a very simple app, like minitime.  
Compare its code to a more complex app.  
pygame-gui has useful documentation within its source code.  
pygame-gui source code is in beepy-sdk/src/pygame_gui/pygame_gui/

candLED and tracstar have GUI controls with attached events.  
Examine these if you are interested in working with controls.  
tracstar and audio apps will crash if no USB sound card is attached. 

# Run snakewm on your desktop computer
Clone the glowfire repo onto your desktop:
```
desktop:$ git clone https://github.com/hack-shack/glowfire ~/Developer/glowfire
desktop:$ cd ~/Developer/glowfire
```
(Optional) Make a new git branch, so any changes will be saved to it:
```
desktop:$ git checkout MyBranch  <-- name it what you like
```
(Recommended) Make a virtual environment, to store your dependencies:
```
desktop:$ python3 -m venv .venv
```
(Recommended) Change to your venv:
```
desktop:$ cd ~/Developer/glowfire
desktop:$ source .venv/bin/activate
```
Run snakewm:
```
(.venv) python3 -m snakewm.wm
```
Assuming you have all dependencies, snakewm will appear.  
The first time, some dependencies will probably be missing.  
You will need to install these into your environment.  
It requires pygame-ce and pygame-gui, and probably other modules.  
Every system is different. The error log should indicate the missing module.  
Install dependencies with pip.  
For example:
```
(.venv) $ pip install pygame-ce pygame-gui
```
Some apps will crash on launch if their dependencies are missing, e.g. pyttsx3 for the text-
to-speech engine:
```
desktop:$ python3 -m pip install pyttsx3
```
Continue this way, attempting to run snakewm, then installing
dependencies, until snakewm runs.

# Technical info
See beepy-sdk/docs directory for experimental notes.

# Contributing
These are guidelines for the overall style of glowfire.  
Follow the programming style from included programs.  
Variable names should describe their functions.  
Write documentation in Simplified Technical English. See ASD-STE100.  
