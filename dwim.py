import iq
import find_start
import auto_correlate
import correlate
import make_prs
import sys
import parameters
import numpy
import os

sample_rate = 2000000
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
f.seek(sample_offset*8,os.SEEK_CUR)

prs_len=len(prs)

shift_signal = numpy.exp(complex(0,-1)*numpy.arange(prs_len)*2*numpy.pi*freq_offset/float(sample_rate))

print len(signal), frame_length
while True:
    signal = iq.read(f, count=prs_len)
    if len(signal)!=prs_len: break

    signal = signal * shift_signal
    start2 = correlate.estimate_prs(signal[:len(prs)], prs)
    print start2
    f.seek((frame_length-prs_len+1*start2[0])*8,os.SEEK_CUR)
