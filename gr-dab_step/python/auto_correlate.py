import sys
import numpy
#import matplotlib.pyplot as plt


def auto_correlate(signal, dp, sample_rate):
    Tu = dp.fft_length
    #Tu = sample_rate / 1000 # 1 ms
    print Tu

    signal_slice = signal[:Tu * 2]
    time_shifted_signal = signal_slice[Tu:]
    auto_correlated = [0] * dp.cp_length
    for i in range(len(auto_correlated)):
        auto_correlated[i] = numpy.angle(signal[i] * numpy.conj(time_shifted_signal[i]))/ 2 / 3.14 * Tu / 2
    #plt.plot(auto_correlated)
    #plt.show()

    fine_offset = numpy.average(auto_correlated)

    print "Fine frequency offset:", fine_offset
    return fine_offset


if __name__ == "__main__":
    import iq
    sample_rate = 2000000

    #Tu = int(2048 * (sample_rate/2048000.))
    Tu = sample_rate / 1000

    signal = iq.read(sys.argv[1])

    time_shifted_signal = signal[Tu:]

    auto_correlated = [0] * len(time_shifted_signal)
    for i in range(len(time_shifted_signal)):
        #auto_correlated[i] = numpy.angle(signal[i] * numpy.conj(time_shifted_signal[i]))/ 2 / 3.14 * 1000
        auto_correlated[i] = numpy.angle(signal[i] * numpy.conj(time_shifted_signal[i]))/ 2 / 3.14 * Tu / 2

    #print auto_correlated

    iq.write("/tmp/bar.cfile", auto_correlated)
