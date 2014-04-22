import matplotlib.pyplot as plt


def myplot(x, w=8, h=4):

    fig = plt.figure(figsize=(w,h))
    ax = fig.add_subplot(111)
    ax.plot(range(x.size), x)
    fig.show()


def spectrum(x):

    X = np.fft.fftshift(np.fft.fft(x))
    X = np.log(np.abs(X))
    myplot(X)