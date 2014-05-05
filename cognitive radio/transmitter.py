from __future__ import division

import numpy as np

from syncronization import *
from FSK import *
from QAM import *
from OFDM import *
from helpers import *
from paudio import *


def transmit_fsk(data, f0, f1, n, symbol_length, sync_width=100, fs=44100.0, sync_pulse = None,ss_pulse = None,pa = None,  dev_out = None, QO = None):

    data_size = data.size
    symbol_size = fs*symbol_length
    if sync_pulse == None:
        sync_pulse = genSyncPulse()
    sync_size = sync_pulse.size
    num_syncs = 1 + data_size // sync_width

    f_list = np.linspace(f0, f1, n)
    
    signal = np.zeros(data_size*symbol_size + sync_size*num_syncs)
    j = 0
    i = 0
    while (i < data_size):
        
        signal[i*symbol_size + j*sync_size : i*symbol_size + (j+1)*sync_size] = sync_pulse
        j+=1
        signal[i*symbol_size + j*sync_size : (i+sync_width)*symbol_size + j*sync_size] = modulateFSK(data[i:i+sync_width], f_list, fs, symbol_length)
        i+=sync_width
    # the terminating sync pulse
    signal[i*symbol_size + j*sync_size : i*symbol_size + (j+1)*sync_size] = sync_pulse
    
    if ss_pulse != None:
        signal[:ss_pulse.size] = ss_pulse
        signal[signal.size-ss_pulse.size:] = ss_pulse

    signal = np.append(np.zeros(fs), signal)
    signal = np.append(signal, np.zeros(fs))

    if QO == None:
        Qout = Queue.Queue()

        if not pa:
            pa = pyaudio.PyAudio()
   
        t_play = threading.Thread(target = play_audio, args = (Qout, pa, fs, dev_out))
        t_play.start()

        Qout.put(signal)

    else:
        for i in np.r_[:signal.size:1024]:
            QO.put(signal[i:i+1024])

def transmit(signal, fs, dev_out):
    pass