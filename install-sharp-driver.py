#!/usr/bin/python
"""
Copyright (c) 2023 Asa Durkee. MIT License.

Installs Sharp Memory LCD driver.
"""
import os
import re
import shutil
import subprocess
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR_NAME = "src"  # what you'd like to call the sources directory
SRC_DIR = os.path.join(SCRIPT_DIR, SRC_DIR_NAME)

def dtc(*args):
    return subprocess.check_call(['dtc'] + list(args))

def make(*args):
    return subprocess.check_call(['make'] + list(args))

def compile_devicetree_sharp(source_dir):
    os.chdir(source_dir)
    make()
    make("modules_install")
    dtc('-@','-I','dts','-O','dtb','-o','sharp.dtbo','sharp.dts')
    os.chdir(source_dir)
    try:
        shutil.copyfile(os.path.join(source_dir,"sharp.dtbo"),os.path.join("/boot/overlays/sharp.dtbo"))
    except:
        print("ERROR: compile_devicetree_sharp: Error copying sharp.dtbo into /boot/overlays/.")
        raise

def register_kernel_module(module_name):
    print("INFO : -------------------------------------------------------------")
    print("INFO : register_kernel_module: Started.")
    if module_name == None:
        print("ERROR: register_kernel_module: Need to specify a module name to register.")
        return 1
    print("INFO : register_kernel_module: Opening /etc/modules to register module: " + module_name)
    print("INFO : register_kernel_module: Cleaning /etc/modules of all references to module: " + module_name)
    with open(os.path.join("/etc/modules"),"r+") as f:
        matches = 0
        new_f = f.readlines()
        f.seek(0)
        for line in new_f:
            if str(module_name) not in line:
                f.write(line)
            if str(module_name + "\n") in line:
                matches += 1
        f.truncate()
        if matches == 1:
            print("INFO : register_kernel_module: Removed 1 line matching: " + module_name)
        else:
            print("INFO : register_kernel_module: Removed " + str(matches) + " lines matching: " + module_name)
    with open(os.path.join("/etc/modules"),"a")as f:
        f.write(str(module_name + "\n"))
    print("INFO : register_kernel_module: Added to /etc/modules: " + module_name)
    print("INFO : -------------------------------------------------------------")
    return 0

def configure_boot_options():
    """/boot/config.txt: ADD 'framebuffer_width=400\nframebuffer_height=240\ndtoverlay=sharp'"""
    lines_to_add = ["framebuffer_width=400","framebuffer_height=240","dtoverlay=sharp"]
    for line_to_add in lines_to_add:
        with open("/boot/config.txt","r+") as f:
            new_f = f.readlines()
            f.seek(0)
            p = re.compile("^" + line_to_add)
            for line in new_f:
                if not re.findall(p,line):
                    f.write(line)
                if re.findall(p,line):
                    print("INFO : configure_boot_options: Found reference, and deleting : " + line_to_add)
            f.truncate()
    for line_to_add in lines_to_add:
        with open("/boot/config.txt","a") as f:
            f.write(line_to_add + "\n")

def configure_boot_cmdline():
    """OPEN /boot/cmdline.txt: APPEND 'fbcon=map:10 fbcon=font:VGA8x8/'"""
    args_to_add = ["fbcon=map:10",
                   "fbcon=font:VGA8x8"]

    print("INFO : -----------------------------------------------------------------")
    print("INFO : configure_boot_cmdline: Opening /boot/cmdline.txt for inspection.")
    with open("/boot/cmdline.txt","r+") as f:
        linecount = 0
        args = []
        args_found = 0

        for line in f:
            args = line.split()
            linecount += 1
        print("INFO : configure_boot_cmdline: linecount: " + str(linecount))
        # TODO: error/exception handling for this file - is it present, what are its expected defaults, etc.
        if linecount == 1:
            print("INFO : configure_boot_cmdline: linecount is exactly 1 line. This is expected.")
        if linecount != 1:
            print("WARN : configure_boot_cmdline: linecount is not 1. To fix this, ensure /boot/cmdline.txt is present, and only is a single line of text, no NL or CR characters, etc.")
        for arg in args:
            print ("INFO : found argument in /boot/cmdline.txt: " + str(arg))
            if arg in args_to_add:
                print("INFO : configure_boot_cmdline: /boot/cmdline.txt already has argument: " + str(arg))
                args_found += 1
        if args_found != len(args_to_add):
            print("WARN : /boot/cmdline.txt is missing arguments.")
            print("INFO : Preparing a combined list of its arguments, plus the ones to add.")
            for arg in args_to_add:
                args.append(arg)
            args_to_write = ""
            for arg in args:
                args_to_write += " " + arg
            args_to_write = args_to_write.lstrip()
            print("INFO : Writing new argument list: " + args_to_write)
            f.seek(0)
            f.truncate()
            f.write(args_to_write)
        if args_found == len(args_to_add):
            print("INFO : /boot/cmdline.txt matches every argument. This is expected.")
    




# MAIN
# =========================================================
uid = os.geteuid()
print("INFO : UID is: " + str(uid))
if os.geteuid() == 0:
    print("INFO : Script is running as root. This is expected behavior.")
if os.geteuid() != 0:
        exit("ERROR: You need to run this script with sudo, or as the root user.")



try:
    print(os.path.join(SRC_DIR,"sharp-drm-driver/"))
    compile_devicetree_sharp(os.path.join(SRC_DIR,"sharp-drm-driver/"))
except:
    error("ERROR: compile_devicetree_sharp returned an error.")
    raise

try:
    register_kernel_module('sharp')
except:
    error("ERROR: register_kernel_module returned an error.")
    raise

try:
    configure_boot_options()
except:
    error("ERROR: configure_boot_options returned an error.")
    raise

try:
    configure_boot_cmdline()
except:
    error("ERROR: configure_boot_cmdline returned an error.")
    raise