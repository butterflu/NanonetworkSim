"""
File with parameters used in simulation
"""
freq_thz = 1  # in THZ restriction of 0.2 to 2 THz
bandwidht_thz = [0.5, 1.5]
freq = freq_thz*10**12
ref_ind = 0.0385714 * freq_thz ** 2 - 0.212262 * freq_thz + 2.1467
lam = 3/(freq_thz*10**4)    # h0 = c/f