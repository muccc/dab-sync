import sys
import iq
import make_prs
import parameters
import numpy
import os
import getopt
import matplotlib.pyplot as plt
import ofdm
import fic
import viterbi
import bindata
import bitstring

options, remainder = getopt.getopt(sys.argv[1:], 'r:f:', [
                                                         'rate=',
                                                         'format=',
                                                         ])


sample_rate = 2048000
sample_type = 'c32'

for opt, arg in options:
    if opt in ('-r', '--rate'):
        sample_rate = int(arg)
    if opt in ('-f', '--format'):
        sample_type = arg

dp = parameters.dab_parameters(1, sample_rate)
#prs_synth = make_prs.modulate_prs(sample_rate, True)
decoder = ofdm.ofdm_decoder(dp)
fic = fic.fic(dp)
#print "dp.prn", dp.prn

f = open(remainder[0], "rb")
reader = iq.IQReader(f, sample_type)

#print(len(prs_synth))
#decoder.reset(prs_synth)

prs_samples, sample_offset = reader.read(count=dp.symbol_length)
decoder.reset(prs_samples)


symbol_samples, sample_offset = reader.read(count=dp.symbol_length)
fic_sym0 = decoder.decode_symbol(symbol_samples)

symbol_samples, sample_offset = reader.read(count=dp.symbol_length)
fic_sym1 = decoder.decode_symbol(symbol_samples)

symbol_samples, sample_offset = reader.read(count=dp.symbol_length)
fic_sym2 = decoder.decode_symbol(symbol_samples)

fics = fic_sym0 + fic_sym1 + fic_sym2
#fics = fic_sym0

fib0 = fics[:dp.fic_punctured_codeword_length]

#print len(fib0)

fib0_unpuctured = fic._unpuncture(fib0)

#print len(fib0_unpuctured)

#polynomials = [0133, 0171, 0145, 0133]
polynomials = [0b1101101,0b1001111,0b1010011,0b1101101]

viterbi_input_data = bindata.BinData(fib0_unpuctured.bin)
deconvoluted = bitstring.BitArray('0b' + str(viterbi.Transitions(polynomials).decode(viterbi_input_data)))

pruned = deconvoluted[:-6]
#print len(pruned.bin)

prbs = bitstring.BitArray('0b' + ''.join([chr(x+0x30) for x in dp.prbs(dp.energy_dispersal_fic_vector_length)]))


foo = (pruned ^ prbs)

print foo.bin
open('test.fib', 'w').write(foo.tobytes())

