#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Sun Sep 23 22:58:19 2018
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import dab_step
import osmosdr
import time


class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2048000

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + '' )
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(222064000, 0)
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
        self.dab_step_dab_sync_0 = dab_step.dab_sync()
        self.blocks_tag_debug_0 = blocks.tag_debug(gr.sizeof_gr_complex*1, '', ""); self.blocks_tag_debug_0.set_display(True)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.dab_step_tune_timer_0, 'command'), (self.osmosdr_source_0, 'command'))
        self.connect((self.dab_step_dab_sync_0, 0), (self.blocks_tag_debug_0, 0))
        self.connect((self.dab_step_dab_sync_0, 0), (self.dab_step_tune_timer_0, 0))
        self.connect((self.dab_step_tune_timer_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.dab_step_dab_sync_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)


def main(top_block_cls=top_block, options=None):

    tb = top_block_cls()
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
