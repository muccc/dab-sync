import iq
import sys
import numpy
import make_prs
import matplotlib.pyplot as plt
import scipy.signal
import cmath

def delay(signal, delay):

    sinc_vect = [0] * 21
    for i in range(21):
        sinc_vect[i] = numpy.sinc(numpy.pi * (10.0 - i - delay))
    return numpy.convolve(signal, sinc_vect, 'same')

def estimate_prs_fine_delay(signal, prs, delay_estimate):
    #c = scipy.signal.fftconvolve(signal, numpy.conj(prs), 'same')
    #delay_estimate = 0
    print "delay_estimate", delay_estimate
    signal = delay(signal, delay_estimate)
    c = numpy.correlate(signal, prs, 'same')
    prs_middle = numpy.argmax(numpy.abs(c))

    #Interpolate the result to get a finer resolution.
    # Based on http://www.dsprelated.com/dspbooks/sasp/Quadratic_Interpolation_Spectral_Peaks.html

    alpha_index = prs_middle - 1
    beta_index = prs_middle
    gamma_index = prs_middle + 1
    alpha = numpy.abs(c[alpha_index])
    beta = numpy.abs(c[beta_index])
    gamma = numpy.abs(c[gamma_index])

    #correction = -0.5 * alpha/beta + 0.5 * gamma/beta
    #correction = -alpha / (alpha + beta) + gamma / (gamma + beta)
    correction = 0.5 * (alpha - gamma) / (alpha - 2*beta + gamma)
    print "correction", correction
    correction += delay_estimate
    print "correction + delay", correction

    prs_middle_fine = prs_middle + correction
    #print prs_middle - len(prs) / 2, "% .02f" % correction,

    #plt.plot(numpy.abs(c))
    #plt.show()
    return prs_middle_fine - len(prs) / 2, numpy.abs(c[prs_middle]), numpy.angle(c[prs_middle]), correction


def estimate_prs_fine(signal, prs):
    #c = scipy.signal.fftconvolve(signal, numpy.conj(prs), 'same')
    c = numpy.correlate(signal, prs, 'same')
    prs_middle = numpy.argmax(numpy.abs(c))

    #Interpolate the result to get a finer resolution.
    # Based on http://www.dsprelated.com/dspbooks/sasp/Quadratic_Interpolation_Spectral_Peaks.html

    alpha_index = prs_middle - 1
    beta_index = prs_middle
    gamma_index = prs_middle + 1
    alpha = numpy.abs(c[alpha_index])
    beta = numpy.abs(c[beta_index])
    gamma = numpy.abs(c[gamma_index])
    correction = 0.5 * (alpha - gamma) / (alpha - 2*beta + gamma)
    prs_middle_fine = prs_middle + correction

    #plt.plot(numpy.abs(c))
    #plt.show()
    return prs_middle_fine - len(prs) / 2, numpy.abs(c[prs_middle]), numpy.angle(c[prs_middle])


def estimate_prs(signal, prs):
    #c = scipy.signal.fftconvolve(signal, numpy.conj(prs), 'same')
    c = numpy.correlate(signal, prs, 'same')
    prs_middle = numpy.argmax(numpy.abs(c))

    #plt.plot(numpy.abs(c))
    #plt.show()
    return prs_middle - len(prs) / 2, numpy.abs(c[prs_middle]), numpy.angle(c[prs_middle])

def find_rough_freq_offset(signal, fine_freq_offset, prs, dp, sample_rate):
    prs_signal = signal[:int(len(prs)*1.5)]

    shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(prs_signal))*2*numpy.pi*fine_freq_offset/float(sample_rate))
    prs_signal = prs_signal * shift_signal

    max_cor = 0
    best_loc = 0
    best_shift = 0
    for offset_khz in range(-10, 10):
        #print offset_khz
        offset = offset_khz * 1000
        shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(prs_signal))*2*numpy.pi*offset/float(sample_rate))
        prs_signal_shifted = prs_signal * shift_signal

        #iq.write("/tmp/bar.cfile", signal_shifted)
        location, cor, phase = estimate_prs(prs_signal_shifted, prs)    
        #print offset, cor, location, phase

        if cor > max_cor:
            #print "better"
            max_cor = cor
            best_loc = location
            best_shift = offset

    #print max_cor, best_loc, best_shift
    #print best_loc - len(prs)/2 + 492
    #print best_loc - len(prs)/2 + 492, best_shift
    #return (best_loc - len(prs)/2 + dp.cp_length, best_shift)
    print best_loc, best_shift
    return (best_loc, best_shift)

if __name__ == "__main__":
    sample_rate = 2000000
    Tu = sample_rate / 1000
    prs = make_prs.modulate_prs(sample_rate, True)
    print "PRS Length:", len(prs)


    signal = iq.read(sys.argv[1])

    #signal = signal[1254:1254+len(prs)+50]

    #offset = 260*2 - 6
    offset = -540 - 6000
    #offset = 260 - 6
    #offset = 260 - 7000
    #shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*offset/float(sample_rate))
    #signal = signal * shift_signal

    #phase = -1.21851901212
    #signal = signal * cmath.rect(1,-phase)

    max_cor = 0
    best_loc = 0
    best_shift = 0
    #for offset_khz in range(0, 1):
    #for offset_khz in range(-10, 10):
    #for offset_khz in range(-8, -6):
    #    offset = offset_khz * 1000
        #print offset_khz
    for offset in range(offset-500, offset+500):
        shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*offset/float(sample_rate))
        signal_shifted = signal * shift_signal

        iq.write("/tmp/bar.cfile", signal_shifted)
        location, cor, phase = estimate_prs(signal_shifted, prs)    
        print offset, cor, location, phase

        if cor > max_cor:
            #print "better"
            max_cor = cor
            best_loc = location
            best_shift = offset

    print max_cor, best_loc, best_shift
    print best_loc + 492
