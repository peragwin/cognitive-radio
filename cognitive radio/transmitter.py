import numpy as np
import scipy.signal as signal

import Queue
import threading
import pyaudio

from paudio import *

from QAM import *

data = np.random.randint(0,16,size = 100)


signal = []

for d in data:
    signal = np.append(signal,modulateQAM(d,16,2000,44100,0.05))



def play_audio( Q, p, fs, dev=None):
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
    if dev:
        ostream = p.open(format=pyaudio.paFloat32, channels=1, rate=int(fs),output=True,output_device_index=dev)
    else:
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


def record_audio( queue, p, fs ,dev=None,chunk=1024):
    # record_audio records audio with sampling rate = fs
    # queue - output data queue
    # p     - pyAudio object
    # fs    - sampling rate
    # dev   - device number 
    # chunk - chunks of samples at a time default 1024
    #
    # Example:
    # fs = 44100
    # Q = Queue.queue()
    # p = pyaudio.PyAudio() #instantiate PyAudio
    # record_audio( Q, p, fs, 1) # 
    # p.terminate() # terminate pyAudio
    
    if dev:
        stream = p.open(format=pyaudio.paFloat32, channels=1, rate=int(fs),input=True,input_device_index=dev,frames_per_buffer=chunk)
    else:
        stream = p.open(format=pyaudio.paFloat32, channels=1, rate= int(fs),input=True,frames_per_buffer=chunk)

    # record audio in chunks and append to frames
    frames = [];
    while (1):
        try:  # when the pyaudio object is distroyed stops
            data_str = istream.read(chunk) # read a chunk of data
        except:
            break
        data_flt = np.fromstring( data_str, 'float32' ) # convert string to float
        queue.put( data_flt ) # append to list



# create an input output FIFO queues
Qout = Queue.Queue()
Qin = Queue.Queue()

# create a pyaudio object
p = pyaudio.PyAudio()

# initialize a playing thread. 
t_play = threading.Thread(target = play_audio,   args = (Qout,   p, 44100  ))

t_rec = threading.Thread(target= record_audio, args = (Qin, p, 44100) )
# start the recording and playing threads#
t_rec.start()
t_play.start()

# record and play about 10 seconds of audio 430*1024/44100 = 9.98 s
Qout.put(signal)

for i in range(420):
    samples = Qin.get()
    output = np.append(output, samples)

print len(output)


#p.terminate()
