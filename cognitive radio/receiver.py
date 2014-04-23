from __future__ import division

import numpy as np
import scipy.signal as sp

from FSK import *
from QAM import *
from paudio import *
from syncronization import *
from OFDM import *

from transmitter import *

class Decoder:

    dataBuffer = []
    bufferSize = 0
    inSync = 0
    start_idx = 0

    rec_data = []

    def __init__(self, f0, f1, n, symbol_length, sync_pulse, sync_width = 100, fs = 44100.0):
        self.f0 = f0
        self.f1 = f1
        self.fs = fs
        self.f_list = np.linspace(f0, f1, n)
        self.symbol_length = symbol_length
        self.symbol_size = int(fs*symbol_length)
        self.sync_pulse = sync_pulse
        self.sync_width = sync_width

    def process(self, data):
        self.dataBuffer = np.append(self.dataBuffer, data)
        self.bufferSize += len(data)

        inSync = self.checkForSync()
        print inSync, self.bufferSize

        if self.inSync:
            
            num_symbols = (self.bufferSize - self.start_idx) // self.symbol_size

            if num_symbols > 100:
                print self.start_idx, self.dataBuffer.size
                self.inSync = self.checkForSync()
                self.dataBuffer = self.dataBuffer[self.start_idx:]
                self.start_idx = 0
                return

            if num_symbols > 0:
                data = self.dataBuffer[self.start_idx:self.start_idx+num_symbols*self.symbol_size]
 
                demod = self.demodulate(data)
                if demod != None:
                    num_demod = demod.size
                    if num_demod == num_symbols:
                         self.rec_data = np.append(self.rec_data, demod)
                         self.start_idx += self.symbol_size
                    else:
                        print 'error demodulating, wrong size:', num_demod, num_symbols
                #else:
                #    if (bufferSize - start_idx) > 2 * self.sync_pulse.size:
                #        self.inSync = self.checkForSync()
                #    print 'error demodulating, nothing found'
                #    return
        else:
            pass             
        

    def checkForSync(self):
        if self.bufferSize > self.sync_width * self.symbol_size :
            start_idx = findSync(self.dataBuffer,sync_pulse = self.sync_pulse)
            if start_idx >= 0:
                self.inSync = True
                self.dataBuffer = self.dataBuffer[start_idx:]
                self.bufferSize = self.dataBuffer.size // self.symbol_size
                self.start_idx = 0
                return True
        return False

    def demodulate(self,data):
        return demodulateFSK(data, self.f_list, self.fs, self.symbol_length)



def realtimeDecoder(f0, f1, n, symbol_length,pa = None, sync_pulse = None):
    
    if sync_pulse == None:
        sync_pulse = genSyncPulse()

    decoder = Decoder(f0, f1, n, symbol_length, sync_pulse)

    bufferedRecord(decoder, 20, pa)

    rec_data = decoder.rec_data

    print rec_data


if __name__ == '__main__':

    sync_pulse = genSyncPulse2()

    data = np.random.randint(0,2,1200)

    p = pyaudio.PyAudio()
    
    transmit(data, 1200, 2400, 2, .01, pa = p,sync_pulse = sync_pulse)
    realtimeDecoder(1200, 2400, 2, .01, pa=p, sync_pulse = sync_pulse)
    
    