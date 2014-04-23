from __future__ import division
import numpy as np
import scipy.signal as sp
import matplotlib.pyplot as plt

import time

from helpers import *

def modulateFSK(data, f_list, fs, symbol_length):
    #t = np.r_[0:symbol_length:1.0/fs]

    symSize = symbol_length*fs
    outSize = symSize * data.size
    out = np.zeros(outSize)

    for i,d in enumerate(data):
        out[i*symSize:(i+1)*symSize] = f_list[d]
       # out = np.append(out, sig)

    out = 2*np.pi*np.cumsum( out/fs ) # replaces need for a time vector
    out = np.sin(out)
   # myplot(out)
    return out

def demodulateFSK(signal, f_list, fs, symbol_length):

    #t = np.r_[0:symbol_length:1.0/fs]
    sym_size = symbol_length*fs
    num_symbols = signal.size // sym_size
   
    fc = np.mean(f_list)
    
    f_cut = ( f_list[f_list.size-1] - f_list[0] )
    h = sp.firwin(80, f_cut/2, nyq=fs/2)
    t = np.r_[0.0:80]/fs
    h = np.exp(2j*np.pi*fc*t) * h
    #h = h * np.cos(2*np.pi*fc*t)

    stream = sp.fftconvolve(signal,h, mode='same')
  #  print stream.size
    out = np.zeros(stream.size)

    A = stream[1:]
    B = stream[:stream.size-1]

    out[1:] = np.angle( A * np.conj(B) ) / (2*np.pi)
    out = out - fc/fs

   

    #out = sp.medfilt(out, 39)
   #myplot(out)

    out = np.sign(out[20::symbol_length*fs])

    #for i,s in enumerate(np.r_[0:ssize-symbol_length*fs:symbol_length*fs]):
    #    sym = signal[s:s+symbol_length*fs]
    #    out[i] = matchedFilter(f_list, sym, fs)
        
    return (out+1)/2

def demodulateFSK_list(signal, f_list, fs, symbol_length):
    
    #f_list = np.linspace(f0, f1, n)

   
    ssize = symbol_length*(signal.size //  symbol_length)
    num_symbols = signal.size // (symbol_length * fs)
    
    out = np.zeros(num_symbols)

    for i,s in enumerate(np.r_[0:ssize-symbol_length*fs:symbol_length*fs]):
        sym = signal[s:s+symbol_length*fs]
        out[i] = matchedFilter(f_list, sym, fs)
        
    return out

def matchedFilter(f_list, sig, fs):

    dft = np.abs(np.fft.fft(sig))

   # fig = plt.figure()
   # ax = fig.add_subplot(111)
   # ax.plot(range(dft.size),dft)
   # fig.show()

    max_idx = np.argmax(dft[:dft.size/2]) / (dft.size/2) * fs/2

    matching = np.abs(f_list - max_idx)

    return  np.argmin(matching)

if (__name__ == '__main__'):

    data = np.random.randint(0,2,size = 100)
    f_list = np.linspace(2000,2400,2)
    fs = 48000.0
    symbol_len = 80.0/48000.0
   
    #data = np.r_[0:16]
    t = time.time()

    modulated = modulateFSK(data, f_list, fs, symbol_len)

    t1 = time.time()

    print t1 - t

    modulated += np.random.normal(size=modulated.size)
   
    t2 = time.time()
    demod = demodulateFSK(modulated, f_list, fs, symbol_len)
    print time.time() - t2
   # for i in range(data.size):
   #     print data[i], demod[i]

    # This better be 100 % or something's wrong...
    
    print 100 * sum(np.equal(data,demod))/data.size, '%'