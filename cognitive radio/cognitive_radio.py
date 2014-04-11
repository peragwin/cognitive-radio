import numpy as np
from numpy.fft import fft
from numpy.fft import fftshift
from numpy.fft import ifft
from numpy.fft import ifftshift

import scipy.signal as signal

import rtlsdr
import time

import matplotlib.pyplot as plt

get_new_data = 1            # whether to record new data (debugging purposes)

num_bands = 256             # this is the number of channels the scan will be broken into
                            # and how much to decimate after applying bandpass filters
                            # 256 @ 2.4e6 sampling results in channels that are 9375kHz wide

                            # this will keep track of which channels are good
channel_weight = np.zeros(num_bands)
                           
max_num_channels = 8        # don't let it try to transmit on more than this number of bands
current_channels = []       # keep a list of currently used channels


sdr_frequency = 148e6       # variables for the SDR:
sdr_sample_rate = 2.4e6     # 
num_samples = 2.56e4        # number of recorded samples


sdr = rtlsdr.RtlSdr()
sdr.set_center_freq(sdr_frequency)
sdr.set_sample_rate(sdr_sample_rate)
sdr.set_gain(31.9)

def sdrGetData():
    data = sdr.read_samples(num_samples)    
    return data

def plotPowerSpec(signal):
    Signal = np.fft.fftshift(np.fft.fft(signal))
    powerSpec = 20*np.log10(np.abs(Signal))
    fig = plt.figure(figsize=(16, 8))
    ax = fig.add_subplot(111);
    ax.plot(range(data.size),powerSpec)
    fig.show()
    

if(get_new_data):
    try:
        data = sdrGetData()
    except:
        print("Failed to record new data.")
        try:
            data = np.load("data.npy")
            print("Defaulting to data.npy...");
        except:
            print("Make sure the SDR is plugged in and configured properly.")
else:
    try:
        data = np.load("data.npy")
    except:
        print("Failure to load: data.npy")

#plotPowerSpec(data)

# The following code is designed to apply several bandpass filters
# over the entire sampled spectrum and determine for each channel
# whether there is already something being transmitted, compiling 
# a list of open channels 

def calc_channel_weights():
    subband_len = int(num_samples/num_bands)

    data_dft = fft(data);
    subbands = np.reshape(data_dft,(num_bands,subband_len))


    band_energy = np.zeros(num_bands)
    for b in range(num_bands):
        band_energy[b] = np.real(np.sum( subbands[b,:] * np.conj(subbands[b,:]) ))

    avg_energy = np.mean(band_energy)
    std_energy = np.std(band_energy)

    band_list = (band_energy-avg_energy)/std_energy   #np.less_equal(band_energy,avg_energy)

    for b in range(num_bands):
        channel_weight[b] /= 2
        if(band_list[b] < 0):
            channel_weight[b] -= np.log(np.abs(band_list[b]))
        
    return channel_weight

fig = plt.figure(figsize = (18,2))
ax = fig.add_subplot(111)


while(1):
    data = sdrGetData()
    weights = calc_channel_weights()

    h = np.hanning(8)
    lp_weight = signal.fftconvolve(weights,h,mode='same')

    ax.plot(range(data.size), np.log(np.abs(fft(data))) )
   # ax.plot(range(lp_weight.size),lp_weight)
    fig.show()
    time.sleep(1)

