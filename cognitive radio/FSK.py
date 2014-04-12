import numpy as np


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

    num_symbols = signal / t.size

    for s in np.r_[0:signal.size:symbol_length*fs]:
        sym = signal[s:s+symbol_length*fs]
