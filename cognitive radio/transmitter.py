from __future__ import division

import numpy as np
import scipy.signal as sp
import Queue
import threading
import pyaudio
import multiprocessing

from paudio import *

from QAM import *
from FSK import *
from syncronization import *

data = np.random.randint(0,16,size = 200)

#signal = []

#for d in data:
#    signal = np.append(signal,modulateQAM(d,16,2000,44100,0.1))
    
signal = modulateFSK(data, 440.0, 4200.0, 16, 44100.0, .1)

signal = np.append(genSyncPulse(),signal)
signal = np.append(signal, genSyncPulse())

signal = np.append(np.zeros(100), signal)
signal = np.append(signal, np.zeros(100))

## create an input output FIFO queues
#Qout = Queue.Queue()
#Qin = Queue.Queue()

## create a pyaudio object
#p = pyaudio.PyAudio()

## initialize a playing thread.
#t_play = threading.Thread(target = play_audio,   args = (Qout,   p, 44100  ))

#t_rec = threading.Thread(target= record_audio, args = (Qin, p, 44100) )
## start the recording and playing threads#
#t_rec.start()
#t_play.start()

# record and play about 10 seconds of audio 430*1024/44100 = 9.98 s
#Qout.put(signal)

#input = []

#for i in range(420/2):
#    samples = Qin.get()
#    input = np.append(input, samples)

#Qout.put(input)
signal += np.random.normal(size=signal.size)

cropped = findSignal(signal)

rec_data = demodulateFSK(cropped, 440.0, 4200.0, 16, 44100.0, 0.1)

for i in range(data.size):
    if (data[i] != rec_data[i]):
        print i, data[i], rec_data[i]

disp = np.equal(rec_data[:data.size],data)

#print disp
print sum(disp)/disp.size
#print rec_data

#p.terminate()
