# vim: set ts=4 sw=4 tw=0 et pm=:
import struct
import numpy
from itertools import izip


class IQReader(object):
    def __init__(self, f, sample_type='c32'):
        self.sample_type = sample_type
        self.offset = 0
        self.f = f

    def set_type(self,sample_type):
        self.sample_type=sample_type

    def read(self, count=-1):
        sample_offset = self.offset
        self.offset += count
        if self.sample_type=='c32':
            return self.read32(count), sample_offset
        elif self.sample_type=='c16':
            return self.read16(count), sample_offset
        elif self.sample_type=='c8':
            return self.read8(count), sample_offset
        else:
            raise ValueError('invalid sample_type')

    def read32(self, count=-1):
        signal = numpy.fromfile(self.f, dtype=numpy.complex64, count=count)
        return signal

    def read16(self, count=-1):
        if count>0: count=count*2
        signal = numpy.fromfile(self.f, dtype=numpy.int16, count=count)
        signal = signal.astype(numpy.float32) # convert to float
        signal = signal/32768.                # Normalize
        signal = signal.view(numpy.complex64) # reinterpret as complex
        return signal

    def read8(self, count=-1):
        if count>0: count=count*2
        signal = numpy.fromfile(self.f, dtype=numpy.uint8, count=count)
        signal = signal.astype(numpy.float32) # convert to float
        signal = (signal-127.35)/128.         # Normalize
        signal = signal.view(numpy.complex64) # reinterpret as complex
        return signal

    def skip(self, count):
        self.offset += count
        if self.sample_type=='c32':
            self.skipN(count*8)
        elif self.sample_type=='c16':
            self.skipN(count*4)
        elif self.sample_type=='c8':
            self.skipN(count*2)
        else:
            raise ValueError('invalid sample_type')

    def skipN(self, count):
        try:
            self.f.seek(count,SEEK_CUR)
        except:
            if (count<0):
                print "Negative seek on non-file"
            else:
                self.f.read(count)

def read(file_name):
   return IQReader(open(file_name)).read()[0]

def write(file_name, signal):
    if type(signal)!=numpy.complex64:
        signal=numpy.asarray(signal,dtype=numpy.complex64)
    signal.tofile(file_name)

def shift(signal, sample_rate, offset):
    shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*offset/float(sample_rate))
    return  signal * shift_signal

def rotate(signal, angle):
    return signal * cmath.rect(1, angle)


