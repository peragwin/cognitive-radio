from __future__ import division

import numpy as np
import scipy.signal as sp

from FSK import *
from QAM import *
from paudio import *
from syncronization import *


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
        self.f_list = np.linsapce(f0, f1, n)
        self.symbol_length = symbol_length
        self.symbol_size = int(fs*symbol_length)
        self.sync_pulse

    def process(self, data):
        self.dataBuffer = np.append(self.dataBuffer, data)
        self.bufferSize += len(data)

        inSync = self.checkForSync()


        if self.inSync:
            
            num_symbols = (bufferSize - start_idx) // self.symbol_size

            if num_symbols > 100:
                self.inSync = self.checkForSync()
                self.dataBuffer = self.dataBuffer[self.start_idx:]
                self.start_idx = 0
                return

            if num_symbols > 0:
                data = dataBuffer[self.start_idx:self.start_idx+num_symbols*self.symbol_size]
                demod = self.demodulate(data)
                if demod:
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
               
        

    def checkForSync(self):
        if bufferSize > self.sync_pulse.size * 2 :
            start_idx = findSync(self.dataBuffer)
            if start_idx >= 0:
                self.inSync = True
                self.dataBuffer = self.dataBuffer[start_idx:]
                self.start_idx = 0
                return True
        return False

    def demodulate(data):
        return demodulateFSK(data, self.f_list, self.fs, self.symbol_length)



def realtimeDecoder(f0, f1, n, symbol_length, sync_pulse = None):
    
    if not sync_pulse:
        sync_pulse = genSyncPulse()

    decoder = Decoder(f0, f1, n, symbol_length, sync_pulse)

    bufferedRecord(decoder, 10)

    rec_data = decoder.rec_data

    print rec_data


if __name__ == '__main__':
