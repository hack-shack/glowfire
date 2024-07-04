""" rammac: Read RAM usage on macOS """

import subprocess

def rammac():
    """ Return the amount of consumed memory as a percentage. """
    pagesize_proc = subprocess.run(['pagesize'],stdout=subprocess.PIPE)  # in bytes
    pagesize = int(pagesize_proc.stdout)
    #print('pagesize: ' + str(pagesize))

    sysctl_proc  = subprocess.run(['sysctl','-a'],stdout=subprocess.PIPE)
    sysctl_output = str(sysctl_proc.stdout)
    sysctl_output = sysctl_output.split('\\n')
    for line in sysctl_output: 
        if 'hw.memsize:' in line:
            memsize = int(line.lstrip('hw.memsize: '))
            #print('memsize : ' + str(memsize))

    vmstat_proc = subprocess.run(['vm_stat'],stdout=subprocess.PIPE)
    vmstat_output = str(vmstat_proc.stdout)
    vmstat_output = vmstat_output.split('\\n')
    for line in vmstat_output:
        if 'wired' in line:
            wiredtmp = line.lstrip('Pages wired down: ')
            wiredtmp = wiredtmp.rstrip('.')
            wiredmem = int(wiredtmp) * int(pagesize)
            #print('wiredmem: ' + str(wiredmem))

    percentage = round((wiredmem / memsize) * 100)
    #print('percentage wired: ' + str(percentage))
    return percentage
