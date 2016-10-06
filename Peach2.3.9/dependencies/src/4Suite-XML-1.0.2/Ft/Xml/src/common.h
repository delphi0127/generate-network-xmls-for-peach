#ifndef COMMON_H
#define COMMON_H

/* Backward compat code recommended in PEP 353 */
#if PY_VERSION_HEX < 0x02050000
    typedef int Py_ssize_t;
#   define PY_FORMAT_SIZE_T ""
#   define PY_SSIZE_T_MAX INT_MAX
#   define PY_SSIZE_T_MIN INT_MIN
/* MvL advises against these quick-fix typedefs of function prototypes.
   See: http://mail.python.org/pipermail/python-dev/2006-March/062561.html
   He is right that they're error prone, as these errors have bitten me --Uche
#   define ssizeargfunc intargfunc
#   define ssizessizeargfunc intintargfunc
#   define ssizeobjargproc intobjargproc
#   define ssizessizeobjargproc intintobjargproc
#   define lenfunc inquiry 
*/
#   define readbufferproc getreadbufferproc
#   define writebufferproc getwritebufferproc
#   define segcountproc getsegcountproc
#   define charbufferproc getcharbufferproc

/*
#if !defined(Py_ssize_t)
#  define Py_ssize_t int
#endif
*/

/*Code borrowed from pyport.h in Python 2.5*/
#   ifndef YY_FORMAT_SIZE_T
#       if SIZEOF_VOID_P == SIZEOF_INT
#           define YY_FORMAT_SIZE_T ""
#       elif SIZEOF_VOID_P == SIZEOF_LONG
#           define YY_FORMAT_SIZE_T "l"
#       elif defined(MS_WINDOWS)
#           define YY_FORMAT_SIZE_T "I"
#       else
#           error "Special treatment needed for this platform re: YY_FORMAT_SIZE_T"
#       endif
#   endif

#else

#   define YY_FORMAT_SIZE_T PY_FORMAT_SIZE_T

#endif


#endif /* COMMON_H */

