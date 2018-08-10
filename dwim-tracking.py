#!/usr/bin/env python2

import iq_fract as iq
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

sample_rate = 2048000
sample_type = 'c32'

multi_starts = []

for opt, arg in options:
    if opt in ('-r', '--rate'):
        sample_rate = int(arg)
    if opt in ('-f', '--format'):
        sample_type = arg

dp = parameters.dab_parameters(1, sample_rate)
prs = make_prs.modulate_prs(sample_rate, True)
frame_length = int(sample_rate * 96e-3)


for filename in remainder:
    f = open(filename, "rb")
    reader = iq.IQReader(f, sample_type)

    #reader.skip(13107200, 0)

    signal, integer_sample_offset, fract_sample_offset = reader.read(count=frame_length)


    #start = 0
    #while start == 0:
    #    start = find_start.find_start(signal, sample_rate)
    #    signal = iq.read(f, count=frame_length)
    rough_start = find_start.find_start(signal, sample_rate)

    signal = signal[rough_start:]
    fine_freq_offset = auto_correlate.auto_correlate(signal, dp, sample_rate)

    fine_start, rough_freq_offset = correlate.find_rough_freq_offset(signal, -fine_freq_offset, prs, dp, sample_rate)
    signal = signal[fine_start:]
    start = rough_start + fine_start

    freq_offset = rough_freq_offset - fine_freq_offset

    shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*freq_offset/float(sample_rate))
    signal = signal * shift_signal

    iq.write("/tmp/bar.cfile", signal)

    print start

    reader.skip(start, 0)

    prs_len=len(prs)

    shift_signal = numpy.exp(complex(0,-1)*numpy.arange(prs_len)*2*numpy.pi*freq_offset/float(sample_rate))

    print len(signal), frame_length

    prev_absolute_start = 0
    lenghts = []
    estimated_lenghts = []
    starts = []
    i = 0
    offset = 0
    error_acc = 0

    while True:
        i+=1
        #print "i", i

        #if i > 10: break
        if i > 500: break

        signal, integer_sample_offset, fract_sample_offset = reader.read(count=prs_len)
        print "read", len(signal), "samples from offset", integer_sample_offset, fract_sample_offset
        if len(signal)!=prs_len: break

        signal = signal * shift_signal
        '''
        fine_freq_offset = auto_correlate.auto_correlate(signal, dp, sample_rate)
        print "fine freq offset before", fine_freq_offset
        fine_shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*-fine_freq_offset/float(sample_rate))
        signal = signal * fine_shift_signal

        fine_freq_offset = auto_correlate.auto_correlate(signal, dp, sample_rate)
        print "fine freq offset after", fine_freq_offset
        '''

        error, cor, phase = correlate.estimate_prs_fine(signal[:len(prs)], prs)
        print "error", error

        absolute_start = integer_sample_offset + fract_sample_offset / 1000. + error
        print "absolute_start:", absolute_start
        starts.append(absolute_start)

        if prev_absolute_start:
            instant_frame_length = absolute_start - prev_absolute_start
            print "instant_frame_length:", instant_frame_length
            lenghts.append(instant_frame_length)
            print i, "% .03f" % (absolute_start - prev_absolute_start - frame_length)
        prev_absolute_start = absolute_start

        P = 0.5
        I = 0.5

        error_acc += error
        estimated_frame_length = frame_length + I * error_acc + P * error 
        print "estimated_frame_length:", estimated_frame_length
        estimated_lenghts.append(estimated_frame_length)


        skip = estimated_frame_length-prs_len
        print "skipping", int(skip),int((skip - int(skip)) * 1000), "samples"
        reader.skip(int(skip), int((skip - int(skip)) * 1000))


    print max(lenghts) - min(lenghts)

    plt.plot(lenghts[10:])
    #plt.plot(estimated_lenghts[10:])
    #plt.yscale(lower=1, upper=3)
    #plt.ylim(-0.08, +0.08)
    #plt.ylim(frame_length-1, frame_length+1)
    plt.show()

    print starts
    multi_starts.append(starts)

#plt.show()
print multi_starts

start_0 = numpy.array(multi_starts[0])
for start in multi_starts[1:]:
    l = min(len(start_0), len(start))
    plt.plot(start_0[:l] - numpy.array(start)[:l])
plt.show()

