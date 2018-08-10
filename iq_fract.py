# vim: set ts=4 sw=4 tw=0 et pm=:
import struct
import numpy
from itertools import izip

def delay(signal, delay):
    print "delay", delay, len(signal)
    if delay == 0:
        return signal
    sinc_vect = [0] * 201
    for i in range(201):
        sinc_vect[i] = numpy.sinc(100.0 - i - delay)
    return numpy.convolve(signal, sinc_vect, 'same')


class IQReader(object):
    def __init__(self, f, sample_type='c32', fract=1000):

        if sample_type not in ['c32', 'c16', 'c8']:
            raise ValueError('invalid sample_type')

        self.sample_type = sample_type
        self.f = f
        self.fract = fract

        self.sample_cache = self._read(1)[0]
        self.integer_offset = 0
        self.fract_offset = 0


    def read(self, count):
        integer_sample_offset = self.integer_offset
        fract_sample_offset = self.fract_offset

        self.integer_offset += count

        samples = self._read(count)

        if len(samples) != count:
            return [], 0, 0
        samples = numpy.concatenate(([self.sample_cache], samples))

        self.sample_cache = samples[-1]

        return delay(samples[:-1], float(self.fract_offset) / self.fract), integer_sample_offset, fract_sample_offset


    def skip(self, integer_count, fract_count):
        assert fract_count < self.fract

        current_integer_offset = self.integer_offset
        current_fract_offset = self.fract_offset

        target_integer_offset = current_integer_offset + integer_count + (current_fract_offset + fract_count) / self.fract
        target_fract_offset = (current_fract_offset + fract_count) % self.fract


        count = target_integer_offset - current_integer_offset
        if count > 0:
            self._skip(count - 1)
            try:
                self.sample_cache = self._read(1)[0]
            except:
                pass


        self.integer_offset = target_integer_offset
        self.fract_offset = target_fract_offset

    def _read(self, count):
        print "_read", count
        if self.sample_type=='c32':
            samples =  self.read32(count)
        elif self.sample_type=='c16':
            samples =  self.read16(count)
        elif self.sample_type=='c8':
            samples = self.read8(count)
        return samples

    def _skip(self, count):
        print "_skip", count
        if self.sample_type=='c32':
            self.skipN(count*8)
        elif self.sample_type=='c16':
            self.skipN(count*4)
        elif self.sample_type=='c8':
            self.skipN(count*2)

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


