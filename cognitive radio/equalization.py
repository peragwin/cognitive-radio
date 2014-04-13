from __future__ import division

import numpy as np
import scipy.signal as sp

import matplotlib.pyplot as plt

from paudio import streamAndRecord
from syncronization import genSyncPulse







if __name__ == '__main__':

    chrp = genSyncPulse(f0 = 0, f1 = 22000, t1 = 1, method='linear')

    rec_chrp = streamAndRecord(chrp,2)


   # h = sp.firwin(48, 4400, nyq = 22050)
   # rec_chrp = sp.fftconvolve(rec_chrp, h)
   # rec_chrp = rec_chrp[::5]

    dft = np.log(np.abs(np.fft.fftshift(np.fft.fft(rec_chrp))))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(range(-dft.size//2, dft.size//2), dft)
    fig.show()