
import numpy as np


mode4coef = [ [1,0], [0,1], [-1,0], [0, -1] ]
mode16coef = [ [1,1], [1, .333], [1,-.333], [1,-1],
               [.333, 1], [.333, .333], [.333,-.333], [.333, -1],
               [-.333, 1], [-.333, .333], [-.333,-.333], [-.333, -1],
               [-1,1], [-1, .333], [-1,-.333], [-1.0,-1.0] ]

def modulateQAM(data, mode, fc, fs, symbol_length):
    if(np.max(data) >= mode):
        print("All data elements must be <= mode")
        return

    waveout = []
    t = np.r_[0:symbol_length:1.0/fs]
    d = data
    if (mode == 4):
       # for d in data:
        wave = mode4coef[d][0]*np.cos(2*np.pi*fc*t) + mode4coef[d][1]*np.sin(2*np.pi*fc*t)
        waveout = np.append(waveout, wave)

    elif (mode == 16):
        #for d in data:
        wave = mode16coef[d][0]*np.cos(2*np.pi*fc*t) + mode16coef[d][1]*np.sin(2*np.pi*fc*t)
        waveout = np.append(waveout, wave)
    else:
        print("Mode", mode, "not supported")
        return

    return waveout

def demodulateQAM(wave, mode, fc, fs, symbol_length):

    num_symbols = wave.size / (fs*symbol_length)

    ret = []

    for s in np.linspace(0,wave.size, num_symbols):

        A = matchedCos(wave[s:s+fs*symbol_length], fc, fs, symbol_length)
        B = matchedSin(wave[s:s+fs*symbol_length], fc, fs, symbol_length)
   # print A, B
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
    data = 11 #[ 5, 2, 7, 4, 11, 2, 0, 1, 14, 4, 8, 6, 10, 5, 2, 3, 1, 11]

    modulated = modulateQAM(data, 16, 440.0, 48000.0, 0.1)
    modulated += np.random.normal(size=modulated.size)
    demod = demodulateQAM(modulated, 16, 440.0, 48000.0, 0.1)

    print(demod == data)


if __name__ == '__main__':
    testQAM()

