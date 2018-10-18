/* -*- c++ -*- */

#define DAB_STEP_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "dab_step_swig_doc.i"

%{
#include "dab_step/dab_sync_cpp.h"
%}


%include "dab_step/dab_sync_cpp.h"
GR_SWIG_BLOCK_MAGIC2(dab_step, dab_sync_cpp);
