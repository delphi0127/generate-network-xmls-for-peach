#include "routines.h"
#include "number.h"
#include "common.h"
#include <string.h>
#include <ctype.h>
#include <stdio.h>

/*

FormatNumber provides decimal formatting for the XSLT format-number
extension function.  It is modeled on the Java DecimalFormat (as per XSLT spec)

See:

http://java.sun.com/products/jdk/1.1/docs/api/java.text.DecimalFormatSymbols.html
http://java.sun.com/products/jdk/1.1/docs/api/java.text.DecimalFormat.html

*/

static void seterror(int, char *, int *, char *, char *);
static char *converttuple(PyObject *, char **, va_list *, int *, char *);
static char *convertsimple(PyObject *, char **, va_list *);
static int getargs(PyObject *, char *, va_list *);
static char *parsepattern(PyObject *, FormatInfo *, DecimalFormatSymbols *);
static PyObject *formatnumber(double, FormatInfo *, DecimalFormatSymbols *);
static void parsenumber(double, int, DigitList *);

static void seterror(int iarg, char *msg, int *levels, char *fname,
                     char *message)
{
    char buf[256];
    int i;
    char *p = buf;

    if (PyErr_Occurred())
        return;
    else if (message == NULL) {
        if (fname != NULL) {
            sprintf(p, "%s() ", fname);
            p += strlen(p);
        }
        if (iarg != 0) {
            sprintf(p, "argument %d", iarg);
            i = 0;
            p += strlen(p);
            while (levels[i] > 0) {
                sprintf(p, ", item %d", levels[i]-1);
                p += strlen(p);
                i++;
            }
        }
        else {
            sprintf(p, "argument");
            p += strlen(p);
        }
        sprintf(p, " %s", msg);
        message = buf;
    }
    PyErr_SetString(PyExc_TypeError, message);
}


/* Convert a single item. */
static char *convertitem(PyObject *arg, char **p_format, va_list *p_va,
                         int *levels, char *msgbuf)
{
    char *msg;
    char *format = *p_format;

    if (*format == '(') {
        format++;
        msg = converttuple(arg, &format, p_va, levels, msgbuf);
        if (msg == NULL)
            format++;
    }
    else {
        msg = convertsimple(arg, &format, p_va);
        if (msg != NULL) {
            sprintf(msgbuf, "must be %.50s, not %.50s", msg,
                    arg == Py_None ? "None" : arg->ob_type->tp_name);
            msg = msgbuf;
            levels[0] = 0;
        }
    }
    if (msg == NULL)
        *p_format = format;
    return msg;
}


/* Convert a tuple argument.
   On entry, *p_format points to the character _after_ the opening '('.
   On successful exit, *p_format points to the closing ')'.
   If successful:
      *p_format and *p_va are updated,
      *levels and *msgbuf are untouched,
      and NULL is returned.
   If the argument is invalid:
      *p_format is unchanged,
      *p_va is undefined,
      *levels is a 0-terminated list of item numbers,
      *msgbuf contains an error message, whose format is:
         "must be <typename1>, not <typename2>", where:
            <typename1> is the name of the expected type, and
            <typename2> is the name of the actual type,
      and msgbuf is returned.
*/

static char *converttuple(PyObject *arg, char **p_format, va_list *p_va,
                          int *levels, char *msgbuf)
{
    int level = 0;
    int n = 0;
    char *format = *p_format;
    int i;

    for (;;) {
        int c = *format++;
        if (c == '(') {
            if (level == 0)
                n++;
            level++;
        }
        else if (c == ')') {
            if (level == 0)
                break;
            level--;
        }
        else if (c == ':' || c == ';' || c == '\0')
            break;
        else if (level == 0 && isalpha(c))
            n++;
    }

    if (!(PyTuple_Check(arg) || PyList_Check(arg))) {
        levels[0] = 0;
        sprintf(msgbuf, "must be %d-item sequence, not %s",
            n, arg == Py_None ? "None" : arg->ob_type->tp_name);
        return msgbuf;
    }

    /* FIXME: May need overflow check */
    if ((i = PySequence_Size(arg)) != n) {
        levels[0] = 0;
        sprintf(msgbuf, "must be sequence of length %d, not %d", n, i);
        return msgbuf;
    }

    format = *p_format;
    for (i = 0; i < n; i++) {
        char *msg;
        PyObject *item;
        item = PySequence_GetItem(arg, (Py_ssize_t)i);
        msg = convertitem(item, &format, p_va, levels+1, msgbuf);
        /* PySequence_GetItem calls tp->sq_item, which INCREFs */
        Py_XDECREF(item);
        if (msg != NULL) {
            levels[0] = i+1;
            return msg;
        }
    }

    *p_format = format;
    return NULL;
}


/* Convert a non-tuple argument.  Return NULL if conversion went OK,
   or a string representing the expected type if the conversion failed.
   When failing, an exception may or may not have been raised.
   Don't call if a tuple is expected. */

static char *convertsimple(PyObject *arg, char **p_format, va_list *p_va)
{
    char *format = *p_format;
    char c = *format++;

    switch (c) {

    case 'd': /* double */
        {
            double *p = va_arg(*p_va, double *);
            double dval = PyFloat_AsDouble(arg);
            if (PyErr_Occurred())
                return "float<d>";
            else
                *p = dval;
            break;
        }

    case 'c': /* char */
        {
            Py_UNICODE *p = va_arg(*p_va, Py_UNICODE *);
	    /* FIXME: PyString_Size may need overflow check */
            if (PyString_Check(arg) && PyString_Size(arg) == 1)
                *p = (Py_UNICODE) PyString_AsString(arg)[0];
	    /* FIXME: PyUnicode_GetSize may need overflow check */
            else if (PyUnicode_Check(arg) && PyUnicode_GetSize(arg) == 1)
                *p = PyUnicode_AsUnicode(arg)[0];
            else
                return "char";
            break;
        }

    case 'U': /* Unicode object */
        {
            PyObject **p = va_arg(*p_va, PyObject **);
            if (PyUnicode_Check(arg) || PyString_Check(arg))
                *p = PyUnicode_FromObject(arg);
            else
                return "unicode";
            break;
        }

    default:
        return "impossible<bad format char>";

    }

    *p_format = format;
    return NULL;
}


static int getargs(PyObject *args, char *format, va_list *p_va)
{
    char msgbuf[256];
    int levels[32];
    char *fname = NULL;
    char *message = NULL;
    int min = -1;
    int max = 0;
    int level = 0;
    char *formatsave = format;
    int i, len;
    char *msg;

    assert(args != (PyObject*)NULL);

    /* validate format string */
    for (;;) {
        int c = *format++;
        if (c == '(') {
            if (level == 0)
                max++;
            level++;
        }
        else if (c == ')') {
            if (level == 0)
                Py_FatalError("excess ')' in getargs format");
            else
                level--;
        }
        else if (c == '\0')
            break;
        else if (c == ':') {
            /* function name */
            fname = format;
            break;
        }
        else if (c == ';') {
            /* user error message (instead of builtin) */
            message = format;
            break;
        }
        else if (level != 0)
            ; /* Pass */
        else if (isalpha(c))
            max++;
        else if (c == '|')
            min = max;
    }

    if (level != 0)
        Py_FatalError("missing ')' in getargs format");

    if (min < 0)
        min = max;

    format = formatsave;

    if (!PyTuple_Check(args)) {
        PyErr_SetString(PyExc_SystemError,
            "new style getargs format but argument is not a tuple");
        return 0;
    }

    /* FIXME: PyTuple_Size may need overflow check */
    len = PyTuple_Size(args);

    if (len < min || max < len) {
        if (message == NULL) {
            sprintf(msgbuf,
                "%s%s takes %s %d argument%s (%d given)",
                fname==NULL ? "function" : fname,
                fname==NULL ? "" : "()",
                min==max ? "exactly"
                         : len < min ? "at least" : "at most",
                len < min ? min : max,
                (len < min ? min : max) == 1 ? "" : "s",
                len);
            message = msgbuf;
        }
        PyErr_SetString(PyExc_TypeError, message);
        return 0;
    }

    for (i = 0; i < len; i++) {
        if (*format == '|')
            format++;
        msg = convertitem(PyTuple_GetItem(args, (Py_ssize_t)i), &format, p_va,
                          levels, msgbuf);
        if (msg) {
            seterror(i+1, msg, levels, fname, message);
            return 0;
        }
    }

    if (*format != '\0' && !isalpha((int)(*format)) &&
        *format != '(' &&
        *format != '|' && *format != ':' && *format != ';') {
        PyErr_Format(PyExc_SystemError,
                     "bad format string: %.200s", formatsave);
        return 0;
    }

    return 1;
}

static int ParseArgs(PyObject *args, char *format, ...)
{
    int retval;
    va_list va;

    va_start(va, format);
    retval = getargs(args, format, &va);
    va_end(va);
    return retval;
}

static char FormatNumber_doc[] = 
"FormatNumber(number, pattern[, symbols]) -> string\n\
\n\
Converts the number argument to a string using the format pattern string\n\
from the pattern argument.  The symbols argument is a 10-item tuple which\n\
specifies the special characters used from interpreting the format pattern.\n\
The tuple format is (decimal-separator, grouping-separator, infinity,\n\
minus-sign, NaN, percent, per-mille, zero-digit, digit, pattern-separator).\n\
See the XSLT 1.0 Recommendation Section 12.3 for the meanings of these.";

static PyObject *FormatNumber(PyObject *self, PyObject *args)
{
    PyObject *pattern;
    PyObject *negativePattern = NULL;
    PyObject *infinity = NULL;
    PyObject *not_a_number = NULL;
    PyObject *numberString;

    char *errormsg;

    double number;
    FormatInfo info;
    DecimalFormatSymbols symbols;
    PatternParts *parts;

    PyObject *result;
    Py_UNICODE *p;
    Py_ssize_t numberSize;

    /* boolean */
    char isNegative;

    /* initialize default symbols */
    symbols.decimalSeparator = '.';
    symbols.groupingSeparator = ',';
    symbols.minus = '-';
    symbols.percent = '%';
    symbols.perMille = 0x2030;
    symbols.zeroDigit = '0';
    symbols.digit = '#';
    symbols.separator = ';';

    /* WARNING - ParseArgs returns an increfed value for 'U' formatted args */
    if (!ParseArgs(args, "dU|(ccUcUccccc)", &number, &pattern,
                   &symbols.decimalSeparator, &symbols.groupingSeparator,
                   &infinity, &symbols.minus, &not_a_number,
                   &symbols.percent, &symbols.perMille, &symbols.zeroDigit,
                   &symbols.digit, &symbols.separator))
    return NULL;

    if (!infinity) {
        /* if infinity is not supplied, then neither is not-a-number */
        infinity = PyUnicode_DecodeASCII("Infinity", (Py_ssize_t)8, NULL);
        not_a_number = PyUnicode_DecodeASCII("NaN", (Py_ssize_t)3, NULL);
        if (!not_a_number || !infinity) {
            Py_XDECREF(infinity);
            Py_XDECREF(not_a_number);
            Py_DECREF(pattern);
            return NULL;
        }
    }

    if (isnan(number)) {
        Py_DECREF(infinity);
        Py_DECREF(pattern);
        return not_a_number;
    }

    /* start out clean */
    info.positive.prefix = info.positive.suffix = NULL;
    info.positive.prefixSize = info.positive.suffixSize = 0;
    info.negative.prefix = info.negative.suffix = NULL;
    info.negative.prefixSize = info.negative.suffixSize = 0;

    if (PyUnicode_GET_SIZE(pattern) > 0) {
        errormsg = parsepattern(pattern, &info, &symbols);
    } else {
        errormsg = "missing integer portion";
    }
    if (errormsg) {
        PyObject *repr = PyObject_Repr(pattern);
        if (repr) {
            PyErr_Format(PyExc_SyntaxError, "%s in pattern %s", errormsg,
                                     PyString_AsString(repr));
            Py_DECREF(repr);
        } else {
            PyErr_SetString(PyExc_SyntaxError, errormsg);
        }
        /* There was an error while parsing pattern */
        Py_DECREF(pattern);
        Py_DECREF(infinity);
        Py_DECREF(not_a_number);
        return NULL;
    }

    /* Detecting whether a double is negative is easy with the exception of
     * the value -0.0.  This is a double which has a zero mantissa (and
     * exponent), but a negative sign bit.  It is semantically distinct from
     * a zero with a positive sign bit, and this distinction is important
     * to certain kinds of computations.  However, it's a little tricky to
     * detect, since (-0.0 == 0.0) and !(-0.0 < 0.0).  How then, you may
     * ask, does it behave distinctly from +0.0?  Well, 1/(-0.0) == -Inf. */

    isNegative = ((number < 0.0) || (number == 0.0 && 1/number) < 0.0);

    if (isNegative) {
        number = -number;
        parts = &info.negative;
        if (!info.negative.prefix && !info.negative.suffix) {
            negativePattern = PyUnicode_FromUnicode(NULL, PyUnicode_GET_SIZE(pattern)+1);
            p = PyUnicode_AS_UNICODE(negativePattern);
            *p++ = symbols.minus;
            memcpy(p, PyUnicode_AS_UNICODE(pattern),
                         PyUnicode_GET_SIZE(pattern) * sizeof(Py_UNICODE));

            info.negative.prefix = PyUnicode_AS_UNICODE(negativePattern);
            info.negative.prefixSize = 1;
            if (info.positive.prefix) {
                p = PyUnicode_AS_UNICODE(pattern);
                info.negative.prefix += info.positive.prefix - p + 1;
            }

            if (info.positive.suffix) {
                info.negative.suffix = PyUnicode_AS_UNICODE(negativePattern);
                p = PyUnicode_AS_UNICODE(pattern);
                info.negative.suffix += info.positive.suffix - p + 1;
            }
        }
    } else {
        parts = &info.positive;
    }

    /* Make sure the result string starts empty */

    if (isinf(number)) {
        numberString = infinity;
        Py_INCREF(infinity);
    } else {
        /* mutate for percent/per-mille */
        if (info.multiplier != 1)
            number *= info.multiplier;
        numberString = formatnumber(number, &info, &symbols);
    }
    /* FIXME: PyUnicode_GetSize may need overflow check */
    numberSize = PyUnicode_GetSize(numberString);

    /* by passing NULL as the unicode data, we create an empty Unicode object
     * of the specified size.
     */

    result = PyUnicode_FromUnicode(NULL, numberSize + parts->prefixSize + parts->suffixSize);
    if (!result) {
        Py_XDECREF(negativePattern);
        Py_DECREF(numberString);
        Py_DECREF(infinity);
        Py_DECREF(not_a_number);
        return NULL;
    }

    p = PyUnicode_AS_UNICODE(result);
    if (parts->prefix) {
        memcpy(p, parts->prefix, parts->prefixSize * sizeof(Py_UNICODE));
        p += parts->prefixSize;
    }

    memcpy(p, PyUnicode_AS_UNICODE(numberString), numberSize * sizeof(Py_UNICODE));

    if (parts->suffix) {
        /* suffix is the start index of the suffix */
        p += numberSize;
        memcpy(p, parts->suffix, parts->suffixSize * sizeof(Py_UNICODE));
    }

    Py_XDECREF(negativePattern);
    Py_DECREF(numberString);
    Py_DECREF(infinity);
    Py_DECREF(not_a_number);
    return result;
}

/* constants for phases */
#define PREFIX_PHASE 0
#define PATTERN_PHASE 1
#define SUFFIX_PHASE 2

/* returns error message */
static char *parsepattern(PyObject *fullpattern, FormatInfo *info,
                          DecimalFormatSymbols *symbols)
{
    Py_UNICODE *pattern = PyUnicode_AS_UNICODE(fullpattern);
    char inPositive = 1;     /* boolean */
    char hasNegative = 0;    /* boolean */

    int start = 0;
    int end = PyUnicode_GET_SIZE(fullpattern);

    do {
        char inQuote = 0;
        int decimalPos = -1;
        int multiplier = 1;
        int digitLeftCount = 0;
        int zeroDigitCount = 0;
        int digitRightCount = 0;
        int groupingCount = -1;

        /* The phase ranges from 0 to 2.  Phase 0 is the prefix.  Phase 1 is
         * the section of the pattern with digits, decimal separator,
         * grouping characters.  Phase 2 is the suffix.  In phases 0 and 2,
         * percent, permille, and currency symbols are recognized and
         * translated.  The separation of the characters into phases is
         * strictly enforced; if phase 1 characters are to appear in the
         * suffix, for example, they must be quoted. */
        int phase = PREFIX_PHASE;

        /* Two variables are used to record the subrange of the pattern
         * occupied by phase 1.  This is used during the processing of the
         * second pattern (the one representing negative numbers) to ensure
         * that no deviation exists in phase 1 between the two patterns. */
        int phaseOneStart = 0;
        int phaseOneLength = 0;

        /* The affix is either the prefix or the suffix. */
        Py_UNICODE *prefix = pattern + start;
        Py_UNICODE *suffix = pattern + end;
        Py_UNICODE *affix = prefix;
        Py_UNICODE *prefixEnd = NULL;
        Py_UNICODE *suffixEnd = suffix;

        int pos;

        for (pos = start; pos < end; pos++) {
            Py_UNICODE ch = pattern[pos];
            switch (phase) {
            case PREFIX_PHASE:
            case SUFFIX_PHASE:
                /* Process the prefix/suffix characters */
                if (inQuote) {
                    /* A quote within quotes indicates either the closing
                     * quote or two quotes, which is a quote literal.    That is,
                     * we have the second quote in 'do' or 'don''t'. */
                    if (ch == QUOTE) {
                        if ((pos+1) < end && pattern[pos+1] == QUOTE) {
                            pos++;
                            *affix++ = ch;
                        } else {
                            inQuote = 0;                /* 'do' */
                        }
                        continue;
                    }
                } else {
                    /* Process unquoted characters seen in prefix or suffix phase. */
                    if (ch == symbols->digit ||
                            ch == symbols->zeroDigit ||
                            ch == symbols->groupingSeparator ||
                            ch == symbols->decimalSeparator) {
                        /* Any of these characters implicitly begins the next
                         * phase.    If we are in phase 2, there is no next phase,
                         * so these characters are illegal. */
                        phaseOneStart = pos;
                        phaseOneLength = 0;
                        prefixEnd = affix;
                        phase = PATTERN_PHASE;
                        pos--;                        /* Reprocess this character */
                        continue;
                    } else if (ch == QUOTE) {
                        /* A quote outside quotes indicates either the opening
                         * quote or two quotes, which is a quote literal.    That is,
                         * we have the first quote in 'do' or o''clock. */
                        if (ch == QUOTE) {
                            if ((pos+1) < end && pattern[pos+1] == QUOTE) {
                                pos++;
                                *affix++ = ch;
                            } else {
                                inQuote = 1;
                            }
                            continue;
                        }
                    } else if (ch == symbols->separator) {
                        /* Don't allow separators before we see digit characters of phase
                         * 1, and don't allow separators in the second pattern. */
                        if (phase == PREFIX_PHASE || !inPositive)
                            return "too many pattern separators";
                        suffixEnd = affix;
                        start = pos + 1;
                        pos = end;
                        hasNegative++;
                        continue;
                    }

                    /* Next handle characters which are appended directly. */
                    else if (ch == symbols->percent) {
                        if (multiplier != 1)
                            return "too many percent/permille symbols";
                        multiplier = 100;
                    } else if (ch == symbols->perMille) {
                        if (multiplier != 1)
                            return "too many percent/permille symbols";
                        multiplier = 1000;
                    }
                }
                *affix++ = ch;
                break;
            case PATTERN_PHASE:
                if (inPositive) {
                    /* Process the digits, decimal, and grouping characters.  We
                     * record five pieces of information.  We expect the digits
                     * to occur in the pattern ####0000.####, and we record the
                     * number of left digits, zero (central) digits, and right
                     * digits.  The position of the last grouping character is
                     * recorded (should be somewhere within the first two blocks
                     * of characters), as is the position of the decimal point,
                     * if any (should be in the zero digits).  If there is no
                     * decimal point, then there should be no right digits. */
                    if (ch == symbols->digit) {
                        if (zeroDigitCount > 0) digitRightCount++;
                        else digitLeftCount++;
                        if (groupingCount >= 0 && decimalPos < 0) groupingCount++;
                    } else if (ch == symbols->zeroDigit) {
                        if (digitRightCount > 0)
                            return "unexpected zero digit";
                        zeroDigitCount++;
                        if (groupingCount >= 0 && decimalPos < 0) groupingCount++;
                    } else if (ch == symbols->groupingSeparator) {
                        groupingCount = 0;
                    } else if (ch == symbols->decimalSeparator) {
                        if (decimalPos >= 0)
                            return "multiple decimal separators";
                        decimalPos = digitLeftCount + zeroDigitCount + digitRightCount;
                    } else {
                        /* Save this position as start of suffix */
                        suffix = pattern + pos;
                        affix = suffix;
                        phase = SUFFIX_PHASE;
                        pos--;
                        continue;
                    }
                } else {
                    /* Phase one must be identical in the two sub-patterns.  We
                     * enforce this by doing a direct comparison.  While
                     * processing the second, we compare characters. */
                    if (ch != pattern[phaseOneStart + phaseOneLength])
                        return "subpattern mismatch";

                    /* Ignore formating in the negative pattern */
                    if (ch == symbols->digit ||
                            ch == symbols->zeroDigit ||
                            ch == symbols->groupingSeparator ||
                            ch == symbols->decimalSeparator) {
                        phaseOneLength++;
                    } else {
                        suffix = pattern + pos;
                        affix = suffix;
                        phase = SUFFIX_PHASE;
                        pos--;
                        continue;
                    }
                }
                break;
            }
        } /* subpattern for-loop */

        /* Handle patterns with no '0' pattern character.  These patterns
         * are legal, but must be interpreted.  "##.###" -> "#0.###".
         * ".###" -> ".0##".
         * We allow patterns of the form "####" to produce a zeroDigitCount of
         * zero (got that?); although this seems like it might make it possible
         * for format() to produce empty strings, format() checks for this
         * condition and outputs a zero digit in this situation.  Having a
         * zeroDigitCount of zero yields a minimum integer digits of zero, which
         * allows proper round-trip patterns.  That is, we don't want "#" to
         * become "#0" when toPattern() is called (even though that's what it
         * really is, semantically).  */
        if (zeroDigitCount == 0 && digitLeftCount > 0 && decimalPos >= 0) {
            /* Handle "###.###" and "###." and ".###" */
            int n = decimalPos;
            if (n == 0) ++n; /* Handle ".###" */
            digitRightCount = digitLeftCount - n;
            digitLeftCount = n - 1;
            zeroDigitCount = 1;
        }

        /* Do syntax checking on the digits. */
        if ((decimalPos < 0 && digitRightCount > 0) ||
                (decimalPos >= 0 && (decimalPos < digitLeftCount
                                                         || decimalPos > (digitLeftCount + zeroDigitCount)))
                || groupingCount == 0 || inQuote)
            return "malformed pattern";

        if (inPositive) {
            int digitTotalCount = digitLeftCount + zeroDigitCount + digitRightCount;
            int effectiveDecimalPos = decimalPos >= 0 ? decimalPos : digitTotalCount;
            if (prefix != prefixEnd) {
                info->positive.prefix = prefix;
                info->positive.prefixSize = prefixEnd - prefix;
            }
            if (suffix != suffixEnd) {
                info->positive.suffix = suffix;
                info->positive.suffixSize = suffixEnd - suffix;
            }
            /* The effectiveDecimalPos is the position the decimal is at or
             * would be at if there is no decimal.  Note that if decimalPos<0,
             * then digitTotalCount == digitLeftCount + zeroDigitCount.  */
            info->minIntegerDigits = effectiveDecimalPos - digitLeftCount;
            info->maxIntegerDigits = DOUBLE_INTEGER_DIGITS;
            if (decimalPos >= 0) {
                info->maxFractionDigits = digitTotalCount - decimalPos;
                info->minFractionDigits = digitLeftCount + zeroDigitCount - decimalPos;
            } else {
                info->minFractionDigits = 0;
                info->maxFractionDigits = 0;
            }
            info->groupingUsed = (groupingCount > 0);
            info->groupingSize = (groupingCount > 0) ? groupingCount : 0;
            info->showDecimalPoint = (decimalPos == 0 || decimalPos == digitTotalCount);
            info->multiplier = multiplier;
        } else {
            if (prefix != prefixEnd) {
                info->negative.prefix = prefix;
                info->negative.prefixSize = prefixEnd - prefix;
            }
            if (suffix != suffixEnd) {
                info->negative.suffix = suffix;
                info->negative.suffixSize = suffixEnd - suffix;
            }
        }

        inPositive--;
    } while (hasNegative--);

    return NULL; /* SUCCESS */
}

static PyObject *formatnumber(double number, FormatInfo *info,
                              DecimalFormatSymbols *symbols)
{
    DigitList digitList;
    Py_UNICODE temp[DOUBLE_FRACTION_DIGITS*2];
    int i, count, digitIndex = 0, pos = 0;
    char fractionPresent; /* boolean */

    /* allocate a new unicode object large enough to hold formatter number */

    parsenumber(number, info->maxFractionDigits, &digitList);

    count = info->minIntegerDigits;

    if (digitList.decimalAt > 0 && count < digitList.decimalAt)
        count = digitList.decimalAt;

    /* Handle the case where maxIntegerDigits is smaller
     * than the real number of integer digits.  If this is so, we
     * output the least significant max integer digits.  For example,
     * the value 1997 printed with 2 max integer digits is just "97". */
    if (count > info->maxIntegerDigits) {
            count = info->maxIntegerDigits;
            digitIndex = digitList.decimalAt - count;
    }

    for (i = count - 1; i >= 0; i--) {
        if (i < digitList.decimalAt && digitIndex < digitList.count)
            /* Output a real digit */
            temp[pos++] = digitList.digits[digitIndex++] + symbols->zeroDigit;
        else
            /* Output a leading zero */
            temp[pos++] = symbols->zeroDigit;

        /* Output grouping separator if necessary.  Don't output a
         * grouping separator if i==0 though; that's at the end of
         * the integer part. */
        if (info->groupingUsed && i > 0 &&
            (info->groupingSize != 0) &&
            (i % info->groupingSize == 0))
            temp[pos++] = symbols->groupingSeparator;
    }

    /* Determine whether or not there are any printable fractional
     * digits.  If we've used up the digits we know there aren't. */
    fractionPresent = (info->minFractionDigits > 0) ||
        (digitIndex < digitList.count);

    /* If there is no fraction present, and we haven't printed any
     * integer digits, then print a zero.  Otherwise we won't print
     * _any_ digits, and we won't be able to parse this string. */
    if (!fractionPresent && pos == 0) {
        temp[pos++] = symbols->zeroDigit;
    }

    /* Output the decimal separator if we always do so. */
    if (info->showDecimalPoint || fractionPresent) {
        temp[pos++] = symbols->decimalSeparator;
    }

    for (i = 0; i < info->maxFractionDigits; i++) {
        /* Here is where we escape from the loop.  We escape if we've output
         * the maximum fraction digits (specified in the for expression above).
         * We also stop when we've output the minimum digits and either:
         * we have an integer, so there is no fractional stuff to display,
         * or we're out of significant digits. */
        if (i >= info->minFractionDigits && (digitIndex >= digitList.count)) {
            break;
        }

        /* Output leading fractional zeros.  These are zeros that come after
         * the decimal but before any significant digits.  These are only
         * output if abs(number being formatted) < 1.0. */
        if (-1 - i > (digitList.decimalAt - 1)) {
            temp[pos++] = symbols->zeroDigit;
            continue;
        }
        /* Output a digit, if we have any precision left, or a
         * zero if we don't.  We don't want to output noise digits. */
        if (digitIndex < digitList.count)
            temp[pos++] = digitList.digits[digitIndex++] + symbols->zeroDigit;
        else
            temp[pos++] = symbols->zeroDigit;
    }

    return PyUnicode_FromUnicode(temp, (Py_ssize_t)pos);
}

void parsenumber(double number, int maximumDigits, DigitList *dl) {
    int i;
    int printedDigits;
    char ch;
    char nonZeroFound = 0;  /* boolean */
    char rounding;
    int zerosSkipped = 0;

    /* One more decimal digit than required for rounding */
    printedDigits = snprintf(dl->digits, DOUBLE_FRACTION_DIGITS, "%.*f",
                             maximumDigits + 1, number);

    dl->decimalAt = -1;
    dl->count = 0;
    for (i = 0; i < printedDigits; i++) {
        ch = dl->digits[i];
        if (ch == '.') {
            dl->decimalAt = dl->count;
            zerosSkipped = 0;
        } else {
            if (!nonZeroFound) {
                nonZeroFound = (ch != '0'); zerosSkipped ++;
            }
            if (nonZeroFound) {
                dl->digits[dl->count++] = ch - '0';
            }
        }
    }

    if (zerosSkipped != 0) {
      dl->decimalAt -= (zerosSkipped - 1);
    }

    i = dl->count;
    rounding = 0;
    do {
        i--;
        if (!rounding && dl->digits[i] >= 5) {
            rounding = 1;
        } else if (rounding) {
            if (dl->digits[i] == 9) {
                /* continue rounding up */
                dl->digits[i] = 0;
            } else {
                dl->digits[i]++;
                rounding = 0;
            }
        }
    } while (rounding);


    /* Remove the rounding digit */
    dl->count--;

    /* Remove any trailing zeros from the decimal part */
    for (i = dl->count-1; i > dl->decimalAt; i--) {
        if (dl->digits[i] == 0) dl->count--;
        else break;
    }
}

static PyMethodDef routinesMethods[] = {
  { "FormatNumber", FormatNumber, METH_VARARGS, FormatNumber_doc },
  { NULL, NULL }
};

DL_EXPORT(void) initroutines(void) {
    PyObject *module;

    module = Py_InitModule("routines", routinesMethods);
};
