
import numpy as np
import scipy.signal as sp
from helpers import *

mode4coef = [ [1,0], [0,1], [-1,0], [0, -1] ]
mode16coef = [ [1,1], [1, .333], [1,-.333], [1,-1],
               [.333, 1], [.333, .333], [.333,-.333], [.333, -1],
               [-.333, 1], [-.333, .333], [-.333,-.333], [-.333, -1],
               [-1,1], [-1, .333], [-1,-.333], [-1.0,-1.0] ]

QAM16code = np.array((-3-3j, -3-1j,-3+3j,-3+1j,-1-3j,-1-1j,-1+3j,-1+1j,+3-3j,+3-1j,+3+3j,3+1j,1-3j,+1-1j,1+3j,1+1j))/4

#def modulateQAM(data, mode, fc, fs, symbol_length):
#    if(np.max(data) >= mode):
#        print("All data elements must be <= mode")
#        return

#    waveout = []
#    t = np.r_[0:symbol_length:1.0/fs]
#    d = data
#    if (mode == 4):
#      for d in data:
#        wave = mode4coef[d][0]*np.cos(2*np.pi*fc*t) + mode4coef[d][1]*np.sin(2*np.pi*fc*t)
#        waveout = np.append(waveout, wave)

#    elif (mode == 16):
#      for d in data:
#        wave = mode16coef[d][0]*np.cos(2*np.pi*fc*t) + mode16coef[d][1]*np.sin(2*np.pi*fc*t)
#        waveout = np.append(waveout, wave)
#    else:
#        print("Mode", mode, "not supported")
#        return

#    return waveout

def modulateQAM16(data, fc, fs, symbol_length):
    Ndata = data.size
    symbol_size = fs*symbol_length
    N = Ndata*symbol_size
    qam_arr =  np.zeros(N, dtype='complex')

    for i,d in enumerate(data):
        qam_arr[i*symbol_size:(i+1)*symbol_size] = QAM16code[d];

    t = np.r_[-N/2:N/2]/fs
    sinc = 2*np.sinc(2*np.pi*symbol_size/2*t)/symbol_size

    qam = sp.fftconvolve(qam_arr, sinc, mode='same')
    mod_qam = np.real(qam) * np.cos(2*np.pi*fc/fs*np.r_[:qam.size]) - np.imag(qam) * np.sin(2*np.pi*fc/fs*np.r_[:qam.size])

    return mod_qam

def demodulateQAM16(signal, fc, fs, symbol_length):
    symbol_size = fs*symbol_length
    #num_symbols = signal.size / symbol_size

    inphase = np.zeros_like(signal)
    quadphase = np.zeros_like(signal)

    h = sp.firwin(80, fc/8, nyq=fs/2)
    h *= np.cos(2*np.pi*fc/fs*np.r_[:h.size])
    signal = sp.fftconvolve(signal, h)
    
    inphase = signal * np.cos(2*np.pi*fc/fs*np.r_[:signal.size])
    quadphase = - signal * np.sin(2*np.pi*fc/fs*np.r_[:signal.size])

    #lowpass after demodulating
    h = sp.firwin(80, fc/8, nyq=fs/2)
    inphase = sp.fftconvolve(inphase, h, mode = 'same')
    quadphase = sp.fftconvolve(quadphase, h, mode='same')

    inphase = sp.medfilt(inphase, int(symbol_size/4)-1)
    #myplot(inphase)
    i_coef = inphase[symbol_size/2::symbol_size]
    q_coef = quadphase[symbol_size/2::symbol_size]

    return matchCode16(i_coef, q_coef)
    #ret = []

    #for i in range(i_coef.size):
    #    i_c = i_coef[i]
    #    q_c = q_coef[i]
    #    C = i_c + 1j*q_c
    #    for i,coef in enumerate(QAM16code):
    #        if (C == 2*coef):
    #            ret = np.append(ret, i)

    #return ret

def matchCode16(i_coef, q_coef):
    
    ret = []

    #normalize maximum to hopefully 1.5
    i_coef = 1.5 * i_coef/np.max(i_coef)
    q_coef = 1.5 * q_coef/np.max(q_coef)

    for i in range(i_coef.size):

        I = i_coef[i]
        Q = q_coef[i]
        #print "from: ", I, Q
    
        if np.abs(I) > 1:
            Ih = 1.5 * np.sign(I)
        else:
            Ih = .5 * np.sign(I)

        if np.abs(Q) > 1:
            Qh = 1.5 * np.sign(Q)
        else:
            Qh = .5 * np.sign(Q)
        #print "coefs: ", Ih, Qh
        for j,coef in enumerate(2*QAM16code):
            if (Ih + 1j*Qh == coef):
                ret = np.append(ret, j)

    return ret

def demodulateQAM(wave, mode, fc, fs, symbol_length):

    num_symbols = wave.size / (fs*symbol_length)

    ret = []

    for s in np.linspace(0,wave.size, num_symbols):

        A = matchedCos(wave[s:s+fs*symbol_length], fc, fs, symbol_length)
        B = matchedSin(wave[s:s+fs*symbol_length], fc, fs, symbol_length)
        print "coefs: ", A, B
    # thresholding:

        if (np.abs(A) > .667):
            Ah = np.sign(A)
        else:
            Ah = .333*np.sign(A)

        if (np.abs(B) > .667):
            Bh = np.sign(B)
        else:
            Bh = .333*np.sign(B)
   # print Ah, Bh
    # return the bit value
        if (mode == 4):
            idx = 0
            for coef in mode4coef:
                if (coef[0] == Ah and coef[1] == Bh):
                    ret = np.append(ret,idx)
                idx+=1
        if (mode == 16):
            idx = 0
            for coef in mode16coef:
                if (coef[0] == Ah and coef[1] == Bh):
                    ret = np.append(ret, idx)
                idx+=1

    return ret

def matchedCos(wave, fc, fs, symbol_length):
    t = np.r_[0:symbol_length:1.0/fs]
    matchedfilt = np.cos(2*np.pi*fc*t)
    if (wave.size == t.size):
        return np.inner(wave, matchedfilt)/(t.size)*2
    else:
        return 0

def matchedSin(wave, fc, fs, symbol_length):
    t = np.r_[0:symbol_length:1.0/fs]
    matchedfilt = np.sin(2*np.pi*fc*t)
    if (wave.size == t.size):
        return np.inner(wave, matchedfilt)/(t.size)*2
    else:
        return 0


def testQAM():
    data = np.random.randint(0,16,160) # [ 5, 2, 7, 4, 11, 2, 0, 1, 14, 4, 8, 6, 10, 5, 2, 3, 1, 11]
    print data
    modulated = modulateQAM16(data, 4*480.0, 48000.0, 0.005)
    
    modulated += .25*np.random.normal(size=modulated.size)
    #myplot(modulated)
    #spectrogram(modulated)
    
    
    demod = demodulateQAM16(modulated, 4*480.0, 48000.0, 0.005)

   
    print(demod)
    print np.sum(demod == data)/160.0


if __name__ == '__main__':
    testQAM()

