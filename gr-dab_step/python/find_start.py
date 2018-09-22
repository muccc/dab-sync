import sys
import numpy
import scipy.signal

def find_start(signal, sample_rate = 2000000):
    input_low_pass = scipy.signal.firwin(13, 1000./sample_rate)

    count = 100e-3 * sample_rate
    signal_mag = numpy.abs(signal)
    signal_mag_filtered = scipy.signal.fftconvolve(signal_mag, input_low_pass, mode='same')
    level = numpy.average(signal_mag_filtered)

    low_count = 0
    for i in xrange(len(signal_mag)):
        if signal_mag_filtered[i] < level / 1.2:
            low_count += 1
        else:
            #if low_count > 100:
            if low_count > sample_rate * 0.5e-3:
                print "start at", i
                return i

            low_count = 0

    raise Exception("No start found")
    return 0


if __name__ == "__main__":
    import iq
    signal = iq.read(sys.argv[1])
    print find_start(signal)
