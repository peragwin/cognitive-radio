import pyaudio
import Queue
import threading
import numpy as np

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
        istream = p.open(format=pyaudio.paFloat32, channels=1, rate=int(fs),input=True,input_device_index=dev,frames_per_buffer=chunk)
    else:
        istream = p.open(format=pyaudio.paFloat32, channels=1, rate= int(fs),input=True,frames_per_buffer=chunk)

    # record audio in chunks and append to frames
    frames = [];
    while (1):
        try:  # when the pyaudio object is distroyed stops
            data_str = istream.read(chunk) # read a chunk of data
        except:
            break
        data_flt = np.fromstring( data_str, 'float32' ) # convert string to float
        queue.put( data_flt ) # append to list

def audioDevNumbers(p):
    # din, dout, dusb = audioDevNumbers(p)
    # The function takes a pyaudio object
    # The function searches for the device numbers for built-in mic and 
    # speaker and the USB audio interface
    # some devices will have the name Generic USB Audio Device. In that case, replace it with the the right name.
    
    dusbin = 'None'
    dusbout = 'None'
    din = 'None'
    dout = 'None'
   

    N = p.get_device_count()
    for n in range(0,N):
            name = p.get_device_info_by_index(n).get('name')
            
            if name == u'Microphone (USB PnP Sound Devic':
                dusbin = n
            if name == u'USB Speakers (USB PnP Sound Dev':
                dusbout = n
            if name == u'Microsoft Sound Mapper - Input':
                din = n
            if name == u'Microsoft Sound Mapper - Output':
                dout = n
                
    if dusbin == 'None':
        print('Could not find a usb audio device')
    return din, dout, dusbin, dusbout


def bufferedAudio(p,process, dev_in=None, dev_out=None):
    # create an input output FIFO queues
    Qin = Queue.Queue()
    Qout = Queue.Queue()


    # create a pyaudio object


    # find the device numbers for builtin I/O and the USB
   

    # initialize a recording thread. The USB device only supports 44.1KHz sampling rate
    t_rec = threading.Thread(target = record_audio,   args = (Qin,   p, 44100, dev_in  ))

    # initialize a playing thread. 
    t_play = threading.Thread(target = play_audio,   args = (Qout,   p, 44100, dev_out  ))

    # start the recording and playing threads
    t_rec.start()
    t_play.start()

    # record and play about 10 seconds of audio 430*1024/44100 = 9.98 s
    for n in range(0,420420):
    
        samples = Qin.get()
        # You can add code here to do processing on samples in chunks of 1024
        # you will have to implement an overlap an add, or overlap an save to get
        # continuity between chunks
    
        samples = process(samples)


        Qout.put(samples)

    p.terminate()


if (__name__ == '__main__'):  

    p = pyaudio.PyAudio()

    def process(samples):
        return samples

    bufferedAudio(p,process)
