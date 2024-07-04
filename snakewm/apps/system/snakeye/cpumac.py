""" cpumac: read CPU usage on macOS """

import multiprocessing
import re
import subprocess

def cpumac():
    """ Return the total processor usage as a percentage. """
    cpu_count = multiprocessing.cpu_count()
    cpu_proc = subprocess.run(['ps','-A','-o','%cpu'],stdout=subprocess.PIPE)
    cpu_usage_list = str(cpu_proc.stdout)
    cpu_usage_list = cpu_usage_list.split('\\n')
    total_cpu_usage = 0.0
    pattern = re.compile("^\\s+(\\d{0,2}.\d{0,2})")
    for each_process in cpu_usage_list:
        match = re.search(pattern,each_process)
        if match:
            total_cpu_usage += float(match[1])
    return round(total_cpu_usage / cpu_count)

cpumac()  # for running interactively
