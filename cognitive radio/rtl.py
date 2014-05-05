from __future__ import division

import numpy as np
import scipy.signal as sp
import rtlsdr
import Queue
import threading

from paudio import *
from helpers import *
from fm_demodulator import Demodulator


def initRtlSdr(sdr, freq, sample_rate, gain):
    sdr.set_center_freq(freq)
    sdr.set_gain(gain)
    sdr.set_sample_rate(sample_rate)
    

def getSamples(sdr, n):
    return sdr.read_samples(256 * n//256)

def getSamplesAsync(sdr, Qin):

    def samplerCallback(samples, context):  
        #print 'callback'
        Qin.put(samples)

    sample_th = threading.Thread(target = sdr.read_samples_async, args = (samplerCallback, 25600))  # set sample block size here
    sample_th.start()
    
#def demodStream(Qout):

def testSdr():
    sdr = rtlsdr.RtlSdr()
    
    radioQ = Queue.Queue()
    Qout = Queue.Queue()

    initRtlSdr(sdr, 105.3e6, 2.4e5, 22)
    getSamplesAsync(sdr, radioQ)
    
    p = pyaudio.PyAudio()
   
    play_t = threading.Thread( target = play_audio, args = (Qout, p, 48000.0) )
    play_t.start()
    
    dem = Demodulator(2.4e5, 80000.0, 48000.0, 16000.0)

    while(True):
       
        data = radioQ.get()
        audio = dem.fm_demodulate(data)
        #spectrogram(audio)
        Qout.put(audio)


if __name__ == '__main__':
    testSdr()