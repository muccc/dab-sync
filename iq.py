# vim: set ts=4 sw=4 tw=0 et pm=:
import struct
import numpy
from itertools import izip

sample_type='c32'

def set_type(the_type):
    global sample_type
    sample_type=the_type

def write(file_name, signal):
    if type(signal)!=numpy.complex64:
        signal=numpy.asarray(signal,dtype=numpy.complex64)
    signal.tofile(file_name)

def read(file_name, count=-1):
    if sample_type=='c32':
        return read32(file_name, count)
    elif sample_type=='c8':
        return read8(file_name, count)
    else:
        raise ValueError('invalid sample_type')

def read32(file_name, count=-1):
    signal = numpy.fromfile(file_name, dtype=numpy.complex64, count=count)
    return signal

def read8(file_name, count=-1):
    if count>0: count=count*2
    signal = numpy.fromfile(file_name, dtype=numpy.uint8, count=count)
    signal = signal.astype(numpy.float32) # convert to float
    signal = (signal-127.35)/128.         # Normalize
    signal = signal.view(numpy.complex64) # reinterpret as complex
    return signal

def skip(file_name, count):
    if sample_type=='c32':
        skipN(file_name, count*8)
    elif sample_type=='c8':
        skipN(file_name,count*2)
    else:
        raise ValueError('invalid sample_type')

def skipN(file_name, count):
    try:
        file_name.seek(count,SEEK_CUR)
    except:
        if (count<0):
            print "Negative seek on non-file"
        else:
            file_name.read(count)

def shift(signal, sample_rate, offset):
    shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*offset/float(sample_rate))
    return  signal * shift_signal

def rotate(signal, angle):
    return signal * cmath.rect(1, angle)


