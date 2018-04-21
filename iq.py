# vim: set ts=4 sw=4 tw=0 et pm=:
import struct
import numpy
from itertools import izip

def write(file_name, signal):
    if type(signal)!=numpy.complex64:
        signal=numpy.asarray(signal,dtype=numpy.complex64)
    signal.tofile(file_name)

def read(file_name, count=-1):
    signal = numpy.fromfile(file_name, dtype=numpy.complex64, count=count)
    return signal

def shift(signal, sample_rate, offset):
    shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*offset/float(sample_rate))
    return  signal * shift_signal

def rotate(signal, angle):
    return signal * cmath.rect(1, angle)


