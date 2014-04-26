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
    process_state = 0

    rec_data = []

    def __init__(self, f0, f1, n, symbol_length, sync_pulse, ss_pulse, sync_width = 100, fs = 44100.0):
        self.f0 = f0
        self.f1 = f1
        self.fs = fs
        self.f_list = np.linspace(f0, f1, n)
        self.symbol_length = symbol_length
        self.symbol_size = int(fs*symbol_length)
        self.sync_pulse = sync_pulse
        self.sync_width = sync_width
        self.ss_pulse = ss_pulse

    def process(self, data):
        # Add to the dataBuffer
        self.dataBuffer = np.append(self.dataBuffer, data)
        # Make sure it cant grow too large. Here its the length of sync_width symbols
        if self.dataBuffer.size > self.symbol_size * self.sync_width:
            self.dataBuffer = self.dataBuffer[self.dataBuffer.size-self.symbol_size*self.sync_width:]

        # Structure:
        # State 0: Listening to incoming stream, looking for a nice start-of-transmission marker
        # State 1: Found the start, so begin decoding bits until sync_width have been decoded
        # State 2: Listening for either a sync_pulse to verify synchronization before coninuing,
        #          or for a end-of-transmission pulse to tell us we are done receiving data.
        # State 3: done! exit.

        # State 0
        if self.process_state == 0:
            print 'made it to 0'
            toStart = self.checkForSync()


        # State 1
        elif self.process_state == 1:
            print 'made it to 1'

            num_symbols = (self.dataBuffer.size - self.start_idx) // self.symbol_size

            if num_symbols > 0:

                data = self.dataBuffer[self.start_idx:self.start_idx+num_symbols*self.symbol_size]
                #myplot(data)
                demod = self.demodulate(data)

                if demod != None:
                    num_demod = demod.size
                    if num_demod == num_symbols:
                        self.rec_data = np.append(self.rec_data, demod)
                        self.start_idx += self.symbol_size*num_symbols
                        self.decode_count += num_symbols
                        # check if we are done with the chunk
                        if self.decode_count >= 100:
                            self.process_state = 2
                            self.decode_count = 0
                    else:
                        print 'error demodulating, wrong size:', num_demod, num_symbols
                else:
                    print 'error demodulating, nothing found'
                    return 1
            else:
                print "No symbols left in buffer, start_idx needs resetting"
                self.process_state = 2
                return 0


        # State 2
        elif self.process_state == 2:
            print 'made it to 2'
            toContinue = self.checkForSync()


        # State 3
        else: 
            print 'made it to 3, yay!'
            return 1

        return 0

    # Note that for checkForSync to work properly, the sync pulses MUST be equal or smaller than processing chunk sizes
    def checkForSync(self):
        if self.process_state == 0: # look for the start pulse

            toStart = findSync(self.dataBuffer, self.ss_pulse)
            if toStart != -1:
                self.process_state = 1
                self.dataBuffer = self.dataBuffer[toStart:]
                self.start_idx = 0
                return True

        elif self.process_state == 2: # now we are done decoding a chunk so look for a sync or end pulse

            toEnd = findSync(self.dataBuffer, sync_pulse = self.ss_pulse)  # check for the end pulse
            if toEnd != -1:
                self.process_state = 3
                return True

            start_idx = findSync(self.dataBuffer,sync_pulse = self.sync_pulse) # no end pulse, check for next sync pulse
            if start_idx >= 0:
                self.process_state = 1
                self.dataBuffer = self.dataBuffer[start_idx:]
                self.start_idx = 0
                return True

        # If nothing was found:
        return False

    def demodulate(self,data):
        return demodulateFSK(data, self.f_list, self.fs, self.symbol_length)

    def complete(self):
        return self.finished and self.bufferSize == 0



def realtimeDecoder(f0, f1, n, symbol_length, time, pa = None,ss_pulse=None, sync_pulse = None, QI = None):

    if sync_pulse == None:
        sync_pulse = genSyncPulse()

    decoder = Decoder(f0, f1, n, symbol_length, sync_pulse, ss_pulse)

    if QI == None:
        bufferedRecord(decoder, time, pa)
    else:
        while(not QI.empty()):
            data = QI.get()
            
            if decoder.process(data):
                break

      #  while(decoder.process()):
      #      print 'finsihing up'


    rec_data = decoder.rec_data

    return rec_data


if __name__ == '__main__':

    sync_pulse = genSyncPulse2(4000, 1200,t=.02)        # make sure t*fs < chunk size (1024)
    start_stop_pulse = genSyncPulse2(2400, 1200, t=.02)

    data = np.random.randint(0,2,1000)

    #data = np.zeros(200)
    #for i in np.r_[:200:8]:
    #    data[i:i+4] = 1

    p = pyaudio.PyAudio()

    Q = Queue.Queue()

    transmit(data, 1200, 2400, 2, .01, pa = p,sync_pulse = sync_pulse, ss_pulse = start_stop_pulse, QO = Q)

    decoded = realtimeDecoder(1200, 2400, 2, .01, 15, pa=p, ss_pulse=start_stop_pulse, sync_pulse = sync_pulse, QI = Q)

    print data[:20]
    print decoded[:20]

    print np.sum(np.equal(data, decoded))/data.size

    for i in range(200):
        if data[i] != decoded[i]:
            print i
   
    p.terminate()