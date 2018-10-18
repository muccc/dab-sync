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


import find_start
import auto_correlate
import correlate
import make_prs
import parameters
import pmt
import sys

FIND_START = 0
GET_PRS = 1
PROCESS_PRS = 2
GET_SAMPLES = 3
SKIP_SAMPLES = 4
SKIP_SAMPLES_INTERNAL = 5
PREPARE_FIND_START = 6
INIT = 7

def delay(signal, delay):
    #print "delay", delay, len(signal)
    if delay == 0:
        return signal
    sinc_vect = [0] * 201
    for i in range(201):
        sinc_vect[i] = numpy.sinc(100.0 - i - delay)
    return numpy.convolve(signal, sinc_vect, 'same')


class dab_sync(gr.sync_block):
    """
    docstring for block dab_sync
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="dab_sync",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.sample_rate = 2048000
        self.step = 1


        self.dp = parameters.dab_parameters(1, self.sample_rate)
        self.prs = make_prs.modulate_prs(self.sample_rate, True)
        self.frame_length = int(self.sample_rate * 96e-3)
        self.prs_len=len(self.prs)
        print "PRS length", self.prs_len

        
        self.correlator = correlate.Correlator(self.prs, self.sample_rate)
        self.P = 0.2 * 3
        self.I = 0.2 * 3

        self.fract = 1000
        self.integer_offset = 0
        self.fract_offset = 0


        self.state = INIT

        self.set_history(self.prs_len+1)

    def work(self, input_items, output_items):
        in0 = input_items[0][self.history()-1:]
        out = output_items[0]

        consumed = 0

        #print "work", len(in0), self.integer_offset, self.nitems_read(0), self.nitems_written(0)

        while True:
            #print self.state
            self.integer_offset = self.nitems_read(0) + consumed
            if self.state == INIT:
                self.state = SKIP_SAMPLES
                self.skip_samples_count = (int(self.frame_length * 10.1), 0)
                self.next_state = PREPARE_FIND_START
                key = pmt.string_to_symbol("sync")
                value = pmt.from_double(0)
                self.add_item_tag(0, self.integer_offset, key, value)

            elif self.state == PREPARE_FIND_START:
                self.state = GET_SAMPLES
                self.count = self.frame_length
                self.samples = numpy.array([],dtype=numpy.complex64)
                self.next_state = FIND_START

            elif self.state == FIND_START:
                #start = 0
                #while start == 0:
                #    start = find_start.find_start(signal, self.sample_rate)
                #    signal = reader.read(f, count=self.frame_length)
                rough_start = find_start.find_start(self.samples, self.sample_rate)

                if rough_start == 0:
                    self.state = INIT
                    continue
                   

                signal = self.samples[rough_start:]
                if len(signal) < self.prs_len:
                    self.state = PREPARE_FIND_START
                    continue
                fine_freq_offset = auto_correlate.auto_correlate(signal, self.dp, self.sample_rate)

                fine_start, rough_freq_offset = self.correlator.find_rough_freq_offset(signal, -fine_freq_offset)
                signal = signal[fine_start:]
                start = rough_start + fine_start

                freq_offset = rough_freq_offset - fine_freq_offset


                self.shift_signal = numpy.exp(complex(0,-1)*numpy.arange(self.prs_len)*2*numpy.pi*freq_offset/float(self.sample_rate))

                self.error_acc = 0


                self.state = SKIP_SAMPLES
                self.skip_samples_count = (start + self.frame_length * (self.step - 1), 0)
                self.next_state = GET_PRS

            elif self.state == GET_PRS:
                self.state = GET_SAMPLES
                self.count = self.prs_len
                self.samples = numpy.array([],dtype=numpy.complex64)
                self.next_state = PROCESS_PRS
                print "get prs at", self.integer_offset

            elif self.state == PROCESS_PRS:
                signal = self.samples * self.shift_signal
                '''
                fine_freq_offset = auto_correlate.auto_correlate(signal, self.dp, self.sample_rate)
                fine_shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*-fine_freq_offset/float(self.sample_rate))
                signal = signal * fine_shift_signal
                '''

                error, cor, phase = self.correlator.estimate_prs_fine(signal[:len(self.prs)], self.fract_offset)
                #print "error:", error
                absolute_start = self.integer_offset + self.fract_offset / 1000. + error
                if self.fract_offset / 1000. + error < 0:
                    print "================================================================"

                self.error_acc += error
                estimated_frame_length = self.frame_length + self.I * self.error_acc + self.P * error 
                ppm = (estimated_frame_length - self.frame_length) / self.frame_length * 1e6
                print "estimated_frame_length:", estimated_frame_length, "(", ppm, "ppm)"
                print "absolute_start:", absolute_start
                print "consumed:", self.nitems_read(0)
                print absolute_start + self.history() - 1 - self.nitems_read(0)

                if abs(ppm) > 100:
                    self.state = INIT
                    continue
 
                key = pmt.string_to_symbol("start_prs")
                fract_offset = (self.fract_offset / 1000. + error) % 1
                value = pmt.from_double(fract_offset)
                self.add_item_tag(0, int(absolute_start), key, value)

                skip = estimated_frame_length*self.step-self.prs_len

                self.state = SKIP_SAMPLES
                self.skip_samples_count = (int(skip), int((skip - int(skip)) * 1000))
                self.next_state = GET_PRS

            elif self.state == GET_SAMPLES:
                n_input_items = len(in0[consumed:])
                to_consume = min(n_input_items, self.count - len(self.samples))
                self.samples = numpy.concatenate((self.samples, in0[consumed:consumed+to_consume]))
                consumed += to_consume

                if len(self.samples) < self.count:
                    break

                #self.samples = delay(self.samples, float(self.fract_offset) / self.fract)
                self.state = self.next_state

            elif self.state == SKIP_SAMPLES:
                current_integer_offset = self.nitems_read(0) + consumed
                current_fract_offset = self.fract_offset

                integer_count = self.skip_samples_count[0]
                fract_count = self.skip_samples_count[1]
                assert fract_count < self.fract

                target_integer_offset = current_integer_offset + integer_count + (current_fract_offset + fract_count) / self.fract
                target_fract_offset = (current_fract_offset + fract_count) % self.fract

                self.count = target_integer_offset - current_integer_offset
                self.fract_offset = target_fract_offset

                self.state = SKIP_SAMPLES_INTERNAL

            elif self.state == SKIP_SAMPLES_INTERNAL:
                n_input_items = len(in0[consumed:])
                to_consume = min(n_input_items, self.count)
                self.count -= to_consume
                consumed += to_consume

                if self.count > 0:
                    break

                self.state = self.next_state

        #XXX: We always consume everything...
        #out0 = in0[:consumed] 
        #return consumed

        if self.history() > 1:
            out[:] = input_items[0][:-self.history()+1]
            #out[:] = in0[self.history()-1:]
        else:
            out0 = in0[:consumed]
        return len(out)



