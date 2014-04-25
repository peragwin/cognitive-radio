from __future__ import division

import numpy as np
import scipy.signal as sp

from helpers import *
#import matplotlib.pyplot as plt

f0 = 440.0
f1 = 4200.0
fs = 44100.0
t1 = 0.05
t = np.r_[0:t1:1.0/fs]

SYNC_PULSE = sp.chirp(t,f0,t1,f1, method='quadratic')

def genPreamble(data = None, mod_func = None, sync_pulse = SYNC_PULSE):
    if data:
        mod_data = mod_func(data)
        return np.append(sync_pulse, mod_data)

    else:
        return sync_pulse

def genSyncPulse(f0 = 440.0, f1 = 4200.0, fs = 44100.0, t1 = 0.05, method='quadratic'):
    t = np.r_[0:t1:1.0/fs]
    return sp.chirp(t,f0,t1,f1, method=method)

def genSyncPulse2(fc= 1800, fd = 600, fs = 44100.0, t = .05):
    num_samples = int(t * fs)
    pulse = np.ones(num_samples)
    for i in range(num_samples):
        if (np.mod(int(i/100),2)==0):
            pulse[i] = -1

    ph = 2*np.pi*np.cumsum(fc + pulse*fd)/fs
    pulse = np.sin(ph)
    return pulse


def findSignal(signal, thresh = .9, sync_pulse = SYNC_PULSE):
    
    corr = sp.fftconvolve(signal, sync_pulse[::-1],mode='full')

   # fig = plt.figure()
   # ax = fig.add_subplot(111)
   # ax.plot(range(corr.size), corr)
   # fig.show()


    peaks = findPeaks(np.abs(corr), thresh, sync_pulse.size)
   # print peaks

    if len(peaks) < 1:
        print "error: couldn't find any sync pulses"
        return signal
    elif peaks.size < 2:
        print 'error: could only find 1 sync pulse'
        return signal
    else:
        return signal[peaks[0]:peaks[peaks.size-1]]

def findPeaks(data,threshold, width=1):
    
    max_val = np.max(data)

    thresh = threshold * max_val

    lookat = np.greater_equal(data, thresh)

    peaks = []

    start_idx = -1
    for i,val in enumerate(lookat):
        if val and start_idx < 0:
            start_idx = i
        if start_idx >= 0 and not val:
            if i >= start_idx + width:
                peak_idx = start_idx + np.argmax(data[start_idx:i])
                peaks = np.append(peaks,peak_idx)
                start_idx = -1
            

    return peaks

def findSync(signal, thresh = .95, sync_pulse = SYNC_PULSE):

    mean = np.mean(np.abs(signal))
    sync_en = np.sum(np.abs(sync_pulse))

    corr = np.abs( sp.fftconvolve(signal, sync_pulse[::-1], mode='full') )
    corrmax = np.max(corr)
   
    if corrmax > sync_en * mean / 2.5:   # threshold for detection
        return np.argmax(corr)

#        #myplot(corr)
#        peaks = findPeaks(corr, thresh)
#        if peaks != []:
#        #myplot(corr)
#         #   print amplitude, mean, corrmax, sync_en
#        #if peaks.size == 1:
#            return peaks[0]
    
    return -1

if __name__ == '__main__' :

    cos = np.cos(2*np.pi*10*np.r_[0:1:.001])
    
    peaks = findPeaks(cos,.9, 10)

    print peaks