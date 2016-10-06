#ifndef ROUTINES_H
#define ROUTINES_H

#include <Python.h>

#if defined(_WIN32) || defined(__WIN32__)
#define snprintf _snprintf
#endif

#define EXTRA 100
#define QUOTE '\''

#define DOUBLE_INTEGER_DIGITS  309
#define DOUBLE_FRACTION_DIGITS 340

typedef struct DigitList {
    char digits[DOUBLE_FRACTION_DIGITS];
    short count;
    short decimalAt;
} DigitList;

typedef struct PatternParts {
  PyObject *pattern;
  Py_UNICODE *prefix, *suffix;
  int prefixSize, suffixSize;
} PatternParts;

typedef struct FormatInfo {
  PatternParts positive;
  PatternParts negative;

  int minIntegerDigits, maxIntegerDigits;
  int minFractionDigits, maxFractionDigits;

  int multiplier;
  int groupingSize;

  /* boolean */
  char groupingUsed, showDecimalPoint;
} FormatInfo;

typedef struct DecimalFormatSymbols {
  Py_UNICODE zeroDigit;
  Py_UNICODE groupingSeparator;
  Py_UNICODE decimalSeparator;
  Py_UNICODE percent;
  Py_UNICODE perMille;
  Py_UNICODE digit;
  Py_UNICODE separator;
  Py_UNICODE minus;
} DecimalFormatSymbols;

#endif /* ROUTINES_H */
