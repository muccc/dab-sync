import iq
import find_start
import auto_correlate
import correlate
import make_prs
import sys
import parameters
import numpy
import os
import getopt
import matplotlib.pyplot as plt

options, remainder = getopt.getopt(sys.argv[1:], 'r:f:', [
                                                         'rate=',
                                                         'format=',
                                                         ])



sample_rate = 2000000

for opt, arg in options:
    if opt in ('-r', '--rate'):
        sample_rate = int(arg)
    if opt in ('-f', '--format'):
        iq.set_type(arg)

dp = parameters.dab_parameters(1, sample_rate)
prs = make_prs.modulate_prs(sample_rate, True)
frame_length = int(sample_rate * 96e-3)
sample_offset = 0

f = open(remainder[0], "rb")
signal = iq.read(f, count=frame_length)

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
iq.skip(f, sample_offset)

prs_len=len(prs)

shift_signal = numpy.exp(complex(0,-1)*numpy.arange(prs_len)*2*numpy.pi*freq_offset/float(sample_rate))

print len(signal), frame_length

sample_offset = 0
prev_start = 0
starts = []
while True:
    signal = iq.read(f, count=prs_len)
    if len(signal)!=prs_len: break
    sample_offset += prs_len

    signal = signal * shift_signal
    relative_start, cor, phase = correlate.estimate_prs_fine(signal[:len(prs)], prs)
    print relative_start
    start = sample_offset + relative_start
    if prev_start: starts.append(start - prev_start)
    print start - prev_start
    prev_start = start

    offset = frame_length-prs_len+1*int(relative_start+0.5)
    iq.skip(f, offset)
    sample_offset += offset

plt.plot(starts)
plt.show()
