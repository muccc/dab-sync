import iq
import sys
import numpy
import make_prs
import cmath
import matplotlib.pyplot as plt

sample_rate = 2000000
Tu = sample_rate / 1000

signal = iq.read(sys.argv[1])

#signal = signal[1254:1254+len(prs)+50]

#for i in range(-300,300,30):
for i in range(-5,5,1):
#for i in range(0, 100, 1):
#for i in range(0, 1, 1):
    offset = 260 - 7000
    #offset = 260 - 7000 + i
    print i
    #offset = 260 - 7000
    shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*offset/float(sample_rate))
    signal_shifted = signal * shift_signal

    #phase = -1.21851901212
    #phase = 1.21851901212
    #signal_shifted = signal_shifted * cmath.rect(1,-phase)

    #signal_shifted = signal_shifted[1305:1305+Tu]
    #signal_shifted = signal_shifted[1305+i:1305+Tu+i]
    #signal_shifted = signal_shifted[1797+i:1797+Tu+i]
    signal_shifted = signal_shifted[1799+i:1799+Tu+i]
    print len(signal_shifted)

    #prs = numpy.fft.fftshift(numpy.fft.fft(signal_shifted))[250:1750]
    prs = numpy.fft.fftshift(numpy.fft.fft(signal_shifted))

    plt.plot(numpy.abs(prs))
    plt.show()
    plt.plot(numpy.angle(prs))
    plt.show()

    #i = numpy.real(prs)
    #q = numpy.imag(prs)

    #plt.scatter(i, q)
    #plt.show()
