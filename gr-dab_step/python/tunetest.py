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

import numpy
import time
from gnuradio import gr

class tunetest(gr.sync_block):
    """
    docstring for block tunetest
    """
    def __init__(self, tune):
        gr.sync_block.__init__(self,
            name="tunetest",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.tune = tune
        self.frame_length = 2048000 * 0.096 * 2
        #self.frame_length = 2048000 * 0.096 * 2 / 3
        self.listen_time = 2048000 * 0.005
        #self.next_tune = 10e6
        #self.next_tune = self.frame_length * 100
        self.next_tune = self.frame_length
        self.items = 0
        self.state = False
        self.t0 = time.time()
        self.t1 = time.time()

    def work(self, input_items, output_items):
        t = time.time()
        in0 = input_items[0]
        out = output_items[0]
        out[:] = in0
        #print "%d data after %f" % (len(in0), t - self.t1)
        self.t1 = t
        self.items += len(in0)
        #print len(in0)
        if self.items >= self.next_tune:
            print "tune after %f" % (t - self.t0)
            self.t0 = t
            self.tune.eval(self.items)
            print "done"
            self.next_tune += self.frame_length
            #if self.state:
            #    self.next_tune += self.frame_length - self.listen_time
            #else:
            #    self.next_tune += self.listen_time
            self.state = not self.state
        return len(output_items[0])

