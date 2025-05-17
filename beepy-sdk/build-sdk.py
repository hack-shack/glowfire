#!/usr/bin/python
"""
build-sdk : create sdk for sqfmi beepy

(c) 2023 Asa Durkee. MIT License.

1/6: Set up Raspberry Pi for beepy hardware.
2/6: Install DirectFB2 graphics library, examples, and tools.
3/6: Install SDL2 on top of DirectFB2.
4/6: Install pygame on top of SDL2.
5/6: Install Bluetooth audio subsystem.
6/6: Finish up and restart.

It is designed to run on a fresh install of Raspberry
Pi OS Lite (64-bit) "bookworm" on a Raspberry Pi Zero 2.

There's not much error handling.
You may need to manually work around issues.
See main() function at end of script. Comment out steps
as needed.


"""
# IMPORTS =================================================
# =========================================================
import argparse
import time
from datetime import timedelta
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# VARIABLES ===============================================
# =========================================================
STARTTIME = time.time()
FINISHTIME = time.time()
VERBOSE     = False  # Extra verbose output when set to True
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # return the Current Working Directory
DATA_DIR_NAME = "data"  # what you'd like to call the data directory
DATA_DIR = os.path.join(SCRIPT_DIR, DATA_DIR_NAME)
SRC_DIR_NAME = "src"  # what you'd like to call the sources directory
SRC_DIR = os.path.join(SCRIPT_DIR, SRC_DIR_NAME)
MESON_CMD_DIR = os.path.join("/usr/local/bin")  # where the meson binary is located
DFBARGS="system=fbdev,fbdev=/dev/fb1"  # export these env. variables to run DirectFB2 on Sharp Memory LCD
LIB32ARGS="LD_LIBRARY_PATH=/usr/local/lib/arm-linux-gnueabihf/"  # 32-bit Raspi OS DirectFB library path
LIB64ARGS="LD_LIBRARY_PATH=/usr/local/lib/aarch64-linux-gnu/"    # 64-bit Raspi OS DirectFB library path

# FUNCTIONS ===============================================
# =========================================================
# Shortcuts to command-line tools
# -------------------------------
def sudo_apt(*args):
    return subprocess.check_call(['sudo','apt'] + list(args))

def autoreconf(*args):
    return subprocess.check_call(['autoreconf'] + list(args))

def sudo_bash(*args):
    return subprocess.check_call(['sudo','bash'] + list(args))

def bash(*args):
    return subprocess.check_call(['bash'] + list(args))

def configure(*args):
    return subprocess.check_call(['./configure'] + list(args))

def cmake(*args):
    return subprocess.check_call(['cmake'] + list(args))

def git(*args):
    return subprocess.check_call(['git'] + list(args))

def sudo_ldconfig(*args):
    return subprocess.check_call(['sudo','ldconfig'] + list(args))

def sudo_make(*args):
    return subprocess.check_call(['sudo','make'] + list(args))

def make(*args):
    return subprocess.check_call(['make'] + list(args))

def sudo_meson(*args):
    return subprocess.check_call(['sudo',os.path.join(MESON_CMD_DIR,'meson')] + list(args))

def meson(*args):
    return subprocess.check_call([os.path.join(MESON_CMD_DIR,'meson')] + list(args))

def patch(*args):
    return subprocess.check_call(['patch'] + list(args))

def sudo_pip(*args):
    # TODO: Move to venv and remove --break-system-packages.
    return subprocess.check_call(['sudo', 'pip'] + list(args) + ['--break-system-packages'])

def pip(*args):
    # TODO: Move to venv and remove --break-system-packages.
    return subprocess.check_call(['pip'] + list(args) + ['--break-system-packages'])

def python(*args):
    return subprocess.check_call(['python'] + list(args))

def sudo_python(*args):
    return subprocess.check_call(['sudo', 'python'] + list(args))

def sudo_raspi_config(*args):
    return subprocess.check_call(['sudo', 'raspi-config'] + list(args))

def sudo_reboot(*args):
    print("INFO : Rebooting system.")
    return subprocess.check_call(['sudo', 'reboot'] + list(args))

def wget(*args):
    return subprocess.check_call(['wget'] + list(args))


# Early and bootstrapping functions
# ---------------------------------
def early_setup():
    sudo_apt("update")
    sudo_apt("install","-y","git")
    sudo_apt("install","-y","raspberrypi-kernel")

def configure_raspi_basics():
    print("INFO : Enabling I2C...")
    sudo_raspi_config("nonint","do_i2c","0")
    print("INFO : Enabling SPI...")
    sudo_raspi_config("nonint","do_spi","0")
    print("INFO : Enabling console auto-login...")
    sudo_raspi_config("nonint","do_boot_behaviour","B2")

def download_source(url,download_dir_name,desc,branch=None,copy_from=None):
    # url = URL
    # download_dir = directory name to clone into, within the sources directory
    # desc = optional description of package you're downloading
    # branch = optional branch name
    dest_dir = os.path.join(SRC_DIR,download_dir_name)
    print("INFO : download_source: Checking if directory exists   : " + dest_dir)
    if os.path.exists(dest_dir):
        print("INFO : download_source: Found source directory         : " + dest_dir)
        print("INFO : download_source: Checking if source dir is empty: " + dest_dir)
        dir_items = os.scandir(dest_dir)
        matches_visible = []
        matches_invisible = []
        for item in dir_items:
            p_invisible = re.compile("^\.\w+$")  # REGEX: match dotfiles: start of line + dot + word chars until end of line
            p_visible   = re.compile("^(?=\.\w+)") # REGEX: negative lookahead to exclude dotfiles
            matches_visible   += re.findall(p_visible, item.name)
            matches_invisible += re.findall(p_invisible, item.name)
        if VERBOSE == True:
            print("Visible matches:")
            for item in matches_visible:
                print("  * " + item)
            print("Invisible matches:")
            for item in matches_invisible:
                print("  * " + item)
        if matches_visible and matches_invisible:  # both visible and invisible files in source dir
            print("INFO : download_source: "+ download_dir_name + " source directory appears full. Skipping download.")
            print("INFO : ---------------------------------------------------------------------")
            return 0

        if not (matches_visible and matches_invisible):  # source dir might be empty
            print("INFO : download_source: " + download_dir_name + " appears empty. Deleting and recreating.")
            print("INFO : download_source: This will trigger a clean build for " + download_dir_name + ".")
            try:
                shutil.rmtree(dest_dir)
            except 0:
                print("INFO : download_source: Successfully deleted empty directory: " + dest_dir)
                print("INFO : download_source: Continuing.")
                raise
            except OSError as ex:
                if ex.errno == errno.ENOTEMPTY:
                    print("ERROR: download_source: There was a problem deleting the directory: " + dest_dir)
                    print("ERROR: download_source: Try manually deleting it: " + dest_dir)
                    raise
            except:
                print("ERROR: download_source : Issue deleting the directory: " + dest_dir)
                raise
    if not os.path.exists(dest_dir):
        if copy_from is not None: # if it's a local filesystem copy, using the copy_from argument
            print("INFO : download_source: Copying folder tree.")
            print("INFO :   Source : " + str(copy_from))
            print("INFO :   Dest   : " + str(dest_dir))
            try:
                shutil.copytree(os.path.join(copy_from),dest_dir)
            except:
                raise
        if copy_from is None:  # if it's a git repo
            print("INFO : download_source: No source directory found; creating at: " + dest_dir)
            try:
                os.makedirs(dest_dir)
            except 0:
                print("INFO: download_source: Successfully created source directory at: " + dest_dir)
                raise
            except:
                print("ERROR: download_source: Error creating source directory at: " + dest_dir)
                print("ERROR: Try manually deleting it, or checking permissions.")
                raise
            print("INFO : download_source: Downloading via full git clone from: " + url)
            # TODO: Check it's created successfully.
            if branch:
                try:
                    git ("clone", url, dest_dir, "--branch", branch)
                except:
                    print("ERROR: Issue cloning the branch of the git repo. Try manually cloning it via: git clone " + url + " " + dest_dir + "--branch " + branch)
                    raise
            else:
                try:
                    git ("clone", url, dest_dir)
                except:
                    print("ERROR: Issue cloning the git repo. Try manually cloning it via: git clone " + url + " " + dest_dir)
                    raise
    print("INFO : download_source: ----------------------------------------------------------")

def resize_swapfile():
    cwd = os.getcwd()
    sudo_python(os.path.join(cwd,"resize-swapfile.py"))

# Create a main directory for source code and builds
# --------------------------------------------------
def create_src_dir():
    print("INFO : create_src_dir: About to create a directory for the SDK source code and builds.")
    for dir in [SRC_DIR]:
        if os.path.isdir(dir):
            print("INFO : create_src_dir: Found an SDK source directory at: " + dir)
        if not os.path.exists(dir):
            print("INFO: create_src_dir: Couldn't find directory: " + dir + ". This is expected. Creating now.")
            os.mkdir(dir)

def create_build_dir(dir):
    print("INFO : create_build_dir: About to create a build directory.")
    if os.path.isdir(dir):
        print("INFO : create_build_dir: Found a directory at: " + dir)
    if not os.path.exists(dir):
        print("INFO: create_build_dir: Couldn't find directory: " + dir + ". This is expected. Creating now.")
        os.mkdir(dir)

# Build ardangelo RP2040 firmware for beepy
# -----------------------------------------
def build_ardangelo_rp2040_firmware(build_clean=True):
    C_SRCDIR = os.path.join(SRC_DIR,"beepberry-rp2040")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    C_PICOSDK = os.path.join(C_SRCDIR,"3rdparty/pico-sdk")
    ELF_FW_SOURCE = os.path.join(C_BUILDDIR,"app/firmware.elf")
    UF2_FW_SOURCE = os.path.join(C_BUILDDIR,"app/firmware.uf2")
    ELF_FW_DEST = os.path.join(SRC_DIR,"rp2040-firmware.elf")
    UF2_FW_DEST = os.path.join(SRC_DIR,"rp2040-firmware.uf2")

    print("INFO : Building RP2040 firmware.")
    if build_clean is True:
        print("INFO : Building clean.")
        try:
            shutil.rmtree(os.path.join(C_SRCDIR,"build"),ignore_errors=True)
            os.mkdir(os.path.join(C_SRCDIR,"build"))
        except:
            pass

    # Set up the pico SDK and its dependencies
    # ----------------------------------------
    print("INFO : Patching .gitmodules with https URL for pico-extras.")
    lines_to_write = [\
    "[submodule \"3rdparty/pico-sdk\"]",
    "        path = 3rdparty/pico-sdk",
    "        url = https://github.com/raspberrypi/pico-sdk.git",
    "[submodule \"pico-flashloader\"]",
    "        path = 3rdparty/pico-flashloader",
    "        url = https://github.com/rhulme/pico-flashloader.git",
    "[submodule \"pico-extras\"]",
    "        path = 3rdparty/pico-extras",
    "        url = https://github.com/ardangelo/pico-extras.git"]
    gitmodules_file = os.path.join(C_SRCDIR,".gitmodules")
    with open(gitmodules_file,mode='w') as f:
        f.seek(0)
        f.truncate()
        for line in lines_to_write:
            f.write(line + "\n")
        f.close()
    print("INFO : Setting up the pico SDK and its dependencies.")
    print("INFO : This will take some time.\n")
    os.chdir(C_SRCDIR)
    git("submodule","update","--init")
    os.chdir(C_PICOSDK)
    git("checkout","6a7db34ff63345a7badec79ebea3aaef1712f374")  # pico sdk v1.5.1, 2023-06-13
    git("submodule","update","--init")  # installs TinyUSB submodule

    # Build ardangelo RP2040 firmware
    # -------------------------------
    if os.path.exists(C_BUILDDIR):
        print("INFO : Found build directory: " + str(C_BUILDDIR))
        print("INFO : This means the RP2040 firmware has probably been built before.")
        if build_clean is True:
            try:
                print("INFO : Removing build directory in preparation for building clean: " + str(C_BUILDDIR))
                shutil.rmtree(C_BUILDDIR)
            except:
                print("INFO : Problem removing directory at: " + str(C_BUILDDIR))
                raise
    if not os.path.exists(C_BUILDDIR):
        print("INFO : Did not find build directory: " + str(C_BUILDDIR))
        print("INFO : This is expected for a clean build.")
        try:
            print("INFO : Creating build directory at: " + str(C_BUILDDIR))
            os.mkdir(C_BUILDDIR)
        except:
            print("INFO : Problem creating build directory at: " + str(C_BUILDDIR))
            raise
    print("INFO : Patching ardangelo driver for dim red LED at boot.")
    try:
        patch("-t",os.path.join(SRC_DIR,"beepberry-rp2040/app/pi.c"),os.path.join(DATA_DIR,"ardangelo-rp2040/pi.c.diff"))
    except:
        raise
    os.chdir(C_BUILDDIR)
    cmake("-DPICO_BOARD=beepy","-DPICO_SDK_PATH=" + str(C_PICOSDK),"..")
    os.chdir(C_BUILDDIR)  # just to be sure cmake hasn't changed current working dir on us
    make()

    # Copy built firmware to more accessible location
    # -----------------------------------------------
    try:
        print("INFO : Copying RP2040 UF2 firmware.")
        print("INFO :     From: " + str(UF2_FW_SOURCE))
        print("INFO :       To: " + str(UF2_FW_DEST))
        shutil.copy(UF2_FW_SOURCE, UF2_FW_DEST)
    except:
        print("ERROR: Problem copying RP2040 UF2 firmware file to: " + str(UF2_FW_DEST))
    """
    # TODO: Add pico-flashloader to ardangelo's ELF output as bootloader. Currently it only adds pico-flashloader bootloader to UF2 files.
    # TODO: https://github.com/rhulme/pico-flashloader
    try:
        print("INFO : Copying RP2040 ELF firmware.")
        print("INFO :     From: " + str(ELF_FW_SOURCE))
        print("INFO :       To: " + str(ELF_FW_DEST))
        shutil.copy(ELF_FW_SOURCE, ELF_FW_DEST)
    except:
        print("ERROR: Problem copying RP2040 ELF firmware file to: " + str(ELF_FW_DEST))
    """
    # Write down instructions for manual flashing
    # -------------------------------------------
    instructions_uf2 = ["RP2040 UF2 firmware has been built and copied to:\n",
                    str(UF2_FW_DEST),
                    "\nIt will need to be manually installed as follows:\n",
                    "  * Copy this UF2 file to a host computer.\n",
                    "  * Shut down the beepy, then turn its power switch off, to the left.\n",
                    "  * Connect beepy to host computer using USB port on bottom of beepy.\n",
                    "  * While holding END CALL (rightmost button on 'touchpad strip'),\n",
                    "    turn beepy power on.\n",
                    "  * In bootloader mode, RGB LED is lit.\n",
                    "  * RP2040 will mount as a disk on your computer.\n",
                    "  * Drag UF2 file onto the disk. beepy will update and reboot.\n"]
    instructions_elf = ["RP2040 ELF firmware has been built and copied to:\n",
                    str(ELF_FW_DEST),
                    "\nThis firmware can be installed via OpenOCD after jumpering\n",
                    "the first and second pads across J45 (SWCLK, SWDIO) on the beepy.\n",
                    "See beepy-sdk/docs/data/beepy-j45.png for a diagram.\n",
                    "Once you have jumpered the pads:\n",
                    "$ sudo apt install -y openocd\n",
                    "$ sudo openocd -f interface/raspberrypi-native.cfg -f target/rp2040.cfg -c 'transport select swd' -c 'adapter gpio swdio 24' -c 'adapter gpio swclk 25' -c 'program rp2040-firmware.elf verify reset exit'\n"]
    try:
        print("INFO : Writing RP2040 flashing instructions to: " + str(os.path.join(SRC_DIR,"rp2040-instructions.txt")))
        with open(os.path.join(SRC_DIR,"rp2040-instructions.txt"),mode='w') as f:
            f.seek(0)     # to be 100% sure
            f.truncate()  # to be 100% sure
            #f.write("You have 2 options to flash the RP2040 firmware. Choose one:\n\n")
            f.write("You will need to manually flash the RP2040 over USB.\n")
            f.write("INSTRUCTIONS FOR USB FLASHING\n")
            f.write("-----------------------------\n")
            for instruction in instructions_uf2:
                f.write(instruction)
            #f.write("\nINSTRUCTIONS FOR ON-DEVICE FLASHING\n")
            #f.write("-----------------------------------\n")
            #for instruction in instructions_elf:
            #    f.write(instruction)
    except:
        print("INFO : Problem writing to : " + str(os.path.join(SRC_DIR,"rp2040-instructions.txt")))

# Install Sharp DRM driver
# ------------------------
def install_sharp_drm_driver():
    print("INFO : Checking to see if sharp-drm-driver is patched for overclocked SPI...")
    p = re.compile("spi-max-frequency = <2000000>;")  # Factory maximum 2MHz. Tested maximum 7MHz. 8MHz produces vertical tearing.
    with open(os.path.join(SRC_DIR,"sharp-drm-driver/sharp-drm.dts"),mode='r') as source_file:
        source = source_file.read()
        matches = re.findall(p,source)
    if matches:
        print("INFO : Found sharp-drm.dts is already patched. Continuing...")
    if not matches:
        print("INFO : sharp-drm-driver not patched.")
        print("INFO : Patching sharp-drm.dts.")
        patch("-t",os.path.join(SRC_DIR,"sharp-drm-driver/sharp-drm.dts"),os.path.join(SCRIPT_DIR,"data/sharp-drm-driver/sharp-drm.dts.diff"))
    
    os.chdir(os.path.join(SRC_DIR,"sharp-drm-driver"))
    make()
    sudo_make("install")

# Install ardangelo keyboard driver (for debian bookworm)
# -------------------------------------------------------
def buildinstall_ardangelo_keyboard_driver():
    print("INFO : Building and installing ardangelo keyboard driver.")
    driver_dir = os.path.join(SRC_DIR,"beepberry-keyboard-driver")
    os.chdir(driver_dir)
    try:
        make()
        sudo_make("install")
    except:
        print("ERROR: Error building ardangelo keyboard driver.")

# Install build tools
# ------------------------------------
def install_apt_dependencies():
    print("INFO : Running apt update.")
    sudo_apt("update")
    print("INFO : Installing core build dependencies via apt.")
    sudo_apt("install","-y","git","cmake","python3-pip","autoconf","libtool")
    print("INFO : Installing libdrm-dev dependency via apt.")
    sudo_apt("install","-y","libdrm-dev")
    print("INFO : Installing dependencies to build RP2040 firmware.")
    sudo_apt("install","-y","gcc-arm-none-eabi","libnewlib-arm-none-eabi","libstdc++-arm-none-eabi-newlib")
    print("INFO : Installing i2c-tools: userland tools for use with the RP2040. (Optional.)")
    sudo_apt("install","-y","i2c-tools")
    print("INFO : Installing dependencies to build Sharp kernel module and keyboard driver.")
    sudo_apt("install","-y","raspberrypi-kernel-headers")
    print("INFO : Installing dependencies for DirectFB2-media image provider library.")
    print("INFO : These allow specific image formats to be decoded: PNG, JPG, etc.")
    sudo_apt("install","-y","libavcodec-dev","libavformat-dev","libavif-dev","libavutil-dev","libswscale-dev","libimlib2-dev","libmpeg3-dev","libopenexr-dev","libspng-dev","libtiff-dev","libvorbisidec-dev","libwebp-dev")
    print("INFO : Installing ALSA development headers. This is a FusionSound dependency.")
    sudo_apt("install","-y","libasound2-dev")
    print("INFO : Installing optional dependencies for DirectFB2.")
    sudo_apt("install","-y","libmad0-dev","libvorbis-dev")
    print("INFO : Installing optional dependencies for SDL2.")
    sudo_apt("install","-y","libsamplerate0-dev","libibus-1.0-dev","libudev0","libudev1","libudev-dev","libgbm-dev")
    print("INFO : Installing optional dependencies for SDL_mixer.")
    sudo_apt("install","-y","libfluidsynth-dev","libopenmpt-dev","libopenmpt-modplug-dev","libopusfile-dev")
    print("INFO : Installing dependencies for pygame-ce.")
    sudo_apt("install","-y","libportmidi-dev")
    print("INFO : Installing updated kernel.")
    sudo_apt("install","-y","raspberrypi-kernel")
    print("INFO : Installing support for flashing RP2040 in-circuit via SWD.")
    sudo_apt("install","-y","openocd")
    print("INFO: Installing text to speech support for Python.")
    sudo_apt("install","-y","python3-espeak")
    sudo_pip("install","pyttsx3")

# Install Ninja - must use pip; apt version is too old
# ----------------------------------------------------
def install_ninja():
    print("INFO : Installing Ninja.")
    sudo_pip("install","ninja")

# Install Meson
# -----------------------
def install_meson():
    print("INFO : Installing Meson. This may take a few seconds with no output.")
    sudo_pip("install","meson")

# Download source code for DirectFB2, its GUI library, and sample graphical programs
# ----------------------------------------------------------------------------------
def download_sources():
    """ Download source code: beepy drivers, DirectFB2, SDL, pygame, etc. """
    print("INFO : download_sources: Starting. Only deleted folders will be replaced.")
    print("INFO : download_sources: If a source folder already exists, it will be untouched.")
    print("INFO : download_sources: To redownload source or build clean, delete its directory.")
    print("INFO : The entire src folder is safe to delete, if you wish to build all clean.")
    print("INFO : download_sources: ----------------------------------------------------------")

    # ardangelo rp2040 firmware
    download_source("https://github.com/ardangelo/beepberry-rp2040","beepberry-rp2040","Beepy RP2040 firmware")
    os.chdir(os.path.join(SRC_DIR,"beepberry-rp2040"))
    git("checkout","e9a286998589a8a35dd017bed857eba2f86c28f2")  # 2024-05-04

    # ardangelo keyboard driver
    download_source("https://github.com/ardangelo/beepberry-keyboard-driver","beepberry-keyboard-driver","BBQ20 keyboard driver, ardangelo version")
    os.chdir(os.path.join(SRC_DIR,"beepberry-keyboard-driver"))
    git("checkout","e65472734decd59450e2448d1218c4f69babcea8")  # 2024-04-30

    # ardangelo sharp driver : temporarily using Kiboneu's repo; contains patch for pull request #15 on ardangelo repo
    download_source("https://github.com/Kiboneu/sharp-drm-driver","sharp-drm-driver","Sharp Memory LCD DRM framebuffer driver")
    os.chdir(os.path.join(SRC_DIR,"sharp-drm-driver"))
    git("checkout","e65472734decd59450e2448d1218c4f69babcea8")  # 2025-04-31
    
    download_source("https://github.com/deniskropp/flux","flux","Flux library for DirectFB2")
    os.chdir(os.path.join(SRC_DIR,"flux"))
    git("checkout","10ad2ebc78b396032714b839f200848ea0dd9503")  # 2022-04-05

    download_source("https://github.com/directfb2/FusionSound2", "FusionSound2", "FusionSound2 library for DirectFB2 - optional")
    os.chdir(os.path.join(SRC_DIR,"FusionSound2"))
    git("checkout","7a98d790c0148a6135f82d8fcbe4603cd57b34df")  # 2023-03-13

    download_source("https://github.com/directfb2/DirectFB2", "DirectFB2", "DirectFB2 library")
    os.chdir(os.path.join(SRC_DIR,"DirectFB2"))
    git("checkout","a7a176bb501c0730cd24bf06420ce35f53e85a15")  # 2023-08-15

    download_source("https://github.com/directfb2/directfb-csource", "directfb-csource", "DirectFB2 C source")
    os.chdir(os.path.join(SRC_DIR,"directfb-csource"))
    git("checkout","2758dee7937e8850d6c8105bd6ef1db06c86064f")  # 2023-06-07

    download_source("https://github.com/directfb2/DirectFB2-tools", "DirectFB2-tools", "DirectFB2 tools")
    os.chdir(os.path.join(SRC_DIR,"DirectFB2-tools"))
    git("checkout","679838c281cbe7849011f7f6db1c815167c44fee")  # 2023-07-19

    download_source("https://github.com/directfb2/DirectFB-examples", "DirectFB-examples", "DirectFB2 examples")
    os.chdir(os.path.join(SRC_DIR,"DirectFB-examples"))
    git("checkout","dcba184f9a72bc03ea5440fde4b9c817b702d9d7")  # 2023-08-21

    download_source("https://github.com/directfb2/DirectFB2-media", "DirectFB2-media", "DirectFB2 image handlers: JPG, PNG, etc.")
    os.chdir(os.path.join(SRC_DIR,"DirectFB2-media"))
    #git("checkout","ec35e5b31949f73b2e1e649f68f290b0c57f4f01")  # 2023-08-07
    git("checkout","8f8cb02a3d67a3eb9726ca2927061e2697b7f2de")  # 2024-04-02

    download_source("https://github.com/directfb2/DirectFB-media-samples", "DirectFB-media-samples", "DirectFB media samples")
    os.chdir(os.path.join(SRC_DIR,"DirectFB-media-samples"))
    git("checkout","e36c07cd0f7fb2553129217448962928a022466a")  # 2023-08-17

    download_source("https://github.com/directfb2/LiTE", "LiTE", "LiTE GUI library for DirectFB2")
    os.chdir(os.path.join(SRC_DIR,"LiTE"))
    git("checkout","486c0878e99f6a3f5a805ac63fc8fb27987d3cb6")  # 2023-06-12

    download_source("https://github.com/directfb2/LiTE-examples", "LiTE-examples", "LiTE GUI examples")
    os.chdir(os.path.join(SRC_DIR,"LiTE-examples"))
    git("checkout","9f88d75da2a965b5f1e002485a7695787624345f")  # 2023-06-12

    download_source("https://github.com/directfb2/DFBTerm", "DFBTerm", "DFBTerm terminal emulator")
    os.chdir(os.path.join(SRC_DIR,"DFBTerm"))
    git("checkout","c6e3d58e7b3a1a789bde9afd172d143a5610a313")  # 2022-09-17


    # Download SDL2 and libraries for it
    # =====================================================
    download_source("https://github.com/libsdl-org/SDL","SDL","SDL2 library","release-2.28.x")
    os.chdir(os.path.join(SRC_DIR,"SDL"))
    git("checkout","031912c4b6c5db80b443f04aa56fec3e4e645153")  # 2023-08-02

    download_source("https://github.com/libsdl-org/SDL_image","SDL_image","SDL2_image library","release-2.6.x")
    os.chdir(os.path.join(SRC_DIR,"SDL_image"))
    git("checkout","d3c6d5963dbe438bcae0e2b6f3d7cfea23d02829")  # 2023-02-06

    download_source("https://github.com/libsdl-org/SDL_mixer","SDL_mixer","SDL2 mixer library","release-2.6.x")
    os.chdir(os.path.join(SRC_DIR,"SDL_mixer"))
    git("checkout","6103316427a8479e5027e41ab9948bebfc1c3c19")  # 2023-02-06

    download_source("https://github.com/libsdl-org/SDL_ttf","SDL_ttf","SDL2 TTF library","release-2.20.x")
    os.chdir(os.path.join(SRC_DIR,"SDL_ttf"))
    git("checkout","89d1692fd8fe91a679bb943d377bfbd709b52c23")  # 2023-02-06


    # Download pygame-ce
    # =====================================================
    download_source("https://github.com/pygame-community/pygame-ce","pygame_ce","pygame_ce 2.4.1")
    os.chdir(os.path.join(SRC_DIR,"pygame_ce"))
    git("checkout","42e561262941f7ff99a3346e00897cc6ddd61786")  # 2024-02-18, v2.4.1 release

    # Download pygame-gui
    # =====================================================
    download_source("https://github.com/MyreMylar/pygame_gui","pygame_gui","pygame_gui 0.6.9")
    os.chdir(os.path.join(SRC_DIR,"pygame_gui"))
    git("checkout","7ed5e711cb05df3d0525e81cef43ef0f9ed1f444")  # 2023-04-23, v0.6.9 release


# Build and install fluxcomp, an interface compiler for DirectFB
# --------------------------------------------------------------
def buildinstall_fluxcomp():
    print("INFO : Checking to see if fluxcomp.cpp is patched...")
    p = re.compile("#include <direct/log.h\>")
    with open(os.path.join(SRC_DIR,"flux/src/fluxcomp.cpp"),mode='r') as source_file:
        source = source_file.read()
        matches = re.findall(p,source)
    if matches:
        print("INFO : Found fluxcomp.cpp is already patched. Continuing...")
    if not matches:
        print("INFO : Patching flux.")  # add "#include <direct/lib.h>" to fluxcomp.cpp
        patch("-t",os.path.join(SRC_DIR,"flux/src/fluxcomp.cpp"),os.path.join(SCRIPT_DIR,"data/fluxcomp.diff"))
    print("INFO : Checking to see if libdirect is already present...")
    file_to_look_for = "/usr/local/lib/arm-linux-gnueabihf/libdirect-2.0.so.0.0.0"
    if os.path.isfile(file_to_look_for):
        print("INFO : Found libdirect shared library. DirectFB2 has been installed already.")
    if not os.path.isfile(file_to_look_for):
        print("INFO : Did not find libdirect shared library. DirectFB2 does not appear to be installed.")
    print("INFO : Building flux.")
    print("INFO : -------------------------------------------------------------")
    print("INFO : This may or may not take a long time, up to 15 minutes on the")
    print("INFO : Pi Zero 2. Your SSH session may disconnect.")
    print("INFO : -------------------------------------------------------------")
    os.chdir(os.path.join(SRC_DIR,"flux"))
    bash("./autogen.sh")  # complains, but hand-off from python works better this way than autoreconf
    configure()
    print("INFO : -------------------------------------------------------------")
    print("INFO : gcc include path details:")
    os.system("echo | gcc -E -Wp,-v -")
    print("INFO : -------------------------------------------------------------")
    print("INFO : buildinstall_fluxcomp: running sudo make install...")
    sudo_make("install")

# Build DirectFB2
# --------------------
# See all configure options in src/DirectFB2/meson_options.txt
def build_directfb2():
    print("INFO : Building DirectFB2...")
    print("INFO : build_directfb2: Updating linker cache so fluxcomp builds correctly.")
    sudo_ldconfig()
    DFB_SRCDIR   = os.path.join(SRC_DIR,"DirectFB2")
    DFB_BUILDDIR = os.path.join(DFB_SRCDIR,"build")
    print("INFO : build_directfb2: DirectFB2 build dir should be at: " + DFB_BUILDDIR)
    print("INFO : build_directfb2: Next command will be: meson setup " + DFB_SRCDIR + " " + DFB_BUILDDIR)
    try:
        meson("setup",DFB_SRCDIR, DFB_BUILDDIR)
    except:
        exception = sys.exc_info()[0]
        print(exception)
    print("INFO : build_directfb2: Configuring DirectFB2 build options...")
    try:
        meson("configure",DFB_BUILDDIR,\
        #"-Dlibdir=lib",\
        "-Dmmx=false",  "-Dneon=false", "-Dmemcpy-probing=true",\
        "-Ddrmkms=true","-Dfbdev=true", "-Dlinux_input=true",\
        "-Dmulti=false", "-Dmulti-kernel=false","-Dtext=true",\
        "-Dsmooth-scaling=false","-Ddebug-support=true")
    except:
        print("ERROR: build_directfb2: Configure phase had an error.")
    print("INFO : build_directfb2: Compiling DirectFB2...")
    try:
        meson("compile","-C",DFB_BUILDDIR)
    except:
        print("ERROR: build_directfb2: DirectFB2 build had an error.")
        return

# Install DirectFB2
# ----------------------
def install_directfb2():
    C_SRCDIR = os.path.join(SRC_DIR,"DirectFB2")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    os.chdir(C_SRCDIR)
    sudo_meson("install","-C",C_BUILDDIR)

# Build and install DirectFB data header file generation utility
# --------------------------------------------------------------
def buildinstall_directfb_csource():
    C_SRCDIR = os.path.join(SRC_DIR,"directfb-csource")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    os.chdir(C_SRCDIR)
    meson("setup",C_BUILDDIR)
    meson("compile","-C",C_BUILDDIR)
    sudo_meson("install","-C",C_BUILDDIR)

# Build and install DirectFB2 tools
# ------------------------------------
def buildinstall_directfb2_tools():
    C_SRCDIR = os.path.join(SRC_DIR,"DirectFB2-tools")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    os.chdir(C_SRCDIR)
    meson("setup",C_SRCDIR, C_BUILDDIR)
    meson("compile","-C",C_BUILDDIR)
    sudo_meson("install","-C",C_BUILDDIR)

# Build and install DirectFB2 examples
# ------------------------------------
def buildinstall_directfb_examples():
    C_SRCDIR = os.path.join(SRC_DIR,"DirectFB-examples")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    os.chdir(C_SRCDIR)
    meson("setup",C_SRCDIR, C_BUILDDIR)
    meson("compile","-C",C_BUILDDIR)
    sudo_meson("install","-C",C_BUILDDIR)

# Build and install DirectFB2 image handlers (JPG, PNG, GIF, etc.)
# ----------------------------------------------------------------
def buildinstall_directfb2_media():
    C_SRCDIR = os.path.join(SRC_DIR,"DirectFB2-media")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    os.chdir(C_SRCDIR)
    meson("setup",C_SRCDIR,C_BUILDDIR)
    meson("compile","-C",C_BUILDDIR)
    sudo_meson("install","-C",C_BUILDDIR)

# Build and install DirectFB2 media samples
# -----------------------------------------
def buildinstall_directfb_media_samples():
    C_SRCDIR = os.path.join(SRC_DIR,"DirectFB-media-samples")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    os.chdir(C_SRCDIR)
    meson("setup",C_SRCDIR,C_BUILDDIR)
    meson("compile","-C",C_BUILDDIR)
    sudo_meson("install","-C",C_BUILDDIR)
    # Samples install in /usr/local/bin. There are four: df_databuffer, df_fonts_sample, df_image_sample, and df_video_sample.

# Build and install LiTE, DirectFB2's GUI library
# -----------------------------------------------
def buildinstall_lite():
    C_SRCDIR = os.path.join(SRC_DIR,"LiTE")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    meson("setup",C_SRCDIR,C_BUILDDIR)
    meson("configure",C_BUILDDIR,"-Dimage-headers=png")
    meson("compile","-C",C_BUILDDIR)
    sudo_meson("install","-C",C_BUILDDIR)

# Patch LiTE's default GUI theme with monochrome widgets for Memory LCD
# ---------------------------------------------------------------------
def patch_lite_monowidgets():
    print("INFO : Patching LiTE GUI widgets with monochrome versions...")
    C_SRCDIR = os.path.join(SCRIPT_DIR,"data/LiTE-monowidgets/")
    C_DSTDIR = os.path.join(SRC_DIR,"LiTE/data/")
    shutil.copytree(C_SRCDIR, C_DSTDIR, dirs_exist_ok=True)

# Build and install LiTE examples
# -------------------------------
def buildinstall_lite_examples():
    C_SRCDIR = os.path.join(SRC_DIR,"LiTE-examples")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    meson("setup",C_SRCDIR,C_BUILDDIR)
    meson("compile","-C",C_BUILDDIR)
    sudo_meson("install","-C",C_BUILDDIR)

# Build and install DFBTerm, a terminal emulator made with DirectFB2
# ------------------------------------------------------------------
def buildinstall_dfbterm():
    C_SRCDIR = os.path.join(SRC_DIR,"DFBTerm")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    meson("setup",C_SRCDIR,C_BUILDDIR)
    meson("compile","-C",C_BUILDDIR)
    sudo_meson("install","-C",C_BUILDDIR)

# Build and install FusionSound2 - audio support for DirectFB (optional)
# ----------------------------------------------------------------------
def buildinstall_fusionsound2():
    print("INFO : Building FusionSound2...")
    C_SRCDIR = os.path.join(SRC_DIR,"FusionSound2")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    os.chdir(C_SRCDIR)
    meson("setup",C_BUILDDIR)
    meson("compile","-C",C_BUILDDIR)
    sudo_meson("install","-C",C_BUILDDIR)



# Build and install SDL2
# ----------------------
def buildinstall_sdl2():
    """ Build and install SDL2. """
    #DIRECTFB_LIBS = '/usr/local/lib/aarch64-linux-gnu/'
    #os.environ['DIRECTFB_LIBS'] = '/usr/local/lib'
    C_SRCDIR = os.path.join(SRC_DIR,"SDL")
    os.chdir(C_SRCDIR)
    bash("./autogen.sh")
    configure(\
    "--disable-directfb-shared",\
    "--enable-video-directfb","--disable-video-kmsdrm",\
    "--disable-video-opengl","--disable-video-opengles2",\
    "--disable-video-vulkan",\
    "--disable-video-wayland","--disable-video-x11",\
    "--disable-video-x11-xinput","--disable-video-x11-xfixes",\
    "--disable-video-rpi", "--disable-video-vivante",\
    "--disable-hidapi-libusb","--disable-hidapi",\
    "--enable-alsa","--disable-oss","--disable-jack",\
    "--disable-esd","--disable-pipewire","--disable-pulseaudio",\
    "--disable-arm-simd","--disable-arm-neon")
    make()
    sudo_make("install")

def buildinstall_sdl2_image():
    """ Build and install SDL2 support for common image formats. """
    C_SRCDIR = os.path.join(SRC_DIR,"SDL_image")
    os.chdir(C_SRCDIR)
    bash("./autogen.sh")
    configure()
    make()
    sudo_make("install")

def buildinstall_sdl2_mixer():
    """ Build and install SDL2 support for sound mixing and effects. """
    C_SRCDIR = os.path.join(SRC_DIR,"SDL_mixer")
    os.chdir(C_SRCDIR)
    bash("./autogen.sh")
    configure()
    make()
    sudo_make("install")

def buildinstall_sdl2_ttf():
    """ Build and install SDL2 library for font support. """
    C_SRCDIR = os.path.join(SRC_DIR,"SDL_ttf")
    os.chdir(C_SRCDIR)
    bash("./autogen.sh")
    configure("--disable-silent-rules","--enable-freetype-builtin=no","--enable-harfbuzz=no","--enable-harfbuzz-builtin=no")
    make()
    sudo_make("install")


# pygame : build and install
# =========================================================
def buildinstall_pygame_ce():
    """ Build and install pygame Community Edition. """
    print("INFO : Building and installing pygame-ce...")
    C_SRCDIR = os.path.join(SRC_DIR,"pygame_ce")
    os.chdir(C_SRCDIR)
    sudo_python("setup.py","-config","-auto")
    sudo_python("setup.py","install")

def buildinstall_pygame_gui():
    """ Build and install pygame-gui. """
    print("INFO : Building and installing pygame-gui...")
    C_SRCDIR = os.path.join(SRC_DIR,"pygame_gui")
    os.chdir(C_SRCDIR)
    python("setup.py","build")
    sudo_python("setup.py","install")


# Bluetooth Audio : download, build and install
# =========================================================
def download_btaudio():
    # Fraunhofer AAC codec
    C_SRCDIR = os.path.join(SRC_DIR,"fdk-aac")
    download_source("https://github.com/mstorsjo/fdk-aac","fdk-aac","Fraunhofer AAC codec")
    os.chdir(C_SRCDIR)
    git("checkout","3f864cce9736cc8e9312835465fae18428d76295") # 2022-05-31

    # bluez-alsa : maps virtual audio devices to bluetooth connections
    C_SRCDIR = os.path.join(SRC_DIR,"bluez-alsa")
    download_source("https://github.com/Arkq/bluez-alsa","bluez-alsa","bluez-alsa system")
    os.chdir(C_SRCDIR)
    git('checkout','221d0969244d5b5785dc6b77e7de2fc932901536')  # 2023-09-09

    # Low Complexity Communication Codec Plus
    C_SRCDIR = os.path.join(SRC_DIR,"LC3plus")
    download_source("https://github.com/arkq/LC3plus","LC3plus","LC3plus library")
    os.chdir(C_SRCDIR)
    git('checkout','22227f8e7384e0f2adee63bad830d400fa702da8')  # 2023-02-27


def buildinstall_aac():
    C_SRCDIR =  os.path.join(SRC_DIR,"fdk-aac")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    os.chdir(C_SRCDIR)
    print("INFO : Creating build directory for AAC codec.")
    create_build_dir(os.path.join(C_SRCDIR,"build"))
    print("INFO : Building AAC codec.")
    os.chdir(C_BUILDDIR)
    cmake('../')
    sudo_make('install')

def buildinstall_lc3plus():
    C_SRCDIR =  os.path.join(SRC_DIR,"LC3plus/src/floating_point")
    os.chdir(C_SRCDIR)
    print("INFO : Building LC3plus.")
    make('libLC3plus.so')
    # Manually install the binary, headers, and shared library:
    sudo_bash(os.path.join(SCRIPT_DIR,'install-lc3plus.sh'))


def buildinstall_btaudio():
    # Build codecs which lack pre-built packages
    buildinstall_aac()
    buildinstall_lc3plus()

    # Download packaged codecs and other dependencies
    sudo_apt('install','-y','bluez','bluez-source','bluez-tools','libbluetooth-dev','libdbus-1-dev','libglib2.0-dev','libreadline-dev','python3-docutils','libbsd0','libbsd-dev','libsbc-dev','libsbc1')

    # Install optional dependencies
    sudo_apt('install','-y','pipewire')
    # Install dependencies for LDAC configure option: --enable-ldac
    sudo_apt('install','-y','libldacbt-abr-dev','libldacbt-enc-dev')
    # Install dependencies for aptX "openaptx" (--with-libopenaptx):
    sudo_apt('install','-y','libopenaptx-dev','libopenaptx0')
    # Install MP3 support dependencies (--enable-mp3lame):
    sudo_apt('install','-y','libmp3lame-dev','libmp3lame0')
    # Install MPEG decoding support dependencies (--enable-mpg123)
    sudo_apt('install','-y','libmpg123-0','libmpg123-dev','mpg123')
    # Install aptX support (for --enable-aptx and/or --enable-aptx-hd)
    # NOTE: This may need to be manually installed.
    # TODO: Add aptX
    # Install spandsp (--enable-msbc):
    sudo_apt('install','-y','libspandsp-dev','libspandsp2')

    ### Download and configure bluez-alsa
    ### ---------------------------------
    C_SRCDIR = os.path.join(SRC_DIR,"bluez-alsa")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")
    print("INFO : Downloading bluez-alsa sources to " + C_SRCDIR + "...")
    #git('clone','https://github.com/Arkq/bluez-alsa')
    print("INFO : Running autoreconf to generate a .configure file. This will take a minute or two.")
    os.chdir(C_SRCDIR)
    autoreconf('--install')
    print("INFO : Creating build directory.")
    create_build_dir(C_BUILDDIR)
    print("INFO : Configuring bluez-alsa.")
    # Configure with these options (change alsaplugindir= to 32-bit version if on 32-bit OS)
    os.chdir(C_BUILDDIR)
    os.environ['CFLAGS']  = '-I/usr/local/include/LC3plus'
    os.environ['LDFLAGS'] = '-L/usr/local/lib/'
    bash('../configure','--enable-manpages',
          '--enable-aac',
          '--enable-lc3plus','--enable-ldac',
          '--enable-mp3lame','--enable-mpg123',
          '--with-libopenaptx','--enable-aptx','--enable-aptx-hd',
          '--enable-msbc','--enable-rfcomm','--enable-hcitop',
          '--with-alsaplugindir=/usr/lib/aarch64-linux-gnu/alsa-lib/')
    print("INFO : Building bluez-alsa.")
    make()
    sudo_make('install')
    # Update shared library 'index' so bluealsa will run
    bash('./libtool','--finish','/usr/lib/aarch64-linux-gnu/alsa-lib/')
    sudo_ldconfig()

    # Configure ALSA for virtual Bluetooth device
    # -------------------------------------------
    os.chdir(SCRIPT_DIR)
    sudo_python('scripts/configure-alsa.py')

# Flash firmware onto RP2040 using SWDIO/SWCLK solder bridge
# ===========================================================
def flash_rp2040_firmware():
    print("INFO : Flashing RP2040 in-circuit.")
    # openocd doesn't accept arguments when used with subprocess, so we have to use os.system
    command_to_run = "sudo openocd -f interface/raspberrypi-native.cfg -f target/rp2040.cfg -c 'transport select swd' -c 'adapter gpio swdio 24' -c 'adapter gpio swclk 25' -c 'program " + os.path.join(SRC_DIR,"rp2040-firmware.elf") + " verify reset exit'"
    print(command_to_run)
    os.system(command_to_run)



# INFORMATIONAL FUNCTIONS
# =========================================================
# Beginning-of-build info for the user
def info_begin():
    STARTTIME = time.time()  # update it ('zeroed' at start of script)
    print("INFO : ------------------------------------------------------")
    print("INFO : build-sdk must be run on a fresh, new installation of")
    print("INFO : Raspberry Pi OS. This provides a known-good baseline.")
    print("INFO : Installing it on a 'dirty' OS will break the script.")
    print("INFO : ------------------------------------------------------")

# End-of-build information for the user
# -------------------------------------
def info_finish():
    FINISHTIME = time.time()  # update it ('zeroed' at start of script)
    BUILDTIME  =  FINISHTIME - STARTTIME
    print("INFO : Buildtime: %s" % timedelta(seconds=round(BUILDTIME)))
    print("INFO : -------------------------------------------------------")
    print("INFO : Build process complete. Reboot before testing examples.")
    print("INFO : -------------------------------------------------------")
    print("INFO : How to flash new RP2040 firmware:")
    print("INFO : " + str(os.path.join(SRC_DIR,"rp2040-instructions.txt")))
    print("INFO : RP2040 firmware UF2 file should be here:")
    print("INFO : " + str(os.path.join(SRC_DIR,"rp2040-firmware.uf2")))
    print("INFO : ------------------------------------------")


# MAIN ====================================================
# =========================================================
def main():
    info_begin()
    print("INFO : Current working directory for build-sdk.py: " + SCRIPT_DIR)
    print("INFO : SDK sources directory: " + SRC_DIR)

    # PART 1/6 (Get a working beepy, with text console on the LCD, and keyboard support)
    # ----------------------------------------------------------------------------------
    configure_raspi_basics()
    resize_swapfile()  # needed to build directfb2 reliably without hanging
    create_src_dir()
    download_sources()
    install_apt_dependencies()
    build_ardangelo_rp2040_firmware()
    # flash_rp2040_firmware()  # Uncomment this to flash the firmware over SWD.
    install_sharp_drm_driver()
    buildinstall_ardangelo_keyboard_driver()

    # PART 2/6 (Install DirectFB onto the beepy)
    # ------------------------------------------
    install_ninja()
    install_meson()
    buildinstall_fluxcomp()
    build_directfb2()
    install_directfb2()
    buildinstall_fusionsound2()  # needs libdirect from directfb2 in order to build
    buildinstall_directfb_csource()
    buildinstall_lite()
    patch_lite_monowidgets()  # TODO: improve widget set; wincursor.png not masked
    #buildinstall_directfb2_media()  # TODO: fails on debian bookworm. not critical to pygame. (2024-04)
    #buildinstall_directfb_media_samples()  # disabled building DirectFB extras for a faster build
    #buildinstall_directfb_examples()  # disabled for faster build
    #buildinstall_directfb2_tools()  # disabled for faster build
    #buildinstall_lite_examples()  # disabled for faster build
    #buildinstall_dfbterm()  # disabled for faster build
    sudo_python(os.path.join(SCRIPT_DIR,'scripts/configure-environment.py'))

    # PART 3/6 (Install SDL2)
    # -----------------------------------------------------
    buildinstall_sdl2()
    buildinstall_sdl2_ttf()
    buildinstall_sdl2_image()
    buildinstall_sdl2_mixer()

    # PART 4/6 (Install pygame)
    # -----------------------------------------------------
    buildinstall_pygame_ce()
    buildinstall_pygame_gui()

    # PART 5/6 (Install Bluetooth audio support)
    # -----------------------------------------------------
    download_btaudio()
    buildinstall_btaudio()

    # PART 6/6 (Display end-of-script message)
    # -----------------------------------------------------
    info_finish()
    #sudo_reboot()  # to activate keyboard and Memory LCD

# ENTRY POINT
# =========================================================
uid = os.geteuid()
print("INFO : UID is: " + str(uid))
if os.geteuid() == 0:
    exit("ERROR: You must run this script as a non-root user, without sudo.")
if os.geteuid() != 0:
    print("INFO : Running as non-root user. This is expected behavior.")

if __name__=="__main__":
    main()
