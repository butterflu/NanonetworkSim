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
battery_capacity = 1400 #max nr. '1' bits to send in a second (limited by battery)
vein_diameter_mm = 6
velocity_cms = 11 #cm/s
recharge_period = 1 #s

rec_limit = 2
use_drihmac = True