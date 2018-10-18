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


#ifndef INCLUDED_DAB_STEP_DAB_SYNC_CPP_H
#define INCLUDED_DAB_STEP_DAB_SYNC_CPP_H

#include <dab_step/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace dab_step {

    /*!
     * \brief <+description of block+>
     * \ingroup dab_step
     *
     */
    class DAB_STEP_API dab_sync_cpp : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<dab_sync_cpp> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of dab_step::dab_sync_cpp.
       *
       * To avoid accidental use of raw pointers, dab_step::dab_sync_cpp's
       * constructor is in a private implementation
       * class. dab_step::dab_sync_cpp::make is the public interface for
       * creating new instances.
       */
      static sptr make(unsigned int sample_rate, unsigned int fft_length, unsigned int cp_length, const std::vector<gr_complex> &prs);
    };

  } // namespace dab_step
} // namespace gr

#endif /* INCLUDED_DAB_STEP_DAB_SYNC_CPP_H */

