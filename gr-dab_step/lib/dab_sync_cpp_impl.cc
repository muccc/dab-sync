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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include <gnuradio/filter/firdes.h>
#include <gnuradio/filter/fir_filter.h>
#include <gnuradio/blocks/rotator.h>
#include <gnuradio/fft/fft.h>
#include <gnuradio/expj.h>
#include <volk/volk.h>
#include <stdio.h>

#include "dab_sync_cpp_impl.h"


namespace gr {
  namespace dab_step {

    dab_sync_cpp::sptr
    dab_sync_cpp::make(unsigned int sample_rate, unsigned int fft_length, unsigned int cp_length, const std::vector<gr_complex> &prs)
    {
      return gnuradio::get_initial_sptr
        (new dab_sync_cpp_impl(sample_rate, fft_length, cp_length, prs));
    }

#if 0
    void write_data_c(const gr_complex * data, size_t len, char *name, int num)
    {
        char filename[256];
        sprintf(filename, "/tmp/signals/%s-%d.cfile", name, num);
        FILE * fp = fopen(filename, "wb");
        fwrite(data, sizeof(gr_complex), len, fp);
        fclose(fp);
    }
#endif

    /*
     * The private constructor
     */
    dab_sync_cpp_impl::dab_sync_cpp_impl(unsigned int sample_rate, unsigned int fft_length, unsigned int cp_length, const std::vector<gr_complex> &prs)
      : gr::sync_block("dab_sync_cpp",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
              d_sample_rate(sample_rate),
              d_fft_length(fft_length),
              d_cp_length(cp_length),
              d_prs(prs),
              d_step(1),
              d_I(0.6),
              d_P(0.6),
              d_frame_length(sample_rate * 96e-3),
              d_fract_offset(0),
              d_state(INIT)
    {
        int alignment = volk_get_alignment();

        //std::cout << std::setprecision(10);

        // Create time-reversed conjugate of PRS
        d_prs_conj_rev = d_prs;
        for(size_t i=0; i < d_prs_conj_rev.size(); i++) {
            d_prs_conj_rev[i] = conj(d_prs_conj_rev[i]);
        }
        std::reverse(d_prs_conj_rev.begin(), d_prs_conj_rev.end());


        // Make the FFT size a power of two
        int corr_fft_size_target = d_prs_conj_rev.size();
        d_corr_fft_size = pow(2, (int)(std::ceil(log(corr_fft_size_target) / log(2))));

        // XXX: It really need to be PRS_LEN + OTHER_SIGNAL_LEN + 1
        // Python says fftpack uses 6400 for 2552 + 2552 * 1.5 + 1
        // 8192 would probably also be an option
        d_corr_fft_size = 6400;
        //d_corr_fft_size = 8192;

        // Temporary FFT to pre transform the filter
        fft::fft_complex fft_engine = fft::fft_complex(d_corr_fft_size);
        memset(fft_engine.get_inbuf(), 0, sizeof(gr_complex) * d_corr_fft_size);

        // Transform the filter
        int prs_len = d_prs_conj_rev.size();
        memcpy(fft_engine.get_inbuf(), &d_prs_conj_rev[0], sizeof(gr_complex) * prs_len);
        fft_engine.execute();

        for(int fract_offset = 0; fract_offset < 1000; fract_offset++) {
            // Allocate space for the pre-transformed PRS
            d_prs_conj_rev_ffts[fract_offset] = (gr_complex *)volk_malloc(d_corr_fft_size * sizeof(gr_complex), alignment);
            memcpy(d_prs_conj_rev_ffts[fract_offset], fft_engine.get_outbuf(), sizeof(gr_complex) * d_corr_fft_size);
            // Add a linear phase term e**(-2*PI*j*k/N * delta) to delay the PRS
            // see https://www.dsprelated.com/freebooks/mdft/Shift_Theorem.html
            for(int n = 0; n < d_corr_fft_size; n++) {
                int k;
                // k needs to be like [0, 1, 2, 3, -4, -3, -2, -1] for N = 8
                if(n < d_corr_fft_size / 2) {
                    k = n;
                } else {
                    k = n - d_corr_fft_size;
                }

                gr_complex c = gr_expj(-2 * M_PI * k * -fract_offset / 1000. / d_corr_fft_size);
                d_prs_conj_rev_ffts[fract_offset][n] *= c;
            }
        }

#if 0
        fft::fft_complex ifft_engine = fft::fft_complex(d_corr_fft_size, false, 1);
        for(int fract_offset = 0; fract_offset < 1000; fract_offset++) {
            memcpy(ifft_engine.get_inbuf(), d_prs_conj_rev_ffts[fract_offset], sizeof(gr_complex) * d_corr_fft_size);
            ifft_engine.execute();
            volk_32fc_s32fc_multiply_32fc(ifft_engine.get_outbuf(), ifft_engine.get_outbuf(), gr_complex(1./d_corr_fft_size, 0), d_corr_fft_size);

            write_data_c(ifft_engine.get_outbuf(), prs_len, "cpp-prs-delayed", fract_offset);
        }
#endif

#if 0
{
        int fft_size = 4096;
        fft::fft_complex fft_engine = fft::fft_complex(fft_size);
        fft::fft_complex ifft_engine = fft::fft_complex(fft_size, false, 1);

        memset(fft_engine.get_inbuf(), 0, sizeof(gr_complex) * fft_size);
        memcpy(fft_engine.get_inbuf(), &prs[0], sizeof(gr_complex) * prs_len);

        fft_engine.execute();

        memcpy(ifft_engine.get_inbuf(), fft_engine.get_outbuf(), sizeof(gr_complex) * fft_size);
        ifft_engine.execute();

        write_data_c(fft_engine.get_inbuf(), prs_len, "cpp", 0);
        write_data_c(ifft_engine.get_outbuf(), prs_len, "cpp-fft", 0);
}
#endif

        // Update the size of the work FFTs
        d_corr_fft = new fft::fft_complex(d_corr_fft_size, true, 1);
        d_corr_ifft = new fft::fft_complex(d_corr_fft_size, false, 1);

        // The inputs need to zero, as we might not use it completely
        memset(d_corr_fft->get_inbuf(), 0, sizeof(gr_complex) * d_corr_fft_size);

        d_magnitude_f = (float *)volk_malloc(d_corr_fft_size * sizeof(float), alignment);

        d_samples =  (gr_complex *)volk_malloc(d_frame_length * sizeof(gr_complex), alignment);

        set_history(d_prs.size()+1);

        //printf("Const done\n");
    }

    /*
     * Our virtual destructor.
     */
    dab_sync_cpp_impl::~dab_sync_cpp_impl()
    {
    }

    int
    dab_sync_cpp_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
        //return noutput_items;
        const gr_complex *in = (const gr_complex *) input_items[0] + history() - 1;
        gr_complex *out = (gr_complex *) output_items[0];

        
        int consumed = 0;
        int rough_start = 0;
        double fine_freq_offset;
        double rough_freq_offset;
        int start;
        int fine_start;
        double absolute_start;
        double error;
        double estimated_frame_length;
        double ppm;
        double skip;
        int n_input_items;
        int to_consume;
        int current_integer_offset;
        int current_fract_offset;
        int integer_count;
        int fract_count;
        int target_integer_offset;
        int target_fract_offset;
        double phase_inc;
        double cor;
        unsigned int integer_offset;
        bool cont = true;

        std::vector<gr_complex> signal;

        pmt::pmt_t key;
        pmt::pmt_t value;

        std::vector<tag_t> in_tags;
        get_tags_in_window(in_tags, 0, 0, noutput_items);

        for(tag_t tag : in_tags) {
            std::cout << "dab sync: got key: " << pmt::symbol_to_string(tag.key) << "\n";
        }


        while(cont) {
            integer_offset = nitems_read(0) + consumed;
            //printf("state: %d\n", d_state);

            switch(d_state) {
                case INIT:
                    d_state = SKIP_SAMPLES;
                    d_next_state = PREPARE_FIND_START;

                    d_skip_samples_count_integer = int(d_frame_length * 10.1);
                    d_skip_samples_count_fract = 0;
                    
                    key = pmt::string_to_symbol("sync");
                    value = pmt::from_double(0);

                    add_item_tag(0, integer_offset, key, value);
                break;

                case PREPARE_FIND_START:
                    printf("PREPARE_FIND_START get %d samples\n", d_frame_length);
                    d_state = GET_SAMPLES;
                    d_next_state = FIND_START;
                    d_count = d_frame_length;
                    d_samples_size = 0;
                break;

                case FIND_START:
                    rough_start = find_start(d_samples, d_samples_size);
                    printf("rough start at %d\n", rough_start);

                    if(rough_start == 0) {
                        d_state = INIT;
                        continue;
                    }

                    signal = std::vector<gr_complex>(d_samples + rough_start, d_samples + d_samples_size);
                    
                    if(signal.size() < d_prs.size()) {
                        d_state = PREPARE_FIND_START;
                        continue;
                    }

                    fine_freq_offset = auto_correlate(signal);
                    printf("fine_freq_offset %f\n", fine_freq_offset);
                    rough_freq_offset = find_rough_freq_offset(&fine_start, signal, -fine_freq_offset);
                    printf("fine start at %d\n", fine_start);
                    printf("rough_freq_offset %f\n", rough_freq_offset);
 
                    signal = std::vector<gr_complex>(signal.begin() + fine_start, signal.end());
                    start = rough_start + fine_start;
                    d_freq_offset = rough_freq_offset - fine_freq_offset;

                    d_error_acc = 0;
                    d_state = SKIP_SAMPLES;
                    d_next_state = GET_PRS;
                    d_skip_samples_count_integer = start + d_frame_length * (d_step - 1);
                    printf("start=%d d_skip_samples_count_integer=%d\n", start, d_skip_samples_count_integer);
                    d_skip_samples_count_fract = 0;
                break;
                
                case GET_PRS:
                    d_state = GET_SAMPLES;
                    d_next_state = PROCESS_PRS;
                    d_count = d_prs.size();
                    d_samples_size = 0;
                break;

                case PROCESS_PRS:
                    // TODO: this could be pre-computed into the PRS
                    phase_inc = -2. * M_PI * d_freq_offset / (double)d_sample_rate;
                    d_r.set_phase_incr(exp(gr_complex(0, phase_inc)));
                    d_r.set_phase(gr_complex(1, 0));
                    d_r.rotateN(d_samples, d_samples, d_samples_size);

                    // TODO: One less memcpy:
                    //d_r.rotateN(d_corr_fft->get_inbuf(), d_samples, d_samples_size);

                    // Optional: correct fine freq offset
                    
                    error = estimate_prs(&cor, d_samples, d_prs.size(), d_fract_offset);
                    
                    absolute_start = integer_offset + d_fract_offset / 1000. + error;

                    d_error_acc += error;
                    estimated_frame_length = d_frame_length + d_I * d_error_acc + d_P * error;
                    ppm = (estimated_frame_length - d_frame_length) / d_frame_length * 1e6;

                    printf("error=%+.6f estimated_frame_length=%.6f %2.1f ppm\n", error, estimated_frame_length, ppm);
                    if(abs(ppm) > 100) {
                        d_state = INIT;
                        continue;
                    }

                    
                    key = pmt::string_to_symbol("start_prs");
                    value = pmt::from_double(d_fract_offset/1000.);
                    add_item_tag(0, (int)absolute_start, key, value);

                    skip = estimated_frame_length * d_step - d_prs.size();
                    d_state = SKIP_SAMPLES;
                    d_next_state = GET_PRS;
                    d_skip_samples_count_integer = (int) skip;
                    d_skip_samples_count_fract = (int)((skip - (int)skip) * 1000);
                break;

                case GET_SAMPLES:
                    n_input_items = noutput_items - consumed;
                    to_consume = std::min((int)n_input_items, (int)d_count - d_samples_size);

                    memcpy(d_samples + d_samples_size, in + consumed, to_consume * sizeof(gr_complex));

                    consumed += to_consume;
                    d_samples_size += to_consume;

                    if(d_samples_size < d_count) {
                        cont = false;
                        break;
                    }

                    d_state = d_next_state;
                break;

                case SKIP_SAMPLES:
                    current_integer_offset = nitems_read(0) + consumed;
                    current_fract_offset = d_fract_offset;

                    integer_count = d_skip_samples_count_integer;
                    fract_count = d_skip_samples_count_fract;

                    assert(fract_count < 1000);

                    target_integer_offset = current_integer_offset + integer_count + (current_fract_offset + fract_count) / 1000;
                    target_fract_offset = (current_fract_offset + fract_count) % 1000;

                    d_count = target_integer_offset - current_integer_offset;
                    d_fract_offset = target_fract_offset;

                    //printf("SS: d_count=%d consumed=%d\n", d_count, consumed);
                    d_state = SKIP_SAMPLES_INTERNAL;
                break;

                case SKIP_SAMPLES_INTERNAL:
                    n_input_items = noutput_items - consumed;

                    to_consume = std::min(n_input_items, (int)d_count);
                    d_count -= to_consume;
                    consumed += to_consume;

                    //printf("SSI d_count=%d consumed=%d\n", d_count, consumed);
                    if(d_count > 0) {
                        cont = false;
                        break;
                    }

                    d_state = d_next_state;
                break;
            }
        }

        memcpy(out, in, sizeof(gr_complex) * noutput_items);
        return noutput_items;
    }



    int
    dab_sync_cpp_impl::find_start(gr_complex *signal_c, int N)
    {
        int alignment = volk_get_alignment();
        //std::vector<float> input_low_pass = gr::filter::firdes::low_pass_2(1, d_sample_rate, 10000, 20000, 60);
        // XXX: simply took the 13 tap low pass from Python
        float input_low_pass_taps[] = {0.01219498,  0.02158952,  0.04725592,  0.08231698,  0.11737815, 0.14304475,  0.15243939,  0.14304475,  0.11737815,  0.08231698, 0.04725592,  0.02158952,  0.01219498};
        std::vector<float> input_low_pass(input_low_pass_taps, input_low_pass_taps + 13);
        filter::kernel::fir_filter_fff input_low_pass_filter(0, input_low_pass);

        // firdes::low_pass_2() always returns an odd number of taps
        int half_fir_size = (input_low_pass_filter.ntaps() - 1) / 2;

        float *magnitude_f = (float *)volk_malloc(N * sizeof(float), alignment);
        float *magnitude_filtered_f = (float *)volk_malloc(N * sizeof(float), alignment);
        float* sum = (float*)volk_malloc(sizeof(float), alignment);

        volk_32fc_magnitude_32f(magnitude_f, signal_c, N);

        int n = N - 2 * half_fir_size;
        // The first element of the output will be magnitude_f[half_fir_size] filtered
        input_low_pass_filter.filterN(magnitude_filtered_f, magnitude_f, n);

        volk_32f_accumulator_s32f(sum, magnitude_filtered_f, n);
        float level = *sum / n;

        int low_count = 0;
        int i;
        for(i = 0; i < n; i++) {
            if(magnitude_filtered_f[i] < level / 1.2) {
                low_count += 1;
            } else {
                if(low_count > d_sample_rate * 0.5e-3) {
                    break;
                }
                low_count = 0;
            }
        }

        volk_free(magnitude_f);
        volk_free(magnitude_filtered_f);
        volk_free(sum);

        return i == n ? 0 : i + half_fir_size;
    }

    double
    dab_sync_cpp_impl::auto_correlate(std::vector<gr_complex> signal)
    {
        unsigned int Tu = d_fft_length;
        unsigned int alignment = volk_get_alignment();


        gr_complex *time_shifted_signal_c = (gr_complex *)volk_malloc(d_cp_length * sizeof(gr_complex), alignment);
        gr_complex *signal_c = (gr_complex *)volk_malloc(d_cp_length * sizeof(gr_complex), alignment);
        float *auto_correlated_f = (float *)volk_malloc(d_cp_length * sizeof(float), alignment);
        float* sum_f = (float*)volk_malloc(sizeof(float), alignment);

        memcpy(signal_c, &signal[0], sizeof(gr_complex) * d_cp_length);
        memcpy(time_shifted_signal_c, &signal[0] + Tu, sizeof(gr_complex) * d_cp_length);

        volk_32fc_conjugate_32fc(time_shifted_signal_c, time_shifted_signal_c, d_cp_length);
        volk_32fc_x2_multiply_32fc(signal_c, signal_c, time_shifted_signal_c, d_cp_length);
        volk_32fc_s32f_atan2_32f(auto_correlated_f, signal_c, 1. / (1. / 2. / 3.14 * Tu / 2.), d_cp_length);
        volk_32f_accumulator_s32f(sum_f, auto_correlated_f, d_cp_length);

        double fine_offset = *sum_f / d_cp_length;
        
        volk_free(auto_correlated_f);
        volk_free(signal_c);
        volk_free(time_shifted_signal_c);
        volk_free(sum_f);
        return fine_offset;
    }

    double
    dab_sync_cpp_impl::estimate_prs(double *cor, gr_complex *signal, int n, int fract_offset)
    {
        memcpy(d_corr_fft->get_inbuf(), &signal[0], sizeof(gr_complex) * n);
        // TODO: If we make sure that n is always the same, we can omit the memset
        memset(d_corr_fft->get_inbuf() + n, 0, sizeof(gr_complex) * (d_corr_fft_size - n));

        // TODO: in the "locked" case we are only interested in a few dot products around
        // the center. They might be faster than doing an IFFT(FFT())
        d_corr_fft->execute();
        volk_32fc_x2_multiply_32fc(d_corr_ifft->get_inbuf(), d_corr_fft->get_outbuf(), d_prs_conj_rev_ffts[fract_offset], d_corr_fft_size);
        d_corr_ifft->execute();
#if 0
        volk_32fc_s32fc_multiply_32fc(d_corr_ifft->get_outbuf(), d_corr_ifft->get_outbuf(), gr_complex(1./d_corr_fft_size, 0), d_corr_fft_size);

#endif
        // Find the peak of the correlation
        volk_32fc_magnitude_squared_32f(d_magnitude_f, d_corr_ifft->get_outbuf(), d_corr_fft_size);
        //volk_32fc_magnitude_32f(d_magnitude_f, d_corr_ifft->get_outbuf(), d_corr_fft_size);
        float *max_p = std::max_element(d_magnitude_f, d_magnitude_f + d_corr_fft_size);
        int max_index = max_p - d_magnitude_f;

        // Remove the offset of the full correlation
        // TODO: The PRS has an even size. Maybe pad it with a single 0 in front?
        int prs_middle = max_index - (d_prs.size() - 1) / 2;

        // TODO: max_p could be at the border or outside of the array
        // Divide by d_corr_fft_size to normalize the IFFT output (in GR IFFT(FFT(X)) is scaled by N)
        double alpha = abs(d_corr_ifft->get_outbuf()[max_index - 1]) / d_corr_fft_size;
        double beta = abs(d_corr_ifft->get_outbuf()[max_index]) / d_corr_fft_size;
        double gamma = abs(d_corr_ifft->get_outbuf()[max_index + 1]) / d_corr_fft_size;

        double correction = 0.5 * (alpha - gamma) / (alpha - 2*beta + gamma);

        double prs_middle_fine = prs_middle + correction;
        // TODO: Determine the interpolated correlation
        *cor = beta;

        return  prs_middle_fine - d_prs.size() / 2;
    }

    int
    dab_sync_cpp_impl::find_rough_freq_offset(int *fine_start, std::vector<gr_complex> signal, float fine_freq_offset)
    {
        unsigned int alignment = volk_get_alignment();
        int n = std::min((int)(d_prs.size() * 1.5), (int)signal.size());

        // TODO: see estimate_prs
        //n = d_prs.size();

        gr_complex *prs_signal_c = (gr_complex *)volk_malloc(n * sizeof(gr_complex), alignment);
        gr_complex *prs_signal_shifted_c = (gr_complex *)volk_malloc(n * sizeof(gr_complex), alignment);
        memcpy(prs_signal_c, &signal[0], n * sizeof(gr_complex));

        blocks::rotator r;

        float phase_inc = -2. * M_PI * fine_freq_offset / (float)d_sample_rate;
        r.set_phase_incr(exp(gr_complex(0, phase_inc)));
        r.set_phase(gr_complex(1, 0));
        r.rotateN(prs_signal_c, prs_signal_c, n);


        float offset;
        float max_cor = 0;
        int best_loc = 0;
        int best_shift = 0;

        for(offset = -10e3; offset < 10e3; offset+=1e3) {
            phase_inc = -2. * M_PI * offset / (float)d_sample_rate;
            r.set_phase_incr(exp(gr_complex(0, phase_inc)));
            r.set_phase(gr_complex(1, 0));
            r.rotateN(prs_signal_shifted_c, prs_signal_c, n);

            double cor;
            //memcpy(d_corr_fft->get_inbuf(), prs_signal_shifted_c, sizeof(gr_complex) * n);
            int location = estimate_prs(&cor, prs_signal_shifted_c, n, 0);

            if(cor > max_cor) {
                max_cor = cor;
                best_loc = location;
                best_shift = offset;
            }
        }

        volk_free(prs_signal_c);
        volk_free(prs_signal_shifted_c);

        *fine_start = best_loc;
        return best_shift;
    }

  } /* namespace dab_step */
} /* namespace gr */

