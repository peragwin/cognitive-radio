from __future__ import division
import numpy as np

from QAM import *
from paudio import *
from receiver import *
import Queue

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

def deconstructOFDM(signal, f_list, fs, symbol_length, predelay = 0):
    num_chan = f_list.size
    symbol_size = fs*symbol_length
    num_data = signal.size / symbol_size * num_chan

    data = np.zeros(num_data)
    if num_chan > 1:
        for i,f in enumerate(f_list):
            data[i::num_chan] = demodulateQAM16(signal, f, fs, symbol_length, predelay)
    else:
         data = demodulateQAM16(signal, f_list, fs, symbol_length)

    return data




def testOFDM():

    n_data = 2400
    n_freq = 12
    T = 0.004

    data = np.random.randint(0,16,n_data) 
    
    f_list = np.linspace(420, 4600, n_freq)
    
    modulated = constructOFDM(data,f_list, 48000.0, T)
    
    spectrogram(modulated,48000.0*T)

    rec_mod = streamAndRecord(modulated, 6, 48000.0)

    demod = deconstructOFDM(modulated, f_list, 48000.0, T)


   # dem = OFDM_Decoder(deconstructOFDM, f_list, T, sync_pulse, ss_pulse, sync_width = 100, fs = 48000.0)


    #print data
    #print demod
    print np.sum(demod == data) / n_data

def testOFDM2():

    n_data = 800
    n_freq = 4
    T = 0.01
    fs = 48000.0

    ss_pulse = genSyncPulse(1200, 3600,fs=48000.0, t1= .02)

    data = np.random.randint(0,16,n_data) 
    
    f_list = np.linspace(420, 4600, n_freq)
    
    modulated = constructOFDM(data,f_list, 48000.0, T)
    
    modulated = np.append(modulated, ss_pulse)
    tx_signal = np.append(ss_pulse, modulated)

    tx_signal = np.append(np.zeros(fs), tx_signal)
    tx_signal = np.append(tx_signal, np.zeros(fs))

    #tx_signal = interleavePulses(modulated, ss_pulse, sync_pulse, 100, 48000.0, T)

    spectrogram(tx_signal,48000.0*T)

    blocksize = .02*fs
    Qout = Queue.Queue()
    N = int(np.ceil(tx_signal.size / blocksize))
    for n in range(N):
        Qout.put(tx_signal[n*blocksize:(n+1)*blocksize])



    #rec_mod = streamAndRecord(modulated, 6, 48000.0)

   # demod = deconstructOFDM(modulated, f_list, 48000.0, T)


    dem = OFDM_Decoder(deconstructOFDM, f_list, T, ss_pulse, fs = 48000.0)


    while(True):

        d = Qout.get()
        if (dem.process(d)):
            break
        
    demod = dem.rec_data

    #print data
    #print demod
    print np.sum(np.equal(demod,data[:demod.size])) / n_data

if __name__ == '__main__':
    testOFDM2()