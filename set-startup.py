#!/usr/bin/python
# (c) 2023 Asa Durkee. MIT License.

import os
import platform
import subprocess

"""
Configure system to autostart snakewm at login

Reference for ardangelo keyboard firmware:
https://github.com/ardangelo/beepberry-keyboard-driver/blob/main/README.md#module-parameters
"""

HOMEUSER = os.getlogin()
HOME_DIR = os.path.join('/home',HOMEUSER)
WORK_DIR = os.path.join(HOME_DIR,'glowfire')
PYTHONPATH = os.path.join(HOME_DIR,'glowfire/snakewm/data/lib')
print('INFO : PYTHONPATH = ' + PYTHONPATH)
WMPATH = os.path.join(HOME_DIR,'glowfire/snakewm/wm.py')


def systemctl(*args):
    """ Shell command for systemctl, followed by a list of arguments. """
    return subprocess.check_call(['systemctl'] + list(args))


def create_snakewm_service():
    print('INFO : Creating snakewm service in systemd as a unit file.')
    lines_to_write = \
['[Unit]',
'Description=snakewm',
'Documentation=https://github.com/hack-shack/glowfire',
'After=multi-user.target',
'\n[Service]',
'Type=simple',
'Environment="PYTHONPATH=' + PYTHONPATH + '" "HOMEUSER=' + HOMEUSER + '"',
'ExecStart=/usr/bin/python ' + WMPATH + ' --dfb:vt-num=1 --dfb:graphics-vt',
'ExecStartPost=/usr/bin/sh -c \'echo always | sudo tee /sys/module/beepy_kbd/parameters/touch_act\'',
'ExecStartPost=/usr/bin/sh -c \'echo mouse | sudo tee /sys/module/beepy_kbd/parameters/touch_as\'',
'ExecStartPost=/usr/bin/sh -c \'echo 0 | sudo tee /sys/firmware/beepy/keyboard_backlight\'',
'ExecStartPost=/usr/bin/sh -c \'echo 0 | sudo tee /sys/class/leds/ACT/brightness\'',
'WorkingDirectory=' + WORK_DIR + '',
'StandardOutput=journal+console',
'Restart=always\nRestartSec=5s\n\n[Install]\nWantedBy=multi-user.target']

    systemd_service_file = os.path.join('/etc/systemd/system/snakewm.service')
    print('INFO : snakewm service file = ' + systemd_service_file)
    print('INFO : The system will appear to hang while the service is created.')
    if not os.path.exists(systemd_service_file):
        os.mknod(systemd_service_file)
    with open(systemd_service_file,'r+') as f:
        f.seek(0)
        f.truncate()
        for line in lines_to_write:
            f.write(line + '\n')

def enable_snakewm_service():
    systemctl('daemon-reload')
    systemctl('enable','snakewm.service')
        
def main():
    if os.getuid() != 0:
        print('ERROR : This script is not running as root. Re-run as root.')
        exit()
    print('INFO : Configuring system to autostart snakewm at login.\n'+56*'-')
    create_snakewm_service()
    enable_snakewm_service()
    print('INFO : snakewm automatically restarts. Use "sudo systemctl disable snakewm.service" to turn it off.')

if __name__ == "__main__":
    main()
