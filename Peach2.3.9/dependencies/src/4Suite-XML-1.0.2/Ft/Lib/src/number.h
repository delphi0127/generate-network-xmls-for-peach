#ifndef NUMBER_H
#define NUMBER_H

#include "Python.h"

#if defined(_WIN32) || defined(__WIN32__)
#  ifdef __MINGW32__
#    include <math.h>
#  else
#    include <float.h>
#    define isnan(x) _isnan(x)
#    define finite(x) _finite(x)
#    define isinf(x) (finite(x) || isnan(x)) ? 0 : (x > 0) ? 1 : -1
#  endif
#elif defined(__sun) || defined(__sgi) || defined(__svr4__) || defined(__osf__)
#  include <ieeefp.h>
#  define isinf(x) (finite(x) || isnan(x)) ? 0 : (x > 0) ? 1 : -1
#elif defined(__hpux)
#  define finite(x) isfinite(x)
#endif

#define _PyNumber_Classify(x, f) \
  ((PyFloat_Check(x) && f(PyFloat_AS_DOUBLE(x))))

#define PyNumber_Finite(x) \
  (_PyNumber_Classify((x), finite) || PyLong_Check(x) || PyInt_Check(x))

#define PyNumber_IsNaN(x) \
  _PyNumber_Classify((x), isnan)

#define PyNumber_IsInf(x) \
  _PyNumber_Classify((x), isinf)

#endif /* NUMBER_H */
