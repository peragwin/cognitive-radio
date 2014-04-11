import numpy as np
import scipy.signal as signal

import Queue
import threading
import pyaudio
import multiprocessing

from paudio import *

from QAM import *


data = np.random.randint(0,16,size = 20)



signal = []

for d in data:
    signal = np.append(signal,modulateQAM(d,16,2000,44100,0.1))


def process(samples):
    return samples



# create an input output FIFO queues
Qout = Queue.Queue()
Qin = Queue.Queue()

# create a pyaudio object
p = pyaudio.PyAudio()

# initialize a playing thread.
t_play = threading.Thread(target = play_audio,   args = (Qout,   p, 44100  ))

t_rec = threading.Thread(target= record_audio, args = (Qin, p, 44100) )
# start the recording and playing threads#
t_rec.start()
t_play.start()

# record and play about 10 seconds of audio 430*1024/44100 = 9.98 s
Qout.put(signal)
output = []
for i in range(420/4):
    samples = Qin.get()
    output = np.append(output, samples)

print len(output)

Qout.put(output)


rec_data = demodulateQAM(output, 16,2000.0,44100.0, 0.1)

print np.equal(rec_data[:data.size],data)


