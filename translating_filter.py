#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Sun Apr 29 22:00:36 2018
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import sys


class top_block(gr.top_block):

    def __init__(self, infile, outfile, sample_rate, shift=0, decimation=1, bandwidth=None):
        gr.top_block.__init__(self, "Top Block")


        taps = filter.firdes.low_pass_2(1, sample_rate, bandwidth, bandwidth/10, 60)

        #make(int decimation, pmt_vector_cfloat taps, double center_freq, double sampling_freq) -> freq_xlating_fir_filter_ccc_sptr
        self.freq_xlating_fir_filter = filter.freq_xlating_fir_filter_ccc(decimation, taps, shift, sample_rate)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, infile, False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, outfile, False)
        self.blocks_file_sink_0.set_unbuffered(False)


        #self.connect((self.blocks_file_source_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.freq_xlating_fir_filter, 0))
        self.connect((self.freq_xlating_fir_filter, 0), (self.blocks_file_sink_0, 0))


def main(top_block_cls=top_block, options=None):

    shift = 5288000
    if sys.argv[1] == 'up':
        pass
    elif sys.argv[1] == 'down':
        shift = -shift
    else:
        print "up or down?"
        return

    tb = top_block_cls(sys.argv[2], sys.argv[3], 2048000*8, shift, 8, 2048000)
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
