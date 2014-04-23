from __future__ import division
import numpy as np

from QAM import *
from paudio import *


def constructOFDM(data, f_list, fs, symbol_length):
    symbol_size = fs*symbol_length
    num_chan = f_list.size

    if (data.size/num_chan != data.size//num_chan): 
        print("data not multiple of freq divisions")
        return

    signal = np.zeros(data.size * symbol_size / num_chan)
    if num_chan > 1:
        for i,f in enumerate(f_list):
            subdata = data[i::num_chan]
            sig = modulateQAM16(subdata, f, fs, symbol_length)
            signal += sig;
    else:
        subdata = data
        sig = modulateQAM16(subdata, f_list, fs, symbol_length)
        signal += sig;

    return signal

def deconstructOFDM(signal, f_list, fs, symbol_length):
    num_chan = f_list.size
    symbol_size = fs*symbol_length
    num_data = signal.size / symbol_size * num_chan

    data = np.zeros(num_data)
    if num_chan > 1:
        for i,f in enumerate(f_list):
            data[i::num_chan] = demodulateQAM16(signal, f, fs, symbol_length)
    else:
         data = demodulateQAM16(signal, f_list, fs, symbol_length)

    return data




def testOFDM():
    data = np.random.randint(0,16,320) 
    f_list = np.linspace(480, 4800, 4)
    print f_list.size

    modulated = constructOFDM(data,f_list, 48000.0, 0.01)
    #spectrogram(modulated,48000.0*0.005)

    rec_mod = streamAndRecord(modulated, 6, 48000.0)

    demod = deconstructOFDM(modulated, f_list, 48000.0, 0.01)

    #print data
    #print demod
    print np.sum(demod == data) / 320

if __name__ == '__main__':
    testOFDM()