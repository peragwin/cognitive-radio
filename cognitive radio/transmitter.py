import numpy as np
import scipy.signal as signal

import Queue
import threading
import pyaudio
import multiprocessing

from paudio import *

from QAM import *








data = np.random.randint(0,16,size = 100)


signal = []

for d in data:
    signal = np.append(signal,modulateQAM(d,16,2000,44100,0.05))


def process(samples):
    return samples

p = pyaudio.PyAudio()

din, dout, dusbin, dusbout = audioDevNumbers(p)

bufferedAudio(p,process,dev_in=dusbin)

