import numpy as np
import scipy.signal as signal

import Queue
import threading
import pyaudio

from QAM import *

data = np.random.randint(0,16,size = 100)
print data

signal = []

for d in data:
    signal = np.append(signal,modulateQAM(d,16,2000,44100,0.05))






def play_audio( Q, p, fs):
    # play_audio plays audio with sampling rate = fs
    # Q - A queue object from which to play
    # p   - pyAudio object
    # fs  - sampling rate
    # dev - device number
    
    # Example:
    # fs = 44100
    # p = pyaudio.PyAudio() #instantiate PyAudio
    # Q = Queue.queue()
    # Q.put(data)
    # Q.put("EOT") # when function gets EOT it will quit
    # play_audio( Q, p, fs,1 ) # play audio
    # p.terminate() # terminate pyAudio
    
    # open output stream
    ostream = p.open(format=pyaudio.paFloat32, channels=1, rate=int(fs),output=True) #,output_device_index=dev)
    # play audio
    while (1):
        data = Q.get()
        if data=="EOT" :
            break
        try:
            ostream.write( data.astype(np.float32).tostring() )
        except:
            break


# create an input output FIFO queues
Qout = Queue.Queue()


# create a pyaudio object
p = pyaudio.PyAudio()

# initialize a playing thread. 
t_play = threading.Thread(target = play_audio,   args = (Qout,   p, 44100  ))

# start the recording and playing threads
#t_rec.start()
t_play.start()

# record and play about 10 seconds of audio 430*1024/44100 = 9.98 s
Qout.put(signal)

#p.terminate()
