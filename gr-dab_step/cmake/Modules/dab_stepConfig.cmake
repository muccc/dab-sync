INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_DAB_STEP dab_step)

FIND_PATH(
    DAB_STEP_INCLUDE_DIRS
    NAMES dab_step/api.h
    HINTS $ENV{DAB_STEP_DIR}/include
        ${PC_DAB_STEP_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    DAB_STEP_LIBRARIES
    NAMES gnuradio-dab_step
    HINTS $ENV{DAB_STEP_DIR}/lib
        ${PC_DAB_STEP_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(DAB_STEP DEFAULT_MSG DAB_STEP_LIBRARIES DAB_STEP_INCLUDE_DIRS)
MARK_AS_ADVANCED(DAB_STEP_LIBRARIES DAB_STEP_INCLUDE_DIRS)

