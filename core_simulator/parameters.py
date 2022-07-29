import random

import numpy

from stats import Stats

"""
File with parameters used in simulation

1 step = 0.1 ms
"""
# choose one
use_rih = True
use_ra = False
use_2way = False

# step settings in reference to 1s
step = 6.4 * 10 ** -5
steps_in_s = int(1 / step)

# main parameters
blood_volume_l = 5
nodes_num = 1000000
sim_time_s = 100
vein_diameter_mm = 2
range_mm = 1  # mm
sim_range = 1.1 * range_mm  # range in mm
battery_capacity = 128  # max nr. '1' bits to send in a second (limited by battery)
data_overhead = 8 # in bits
node_relevant_range = 2.1 * range_mm

# From Understanding the Applicability of THz Flow-Guided Nano-Networks for Medical Applications
throughput_bps = 1000000  # 1 Mbps
throughput_bpstep = throughput_bps * step

rxon_duration = numpy.floor(
    battery_capacity / 2 * 10 / step * 10 ** -5)  # amout of time spent reeiving (10**-5 is 1 us and is time of 1 bit)
startup_time = 6  # in seconds
approx_segment_size_s = 5
stats_timer = [0, steps_in_s * (sim_time_s + startup_time)]  # start, end

recharge_period_s = 1  # in seconds
recharge_period = recharge_period_s * steps_in_s  # ms

rec_limit = 1
buffer_size = 1  # in packets

rih_data_limit = 7  # bytes
rtr_interval_s = 0.005#60/steps_in_s  # in seconds
rtr_interval = rtr_interval_s * steps_in_s

ra_data_limit = 7  # bytes
ra_data_interval = int(1 * steps_in_s)  # in steps


tw_hello_interval = (steps_in_s/7)  # in steps
tw_data_limit = 3
tw_rtr_listening_time = 2  # in steps

# data generation settings
time_gen_function = random.randint
time_gen_limits_s = [0.5, 0.5]
time_gen_limits = [x * steps_in_s for x in time_gen_limits_s]

# binomial distribution
p = 0.5

# mobility settings
velocity_cmps = 10  # cm/s
velocity_mmps = velocity_cmps * 10

global all_nodes, simulated_nodes, stats, relevant_nodes
stats = Stats()
all_nodes = []          #list to store all nodes
simulated_nodes = []    # list to store all nodes that have chance to transmitt to ap
relevant_nodes = []     # list of all nodes that have influence on simulated nodes
