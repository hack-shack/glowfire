#!/usr/bin/python
"""
Copyright (c) 2023 Asa Durkee. MIT License.

Sets up Raspberry Pi for beepy hardware.
Installs DirectFB2 graphics library and examples.

It is designed to be run on a clean install of
Raspbian Lite (32-bit) on a Raspberry Pi Zero 2.

There's not much error handling. You may need to
manually work around issues.
"""
# IMPORTS =================================================
# =========================================================
import argparse
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
CLEAN_BUILD = False  # Enables clean build every time script is run
VERBOSE     = False  # Extra verbose output when set to True
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # return the Current Working Directory
SRC_DIR_NAME = "src"  # what you'd like to call the sources directory
SRC_DIR = os.path.join(SCRIPT_DIR, SRC_DIR_NAME)
MESON_CMD_DIR = os.path.join("/usr/local/bin")  # where the meson binary is located
DFBARGS="system=fbdev,fbdev=/dev/fb1"  # export these env. variables to run DirectFB2 on Sharp Memory LCD

# FUNCTIONS ===============================================
# =========================================================
# Shortcuts to command-line tools
# -------------------------------
def sudo_apt(*args):
    return subprocess.check_call(['sudo','apt'] + list(args))

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
    return subprocess.check_call(['sudo', 'pip'] + list (args))

def pip(*args):
    return subprocess.check_call(['pip'] + list(args))

def sudo_python(*args):
    return subprocess.check_call(['sudo', 'python'] + list (args))

def sudo_raspi_config(*args):
    return subprocess.check_call(['sudo', 'raspi-config'] + list (args))

def sudo_reboot(*args):
    print("INFO : Rebooting system.")
    return subprocess.check_call(['sudo', 'reboot'] + list (args))


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

def download_source(url,download_dir_name,desc):
    # url = URL
    # download_dir = directory name to clone into, within the sources directory
    # desc = optional description of package you're downloading
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
        print("INFO : download_source: Downloading via shallow git clone from: " + url)
        # TODO: Check it's created successfully.
        try:
            git ("clone", "--depth", "1", url, dest_dir)
        except:
            print("ERROR: Issue cloning the git repo. Try manually cloning it via: git clone " + url + " " + dest_dir)
            raise
    print("INFO : download_source: ----------------------------------------------------------")


# Create a directory for source code and builds
# ---------------------------------------------
def create_src_dir():
    print("INFO : create_src_dir: About to create a directory for the SDK source code and builds.")
    for dir in [SRC_DIR]:
        if os.path.isdir(dir):
            print("INFO : create_src_dir: Found an SDK source directory at: " + dir)
        if not os.path.exists(dir):
            print("INFO: create_src_dir: Couldn't find directory: " + dir + ". This is expected. Creating now.")
            os.mkdir(dir)

# Build RP2040 firmware
# ---------------------------------
def build_rp2040_firmware():
    C_SRCDIR = os.path.join(SRC_DIR,"beepberry-rp2040")
    C_BUILDDIR = os.path.join(C_SRCDIR,"build")

    print("INFO : Changing into directory: " + str(C_SRCDIR))
    os.chdir(C_SRCDIR)
    git("submodule","update","--init")
    os.chdir(os.path.join(C_SRCDIR,"3rdparty/pico-sdk"))
    git("submodule","update","--init")
    if os.path.exists(C_BUILDDIR):
        print("INFO : Found build directory: " + str(C_BUILDDIR))
        print("INFO : This means the RP2040 firmware has probably been built before.")
        try:
            print("INFO : Removing directory in preparation for building clean: " + str(C_BUILDDIR))
            shutil.rmtree(C_BUILDDIR)
        except:
            print("INFO : Problem removing directory at: " + str(C_BUILDDIR))
    if not os.path.exists(C_BUILDDIR):
        print("INFO : Did not find build directory: " + str(C_BUILDDIR))
        print("INFO : This is expected for a clean build.")
        try:
            print("INFO : Creating build directory at: " + str(C_BUILDDIR))
            os.mkdir(C_BUILDDIR)
        except:
            print("INFO : build_rp2040_firmware: Problem creating build directory at: " + str(C_BUILDDIR))
    os.chdir(C_BUILDDIR)
    cmake("-DPICO_BOARD=beepberry","-DCMAKE_BUILD_TYPE=Debug","..")
    os.chdir(C_BUILDDIR)  # just to be sure cmake hasn't changed current working dir on us
    make()
    try:
        print("INFO : Copying RP2040 firmware to: " + str(os.path.join(SRC_DIR,"rp2040-firmware.uf2")))
        shutil.copy(os.path.join(C_BUILDDIR,"app/i2c_puppet.uf2"), os.path.join(SRC_DIR,"rp2040-firmware.uf2"))
    except:
        print("ERROR: Problem copying built RP2040 firmware UF2 file to: " + str(os.path.join(SRC_DIR,"rp2040-firmware.uf2")))
    
    instructions = ["RP2040 firmware has been built and copied to:\n",
                    os.path.join(SRC_DIR,"rp2040-firmware.uf2"),
                    "It will need to be manually installed as follows:\n",
                    "  * Copy this UF2 file to a host computer.\n",
                    "  * Shut down the beepy, then turn its power switch off, to the left.\n",
                    "  * Connect beepy to host computer using USB port on bottom of beepy.\n",
                    "  * While holding END CALL (rightmost button on 'touchpad strip'),\n",
                    "    turn beepy power on.\n",
                    "  * In bootloader mode, RGB LED is lit.\n",
                    "  * RP2040 will mount as a disk on your computer.\n",
                    "  * Drag UF2 file onto the disk. beepy will update and reboot.\n"]
    try:
        print("INFO : Writing RP2040 flashing instructions to: " + str(os.path.join(SRC_DIR,"rp2040-instructions.txt")))
        with open(os.path.join(SRC_DIR,"rp2040-instructions.txt"),mode='w') as f:
            f.seek(0)     # to be 100% sure
            f.truncate()  # to be 100% sure
            for instruction in instructions:
                f.write(instruction)
    except:
        print("INFO : Problem writing to : " + str(os.path.join(SRC_DIR,"rp2040-instructions.txt")))

# Install Sharp DRM driver
# ------------------------
def install_sharp_drm_driver():
    os.chdir(os.path.join(SCRIPT_DIR))
    sudo_python(os.path.join(SCRIPT_DIR,"install-sharp-driver.py"))

# Install keyboard driver
# -----------------------
def install_keyboard_driver():
    print("INFO : Installing i2c-tools for keyboard diagnostics.")
    sudo_apt("install","-y","i2c-tools")
    print("INFO : Installing keyboard driver.")
    DRIVERDIR = os.path.join(SRC_DIR,"bbqX0kbd_driver")
    os.chdir(DRIVERDIR)
    # installer.sh doesn't accept arguments when used with subprocess, so we have to use os.system
    command_to_run = DRIVERDIR + '/installer.sh --BBQX0KBD_TYPE BBQ20KBD_PMOD --BBQ20KBD_TRACKPAD_USE BBQ20KBD_TRACKPAD_AS_MOUSE --BBQX0KBD_INT BBQX0KBD_USE_INT --BBQX0KBD_INT_PIN 4'
    os.system(command_to_run)

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
    print("INFO : Installing dependencies to build Sharp kernel module.")
    sudo_apt("install","-y","raspberrypi-kernel-headers")
    print("INFO : Installing dependencies for DirectFB2-media image provider library.")
    print("INFO : These allow specific image formats to be decoded: PNG, JPG, etc.")
    sudo_apt("install","-y","libavcodec-dev","libavformat-dev","libavutil-dev","libswscale-dev","libimlib2-dev","libopenexr-dev","libtiff-dev","libwebp-dev")
    print("INFO : Installing ALSA development headers. This is a FusionSound dependency.")
    sudo_apt("install","-y","libasound2-dev")
    print("INFO : Installing optional dependencies for DirectFB.")
    sudo_apt("install","-y","libmad0-dev","libvorbis-dev")
    print("INFO : Installing updated kernel.")
    sudo_apt("install","-y","raspberrypi-kernel")

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
    print("INFO : download_sources: Starting. Only deleted folders will be replaced.")
    print("INFO : download_sources: If a source folder already exists, it will be untouched.")
    print("INFO : download_sources: To redownload source or build clean, delete its directory.")
    print("INFO : download_sources: ----------------------------------------------------------")
    download_source("https://github.com/ardangelo/beepberry-rp2040","beepberry-rp2040","Beepy RP2040 firmware")
    # TODO: replace SQFMI kbd driver with ardangelo fork for integration with display/rp2040 drivers
    #download_source("https://github.com/ardangelo/beepberry-keyboard-driver","beepberry-keyboard-driver","BBQ20 keyboard driver")
    download_source("https://github.com/sqfmi/bbqX0kbd_driver","bbqX0kbd_driver","BBQ20 keyboard driver")
    download_source("https://github.com/ardangelo/sharp-drm-driver","sharp-drm-driver","Sharp Memory LCD DRM framebuffer driver")
    download_source("https://github.com/deniskropp/flux","flux","Flux library for DirectFB2")
    download_source("https://github.com/directfb2/FusionSound2", "FusionSound2", "FusionSound2 library for DirectFB2 - optional")
    download_source("https://github.com/directfb2/DirectFB2", "DirectFB2", "DirectFB2 library")
    download_source("https://github.com/directfb2/directfb-csource", "directfb-csource", "/DirectFB2 C source")
    download_source("https://github.com/directfb2/DirectFB-examples", "DirectFB-examples", "DirectFB2 examples")
    download_source("https://github.com/directfb2/DirectFB2-media", "DirectFB2-media", "DirectFB2 image handlers: JPG, PNG, etc.")
    download_source("https://github.com/directfb2/DirectFB-media-samples", "DirectFB-media-samples", "DirectFB media samples")
    download_source("https://github.com/directfb2/LiTE", "LiTE", "LiTE GUI library for DirectFB2")
    download_source("https://github.com/directfb2/LiTE-examples", "LiTE-examples", "LiTE GUI examples")
    download_source("https://github.com/directfb2/DFBTerm", "DFBTerm", "DFBTerm terminal emulator")

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
        meson("configure",DFB_BUILDDIR,"-Dmmx=false","-Dneon=false","-Dmulti=true")
    except:
        print("ERROR: build_directfb2: Configure phase had an error.")
    print("INFO : build_directfb2: Compiling DirectFB2...")
    try:
        meson("compile","-C",DFB_BUILDDIR)
    except:
        print("ERROR: build_directfb2: DirectFB2 build had problems.")
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

# End-of-build information for the user
# -------------------------------------
def finish():
    print("INFO : -------------------------------------------------------")
    print("INFO : Build process complete. Reboot before testing examples.")
    print("INFO : -------------------------------------------------------")
    print("INFO : How to flash new RP2040 firmware:")
    print("INFO : " + str(os.path.join(SRC_DIR,"rp2040-instructions.txt")))
    print("INFO : RP2040 firmware file should be here:")
    print("INFO : " + str(os.path.join(SRC_DIR,"rp2040-firmware.uf2")))
    print("INFO : ------------------------------------------")


# MAIN ====================================================
# =========================================================
def main():
    print("INFO : Current working directory for build-sdk.py: " + SCRIPT_DIR)
    print("INFO : SDK sources directory: " + SRC_DIR)
 
    # 1ST HALF (getting a working beepy, with text console on the LCD, and keyboard support)
    # ------------------------------------------------------------------------------------------
    configure_raspi_basics()
    create_src_dir()
    download_sources()
    install_apt_dependencies()
    build_rp2040_firmware()
    install_sharp_drm_driver()
    install_keyboard_driver()  # TODO: Non-breaking: appends to files in /boot when run repeatedly
    # TODO : check if sharp/kbd modules are, or can be, loaded - did we buildinstall correctly?

    # 2ND HALF (Installing DirectFB onto the beepy)
    # -------------------------------------------------
    install_ninja()
    install_meson()
    buildinstall_fluxcomp()  # needs libdirect for debug output - build twice, once after directfb?
    build_directfb2()
    install_directfb2()
    buildinstall_fusionsound2()  # needs libdirect from directfb2 in order to build
    buildinstall_directfb_csource()
    buildinstall_lite()
    patch_lite_monowidgets()  # TODO: improve widget set; wincursor.png not masked
    buildinstall_directfb2_media()
    buildinstall_directfb_media_samples()
    buildinstall_directfb_examples()
    buildinstall_lite_examples()
    buildinstall_dfbterm()
    finish()

    #sudo_reboot()  # to activate keyboard and Memory LCD

if __name__=="__main__":
    main()
