from __future__ import division
import numpy as np
import scipy.signal as sp
import matplotlib.pyplot as plt

def modulateFSK(data, f0, f1, n, fs, symbol_length):
    
    f_list = np.linspace(f0,f1,n)
   
    t = np.r_[0:symbol_length:1.0/fs]

    out = []

    for d in data:
        sig = np.sin(2*np.pi*f_list[d]*t)
        out = np.append(out, sig)


    

    return out

def demodulateFSK(signal, f0, f1, n, fs, symbol_length):
    
    f_list = np.linspace(f0, f1, n)

    t = np.r_[0:symbol_length:1.0/fs]
    ssize = symbol_length*(signal.size //  symbol_length)
    num_symbols = signal.size // t.size
    print num_symbols
    out = np.zeros(num_symbols)

    for i,s in enumerate(np.r_[0:ssize-symbol_length*fs:symbol_length*fs]):
        sym = signal[s:s+symbol_length*fs]
        out[i] = matchedFilter(f_list, sym, fs)
        
    return out

def matchedFilter(f_list, sig, fs):

    f_min = f_list[0]
    f_max = f_list[f_list.size-1]
    scl = f_list.size/(f_list.size-1)
    
    h = sp.firwin(24, 8800, nyq=fs)
    sig = sp.fftconvolve(sig,h)
    sig = sig[::5]

    # could have done that - makes sense to do but realistically its probably faster to use only one fft

    dft = np.abs(np.fft.fft(sig))

    #fft_levels = np.histogram(dft[:dft.size/2],bins = f_list.size)


   # fig = plt.figure()
   # ax = fig.add_subplot(111)
   # ax.plot(range(dft.size),dft)
   # fig.show()

   # Note: the 48/44 is because 4800 is half the de

    max_idx = np.argmax(dft[:dft.size/2]) / (dft.size/2) * fs/10

    matching = np.abs(f_list - max_idx)

    return  np.argmin(matching)

if (__name__ == '__main__'):

    data = np.random.randint(0,16,size = 1000)
  
    #data = np.r_[0:16]


    modulated = modulateFSK(data, 440, 4200, 16, 44100.0, 0.01)

    modulated += np.random.normal(size=modulated.size)
   
    demod = demodulateFSK(modulated, 440, 4200, 16, 44100.0, 0.01)
    
   # for i in range(data.size):
   #     print data[i], demod[i]

    # This better be 100 % or something's wrong...
    
    print 100 * sum(np.equal(data,demod))/data.size, '%'