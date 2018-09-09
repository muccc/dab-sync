#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2018 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr
import osmosdr
import tunetest
import threading


class tune_notifier(gr.feval_ll):
    """
    This class allows C++ code to callback into python.
    """
    def __init__(self, b):
        gr.feval_ll.__init__(self)
        self.b = b

    def eval(self, state):
        """
        This method is called by vector_sink_cn when it is full
        """
        threading.Thread(target=self.b, args = (state, )).start()

class RTLDABStep(gr.hier_block2):
    """
    docstring for block RTLDABStep
    """
    def __init__(self, gain):
        gr.hier_block2.__init__(self,
            "RTLDABStep",
            gr.io_signature(0,0,0),  # Input signature
            gr.io_signature(2, 2, gr.sizeof_gr_complex)# Output signature
            )

        self.gain = gain
        self.sample_rate = 2048000
        self.ppm = 0

        #rtl_args = 'buflen=20480'
        #rtl_args = 'buflen=40960'
        rtl_args = ''
        self.rtlsdr_source = osmosdr.source(args=rtl_args) 

        self.rtlsdr_source.set_sample_rate(self.sample_rate)
        self.rtlsdr_source.set_freq_corr(self.ppm, 0)
#       self.rtlsdr_source.set_dc_offset_mode(2, 0)
#       self.rtlsdr_source.set_iq_balance_mode(2, 0)
        self.rtlsdr_source.set_gain_mode(False, 0)

        self.rtlsdr_source.set_if_gain(24, 0)
        self.rtlsdr_source.set_gain(24, 0)

        #self.rtlsdr_source.set_if_gain(3, 0)
        #self.rtlsdr_source.set_gain(4, 0)

        self.rtlsdr_source.set_antenna("", 0)
#       self.rtlsdr_source.set_bandwidth(0, 0)

        self.notifier = tune_notifier(self.tune)
        self.tunetest = tunetest.tunetest(self.notifier)


        self.connect((self.rtlsdr_source, 0), (self.tunetest, 0), (self, 0))
        self.connect((self.rtlsdr_source, 0), (self, 1))

        #self.freq1 = 100e6
        #self.freq1 = 178352000
        self.freq1 = 220352000
        self.freq2 = 222064000
        #self.freq2 = 178352001

        self.rtlsdr_source.set_center_freq(self.freq1, 0)
        self.state = False

        self.d_mutex = threading.Lock()

    def tune(self, state):
        self.d_mutex.acquire()
        try:
            print state
            if self.state:
                self.rtlsdr_source.set_center_freq(self.freq1, 0)
            else:
                self.rtlsdr_source.set_center_freq(self.freq2, 0)
            self.state = not self.state
        except Exception, e:
            print "Vector sink fullness notification exception: ", e
        finally:
            self.d_mutex.release()

