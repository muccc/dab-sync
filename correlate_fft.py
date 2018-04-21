import iq
import sys
import numpy
import make_prs
import matplotlib.pyplot as plt
import scipy.signal
import cmath

def estimate_prs(signal, prs):
    c = scipy.signal.fftconvolve(signal, prs, 'same')
    prs_middle = numpy.argmax(numpy.abs(c))

    #plt.plot(numpy.abs(c))
    #plt.show()
    return prs_middle, numpy.abs(c[prs_middle]), numpy.angle(c[prs_middle])



sample_rate = 2000000
Tu = sample_rate / 1000
prs = make_prs.modulate_prs(sample_rate)
print "PRS Length:", len(prs)


signal = iq.read(sys.argv[1])

#signal = signal[1254:1254+len(prs)+50]

offset = 260
#offset = 260 - 7000
shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*offset/float(sample_rate))
signal = signal * shift_signal

#phase = -1.21851901212
#signal = signal * cmath.rect(1,-phase)

'''
max_cor = 0
best_loc = 0
best_shift = 0
for offset_khz in range(-10, 10):
    offset = offset_khz * 1000
    print offset
    shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*offset/float(sample_rate))
    signal_shifted = signal * shift_signal

    iq.write("/tmp/bar.cfile", signal_shifted)
    location, cor, phase = estimate_prs(signal_shifted, prs)    
    print cor, location, phase

    if cor > max_cor:
        print "better"
        max_cor = cor
        best_loc = location
        best_shift = offset

print max_cor, best_loc, best_shift
'''
