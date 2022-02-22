import numpy, math
from parameters import *
import matplotlib.pyplot as plt

pi = numpy.pi


def getdelay(dist: float):
    # za Yang_Ke_PhD 4.2.3
    return dist*ref_ind/3/10**8        # d*nr/c

#for debugging
def pathlossforfreq(dist: float, freq_thz: float):
    ref_ind = 0.0385714 * freq_thz ** 2 - 0.212262 * freq_thz + 2.1467
    lam = 3 / (freq_thz * 10 ** 4)  # h0 = c/f
    h = lam / ref_ind
    pl_spread = (4 * pi * dist / h) ** 2
    pl_absorpsion = numpy.e ** ((12551 * freq_thz + 8785.71) * dist)
    total_pl_db = 10 * math.log(pl_spread, 10) + 10 * math.log(pl_absorpsion, 10)

    return total_pl_db

# to be removed
def pathloss(dist: float):
    h = lam/ref_ind
    pl_spread = (4*pi*dist/h)**2
    pl_absorpsion = numpy.e**((12551*freq_thz+8785.71)*dist)
    total_pl_db = 10*math.log(pl_spread,10) + 10*math.log(pl_absorpsion,10)
    """
    P Ltotal[dB] = (4*π*d/λg)^2 + e^(α(f)*d)
λg = λo/nr stands for the wavelength in medium with free-space wavelength
λo, and d is the travelling distance of the wave.
    :return:
    """
    return total_pl_db

if __name__ == "__main__":
    print((getdelay(10**-3)*10**12),"picosekund")
    print(pathloss(10**-3))

    #histogram generation
    fthz = [x for x in numpy.arange(0.1, 2.001, 0.05)]
    dist = numpy.arange(0.0001, 2.01*10**-3, 10**-4)
    dist = dist[::-1]
    results = [[pathlossforfreq(d, f) for f in fthz] for d in dist]
    fig, ax = plt.subplots()
    im = ax.imshow(results, 'hot',interpolation='none')
    ax.set_xticks(range(len(fthz)),labels=[round(x,4) for x in fthz])
    ax.set_yticks(range(len(dist)),labels=[round(x,4) for x in dist])
    cbar = ax.figure.colorbar(im, ax=ax)
    plt.show()

