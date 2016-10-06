########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/Exslt/DateTime.py,v 1.25.4.1 2006/08/31 18:39:08 jkloth Exp $
"""
Implementation of EXSLT Dates and Times module

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import re, time, calendar, math
from Ft.Lib import boolean, number
from Ft.Xml.Xslt import XsltElement
from Ft.Xml.XPath import Conversions, XPathTypes

EXSL_DATE_TIME_NS = 'http://exslt.org/dates-and-times'

try:
    sum
except NameError:
    import operator
    sum = lambda sequence, start=0: reduce(operator.add, sequence, start)


## EXSLT Dates and Times: Core Elements


## EXSLT Dates and Times: Core Functions

def DateTime(context):
    """
    The date:date-time function returns the current local date/time as an
    ISO 8601 formatted date/time string, with a time zone.

    Implements version 1.
    """
    return unicode(_DateTime.now())


def Date(context, dateTime=None):
    """
    The date:date function returns the date portion of the dateTime
    argument if present, or of the current local date/time. The
    argument can be given in xs:dateTime or xs:date format.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date'))
    except ValueError:
        return u''
    return u'%-.4d-%02d-%02d%s' % (dateTime.year, dateTime.month, dateTime.day,
                                   dateTime.timezone or '')


def Time(context, dateTime=None):
    """
    The date:time function returns the time portion of the dateTime
    argument if present, or of the current local date/time. The
    argument can be given in xs:dateTime or xs:time format.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'time'))
    except ValueError:
        return u''
    if dateTime.second < 10:
        second_as_string = '0%0.12g' % dateTime.second
    else:
        second_as_string = '%0.12g' % dateTime.second
    return u'%02d:%02d:%s%s' % (dateTime.hour, dateTime.minute, second_as_string,
                                dateTime.timezone or '')


def Year(context, dateTime=None):
    """
    The date:year function returns the year portion of the
    dateTime supplied, or of the current year, as an integer.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date', 'gYearMonth',
                                      'gYear'))
    except ValueError:
        return number.nan
    return dateTime.year


def LeapYear(context, dateTime=None):
    """
    The date:leap-year function returns true if the year argument
    (defaults to current year) is a leap year, false otherwise.

    Implements version 1.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date', 'gYearMonth',
                                      'gYear'))
    except ValueError:
        return number.nan
    return calendar.isleap(dateTime.year) and boolean.true or boolean.false


def MonthInYear(context, dateTime=None):
    """
    The date:month-in-year function returns the month portion of
    the dateTime argument (defaults to current month) as an integer.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date', 'gYearMonth',
                                      'gMonthDay', 'gMonth'))
    except ValueError:
        return number.nan
    return dateTime.month


def MonthName(context, dateTime=None):
    """
    The date:month-name function returns the full English name
    of the month portion of a date.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date', 'gYearMonth',
                                      'gMonthDay', 'gMonth'))
    except ValueError:
        month = 0
    else:
        month = dateTime.month
    return (u'', u'January', u'February', u'March', u'April', u'May', u'June',
            u'July', u'August', u'September', u'October', u'November',
            u'December')[month]


def MonthAbbreviation(context, dateTime=None):
    """
    The date:month-abbreviation function returns the abbreviation
    of the month of a date.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date', 'gYearMonth',
                                      'gMonthDay', 'gMonth'))
    except ValueError:
        month = 0
    else:
        month = dateTime.month
    return (u'', u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul',
            u'Aug', u'Sep', u'Oct', u'Nov', u'Dec')[month]


def WeekInYear(context, dateTime=None):
    """
    The date:week-in-year function returns a number representing
    the week of the year a date is in.

    Implements version 3.
    """
    # Notes:
    #  - ISO 8601 specifies that Week 01 of the year is the week containing
    #    the first Thursday;
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date'))
    except ValueError:
        return number.nan

    year, month, day = dateTime.year, dateTime.month, dateTime.day

    # Find Jan 1 weekday for Y
    # _dayOfWeek returns 0=Sun, we need Mon=0
    day_of_week_0101 = (_dayOfWeek(year, 1, 1) + 6) % 7

    # Find weekday for Y M D
    day_number = _dayInYear(year, month, day)
    day_of_week = (day_number + day_of_week_0101 - 1) % 7

    # Find if Y M D falls in year Y-1, week 52 or 53
    #  (i.e., the first 3 days of the year and DOW is Fri, Sat or Sun)
    if day_of_week_0101 > 3 and day_number <= (7 - day_of_week_0101):
        week = 52 + (day_of_week_0101 == (4 + calendar.isleap(year - 1)))
    # Find if Y M D falls in Y+1, week 1
    #  (i.e., the last 3 days of the year and DOW is Mon, Tue, or Wed)
    elif (365 + calendar.isleap(year) - day_number) < (3 - day_of_week):
        week = 1
    else:
        week = (day_number + (6 - day_of_week) + day_of_week_0101) / 7
        if day_of_week_0101 > 3:
            week -= 1
    return week


def DayInYear(context, dateTime=None):
    """
    The date:day-in-year function returns a number representing
    the position of a date in the year.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date'))
    except ValueError:
        return number.nan
    return _dayInYear(dateTime.year, dateTime.month, dateTime.day)


def DayInMonth(context, dateTime=None):
    """
    The date:day-in-month function returns the numerical date, i.e.
    27 for the 27th of March.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date', 'gMonthDay', 'gDay'))
    except ValueError:
        return number.nan
    return dateTime.day


def DayOfWeekInMonth(context, dateTime=None):
    """
    The date:day-of-week-in-month function returns the day-of-the-week
    in a month of a date as a number (e.g. 3 for the 3rd Tuesday in May).

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date'))
    except ValueError:
        return number.nan
    return ((dateTime.day - 1) / 7) + 1


def DayInWeek(context, dateTime=None):
    """
    The date:day-in-week function returns a number representing the
    weekday of a given date. Sunday is 1, Saturday is 7.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date'))
    except ValueError:
        year, month, day = None, None, None
    else:
        year, month, day = dateTime.year, dateTime.month, dateTime.day
    if year is None or month is None or day is None:
        return number.nan
    # _dayOfWeek is zero-based Sunday, EXSLT needs 1-based
    return _dayOfWeek(year, month, day) + 1


def DayName(context, dateTime=None):
    """
    The date:day-name function returns the full English day name of
    a given date.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date'))
    except ValueError:
        year, month, day = None, None, None
    else:
        year, month, day = dateTime.year, dateTime.month, dateTime.day
    if year is None or month is None or day is None:
        return u''
    weekday = _dayOfWeek(year, month, day)
    return (u'Sunday', u'Monday', u'Tuesday', u'Wednesday', u'Thursday',
            u'Friday', u'Saturday', u'Sunday')[weekday]


def DayAbbreviation(context, dateTime=None):
    """
    The date:day-abbreviation function returns the English abbreviation
    for the day name of a given date.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date'))
    except ValueError:
        year, month, day = None, None, None
    else:
        year, month, day = dateTime.year, dateTime.month, dateTime.day
    if year is None or month is None or day is None:
        return u''
    weekday = _dayOfWeek(year, month, day)
    return (u'Sun', u'Mon', u'Tue', u'Wed', u'Thu', u'Fri', u'Sat')[weekday]


def HourInDay(context, dateTime=None):
    """
    The date:hour-in-date function returns the hour portion of a date-
    time string as an integer.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'time'))
    except ValueError:
        return number.nan
    return dateTime.hour


def MinuteInHour(context, dateTime=None):
    """
    The date:minute-in-hour function returns the minute portion of a
    date-time string as an integer.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'time'))
    except ValueError:
        return number.nan
    return dateTime.minute


def SecondInMinute(context, dateTime=None):
    """
    The date:second-in-minute function returns the seconds portion
    of a date-time string as an integer.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'time'))
    except ValueError:
        return number.nan
    return dateTime.second


## EXSLT Dates and Times: Other Elements (unstable)

class DateFormatElement(XsltElement):
    """
    The date:date-format element declares a date format, which controls the
    interpretation of a format pattern used by the date:format-date and
    date:parse-date functions.

    Unimplemented (actually unused by afore mentioned functions).
    """
    pass


## EXSLT Dates and Times: Other Functions (unstable)

_re_SimpleDateFormat = re.compile(r"(?P<symbol>([GyMdhHmsSEDFwWakKz])\2*)"
                                  r"|'(?P<escape>(?:[^']|'')*)'")

def FormatDate(context, dateTime, pattern):
    """
    The date:format-date function formats a date/time according to a pattern.

    The first argument to date:format-date specifies the date/time to be
    formatted. It must be right or left-truncated date/time strings in one of
    the formats defined in XML Schema Part 2: Datatypes.  The permitted
    formats are as follows: xs:dateTime, xs:date, xs:time, xs:gYearMonth,
    xs:gYear, xs:gMonthDay, xs:gMonth and xs:gDay.

    The second argument is a string that gives the format pattern used to
    format the date. The format pattern must be in the syntax specified by
    the JDK 1.1 SimpleDateFormat class. The format pattern string is
    interpreted as described for the JDK 1.1 SimpleDateFormat class.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date', 'time', 'gYearMonth',
                                      'gYear', 'gMonthDay', 'gMonth', 'gDay'))
    except ValueError:
        return u''

    pattern = Conversions.StringValue(pattern)

    # Fill in missing components for right-truncated formats
    if dateTime.year is not None:
        if dateTime.month is None:
            dateTime.month = 1
        if dateTime.day is None:
            dateTime.day = 1
    if dateTime.hour is None:
        dateTime.hour = 0
    if dateTime.minute is None:
        dateTime.minute = 0
    if dateTime.second is None:
        dateTime.second = 0.0

    def repl(match):
        # NOTE: uses inherited context and dateTime variables
        groups = match.groupdict()
        if groups['symbol'] is not None:
            symbol = groups['symbol']
            width = len(symbol)
            symbol = symbol[:1]
            if symbol == 'G':           # era designator
                if dateTime.year is None:
                    rt = u''
                elif dateTime.year > 0:
                    rt = u'AD'
                else:
                    rt = u'BC'
            elif symbol == 'y':         # year
                if dateTime.year is None:
                    rt = u''
                elif width > 2:
                    rt = u'%0.*d' % (width, dateTime.year)
                else:
                    rt = u'%0.2d' % (dateTime.year % 100)
            elif symbol == 'M':         # month in year
                if dateTime.month is None:
                    rt = u''
                elif width >= 4:
                    rt = MonthName(context, dateTime)
                elif width == 3:
                    rt = MonthAbbreviation(context, dateTime)
                else:
                    rt = u'%0.*d' % (width, dateTime.month)
            elif symbol == 'd':         # day in month
                if dateTime.day is None:
                    rt = u''
                else:
                    rt = u'%0.*d' % (width, dateTime.day)
            elif symbol == 'h':         # hour in am/pm (1-12)
                hours = dateTime.hour
                if hours > 12:
                    hours -= 12
                elif hours == 0:
                    hours = 12
                rt = u'%0.*d' % (width, hours)
            elif symbol == 'H':         # hour in day (0-23)
                rt = u'%0.*d' % (width, dateTime.hour)
            elif symbol == 'm':         # minute in hour
                rt = u'%0.*d' % (width, dateTime.minute)
            elif symbol =='s':          # second in minute
                rt = u'%0.*d' % (width, dateTime.second)
            elif symbol == 'S':         # millisecond
                fraction, second = math.modf(dateTime.second)
                fraction, millisecond = math.modf(fraction * 10**width)
                rt = u'%0.*d' % (width, millisecond + round(fraction))
            elif symbol == 'E':         # day in week
                if (dateTime.year is None or
                    dateTime.month is None or
                    dateTime.day is None):
                    rt = u''
                elif width >= 4:
                    rt = DayName(context, dateTime)
                else:
                    rt = DayAbbreviation(context, dateTime)
            elif symbol == 'D':         # day in year
                if (dateTime.year is None or
                    dateTime.month is None or
                    dateTime.day is None):
                    rt = u''
                else:
                    rt = u'%0.*d' % (width, DayInYear(context, dateTime))
            elif symbol == 'F':         # day of week in month
                if dateTime.day is None:
                    rt = u''
                else:
                    day_of_week = DayOfWeekInMonth(context, dateTime)
                    rt = u'%0.*d' % (width, day_of_week)
            elif symbol == 'w':         # week in year
                if (dateTime.year is None or
                    dateTime.month is None or
                    dateTime.day is None):
                    rt = u''
                else:
                    rt = u'%0.*d' % (width, WeekInYear(context, dataTime))
            elif symbol == 'W':         # week in month
                if (dateTime.year is None or
                    dateTime.month is None or
                    dateTime.day is None):
                    rt = u''
                else:
                    rt = u'%0.*d' % (width, WeekInMonth(context, dateTime))
            elif symbol == 'a':
                if dateTime.hour < 12:
                    rt = u'AM'
                else:
                    rt = u'PM'
            elif symbol == 'k':         # hour in day (1-24)
                rt = u'%0.*d' % (width, dateTime.hour + 1)
            elif symbol == 'K':         # hour in am/pm (0-11)
                hours = dateTime.hour
                if hours >= 12:
                    hours -= 12
                rt = u'%0.*d' % (width, hours)
            elif symbol == 'z':
                rt = dateTime.timezone or u''
            else:
                # not reached due to regular expression (supposedly)
                raise RuntimeException("bad format symbol '%s'" % symbol)
        elif groups['escape']:
            rt = groups['escape'].replace(u"''", u"'")
        else:
            # 'escape' group was empty, just matched '' (escaped single quote)
            rt = u"'"
        return rt

    return _re_SimpleDateFormat.sub(repl, pattern)


def ParseDate(context, dateString, pattern):
    print "Warning: ParseDate not implemented"
    return "error"


def WeekInMonth(context, dateTime=None):
    """
    The date:week-in-month function returns the week in a month of a date as
    a number. If no argument is given, then the current local date/time, as
    returned by date:date-time is used the default argument. For the purposes
    of numbering, the first day of the month is in week 1 and new weeks begin
    on a Monday (so the first and last weeks in a month will often have less
    than 7 days in them).

    Implements version 3.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date'))
    except ValueError:
        return number.nan
    day_of_week = _dayOfWeek(dateTime.year, dateTime.month, dateTime.day)
    # _dayOfWeek returns 0=Sun, we need Sun=7
    day_of_week = ((day_of_week + 6) % 7) + 1
    week_offset = dateTime.day - day_of_week
    return (week_offset / 7) + (week_offset % 7 and 2 or 1)


def Difference(context, start, end):
    """
    The date:difference function returns the difference between the first date
    and the second date as a duration in string form.

    Implements version 1.
    """
    try:
        start = _coerce(start, ('dateTime', 'date', 'gYearMonth', 'gYear'))
        end = _coerce(end, ('dateTime', 'date', 'gYearMonth', 'gYear'))
    except ValueError:
        return u''
    return unicode(_difference(start, end))


def Add(context, dateTime, duration):
    """
    The date:add function returns the result of adding a duration to a dateTime.

    Implements version 2.
    """
    try:
        dateTime = _coerce(dateTime, ('dateTime', 'date', 'gYearMonth',
                                      'gYear'))
        duration = _Duration.parse(Conversions.StringValue(duration))
    except ValueError:
        return u''

    result = _DateTime()
    # Get the "adjusted" duration values
    if duration.negative:
        years, months, days, hours, minutes, seconds = (-duration.years,
                                                        -duration.months,
                                                        -duration.days,
                                                        -duration.hours,
                                                        -duration.minutes,
                                                        -duration.seconds)
    else:
        years, months, days, hours, minutes, seconds = (duration.years,
                                                        duration.months,
                                                        duration.days,
                                                        duration.hours,
                                                        duration.minutes,
                                                        duration.seconds)
    # Months (may be modified below)
    months += (dateTime.month or 1)
    carry, result.month = divmod(months - 1, 12)
    result.month += 1

    # Years (may be modified below)
    result.year = dateTime.year + years + carry

    # Timezone
    result.timezone = dateTime.timezone

    # Seconds
    seconds += (dateTime.second or 0)
    carry, result.second = divmod(seconds, 60)

    # Minutes
    minutes += (dateTime.minute or 0) + carry
    carry, result.minute = divmod(minutes, 60)

    # Hours
    hours += (dateTime.hour or 0) + carry
    carry, result.hour = divmod(hours, 24)

    # Days
    max_day = _daysInMonth(result.year, result.month)
    if dateTime.day > max_day:
        day = max_day
    if dateTime.day < 1:
        day = 1
    else:
        day = dateTime.day
    result.day = day + days + carry
    while True:
        max_day = _daysInMonth(result.year, result.month)
        if result.day > max_day:
            result.day -= max_day
            carry = 1
        elif result.day < 1:
            if result.month == 1:
                max_day = _daysInMonth(result.year - 1, 12)
            else:
                max_day = _daysInMonth(result.year, result.month - 1)
            result.day += max_day
            carry = -1
        else:
            break
        carry, result.month = divmod(result.month + carry - 1, 12)
        result.month += 1
        result.year += carry

    # Create output representation based in dateTime input
    # xs:gYear
    if dateTime.month is None:
        result = u'%0.4d%s' % (result.year, result.timezone or '')

    # xs:gYearMonth
    elif dateTime.day is None:
        result = u'%0.4d-%02d%s' % (result.year, result.month,
                                    result.timezone or '')

    # xs:date
    elif dateTime.hour is None:
        result = u'%0.4d-%02d-%02d%s' % (result.year, result.month, result.day,
                                         result.timezone or '')

    # xs:dateTime
    else:
        result = unicode(result)
    return result


def AddDuration(context, duration1, duration2):
    """
    The date:add-duration function returns the duration resulting from adding
    two durations together.

    Implements version 2.
    """
    duration1 = Conversions.StringValue(duration1)
    duration2 = Conversions.StringValue(duration2)
    try:
        duration1 = _Duration.parse(duration1)
        duration2 = _Duration.parse(duration2)
        duration = _addDurations(duration1, duration2)
    except ValueError:
        return u''

    return unicode(duration)


def Sum(context, nodeset):
    """
    The date:sum function adds a set of durations together. The string values
    of the nodes in the node set passed as an argument are interpreted as
    durations and added together as if using the date:add-duration function.

    Implements version 1.
    """
    if not isinstance(nodeset, XPathTypes.NodesetType):
        return u''
    try:
        strings = map(Conversions.StringValue, nodeset)
        durations = map(_Duration.parse, strings)
        duration = _addDurations(*durations)
    except ValueError:
        return u''

    return unicode(duration)


def Seconds(context, string=None):
    """
    The date:seconds function returns the number of seconds specified by the
    argument string. If no argument is given, then the current local
    date/time, as returned by date:date-time is used as a default argument.

    Implements version 1.
    """
    if string is None:
        string = str(_DateTime.now())
    else:
        string = Conversions.StringValue(string)

    try:
        if 'P' in string:
            # its a duration
            duration = _Duration.parse(string)
        else:
            # its a dateTime
            dateTime = _DateTime.parse(string, ('dateTime', 'date',
                                                'gYearMonth', 'gYear'))
            duration = _difference(_EPOCH, dateTime)
    except ValueError:
        return number.nan

    # The number of years and months must both be equal to zero
    if duration.years or duration.months:
        return number.nan

    # Convert the duration to just seconds
    seconds = (duration.days * 86400 + duration.hours * 3600 +
               duration.minutes * 60 + duration.seconds )
    if duration.negative:
        seconds *= -1
    return seconds


def Duration(context, seconds=None):
    """
    The date:duration function returns a duration string representing the
    number of seconds specified by the argument string. If no argument is
    given, then the result of calling date:seconds without any arguments is
    used as a default argument.

    Implements version 1.
    """
    if seconds is None:
        # The epoch for EXSLT is 1970-01-01T00:00:00Z
        # FIXME: we could code around this, but most (all?) platforms we
        # support have a time() epoch of 1970-01-01, so why bother.
        if time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0)) != time.timezone:
            warnings.warn("platform epoch != 1970-01-01", RuntimeWarning)
        # Don't use fractional seconds to keep with constructed dateTimes
        seconds = int(time.time())
    else:
        seconds = Conversions.NumberValue(seconds)
        if not number.finite(seconds):
            # +/-Inf or NaN
            return u''
    duration = _Duration(negative=(seconds < 0), seconds=abs(seconds))
    return unicode(duration)


## Internals

class _DateTime(object):
    """
    INTERNAL: representation of an exact point on a timeline.
    """

    __slots__ = ('year', 'month', 'day', 'hour', 'minute', 'second', 'timezone')

    patterns = {
        'year'     : '[-]?[0-9]{4,}',
        'month'    : '[0-9]{2}',
        'day'      : '[0-9]{2}',
        'hour'     : '[0-9]{2}',
        'minute'   : '[0-9]{2}',
        'second'   : '[0-9]{2}(?:[.][0-9]+)?',
        'timezone' : 'Z|[-+][0-9]{2}:[0-9]{2}'
        }
    for name, pattern in patterns.iteritems():
        patterns[name] = '(?P<%s>%s)' % (name, pattern)
    del name, pattern

    datatypes = {
        'dateTime'   : '%(date)sT%(time)s',
        'date'       : '%(year)s-%(month)s-%(day)s',
        'time'       : '%(hour)s:%(minute)s:%(second)s',
        'gYearMonth' : '%(year)s-%(month)s',
        'gYear'      : '%(year)s',
        'gMonthDay'  : '--%(month)s-%(day)s',
        'gMonth'     : '--%(month)s',
        'gDay'       : '---%(day)s',
        }
    datatypes['dateTime'] = datatypes['dateTime'] % datatypes
    for name, pattern in datatypes.iteritems():
        pattern = '^' + pattern + '%(timezone)s?$'
        datatypes[name] = re.compile(pattern % patterns)
    del name, pattern

    def parse(cls, string, datatypes=None):
        if not datatypes:
            datatypes = cls.datatypes
        for name in datatypes:
            try:
                regexp = cls.datatypes[name]
            except KeyError:
                raise RuntimeException('unsupported datatype: %r' % name)
            match = regexp.match(string)
            if match:
                return cls(**match.groupdict())
        raise ValueError('invalid date/time literal: %r' % string)
    parse = classmethod(parse)

    def now(cls):
        year, month, day, hour, minute, second  = time.gmtime()[:6]
        return cls(year=year, month=month, day=day, hour=hour, minute=minute,
                   second=second, timezone='Z')
    now = classmethod(now)

    def __init__(self, year=None, month=None, day=None, hour=None,
                 minute=None, second=None, timezone=None):
        self.year = year and int(year)
        self.month = month and int(month)
        self.day = day and int(day)
        self.hour = hour and int(hour)
        self.minute = minute and int(minute)
        self.second = second and float(second)
        self.timezone = timezone and unicode(timezone)
        return

    def utcoffset(self):
        """
        Returns the offset from UTC in minutes.
        """
        if not self.timezone:
            offset = None
        elif self.timezone == 'Z':
            offset = 0
        else:
            # timezone is in +/-HH:MM format
            hours, minutes = map(int, self.timezone.split(':'))
            if hours < 0:
                offset = hours * 60 - minutes
            else:
                offset = hours * 60 + minutes
        return offset

    def __str__(self):
        if not self.second:
            second_as_string = '00'
        elif self.second < 10:
            second_as_string = '0%.12g' % self.second
        else:
            second_as_string = '%.12g' % self.second
        return '%-.4d-%02d-%02dT%02d:%02d:%s%s' % (self.year or 0,
                                                   self.month or 0,
                                                   self.day or 0,
                                                   self.hour or 0,
                                                   self.minute or 0,
                                                   second_as_string,
                                                   self.timezone or '')

    def __repr__(self):
        return '%s(%r, %r, %r, %r, %r, %r, %r)' % (
            self.__class__.__name__, self.year, self.month, self.day,
            self.hour, self.minute, self.second, self.timezone)


_EPOCH = _DateTime.parse('1970-01-01T00:00:00Z')


class _Duration(object):

    __slots__ = ('negative', 'years', 'months', 'days', 'hours', 'minutes',
                 'seconds')

    regexp = re.compile('^(?P<negative>[-])?P(?:(?P<years>[0-9]+)Y)?'
                        '(?:(?P<months>[0-9]+)M)?(?:(?P<days>[0-9]+)D)?'
                        '(?P<time>T(?:(?P<hours>[0-9]+)H)?'
                        '(?:(?P<minutes>[0-9]+)M)?'
                        '(?:(?P<seconds>[0-9]+(?:[.][0-9]+)?)S)?)?$')

    def parse(cls, string):
        match = cls.regexp.match(string)
        if match:
            parts = match.groupdict()
            # Verify that if the time designator is given, there is at least
            # one time component as well.  This cannot be done easily with
            # just the RE.
            time = parts['time']
            try:
                time is None or time[1]
            except IndexError:
                # Fall through to the ValueError below
                pass
            else:
                del parts['time']
                return cls(**parts)
        raise ValueError('invalid duration literal: %r' % string)
    parse = classmethod(parse)

    def __init__(self, negative=None, years=None, months=None, days=None,
                 hours=None, minutes=None, seconds=None):
        self.negative = negative and True or False
        self.years = years and int(years) or 0
        self.months = months and int(months) or 0
        self.days = days and int(days) or 0
        self.hours = hours and int(hours) or 0
        self.minutes = minutes and int(minutes) or 0
        self.seconds = seconds and float(seconds) or 0

        # Normalize the values to range
        minutes, self.seconds = divmod(self.seconds, 60)
        hours, self.minutes = divmod(self.minutes + int(minutes), 60)
        days, self.hours = divmod(self.hours + hours, 24)
        self.days += days
        years, self.months = divmod(self.months, 12)
        self.years += years
        return

    def __repr__(self):
        return '%s(%r, %r, %r, %r, %r, %r, %r)' % (
            self.__class__.__name__, self.negative, self.years, self.months,
            self.days, self.hours, self.minutes, self.seconds)

    def __str__(self):
        have_time = (self.hours or self.minutes or self.seconds)
        # Always format the duration in minimized form
        if not (self.years or self.months or self.days or have_time):
            # at least one designator MUST be present (arbitrary decision)
            return 'PT0S'
        parts = [self.negative and '-P' or 'P']
        if self.years:
            parts.append('%dY' % self.years)
        if self.months:
            parts.append('%dM' % self.months)
        if self.days:
            parts.append('%dD' % self.days)
        if have_time:
            parts.append('T')
        if self.hours:
            parts.append('%dH' % self.hours)
        if self.minutes:
            parts.append('%dM' % self.minutes)
        if self.seconds:
            parts.append('%0.12gS' % self.seconds)
        return ''.join(parts)


def _coerce(obj, datatypes):
    """
    INTERNAL: converts an XPath object to a _DateTime instance.
    """
    if obj is None:
        obj = _DateTime.now()
    elif not isinstance(obj, _DateTime):
        obj = _DateTime.parse(Conversions.StringValue(obj), datatypes)
    return obj


def _daysInMonth(year, month):
    """
    INTERNAL: calculates the number of days in a month for the given date.
    """
    days = (None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[month]
    if month == 2 and calendar.isleap(year):
        days += 1
    return days


def _dayInYear(year, month, day):
    """
    INTERNAL: calculates the ordinal date for the given date.
    """
    days = (None, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)[month]
    if month > 2 and calendar.isleap(year):
        days += 1
    return days + day


def _julianDay(year, month, day):
    """
    INTERNAL: calculates the Julian day (1-1-1 is day 1) for the given date.
    """
    date = _dayInYear(year, month, day)
    year -= 1
    return year*365 + (year / 4) - (year / 100) + (year / 400) + date


def _dayOfWeek(year, month, day):
    """
    INTERNAL: calculates the day of week (0=Sun, 6=Sat) for the given date.
    """
    return _julianDay(year, month, day) % 7


def _difference(start, end):
    """
    INTERNAL: subtracts the end date from the start date.
    """
    if type(start.timezone) is not type(end.timezone):
        raise TypeError('cannot subtract dateTimes with timezones and '
                        'dateTimes without timezones')

    years = end.year - start.year
    negative = start.year > end.year
    # If the least specific format is xs:gYear, just subtract the years.
    if start.month is None or end.month is None:
        return _Duration(negative=negative, years=abs(years))

    # If the least specific format is xs:gYearMonth, just subtract the years
    # and months.
    if start.day is None or end.day is None:
        months = abs(end.month - start.month + (years * 12))
        years, months = divmod(months, 12)
        negative = negative or (start.month > end.month)
        return _Duration(negative=negative, years=years, months=months)

    start_days = _julianDay(start.year, start.month, start.day)
    end_days = _julianDay(end.year, end.month, end.day)
    days = end_days - start_days
    negative = start_days > end_days

    # If the least specific format is xs:date, just subtract the days
    if start.hour is None or end.hour is None:
        return _Duration(negative=negative, days=abs(days))

    # They both are in the xs:dateTime format, continue to subtract the time.
    start_secs = start.hour * 3600 + start.minute * 60 + start.second
    end_secs = end.hour * 3600 + end.minute * 60 + end.second
    seconds = abs(end_secs - start_secs + (days * 86400))
    if start.timezone:
        # adjust seconds to be UTC
        assert end.timezone
        # Note, utcoffset() returns minutes
        seconds += (end.utcoffset() - start.utcoffset()) * 60
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    negative = negative or (start_secs > end_secs)
    return _Duration(negative=negative, days=days, hours=hours,
                     minutes=minutes, seconds=seconds)


def _addDurations(*durations):
    """
    INTERNAL: returns a new duration from the sum of the sequence of durations
    """
    if not durations:
        raise ValueError('no durations')

    months, seconds = 0, 0
    for duration in durations:
        other_months = duration.years * 12 + duration.months
        other_seconds = (duration.days * 86400 + duration.hours * 3600 +
                         duration.minutes * 60 + duration.seconds)
        if duration.negative:
            months -= other_months
            seconds -= other_seconds
        else:
            months += other_months
            seconds += other_seconds

    if (months < 0 and seconds > 0) or (months > 0 and seconds < 0):
        raise ValueError('months/seconds sign mismatch')

    return _Duration(negative=(months < 0 or seconds < 0),
                     months=abs(months), seconds=abs(seconds))


ExtNamespaces = {
    EXSL_DATE_TIME_NS : 'date',
    }

ExtElements = {
##    (EXSL_DATE_TIME_NS, 'date-format'): DateFormatElement
    }

ExtFunctions = {
    (EXSL_DATE_TIME_NS, 'date-time'): DateTime,
    (EXSL_DATE_TIME_NS, 'date'): Date,
    (EXSL_DATE_TIME_NS, 'time'): Time,
    (EXSL_DATE_TIME_NS, 'year'): Year,
    (EXSL_DATE_TIME_NS, 'leap-year'): LeapYear,
    (EXSL_DATE_TIME_NS, 'month-in-year'): MonthInYear,
    (EXSL_DATE_TIME_NS, 'month-name'): MonthName,
    (EXSL_DATE_TIME_NS, 'month-abbreviation'): MonthAbbreviation,
    (EXSL_DATE_TIME_NS, 'week-in-year'): WeekInYear,
    (EXSL_DATE_TIME_NS, 'day-in-year'): DayInYear,
    (EXSL_DATE_TIME_NS, 'day-in-month'): DayInMonth,
    (EXSL_DATE_TIME_NS, 'day-of-week-in-month'): DayOfWeekInMonth,
    (EXSL_DATE_TIME_NS, 'day-in-week'): DayInWeek,
    (EXSL_DATE_TIME_NS, 'day-name'): DayName,
    (EXSL_DATE_TIME_NS, 'day-abbreviation'): DayAbbreviation,
    (EXSL_DATE_TIME_NS, 'hour-in-day'): HourInDay,
    (EXSL_DATE_TIME_NS, 'minute-in-hour'): MinuteInHour,
    (EXSL_DATE_TIME_NS, 'second-in-minute'): SecondInMinute,
    (EXSL_DATE_TIME_NS, 'format-date'): FormatDate,
    #(EXSL_DATE_TIME_NS, 'parse-date'): ParseDate,
    (EXSL_DATE_TIME_NS, 'week-in-month'): WeekInMonth,
    (EXSL_DATE_TIME_NS, 'difference'): Difference,
    (EXSL_DATE_TIME_NS, 'add'): Add,
    (EXSL_DATE_TIME_NS, 'add-duration'): AddDuration,
    (EXSL_DATE_TIME_NS, 'sum'): Sum,
    (EXSL_DATE_TIME_NS, 'seconds'): Seconds,
    (EXSL_DATE_TIME_NS, 'duration'): Duration
    }

