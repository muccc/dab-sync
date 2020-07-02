#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Sun Jun 21 16:09:21 2020
##################################################


from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import dab_step
import dab_step.make_prs
import dab_step.parameters
import osmosdr
import time


class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2048000
        self.parameters = parameters = dab_step.parameters.dab_parameters(1, samp_rate)
        self.modulated_prs = modulated_prs = dab_step.make_prs.modulate_prs(samp_rate, True)

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + '' )
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(222064000 * 1 + 178352000 * 0, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(10, 0)
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)

        self.dab_step_tune_timer_0 = dab_step.tune_timer()
        self.dab_step_dab_sync_cpp_0 = dab_step.dab_sync_cpp(samp_rate, parameters.fft_length, parameters.cp_length, modulated_prs)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.dab_step_tune_timer_0, 'command'), (self.osmosdr_source_0, 'command'))
        self.connect((self.dab_step_dab_sync_cpp_0, 0), (self.dab_step_tune_timer_0, 0))
        self.connect((self.dab_step_tune_timer_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.dab_step_dab_sync_cpp_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_parameters(dab_step.parameters.dab_parameters(1, self.samp_rate))
        self.set_modulated_prs(dab_step.make_prs.modulate_prs(self.samp_rate, True))
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)

    def get_parameters(self):
        return self.parameters

    def set_parameters(self, parameters):
        self.parameters = parameters

    def get_modulated_prs(self):
        return self.modulated_prs

    def set_modulated_prs(self, modulated_prs):
        self.modulated_prs = modulated_prs


def main(top_block_cls=top_block, options=None):

    tb = top_block_cls()
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
