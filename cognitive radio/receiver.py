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
    decode_count = 0
    inSync = 0
    start_idx = 0
    finished = 0

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

    def process(self, data = None):
        if data != None:
            self.dataBuffer = np.append(self.dataBuffer, data)
            #self.bufferSize += len(data)

        print self.inSync, self.dataBuffer.size, (self.dataBuffer.size - self.start_idx) // self.symbol_size

        if self.inSync:
            
            num_symbols = (self.dataBuffer.size - self.start_idx) // self.symbol_size
            print num_symbols
            

            if num_symbols > 0:
                data = self.dataBuffer[self.start_idx:self.start_idx+num_symbols*self.symbol_size]
 
                demod = self.demodulate(data)
                if demod != None:
                    num_demod = demod.size
                    if num_demod == num_symbols:
                         self.rec_data = np.append(self.rec_data, demod)
                         self.start_idx += self.symbol_size*num_symbols
                         self.decode_count += num_symbols
                    else:
                        print 'error demodulating, wrong size:', num_demod, num_symbols
                else:
                    #if (bufferSize - start_idx) > 2 * self.sync_pulse.size:
                    #    self.inSync = self.checkForSync()
                    print 'error demodulating, nothing found'
                    return 1
            else:
                print "neg symbols? >>> Must be done."
                return 0

            if self.decode_count >= (self.sync_width):
                # done with this section
                #print self.start_idx, self.dataBuffer.size
                self.decode_count = 0
                self.inSync = self.checkForSync()
                print 'end of chuck, inSync?', self.inSync
                ####self.dataBuffer = self.dataBuffer[self.start_idx:]
                
                ####self.start_idx = 0
                return 1
                
        else:
            self.inSync = self.checkForSync()            
        
        return 0

    def checkForSync(self):
        if self.decode_count == 0: # and self.dataBuffer.size >= self.sync_pulse.size: #self.dataBuffer.size > self.sync_width/50 * self.symbol_size :
            start_idx = findSync(self.dataBuffer,sync_pulse = self.sync_pulse)
            
            if start_idx >= 0:
                self.inSync = True
                self.dataBuffer = self.dataBuffer[start_idx:]
                #self.bufferSize = self.dataBuffer.size // self.symbol_size
                self.start_idx = 0
                return True

        return False

    def demodulate(self,data):
        return demodulateFSK(data, self.f_list, self.fs, self.symbol_length)

    def complete(self):
        return self.finished and self.bufferSize == 0



def realtimeDecoder(f0, f1, n, symbol_length,pa = None, sync_pulse = None, QI = None):
    
    if sync_pulse == None:
        sync_pulse = genSyncPulse()

    decoder = Decoder(f0, f1, n, symbol_length, sync_pulse)

    if QI == None:
        bufferedRecord(decoder, 20, pa)
    else:
        while(not QI.empty()):
            data = QI.get()
            #if data == None:
            #    break
            decoder.process(data)
        while(decoder.process()):
            print 'finsihing up'


    rec_data = decoder.rec_data

    return rec_data


if __name__ == '__main__':

    sync_pulse = genSyncPulse2(4000, 1200)

    data = np.random.randint(0,2,1000)

    p = pyaudio.PyAudio()
    
    Q = Queue.Queue()

    transmit(data, 1200, 2400, 2, .01, pa = p,sync_pulse = sync_pulse, QO = Q)
 
    decoded = realtimeDecoder(1200, 2400, 2, .01, pa=p, sync_pulse = sync_pulse, QI = Q)
    
    print data[:20]
    print decoded[:20]

    print np.sum(np.equal(data, decoded))/data.size

    p.terminate()