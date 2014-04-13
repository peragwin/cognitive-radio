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

#signal = []

#for d in data:
#    signal = np.append(signal,modulateQAM(d,16,2000,44100,0.1))

signal = modulateFSK(data, 440.0, 4200.0, 64, 44100.0, .02)

signal = np.append(genSyncPulse(),signal)
signal = np.append(signal, genSyncPulse())

signal = np.append(np.zeros(100), signal)
signal = np.append(signal, np.zeros(100))

#signal += np.random.normal(size=signal.size)
signalin = streamAndRecord(signal, 6)

startTime = time.time()

h = sp.firwin(24,4400, nyq = 22050)
signal = sp.fftconvolve(signalin, h)
signal = signal[::5]


cropped = findSignal(signal,sync_pulse=genSyncPulse(fs=44100/5))

rec_data = demodulateFSK(cropped, 440.0, 4200.0, 64, 44100.0/5, 0.02)


endTime = time.time()

print endTime - startTime

for i in range(min(data.size,rec_data.size)):
    if (data[i] != rec_data[i]):
        print i, data[i], rec_data[i]
try:
    disp = np.equal(rec_data[:data.size],data)
except:
    print "lost some symbols!"

#print disp
print sum(disp)/disp.size
#print rec_data

