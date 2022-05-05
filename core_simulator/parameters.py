import random
"""
File with parameters used in simulation

1 step = 1 ms
"""
freq_thz = 1  # in THZ restriction of 0.2 to 2 THz
bandwidht_thz = [0.5, 1.5]
freq = freq_thz*10**12
ref_ind = 0.0385714 * freq_thz ** 2 - 0.212262 * freq_thz + 2.1467
lam = 3/(freq_thz*10**4)    # h0 = c/f

# From Understanding the Applicability of THz Flow-Guided Nano-Networks for Medical Applications
throuhput_mbps = 1000000
range_mm = 1  #mm
battery_capacity = 64 #max nr. '1' bits to send in a second (limited by battery)
vein_diameter_mm = 6
velocity_cms = 11 #cm/s

recharge_period = 1000 #ms

rec_limit = 2
use_drihmac = True
DRIH_data_payload_limit=20 #bytes
buffer_size = 1 #in packets
rtr_interval=500

#data generation settings
payload_gen_function = random.randint
data_size_limits = [1, DRIH_data_payload_limit]     #in bytes
time_gen_function = random.randint
time_gen_limits = [500, 3000]

global all_nodes
all_nodes = []