from __future__ import division

import numpy as np
from rtl import *

from paudio import *
from FSK import *
from QAM import *
from OFDM import *
from syncronization import *
from receiver import *
from fm_demodulator import Demodulator
from helpers import *

# This file tests various parts of my project over an actual RF channel. 
#
# 1) I will be using UHF experimental channels. Every broadcast will be 
#   preceded by morse code with my call sign and a short explanation of 
#   the transmission.

def genPTT(plen,zlen,fs):
    Nz = np.floor(zlen*fs)
    Nt = np.floor(plen*fs)
    pttsig = np.zeros(Nz)
    t=np.r_[0.0:Nt]/fs
    pttsig[:Nt] = 0.5*np.sin(2*np.pi*t*2000)
    return pttsig

def text2Morse(text,fc,fs,dt):
    CODE = {'A': '.-',     'B': '-...',   'C': '-.-.', 
        'D': '-..',    'E': '.',      'F': '..-.',
        'G': '--.',    'H': '....',   'I': '..',
        'J': '.---',   'K': '-.-',    'L': '.-..',
        'M': '--',     'N': '-.',     'O': '---',
        'P': '.--.',   'Q': '--.-',   'R': '.-.',
     	'S': '...',    'T': '-',      'U': '..-',
        'V': '...-',   'W': '.--',    'X': '-..-',
        'Y': '-.--',   'Z': '--..',
        
        '0': '-----',  '1': '.----',  '2': '..---',
        '3': '...--',  '4': '....-',  '5': '.....',
        '6': '-....',  '7': '--...',  '8': '---..',
        '9': '----.',

        ' ': ' ', "'": '.----.', '(': '-.--.-',  ')': '-.--.-',
        ',': '--..--', '-': '-....-', '.': '.-.-.-',
        '/': '-..-.',   ':': '---...', ';': '-.-.-.',
        '?': '..--..', '_': '..--.-'
        }
    
    Ndot= 1.0*fs*dt
    Ndah = 3*Ndot
    
    sdot = np.sin(2*np.pi*fc*np.r_[0.0:Ndot]/fs)
    sdah = np.sin(2*np.pi*fc*np.r_[0.0:Ndah]/fs)
    
    # convert to dit dah
    mrs = ""
    for char in text:
        mrs = mrs + CODE[char.upper()] + "*"
    
    sig = np.zeros(1)
    for char in mrs:
        if char == " ":
            sig = np.concatenate((sig,np.zeros(Ndot*7)))
        if char == "*":
            sig = np.concatenate((sig,np.zeros(Ndot*3)))
        if char == ".":
            sig = np.concatenate((sig,sdot,np.zeros(Ndot)))
        if char == "-":
            sig = np.concatenate((sig,sdah,np.zeros(Ndot)))
    return sig
            

def tx_intro(fs):
    
    msg = 'KK6KLA: Experiemental use.'

    tx = genPTT(.5, 1, fs)
    tx = np.append(tx, text2Morse(msg, 880, fs, .025))

    tx = np.append(tx, np.zeros(fs*2)) # add silence for 5 seconds before starting

    return tx

def tx_fsk(data, fs, f0, f1, n, symbol_length, sync_width, sync_pulse, start_stop_pulse):
    
    

    data_size = data.size
    symbol_size = fs*symbol_length
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
    
    # start-stop pulses
    ss_pulse = start_stop_pulse    
    signal[:ss_pulse.size] = ss_pulse
    signal[signal.size-ss_pulse.size:] = ss_pulse

    signal = np.append(np.zeros(fs), signal)
    signal = np.append(signal, np.zeros(fs))

    return signal


def main():

   fs_out = 44100.0
   fs_in = fs_out #48000.0
   channel = 432.079e6

   sync_pulse = genSyncPulse2(4000, 1200,t=.02)        # make sure t*fs < chunk size (1024)
   start_stop_pulse = genSyncPulse2(2400, 1200, t=.02)

   radioQ = Queue.Queue()
   Qin = Queue.Queue()
   Qout = Queue.Queue()

   sdr = rtlsdr.RtlSdr()
   initRtlSdr(sdr, channel, 2.4e5, 32)
   getSamplesAsync(sdr, radioQ)

   tx_data = np.random.randint(0, 2, 1000)

   transmission = np.append(tx_intro(fs_out), tx_fsk(tx_data, fs_out, 1200, 2400, 2, .01, 200, sync_pulse, start_stop_pulse))
   #transmission = tx_fsk(data, fs_out, 1200, 2400, 2, .005, 200, sync_pulse, start_stop_pulse)

   p = pyaudio.PyAudio()
   din, dout, dusbin, dusbout = audioDevNumbers(p)
   
   tx_t = threading.Thread(target=play_audio, args = (Qout, p, fs_out, dusbout))
   tx_t.start()
   Qout.put(transmission)

   play_t = threading.Thread(target = play_audio, args = (Qin, p, fs_in, dout))
   play_t.start()

   dem = Demodulator(2.4e5,16000.0, fs_in, 4000.0)
   dec = Decoder(1200, 2400, 2, .01, sync_pulse, start_stop_pulse, 200, fs_in)

   data = radioQ.get()
   audio = dem.fm_demodulate(data)
   Qin.put(audio) # play the incomming signal

   while(True):
        
       rx_signal = radioQ.get()
       audio = dem.fm_demodulate(rx_signal)
       #audio *= 2
       Qin.put(audio) # play the incomming signal

       if(dec.process(audio)):
           break
    
   rx_data = dec.rec_data

   print tx_data[:20]
   print rx_data[:20]
   
   print np.sum(np.equal(tx_data, rx_data))/1000

   for i in range(400):
       if (tx_data[i] != rx_data[i]):
           print(i),

   p.terminate()
   sdr.close()

if __name__ == '__main__':
    main()