#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2018 gr-dab_step author.
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

import numpy
from gnuradio import gr
import pmt
from monotonic_cffi import monotonic
from threading import Timer
import signal

class tune_timer(gr.sync_block):
    """
    docstring for block tune_timer
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="tune_timer",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])
        self.message_port_register_out(gr.pmt.intern('command'))
        self.sample_rate = 2048000
        self.last_rx_time = (None, None)
        self.last_rx_time = (0, 0)
        self.i = 0
        self.t1 = 0
        signal.signal(signal.SIGALRM, self.handler)


    def monotonic_raw_from_offset(self, offset):
        return (self.last_rx_time[1] + (offset - self.last_rx_time[0]) * 1e6 / float(self.sample_rate))/1e6

    def send_tune(self, freq):
        cmd = pmt.cons(pmt.intern("set_center_freq"),
                pmt.list2(pmt.from_double(freq), pmt.from_uint64(0)))
        self.message_port_pub(pmt.intern('command'), cmd)

    def handler(self, signum, frame):
        self.tune_1()

    def tune_1(self):
        t = monotonic()
        #self.t20 = monotonic()
        self.timer = Timer(0.082, self.tune_2)
        self.timer.start()

        self.send_tune(100000000)

        #print "t1 fired after", self.t10 - t, "should have after", self.t1

    def tune_2(self):
        #t = monotonic()
        self.send_tune(222064000)
        #print "t2 fired after", self.t20 - t, "should have after 0.02"

    def update_timer(self, next_prs):
        self.i += 1
        if self.i < 10:
            return
        self.t10 = monotonic()
        self.t1 = next_prs - self.t10 - 0.006
        #print "setting timer for", self.t1
        signal.setitimer(signal.ITIMER_REAL, self.t1, 0.096)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        n = len(in0)

        tags = self.get_tags_in_window(0, 0, n)
        for tag in tags:
            key = pmt.symbol_to_string(tag.key)
            if key == 'start_prs':
                value = pmt.to_double(tag.value)
                prs_rx_time = self.monotonic_raw_from_offset(tag.offset)
                #print "prs @", tag.offset + value, prs_rx_time
                #print "that was", monotonic() - prs_rx_time, "seconds ago"
                next_prs = prs_rx_time + 0.096 * (int((monotonic() - prs_rx_time) / 0.096) + 1)
                #print "next prs @", next_prs
                next_prs_in = next_prs - monotonic()
                #print "next prs in", next_prs - monotonic()
                if next_prs_in > 0.010:
                    self.update_timer(next_prs)
            elif key == 'rx_time':
                value = pmt.to_uint64(tag.value)
                #print "sample", tag.offset, "sampled at", value
                self.last_rx_time = (tag.offset, value)
        out[:] = in0
        return len(output_items[0])

