import parameters
import numpy.fft
import struct
from itertools import izip
import matplotlib.pyplot as plt
import iq

def make_prs(sample_rate=2048000):
    dp = parameters.dab_parameters(1, sample_rate)
    prs = dp.prn

    def write(file_name, signal):
        if type(signal)!=numpy.complex64:
            signal=numpy.asarray(signal,dtype=numpy.complex64)
        signal.tofile(file_name)

    def interleave(symbol):
        return [symbol[i] for i in dp.frequency_interleaving_sequence_array]

    def pad(symbol):
        zeros_on_left = (dp.fft_length-dp.num_carriers)/2;
        zeros_on_right = dp.fft_length - zeros_on_left - dp.num_carriers - 1
        return [0] * zeros_on_left + symbol[0:dp.num_carriers/2] + [0] + symbol[dp.num_carriers/2:] + [0] * zeros_on_right

    #print prs
    interleaved_prs = interleave(prs)

    #padded_prs = pad(interleaved_prs)
    padded_prs = pad(prs)
    return padded_prs



def modulate_prs(sample_rate=2048000, cp=True):
    dp = parameters.dab_parameters(1, sample_rate)
    padded_prs = make_prs(sample_rate)

    #plt.plot(numpy.abs(padded_prs))
    #plt.show()
    #plt.plot(numpy.angle(padded_prs))
    #plt.show()

    shifted_prs = numpy.fft.fftshift(padded_prs)

    #plt.plot(numpy.abs(shifted_prs))
    #plt.show()

    ifft_prs = numpy.fft.ifft(shifted_prs)

    if cp:
        print "CP length", dp.cp_length
        cycled_prs = numpy.concatenate((ifft_prs[-dp.cp_length:], ifft_prs))
        return cycled_prs
    else:
        return ifft_prs

    #print cycled_prs
    #print len(cycled_prs)

if __name__ == "__main__":

    #sample_rate = 2048000
    sample_rate = 2000000
    cycled_prs = modulate_prs(sample_rate)
    iq.write("/tmp/generated.cfile", cycled_prs)

    signal = numpy.concatenate(([0] * 2048, cycled_prs))
    #signal = numpy.concatenate(([0] * 2048, cycled_prs, [0] * 2048, cycled_prs))
    #signal = numpy.concatenate(([0] * 2048, prs, [0] * 2048, prs))

    iq.write("/tmp/foo.cfile", signal)
    #print dp.frequency_interleaving_sequence_array

    dp = parameters.dab_parameters(1, sample_rate)
    Tu = dp.fft_length

    offset = 600
    shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*offset/float(sample_rate))
    signal = signal * shift_signal

    time_shifted_signal = signal[Tu:]

    auto_correlated = [0] * len(time_shifted_signal)
    for i in range(len(time_shifted_signal)):
        auto_correlated[i] = numpy.angle(signal[i] * numpy.conj(time_shifted_signal[i]))/ 2 / 3.14/(2048./sample_rate)

    #print auto_correlated

    iq.write("/tmp/bar.cfile", auto_correlated)


