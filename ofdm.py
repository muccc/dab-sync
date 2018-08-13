import numpy.fft
import numpy
import cmath
import matplotlib.pyplot as plt
import bitstring

class ofdm_decoder(object):
    def __init__(self, dp):
        self._dp = dp
        self._last_symbol_carriers = None

    def reset(self, prs_samples):
        self._last_symbol_carriers = self._fft(prs_samples)
        #plt.scatter(self._last_symbol_carriers.real, self._last_symbol_carriers.imag)
        #plt.ylim(-180, 180)
        #plt.plot(numpy.rad2deg(numpy.angle(self._last_symbol_carriers)))
        #plt.show()

        #phase_offset = self._last_symbol_carriers * numpy.conj(self._dp.prn)
        #plt.plot(numpy.rad2deg(numpy.angle(phase_offset)))
        #plt.ylim(-180, 180)
        #plt.show()
        #print self._last_symbol_carriers

    def _fft(self, symbol_samples, offset=None):
        if offset == None:
            offset = self._dp.cp_length
        fft_input = symbol_samples[offset:offset+self._dp.fft_length]
        #fft_input = symbol_samples[:-self._dp.cp_length]
        fft_output = numpy.fft.fft(fft_input)
        carriers = numpy.fft.fftshift(fft_output)
        #print abs(carriers[1024])
        #print "carriers[256:266]", carriers[256:266]
        #print "carriers[1024:1034]", carriers[1024:1034]
    
        #print self._dp.fft_length / 2 - self._dp.num_carriers/2, self._dp.fft_length / 2
        #print self._dp.fft_length / 2 +1, self._dp.fft_length / 2 + 1 + self._dp.num_carriers/2

        front = carriers[self._dp.fft_length / 2 - self._dp.num_carriers/2: self._dp.fft_length / 2]
        back = carriers[self._dp.fft_length / 2 +1: self._dp.fft_length / 2 + 1 + self._dp.num_carriers/2]

        #print "front[:10]", front[:10]
        #print "front[:10](turned)", front[:10] * numpy.conj(front[0]) * 1j / 6
        #print "back[:10]", back[:10]
        return numpy.concatenate((front, back))

    def _phase_diff(self, symbol_carriers):
        #plt.scatter(symbol_carriers.real, symbol_carriers.imag)
        #plt.ylim(-180, 180)
        #plt.plot(numpy.rad2deg(numpy.angle(symbol_carriers)))
        #plt.show()

        diff = symbol_carriers * numpy.conj(self._last_symbol_carriers)
        self._last_symbol_carriers = symbol_carriers

        #print "diff[:10]", diff[:10]
        #plt.scatter(diff.real,diff.imag)
        #plt.ylim(-180, 180)
        #plt.plot(numpy.rad2deg(numpy.angle(diff)))
        #plt.show()

        return diff

    def _deinterleave(self, symbol_carriers):
        #out = [symbol_carriers[self._dp.frequency_deinterleaving_sequence_array[i]] for i in range(len(symbol_carriers))]
        out = [symbol_carriers[self._dp.frequency_interleaving_sequence_array[i]] for i in range(len(symbol_carriers))] # probably this one
        return out

    def _qpsk_demap(self, symbol_carriers):
        data = bitstring.BitArray()
        for carrier in symbol_carriers:
            if carrier.real < 0:
                data.append('0b1')
            else:
                data.append('0b0')
                
        for carrier in symbol_carriers:
            if carrier.imag < 0:
                data.append('0b1')
            else:
                data.append('0b0')

        #print data.bin
        #return data.tobytes()
        return data

    def decode_symbol(self, symbol_samples):
        symbol_carriers = self._fft(symbol_samples)
        symbol_carriers = self._phase_diff(symbol_carriers)
        symbol_carriers = self._deinterleave(symbol_carriers)
        data = self._qpsk_demap(symbol_carriers)

        return data
