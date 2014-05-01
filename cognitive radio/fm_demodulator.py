from __future__ import division

import numpy as np
import scipy.signal as sp




def fm_demodulate(data, cutoff, fs_in, fs_out, fc):

    h = sp.firwin(128, cutoff, nyq=fs_in/2)
    data = sp.fftconvolve(data, h)

    A = data[1:]
    B = data[:data.size-1]

    demod = np.real( np.angle( A * np.conj(B) ) / np.pi )

    decim = fs_in // fs_out

    h = sp.firwin(128, fc, nyq = fs_in/2)
    out = sp.fftconvolve(demod, h)[::decim]

    return out



class Demodulator:

    # implements a demodulator with continuous filtering via sp.lfilter

    zi1 = np.zeros(127)
    zi2 = np.zeros(127)

    def __init__(self, fs_in, fcut_in, fs_out, fcut_out):

        self.fs_in = fs_in
        self.fcut_in = fcut_in
        self.fs_out = fs_out
        self.fcut_out = fcut_out

    def fm_demodulate(self, data):#, cutoff, fs_in, fs_out, fc):

        h = sp.firwin(128, self.fcut_in, nyq=self.fs_in/2)
        data, self.zi1 = sp.lfilter(h, 1.0, data, zi=self.zi1)


        A = data[1:]
        B = data[:data.size-1]
        demod = np.real( np.angle( A * np.conj(B) ) / np.pi )


        h = sp.firwin(128, self.fcut_out, nyq = self.fs_in/2)
        data, self.zi2 = sp.lfilter(h, 1.0, demod, zi= self.zi2)


        decim = self.fs_in // self.fs_out
        out = data[::decim]

        return out