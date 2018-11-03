/* -*- c++ -*- */
/* 
 * Copyright 2018 gr-dab_step author.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_DAB_STEP_DAB_SYNC_CPP_IMPL_H
#define INCLUDED_DAB_STEP_DAB_SYNC_CPP_IMPL_H

#include <dab_step/dab_sync_cpp.h>

namespace gr {
  namespace dab_step {

    enum state_e {
        INIT = 0,
        PREPARE_FIND_START = 1,
        FIND_START = 2,
        GET_PRS = 3,
        PROCESS_PRS = 4,
        GET_SAMPLES = 5,
        SKIP_SAMPLES = 6,
        SKIP_SAMPLES_INTERNAL = 7
    };

    class dab_sync_cpp_impl : public dab_sync_cpp
    {
     private:
        unsigned int d_sample_rate;
        unsigned int d_fft_length;
        unsigned int d_cp_length;
        std::vector<gr_complex> d_prs;
        std::vector<gr_complex> d_prs_conj_rev;
        gr_complex *d_samples;
        double d_P;
        double d_I;
        unsigned int d_fract_offset;
        state_e d_state;
        state_e d_next_state;
        unsigned int d_frame_length;
        unsigned int d_skip_samples_count_integer;
        unsigned int d_skip_samples_count_fract;
        unsigned int d_count;
        unsigned int d_step;
        double d_error_acc;
        int d_corr_fft_size;
        gr_complex *d_prs_conj_rev_ffts[1000];
        gr::fft::fft_complex * d_corr_fft;
        gr::fft::fft_complex * d_corr_ifft;
        float *d_magnitude_f;
        int d_samples_size;
        double d_freq_offset;
        blocks::rotator d_r;

        int find_start(gr_complex *signal, int N);
        double auto_correlate(std::vector<gr_complex> signal);
        int find_rough_freq_offset(int *fine_start, std::vector<gr_complex> signal, float fine_freq_offset);
        double estimate_prs(double *cor, gr_complex *signal, int n, int fract_offset);
        void delay(gr_complex *signal, int n, float delay);

     public:
      dab_sync_cpp_impl(unsigned int sample_rate, unsigned int fft_length, unsigned int cp_length, const std::vector<gr_complex> &prs);
      ~dab_sync_cpp_impl();

      // Where all the action really happens
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);
    };

  } // namespace dab_step
} // namespace gr

#endif /* INCLUDED_DAB_STEP_DAB_SYNC_CPP_IMPL_H */

