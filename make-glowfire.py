#!/usr/bin/python3
# (c) 2023 Asa Durkee. MIT License.

""" Build beepy-sdk, then run set-startup.py. """

import os
from pathlib import Path
import platform
import subprocess

HOMEUSER = os.getlogin()
HOME_DIR = os.path.join('/home',HOMEUSER)
GLOW_DIR = os.path.join(HOME_DIR,'glowfire')
SDK_DIR  = os.path.join(GLOW_DIR,'beepy-sdk')
MUSIC_DIR = os.path.join(HOME_DIR,'music')

SONG1_URL = 'https://upload.wikimedia.org/wikipedia/commons/e/e2/Holst_The_Planets_Jupiter.ogg'
SONG1_LICENSE = """
Title: Jupiter, the Bringer of Jollity
Album: The Planets
Artist: Gustav Holst feat. U.S. Air Force Heritage of America Band
License: Public Domain
Wikimedia Commons URL: https://commons.wikimedia.org/wiki/File:Holst_The_Planets_Jupiter.ogg
"""

SONG2_URL = 'https://archive.org/download/Boccherini-Passacalle/Passacalle.ogg'
SONG2_LICENSE = """
Title: Passacalle
Album: La Musica Notturna delle Strade di Madrid
Artist: Luigi Boccherini feat. cellochap
License: Attribution - No Derivative Works 3.0 United States
Internet Archive URL: https://archive.org/details/Boccherini-Passacalle
"""

def download_song(url):
    """ Download a song. """
    print(__doc__)
    try:
        Path(MUSIC_DIR).mkdir()
    except:
        print('DEBUG: Music directory seems to exist. Skipping creation.')

    os.chdir(MUSIC_DIR)
    try:
        subprocess.check_call(['wget',url])
    except:
        print('ERROR: Unable to download music file from URL.')
        raise

def add_metadata_to_track():
    # Passacalle does not have tags, so we need to add them
    # search within file Passacalle.ogg
    # match its MD5 hash; if pre-fix, continue; if post-fix, quit; if none, pass
    # Add the metadata tags from SONG2_LICENSE above
    return NotImplementedError

def install_python_dependencies():
    """ Install Python media dependencies. """
    # Install tinytag, a metadata reader for media tracks.
    try:
        subprocess.check_call(['sudo','python3','-m','pip','install','tinytag','--break-system-packages'])
    except:
        raise

def print_firmware_instructions(instructions):
    """ Print instructions for flashing firmware. """
    print('\n\n')
    try:
        with open(instructions,'r') as file:
            for line in file:
                print(line,end='')
    except FileNotFoundError:
        print(f'ERROR: RP2040 instructions not found at {instructions}.')
    except IOError:
        print(f'ERROR: IOError when reading {instructions}.')

def python(*args):
    """ Shell command for python, followed by a list of arguments. """
    return subprocess.check_call(['python'] + list(args))

def sudo_python(*args):
    """ Shell command for sudo python, followed by a list of arguments. """
    return subprocess.check_call(['sudo','python'] + list(args))

def sudo_reboot(*args):
    """ Shell command to reboot the system. """
    return subprocess.check_call(['sudo','reboot'])

def main():
    os.chdir(SDK_DIR)
    python('build-sdk.py')
    # TODO: copy / paste message from build-sdk explaining how to flash firmware
    # currently this shows up as instructions text file in the build directory
    os.chdir(GLOW_DIR)
    sudo_python('set-startup.py')
    install_python_dependencies()
    download_song(SONG1_URL)
    download_song(SONG2_URL)
    print_firmware_instructions(os.path.join(SDK_DIR,'src/rp2040-instructions.txt'))
    sudo_reboot()

main()
