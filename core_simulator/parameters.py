import random

"""
File with parameters used in simulation

1 step = 0.1 ms
"""

# step settings in reference to 1s
step = 0.001
steps_in_s = int(1 / step)

freq_thz = 1  # in THZ restriction of 0.2 to 2 THz
bandwidth_thz = [0.5, 1.5]
freq = freq_thz * 10 ** 12
ref_ind = 0.0385714 * freq_thz ** 2 - 0.212262 * freq_thz + 2.1467
lam = 3 / (freq_thz * 10 ** 4)  # h0 = c/f

# From Understanding the Applicability of THz Flow-Guided Nano-Networks for Medical Applications
throughput_mbps = 1000000
throughput_mbpstep = throughput_mbps * step
range_mm = 1  # mm
battery_capacity = 64  # max nr. '1' bits to send in a second (limited by battery)

recharge_period_s = 1  # in seconds
recharge_period = recharge_period_s * steps_in_s  # ms

rec_limit = 2
use_drihmac = True
DRIH_data_payload_limit = 20  # bytes
buffer_size = 1  # in packets

rtr_interval_s = 0.5  # in seconds
rtr_interval = rtr_interval_s * steps_in_s

# data generation settings
payload_gen_function = random.randint
data_size_limits = [1, DRIH_data_payload_limit]  # in bytes
time_gen_function = random.randint
time_gen_limits_s = [0.5, 3]
time_gen_limits = [x * steps_in_s for x in time_gen_limits_s]

# mobility settings
velocity_cmps = 10  # cm/s
velocity_mmps = velocity_cmps * 10
vein_diameter_mm = 6

blood_volume_l = 5
nodes_num = 1000000
sim_time_s = 10

global all_nodes, moving_nodes
all_nodes = []
moving_nodes = []