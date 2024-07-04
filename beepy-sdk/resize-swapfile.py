#!/usr/bin/python

"""
Copyright (c) 2023 Asa Durkee. MIT License.
Resizes swapfile on Raspberry Pi.
"""

import os
import re
import subprocess

def sudo_bash(*args):
    return subprocess.check_call(['sudo','bash'] + list(args))

def resize_swapfile(size_in_megabytes):
    sudo_bash("dphys-swapfile","swapoff")
    with open ("/etc/dphys-swapfile", "r+") as f:
        new_f = f.readlines()
        f.seek(0)
        p = re.compile("^CONF_SWAPSIZE=(\d+)$")
        for line in new_f:
            if not re.findall(p,line):
                f.write(line)
            if re.findall(p,line):
                match = re.findall(p,line)
                print("INFO : Found swapsize configured to " + match[0] + "MB." )
                print("INFO : Resizing swap to " + str(size_in_megabytes) + "MB.")
                f.write("CONF_SWAPSIZE=" + str(size_in_megabytes) + "\n")
        f.truncate()
    sudo_bash("dphys-swapfile","setup")
    sudo_bash("dphys-swapfile","swapon")

def main():
    resize_swapfile(1000)


# ENTRY POINT
# =========================================================
uid = os.geteuid()
print("INFO : UID is: " + str(uid))
if os.geteuid() == 0:
    print("INFO : Running as root user. This is expected behavior.")
if os.geteuid() != 0:
    exit("ERROR: This script must be run with sudo, or as the root user.")

if __name__=="__main__":
    main()
