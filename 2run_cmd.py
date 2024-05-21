import os
import subprocess
import time
import multiprocessing

def os_quiet(cmd):
    try:
        os.system(cmd)
    except:
        pass


with open('cmd.txt') as f:
    lines = f.readlines()
    # Remove newline characters from each line
    lines = [line.rstrip('\n') for line in lines]

cmd_list = lines

# set up parallel processing
#print(cmd_list[:10])
nCPU = len(cmd_list)
if nCPU > 10: nCPU = 10 # number of cores to use
pool = multiprocessing.Pool(nCPU) # Set up multi-processing
t0 = time.time() # start time


pool.map(os_quiet, cmd_list) # run multiple commands at once
elapsed_time = time.time() - t0 # end time
print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

