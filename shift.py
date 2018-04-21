import iq
import sys
import numpy
import make_prs
import matplotlib.pyplot as plt
import scipy.signal


sample_rate = 2000000

signal = iq.read(sys.argv[1])

offset = -6000
shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*offset/float(sample_rate))
signal = signal * shift_signal

iq.write("/tmp/bar.cfile", signal)

