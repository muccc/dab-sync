import iq
import find_start
import auto_correlate
import correlate
import make_prs
import sys
import parameters
import numpy

sample_rate = 2000000
dp = parameters.dab_parameters(1, sample_rate)
prs = make_prs.modulate_prs(sample_rate, True)
frame_length = int(sample_rate * 96e-3)
sample_offset = 0

signal = iq.read(sys.argv[1])

start = find_start.find_start(signal, sample_rate)
signal = signal[start:]
sample_offset += start

fine_freq_offset = auto_correlate.auto_correlate(signal, dp, sample_rate)

start, rough_freq_offset = correlate.find_rough_freq_offset(signal, -fine_freq_offset, prs, dp, sample_rate)
signal = signal[start:]
sample_offset += start

freq_offset = rough_freq_offset - fine_freq_offset

shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*freq_offset/float(sample_rate))
signal = signal * shift_signal

iq.write("/tmp/bar.cfile", signal)

print start

while len(signal) > frame_length + len(prs):
    signal = signal[frame_length:]
    sample_offset += frame_length

    print len(signal)
    start2 = correlate.estimate_prs(signal[:len(prs)], prs)

    print start2
