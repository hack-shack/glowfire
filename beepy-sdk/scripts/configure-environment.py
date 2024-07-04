#!/usr/bin/python
# (c) 2023 Asa Durkee. MIT License.

import os
import platform
import subprocess

"""
Configure system environment: DirectFB2, SDL2, etc.
Create configuration files with Memory LCD settings.
"""

def configure_directfb2_environment():
    # The defaults in directfbrc can be overridden at runtime
    # by appending -dfb:system=fbdev -dfb:no-cursor, etc.
    # to the command line when you launch your program.
    # e.g. python main.py -dfb:system=fbdev -dfb:fbdev:/dev/fb1
    # Hide DirectFB cursor: no-cursor
    directfbrc='/usr/local/etc/directfbrc'
    lines_to_write="""\
system=fbdev    # Use framebuffer subsystem
fbdev=/dev/fb1  # Sharp Memory LCD
graphics-vt     # Use graphics VT (hide tty console text)
dma             # Enable DMA acceleration, if supported by driver 
no-cursor       # Disable DirectFB2 mouse cursor
#debug          # Display debug messages
#linux-input-grab  # Takes Linux Input devices for its exclusive use (blocks others)
#linux-input-devices=/dev/<our-device-name>  # Placeholder for possible linux uinput.h emulated input device
#    URL: https://www.kernel.org/doc/html/v4.12/input/uinput.html
#linux-input-touch-abs  # Experimental. Possible touchpad-to-DFB-cursor synchronization mechanism.
"""
    if not os.path.exists(directfbrc):
        os.mknod(directfbrc)
    with open (directfbrc,'r+') as f:
        f.seek(0)
        f.truncate()
        for line in lines_to_write:
            f.write(line)
    
    library_conf_file = '/etc/ld.so.conf.d/locallibs.conf'
    if platform.architecture()[0] == '64bit':
        library_path_to_add = '/usr/local/lib/aarch64-linux-gnu/'
    if platform.architecture()[0] == '32bit':
        library_path_to_add = '/usr/local/lib/arm-linux-gnueabihf/'
    if not os.path.exists(library_conf_file):
        os.mknod(library_conf_file)
    
    with open (library_conf_file,'r+') as f:
        f.seek(0)
        f.truncate()
        f.write(library_path_to_add)
    
    # Update the system with the newly-added libraries.
    print('DEBUG: Running ldconfig to update the system with newly added libraries.')
    subprocess.run(['sudo','ldconfig'])

def configure_sdl2_environment():
    """ Configure SDL2 to use DirectFB2. """
    # See https://www.libsdl.org/release/SDL-1.2.15/docs/html/sdlenvvars.html
    profile_script      = 'environment'   
    profile_script_path = os.path.join('/etc',profile_script)
    lines_to_write = """\
#export SDL_DIRECTFB_LINUX_INPUT=1  # When set to 1, enable use of Linux input devices.
#export SDL_DIRECTFB_X11_CHECK=0  # Disable use of X11 backend when DISPLAY variable is found.
#export SDL_DIRECTFB_YUV_DIRECT=1  # Use hardware accelerated YUV overlay for the first YUV texture.
#export SDL_DIRECTFB_WM=0  # If set to 1, enables basic window manager with window borders.
#export SDL_MOUSE_RELATIVE=1  # If set to 0, do not use mouse relative mode in X11.
#export SDL_MOUSEDEV=<placeholder for new mouse>
#export SDL_MOUSEDRV=<for the linux fbcon driver; if set to ELO, use ELO TS>
#export SDL_NOMOUSE   # if set, the linux fbcon driver will not use a mouse at all
#export SDL_DEBUG     # If set, every call to SDL_SetError() prints to sderr
    """
    if not os.path.exists(profile_script_path):
        os.mknod(profile_script_path)
    with open(profile_script_path,'r+') as f:
        f.seek(0)
        f.truncate()
        for line in lines_to_write:
            f.write(line)

def main():
    if os.getuid() != 0:
        exit('ERROR: This script must be run as root.')
    print('INFO : Configuring environment for DirectFB2.')
    configure_directfb2_environment()
    print('INFO : Configuring environment for SDL2.')
    configure_sdl2_environment()

if __name__ == "__main__":
    main()
