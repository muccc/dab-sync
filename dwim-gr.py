#!/usr/bin/env python2

import find_start
import auto_correlate
import correlate
import make_prs
import parameters
import numpy

def delay(signal, delay):
    print "delay", delay, len(signal)
    if delay == 0:
        return signal
    sinc_vect = [0] * 201
    for i in range(201):
        sinc_vect[i] = numpy.sinc(100.0 - i - delay)
    return numpy.convolve(signal, sinc_vect, 'same')


class block:

    def init(self):
        self.sample_rate = 2048000
        self.step = 1


        self.dp = parameters.dab_parameters(1, self.sample_rate)
        self.prs = make_prs.modulate_prs(self.sample_rate, True)
        self.frame_length = int(self.sample_rate * 96e-3)
        self.prs_len=len(self.prs)

        self.P = 0.2 * 3
        self.I = 0.2 * 3

        self.fract = 1000
        self.integer_offset = 0
        self.fract_offset = 0


        self.state = get_samples
        self.get_samples_count = self.frame_length
        self.next_state = find_start

    def work(self, input_items, output_items):

        consumed = 0
        while True:
            if self.state == find_start:
                #start = 0
                #while start == 0:
                #    start = find_start.find_start(signal, self.sample_rate)
                #    signal = reader.read(f, count=self.frame_length)
                rough_start = find_start.find_start(signal, self.sample_rate)

                signal = signal[rough_start:]
                fine_freq_offset = auto_correlate.auto_correlate(signal, self.dp, self.sample_rate)

                fine_start, rough_freq_offset = correlate.find_rough_freq_offset(signal, -fine_freq_offset, self.prs, self.dp, self.sample_rate)
                signal = signal[fine_start:]
                start = rough_start + fine_start

                freq_offset = rough_freq_offset - fine_freq_offset


                self.shift_signal = numpy.exp(complex(0,-1)*numpy.arange(self.prs_len)*2*numpy.pi*freq_offset/float(self.sample_rate))

                self.error_acc = 0


                self.state = skip_samples
                self.skip_samples_count = (start + self.frame_length * (self.step - 1), 0)
                self.next_state = get_prs

            elif self.state == get_prs:
                self.state = get_samples
                self.get_samples_count = self.frame_length
                self.samples = []
                self.next_state = process_prs

            elif self.state == process_prs:
                self.signal = self.samples * self.shift_signal
                '''
                fine_freq_offset = auto_correlate.auto_correlate(signal, self.dp, self.sample_rate)
                fine_shift_signal = numpy.exp(complex(0,-1)*numpy.arange(len(signal))*2*numpy.pi*-fine_freq_offset/float(self.sample_rate))
                signal = signal * fine_shift_signal
                '''

                error, cor, phase = correlate.estimate_prs_fine(signal[:len(self.prs)], self.prs)
                absolute_start = self.integer_offset + self.fract_offset / 1000. + error

                self.error_acc += error
                estimated_frame_length = self.frame_length + self.I * self.error_acc + self.P * error 
                print estimated_frame_length

                skip = estimated_frame_length*self.step-self.prs_len

                self.state = skip_samples
                self.skip_samples_count = (int(skip), int((skip - int(skip)) * 1000))
                self.next_state = get_prs

            elif self.state == get_samples:
                n_input_items = len(input_items[0][consumed:])
                to_consume = min(n_input_itmes, self.count - len(self.samples))
                self.samples.append(input_items[0][consumed:consumed+to_consume])
                consumed += to_consume

                if len(self.samples) < self.count:
                    break

                self.integer_offset += count
                self.samples = delay(self.samples, float(self.fract_offset) / self.fract)
                self.state = self.next_state

            elif self.state == skip_samples:
                assert fract_count < self.fract

                current_integer_offset = self.integer_offset
                current_fract_offset = self.fract_offset

                integer_count = self.skip_samples_count[0]
                fract_count = self.skip_samples_count[1]

                target_integer_offset = self.integer_offset + integer_count + (current_fract_offset + fract_count) / self.fract
                target_fract_offset = (current_fract_offset + fract_count) % self.fract

                self.count = target_integer_offset - current_integer_offset
                self.integer_offset = target_integer_offset
                self.fract_offset = target_fract_offset

                self.state = skip_samples_internal

            elif self.state == skip_samples_internal:
                n_input_items = len(input_items[0][consumed:])
                to_consume = min(n_input_itmes, self.count)
                self.count -= to_consume
                consumed += to_consume

                if self.count > 0:
                    break

                self.state = self.next_state


        #XXX: We always consume everything...
        output_items[0] = input_items[0][:consumed] 
        return consumed
