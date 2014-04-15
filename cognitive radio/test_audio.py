from __future__ import division

import numpy as np
import scipy.signal as sp
#import Queue
#import threading
#import pyaudio
#import multiprocessing

import time

from paudio import *

from QAM import *
from FSK import *
from syncronization import *

data = np.random.randint(0,32,size = 40)

fs = 48000.0

signal = modulateFSK(data, 440.0, 4200.0, 32, fs, .04)

signal = np.append(genSyncPulse(),signal)
signal = np.append(signal, genSyncPulse())

signal = np.append(np.zeros(100), signal)
signal = np.append(signal, np.zeros(100))

#signal += np.random.normal(size=signal.size)
signalin = streamAndRecord(signal, 6, fs)

startTime = time.time()

h = sp.firwin(24,4400, nyq = fs/2)
signal = sp.fftconvolve(signalin, h)
signal = signal[::5]


cropped = findSignal(signal,sync_pulse=genSyncPulse(fs=fs/5))

rec_data = demodulateFSK(cropped, 440.0, 4200.0, 32, fs/5, 0.04)


endTime = time.time()

print endTime - startTime

for i in range(min(data.size,rec_data.size)):
    if (data[i] != rec_data[i]):
        print i, data[i], rec_data[i]
try:
    disp = np.equal(rec_data[:data.size],data)
    print sum(disp)/disp.size
except:
    print "lost some symbols!"

#print disp 

#print rec_data

