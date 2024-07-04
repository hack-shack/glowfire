#!/usr/bin/python
import os

ALSA_CFGFILE = os.path.join('/etc/asound.conf')

def write_alsa_cfgfile(file):
    lines_to_add = (
        'pcm.bt-headphones {\n'
        '    type bluealsa\n'
        '    device xx:xx:xx:xx:xx:xx\n'  # use your device's mac address
        '    profile a2dp\n'
        '}\n'
        'pcm.usbdac-headphones {\n'
        '    type hw\n'
        '    card 1\n'
        '}\n'
        'pcm.usbdac-mic {\n'
        '    type front\n'
        '    card 1\n'
        '}\n'
    )

    if not os.path.exists(file):
        try:
            open(file, 'w').close()
        except PermissionError as error:
            exit('ERROR: ' + str(error))

    try:
        with open(file,'r+') as f:
                f.seek(0)
                f.truncate()
                for line in lines_to_add:
                        f.write(line)
    except PermissionError as error:
        exit('ERROR: ' + str(error))

def main():
    if not os.getuid() == 0: print('-' * 40 + \
    '\n\nINFO :\tNot running as root.\n\tMay fail to write configuration.\n\n' + '-' * 40)
    write_alsa_cfgfile(ALSA_CFGFILE)

main()