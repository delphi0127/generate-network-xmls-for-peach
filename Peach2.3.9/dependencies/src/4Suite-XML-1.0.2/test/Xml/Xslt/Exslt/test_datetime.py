########################################################################
# $Header: /var/local/cvsroot/4Suite/test/Xml/Xslt/Exslt/test_datetime.py,v 1.2 2006/01/04 16:00:55 jkloth Exp $
"""Tests for EXSLT Dates and Times"""

import re

from Ft.Lib import boolean, number
from Ft.Xml.Xslt.Exslt import DateTime

DATE = r'-?[0-9]{4,}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[01])'
TIME = r'[012]\d:[0-5]\d:[0-6]\d'
DATETIME = DATE + 'T' + TIME
TZ = r'(Z|[-+][0-9]{2}:[0-9]{2})?'
DATE += TZ
TIME += TZ
DATETIME += TZ

TESTS = []

# date:date-time()
def test_DateTime(tester):
    tester.startTest('date:date-time() syntax')
    result = DateTime.DateTime(None)
    tester.compare(True, re.search('^%s$' % DATETIME, result) is not None,
                   'Result %r does not match regexp %r' % (result, DATETIME))
    tester.testDone()
    return
TESTS.append(test_DateTime)


# date:date()
def test_Date(tester):
    tester.startTest('date:date() syntax')
    result = DateTime.Date(None)
    tester.compare(True, re.search('^%s$' % DATE, result) is not None,
                   'Result %r does not match regexp %r' % (result, DATE))
    tester.testDone()

    dates = [
        (u'2003-09-12T23:59:59-0400', u''),     # RFC822 TZ format bad!
        (u'2003-09-12T23:59:59-04:00', u'2003-09-12-04:00'),
        # TZ on input, MUST have TZ on output
        (u'2001-01-01T00:00:00Z', u'2001-01-01Z'),
        # no TZ on input, MUST NOT have TZ on output
        (u'2000-01-01T00:00:00', u'2000-01-01'),
        (u'2005-05-05', u'2005-05-05'),
        (u'Jan 01, 2001', u''),
        #(u'2005-05-05+0100', u'2005-05-05+0100'), # tz in = tz out? spec unclear
        ]
    for source, expected in dates:
        tester.startTest("date:date('%s')" % source)
        result = DateTime.Date(None, source)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_Date)


# date:time()
def test_Time(tester):
    tester.startTest('date:time() syntax')
    result = DateTime.Time(None)
    tester.compare(True, re.search('^%s$' % TIME, result) is not None,
                   'Result %r does not match regexp %r' % (result, TIME))
    tester.testDone()

    times = [
        (u'2003-09-12T23:59:59-0400', u''),     # RFC822 format TZ bad!
        (u'2003-09-12T23:59:59-04:00', u'23:59:59-04:00'),
        # TZ on input, MUST have TZ on output
        (u'2001-01-01T00:00:00Z', u'00:00:00Z'),
        # no TZ on input, MUST NOT have TZ on output
        (u'2000-01-01T00:00:00', u'00:00:00'),
        (u'00:00:00', u'00:00:00'), # xs:date input good!
        (u'T00:00:00', u''),        # ISO 8601 date input bad!
        (u'02:22:22 PM', u''),
        ]
    for time, expected in times:
        tester.startTest("date:time('%s')" % time)
        result = DateTime.Time(None, time)
        if isinstance(expected, list):
            tester.compareIn(expected, result)
        else:
            tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_Time)


# date:year()
def test_Year(tester):
    tests = [
        (u'2003-09-12T23:59:59-04:00', 2003),
        (u'2001-01-01', 2001),
        (u'2000-01', 2000),
        (u'1999', 1999)
        ]
    for datetime, expected in tests:
        tester.startTest("date:year('%s')" % datetime)
        result = DateTime.Year(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_Year)


# date:leap-year()
def test_LeapYear(tester):
    tests = [
        (u'2004-09-12T23:59:59-04:00', boolean.true),
        (u'2000-01-01', boolean.true),
        (u'1900', boolean.false),
        (u'3000', boolean.false)
        ]
    for datetime, expected in tests:
        tester.startTest("date:leap-year('%s')" % datetime)
        result = DateTime.LeapYear(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_LeapYear)


# date:month-in-year()
def test_MonthInYear(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', 5),      # xs:dateTime
        (u'2002-05-09T19:00:00Z', 5),           # xs:dateTime
        (u'2002-11-09T19:00:00', 11),           # xs:dateTime
        (u'2002-03-10+13:00', 3),               # xs:date
        (u'2002-06-09-11:00', 6),               # xs:date
        (u'2002-02-08', 2),                     # xs:date
        (u'12:20:00-05:00', number.nan),        # xs:time
        (u'17:20:00Z', number.nan),             # xs:time
        (u'24:00:00', number.nan),              # xs:time
        (u'1999-12Z', 12),                      # xs:gYearMonth
        (u'1999-04', 4),                        # xs:gYearMonth
        (u'1999-07:00', number.nan),            # xs:gYear
        (u'1999', number.nan),                  # xs:gYear
        (u'--08-14+14:00', 8),                  # xs:gMonthDay
        (u'--09-14', 9),                        # xs:gMonthDay
        (u'--07-11:00', 7),                     # xs:gMonth
        (u'--10', 10),                          # xs:gMonth
        (u'---05Z', number.nan),                # xs:gDay
        (u'---09', number.nan),                 # xs:gDay
        ]
    for datetime, expected in tests:
        tester.startTest("date:month-in-year('%s')" % datetime)
        result = DateTime.MonthInYear(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_MonthInYear)


# date:month-name()
def test_MonthName(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', u'May'), # xs:dateTime
        (u'2002-05-09T19:00:00Z', u'May'),      # xs:dateTime
        (u'2002-11-09T19:00:00', u'November'),  # xs:dateTime
        (u'2002-03-10+13:00', u'March'),        # xs:date
        (u'2002-06-09-11:00', u'June'),         # xs:date
        (u'2002-04-08', u'April'),              # xs:date
        (u'12:20:00-05:00', u''),               # xs:time
        (u'17:20:00Z', u''),                    # xs:time
        (u'24:00:00', u''),                     # xs:time
        (u'1999-12Z', u'December'),             # xs:gYearMonth
        (u'1999-04', u'April'),                 # xs:gYearMonth
        (u'1999-07:00', u''),                   # xs:gYear
        (u'1999', u''),                         # xs:gYear
        (u'--08-14+14:00', u'August'),          # xs:gMonthDay
        (u'--09-14', u'September'),             # xs:gMonthDay
        (u'--07-11:00', u'July'),               # xs:gMonth
        (u'--10', u'October'),                  # xs:gMonth
        (u'---05Z', u''),                       # xs:gDay
        (u'---09', u''),                        # xs:gDay
        ]
    for datetime, expected in tests:
        tester.startTest("date:month-name('%s')" % datetime)
        result = DateTime.MonthName(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_MonthName)


# date:month-abbreviation()
def test_MonthAbbreviation(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', u'May'), # xs:dateTime
        (u'2002-05-09T19:00:00Z', u'May'),      # xs:dateTime
        (u'2002-11-09T19:00:00', u'Nov'),       # xs:dateTime
        (u'2002-03-10+13:00', u'Mar'),          # xs:date
        (u'2002-06-09-11:00', u'Jun'),          # xs:date
        (u'2002-04-08', u'Apr'),                # xs:date
        (u'12:20:00-05:00', u''),               # xs:time
        (u'17:20:00Z', u''),                    # xs:time
        (u'24:00:00', u''),                     # xs:time
        (u'1999-12Z', u'Dec'),                  # xs:gYearMonth
        (u'1999-04', u'Apr'),                   # xs:gYearMonth
        (u'1999-07:00', u''),                   # xs:gYear
        (u'1999', u''),                         # xs:gYear
        (u'--08-14+14:00', u'Aug'),             # xs:gMonthDay
        (u'--09-14', u'Sep'),                   # xs:gMonthDay
        (u'--07-11:00', u'Jul'),                # xs:gMonth
        (u'--10', u'Oct'),                      # xs:gMonth
        (u'---05Z', u''),                       # xs:gDay
        (u'---09', u''),                        # xs:gDay
        ]
    for datetime, expected in tests:
        tester.startTest("date:month-abbreviation('%s')" % datetime)
        result = DateTime.MonthAbbreviation(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_MonthAbbreviation)


# date:week-in-year()
def test_WeekInYear(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', 19),     # xs:dateTime
        (u'2002-05-09T19:00:00Z', 19),          # xs:dateTime
        (u'2002-11-09T19:00:00', 45),           # xs:dateTime
        (u'2002-03-10+13:00', 10),              # xs:date
        (u'2002-06-09-11:00', 23),              # xs:date
        (u'2002-04-08', 15),                    # xs:date
        (u'12:20:00-05:00', number.nan),        # xs:time
        (u'17:20:00Z', number.nan),             # xs:time
        (u'24:00:00', number.nan),              # xs:time
        (u'1999-12Z', number.nan),              # xs:gYearMonth
        (u'1999-04', number.nan),               # xs:gYearMonth
        (u'1999-07:00', number.nan),            # xs:gYear
        (u'1999', number.nan),                  # xs:gYear
        (u'--08-14+14:00', number.nan),         # xs:gMonthDay
        (u'--09-14', number.nan),               # xs:gMonthDay
        (u'--07-11:00', number.nan),            # xs:gMonth
        (u'--10', number.nan),                  # xs:gMonth
        (u'---05Z', number.nan),                # xs:gDay
        (u'---09', number.nan),                 # xs:gDay
        # test case some edge cases
        (u'1969-12-30', 1),
        (u'1971-01-01', 53),
        (u'1979-12-31', 1),
        (u'1984-01-01', 52),
        (u'1991-12-30', 1),
        (u'1999-01-03', 53),
        (u'2012-12-31', 1),
        (u'2017-01-01', 52),
        (u'2029-01-01', 1),
        ]
    for datetime, expected in tests:
        tester.startTest("date:month-in-year('%s')" % datetime)
        result = DateTime.WeekInYear(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_WeekInYear)


# date:day-in-year()
def test_DayInYear(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', 130),    # xs:dateTime
        (u'2002-05-09T19:00:00Z', 129),         # xs:dateTime
        (u'2002-11-09T19:00:00', 313),          # xs:dateTime
        (u'2002-03-10+13:00', 69),              # xs:date
        (u'2002-06-09-11:00', 160),             # xs:date
        (u'2002-04-08', 98),                    # xs:date
        (u'12:20:00-05:00', number.nan),        # xs:time
        (u'17:20:00Z', number.nan),             # xs:time
        (u'24:00:00', number.nan),              # xs:time
        (u'1999-12Z', number.nan),              # xs:gYearMonth
        (u'1999-04', number.nan),               # xs:gYearMonth
        (u'1999-07:00', number.nan),            # xs:gYear
        (u'1999', number.nan),                  # xs:gYear
        (u'--08-14+14:00', number.nan),         # xs:gMonthDay
        (u'--09-14', number.nan),               # xs:gMonthDay
        (u'--07-11:00', number.nan),            # xs:gMonth
        (u'--10', number.nan),                  # xs:gMonth
        (u'---05Z', number.nan),                # xs:gDay
        (u'---09', number.nan),                 # xs:gDay
        ]
    for datetime, expected in tests:
        tester.startTest("date:day-in-year('%s')" % datetime)
        result = DateTime.DayInYear(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_DayInYear)


# date:day-in-month()
def test_DayInMonth(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', 10),     # xs:dateTime
        (u'2002-05-09T19:00:00Z', 9),           # xs:dateTime
        (u'2002-11-09T19:00:00', 9),            # xs:dateTime
        (u'2002-03-10+13:00', 10),              # xs:date
        (u'2002-06-09-11:00', 9),               # xs:date
        (u'2002-04-08', 8),                     # xs:date
        (u'12:20:00-05:00', number.nan),        # xs:time
        (u'17:20:00Z', number.nan),             # xs:time
        (u'24:00:00', number.nan),              # xs:time
        (u'1999-12Z', number.nan),              # xs:gYearMonth
        (u'1999-04', number.nan),               # xs:gYearMonth
        (u'1999-07:00', number.nan),            # xs:gYear
        (u'1999', number.nan),                  # xs:gYear
        (u'--08-14+14:00', 14),                 # xs:gMonthDay
        (u'--09-14', 14),                       # xs:gMonthDay
        (u'--07-11:00', number.nan),            # xs:gMonth
        (u'--10', number.nan),                  # xs:gMonth
        (u'---05Z', 5),                         # xs:gDay
        (u'---09', 9),                          # xs:gDay
        ]
    for datetime, expected in tests:
        tester.startTest("date:day-in-month('%s')" % datetime)
        result = DateTime.DayInMonth(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_DayInMonth)


# date:day-of-week-in-month()
def test_DayOfWeekInMonth(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', 2),      # xs:dateTime
        (u'2002-05-09T19:00:00Z', 2),           # xs:dateTime
        (u'2002-11-09T19:00:00', 2),            # xs:dateTime
        (u'2002-03-10+13:00', 2),               # xs:date
        (u'2002-06-09-11:00', 2),               # xs:date
        (u'2002-04-08', 2),                     # xs:date
        (u'12:20:00-05:00', number.nan),        # xs:time
        (u'17:20:00Z', number.nan),             # xs:time
        (u'24:00:00', number.nan),              # xs:time
        (u'1999-12Z', number.nan),              # xs:gYearMonth
        (u'1999-04', number.nan),               # xs:gYearMonth
        (u'1999-07:00', number.nan),            # xs:gYear
        (u'1999', number.nan),                  # xs:gYear
        (u'--08-14+14:00', number.nan),         # xs:gMonthDay
        (u'--09-14', number.nan),               # xs:gMonthDay
        (u'--07-11:00', number.nan),            # xs:gMonth
        (u'--10', number.nan),                  # xs:gMonth
        (u'---05Z', number.nan),                # xs:gDay
        (u'---09', number.nan),                 # xs:gDay
        ]
    for datetime, expected in tests:
        tester.startTest("date:day-of-week-in-month('%s')" % datetime)
        result = DateTime.DayOfWeekInMonth(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_DayOfWeekInMonth)


# date:day-in-week()
def test_DayInWeek(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', 6),      # xs:dateTime
        (u'2002-05-09T19:00:00Z', 5),           # xs:dateTime
        (u'2002-11-09T19:00:00', 7),            # xs:dateTime
        (u'2002-03-10+13:00', 1),               # xs:date
        (u'2002-06-09-11:00', 1),               # xs:date
        (u'2002-04-08', 2),                     # xs:date
        (u'12:20:00-05:00', number.nan),        # xs:time
        (u'17:20:00Z', number.nan),             # xs:time
        (u'24:00:00', number.nan),              # xs:time
        (u'1999-12Z', number.nan),              # xs:gYearMonth
        (u'1999-04', number.nan),               # xs:gYearMonth
        (u'1999-07:00', number.nan),            # xs:gYear
        (u'1999', number.nan),                  # xs:gYear
        (u'--08-14+14:00', number.nan),         # xs:gMonthDay
        (u'--09-14', number.nan),               # xs:gMonthDay
        (u'--07-11:00', number.nan),            # xs:gMonth
        (u'--10', number.nan),                  # xs:gMonth
        (u'---05Z', number.nan),                # xs:gDay
        (u'---09', number.nan),                 # xs:gDay
        ]
    for datetime, expected in tests:
        tester.startTest("date:day-in-week('%s')" % datetime)
        result = DateTime.DayInWeek(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_DayInWeek)


# date:day-name()
def test_DayName(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', u'Friday'), # xs:dateTime
        (u'2002-05-09T19:00:00Z', u'Thursday'), # xs:dateTime
        (u'2002-11-09T19:00:00', u'Saturday'),  # xs:dateTime
        (u'2002-03-10+13:00', u'Sunday'),       # xs:date
        (u'2002-06-09-11:00', u'Sunday'),       # xs:date
        (u'2002-04-08', u'Monday'),             # xs:date
        (u'12:20:00-05:00', u''),               # xs:time
        (u'17:20:00Z', u''),                    # xs:time
        (u'24:00:00', u''),                     # xs:time
        (u'1999-12Z', u''),                     # xs:gYearMonth
        (u'1999-04', u''),                      # xs:gYearMonth
        (u'1999-07:00', u''),                   # xs:gYear
        (u'1999', u''),                         # xs:gYear
        (u'--08-14+14:00', u''),                # xs:gMonthDay
        (u'--09-14', u''),                      # xs:gMonthDay
        (u'--07-11:00', u'') ,                  # xs:gMonth
        (u'--10', u''),                         # xs:gMonth
        (u'---05Z', u''),                       # xs:gDay
        (u'---09', u''),                        # xs:gDay
        ]
    for datetime, expected in tests:
        tester.startTest("date:day-name('%s')" % datetime)
        result = DateTime.DayName(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_DayName)


# date:day-abbreviation()
def test_DayAbbreviation(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', u'Fri'), # xs:dateTime
        (u'2002-05-09T19:00:00Z', u'Thu'),      # xs:dateTime
        (u'2002-11-09T19:00:00', u'Sat'),       # xs:dateTime
        (u'2002-03-10+13:00', u'Sun'),          # xs:date
        (u'2002-06-09-11:00', u'Sun'),          # xs:date
        (u'2002-04-08', u'Mon'),                # xs:date
        (u'12:20:00-05:00', u''),               # xs:time
        (u'17:20:00Z', u''),                    # xs:time
        (u'24:00:00', u''),                     # xs:time
        (u'1999-12Z', u''),                     # xs:gYearMonth
        (u'1999-04', u''),                      # xs:gYearMonth
        (u'1999-07:00', u''),                   # xs:gYear
        (u'1999', u''),                         # xs:gYear
        (u'--08-14+14:00', u''),                # xs:gMonthDay
        (u'--09-14', u''),                      # xs:gMonthDay
        (u'--07-11:00', u'') ,                  # xs:gMonth
        (u'--10', u''),                         # xs:gMonth
        (u'---05Z', u''),                       # xs:gDay
        (u'---09', u''),                        # xs:gDay
        ]
    for datetime, expected in tests:
        tester.startTest("date:day-abbreviation('%s')" % datetime)
        result = DateTime.DayAbbreviation(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_DayAbbreviation)


# date:hour-in-day()
def test_HourInDay(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', 0),      # xs:dateTime
        (u'2002-05-09T19:00:00Z', 19),          # xs:dateTime
        (u'2002-11-09T19:00:00', 19),           # xs:dateTime
        (u'2002-03-10+13:00', number.nan),      # xs:date
        (u'2002-06-09-11:00', number.nan),      # xs:date
        (u'2002-04-08', number.nan),            # xs:date
        (u'12:20:00-05:00', 12),                # xs:time
        (u'17:20:00Z', 17),                     # xs:time
        (u'24:00:00', 24),                      # xs:time
        (u'1999-12Z', number.nan),              # xs:gYearMonth
        (u'1999-04', number.nan),               # xs:gYearMonth
        (u'1999-07:00', number.nan),            # xs:gYear
        (u'1999', number.nan),                  # xs:gYear
        (u'--08-14+14:00', number.nan),         # xs:gMonthDay
        (u'--09-14', number.nan),               # xs:gMonthDay
        (u'--07-11:00', number.nan),            # xs:gMonth
        (u'--10', number.nan),                  # xs:gMonth
        (u'---05Z', number.nan),                # xs:gDay
        (u'---09', number.nan),                 # xs:gDay
        ]
    for datetime, expected in tests:
        tester.startTest("date:hour-in-day('%s')" % datetime)
        result = DateTime.HourInDay(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_HourInDay)


# date:minute-in-hour()
def test_MinuteInHour(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', 0),      # xs:dateTime
        (u'2002-05-09T19:00:00Z', 0),           # xs:dateTime
        (u'2002-11-09T19:00:00', 0),            # xs:dateTime
        (u'2002-03-10+13:00', number.nan),      # xs:date
        (u'2002-06-09-11:00', number.nan),      # xs:date
        (u'2002-04-08', number.nan),            # xs:date
        (u'12:20:00-05:00', 20),                # xs:time
        (u'17:20:00Z', 20),                     # xs:time
        (u'24:00:00', 0),                       # xs:time
        (u'1999-12Z', number.nan),              # xs:gYearMonth
        (u'1999-04', number.nan),               # xs:gYearMonth
        (u'1999-07:00', number.nan),            # xs:gYear
        (u'1999', number.nan),                  # xs:gYear
        (u'--08-14+14:00', number.nan),         # xs:gMonthDay
        (u'--09-14', number.nan),               # xs:gMonthDay
        (u'--07-11:00', number.nan),            # xs:gMonth
        (u'--10', number.nan),                  # xs:gMonth
        (u'---05Z', number.nan),                # xs:gDay
        (u'---09', number.nan),                 # xs:gDay
        ]
    for datetime, expected in tests:
        tester.startTest("date:minute-in-hour('%s')" % datetime)
        result = DateTime.MinuteInHour(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_MinuteInHour)


# date:second-in-minute()
def test_SecondInMinute(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', 0),      # xs:dateTime
        (u'2002-05-09T19:00:10Z', 10),          # xs:dateTime
        (u'2002-11-09T19:00:20', 20),           # xs:dateTime
        (u'2002-03-10+13:00', number.nan),      # xs:date
        (u'2002-06-09-11:00', number.nan),      # xs:date
        (u'2002-04-08', number.nan),            # xs:date
        (u'12:20:46-05:00', 46),                # xs:time
        (u'17:20:46Z', 46),                     # xs:time
        (u'24:00:00', 0),                       # xs:time
        (u'1999-12Z', number.nan),              # xs:gYearMonth
        (u'1999-04', number.nan),               # xs:gYearMonth
        (u'1999-07:00', number.nan),            # xs:gYear
        (u'1999', number.nan),                  # xs:gYear
        (u'--08-14+14:00', number.nan),         # xs:gMonthDay
        (u'--09-14', number.nan),               # xs:gMonthDay
        (u'--07-11:00', number.nan),            # xs:gMonth
        (u'--10', number.nan),                  # xs:gMonth
        (u'---05Z', number.nan),                # xs:gDay
        (u'---09', number.nan),                 # xs:gDay
        ]
    for datetime, expected in tests:
        tester.startTest("date:second-in-minute('%s')" % datetime)
        result = DateTime.SecondInMinute(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_SecondInMinute)


# date:format-date()
def test_FormatDate(tester):
    datetime = "2001-07-04T12:08:56.235-07:00"
    tests = [
        ("yyyy.MM.dd G 'at' HH:mm:ss", u"2001.07.04 AD at 12:08:56"),
        ("EEE, MMM d, ''yy", u"Wed, Jul 4, '01"),
        ("h:mm a", u"12:08 PM"),
        ("hh 'o''clock' a, zzzz", u"12 o'clock PM, -07:00"),
        ("K:mm a", u"0:08 PM"),
        ("yyyyy.MMMMM.dd GGG hh:mm aaa", u"02001.July.04 AD 12:08 PM"),
        ("EEE, d MMM yyyy HH:mm:ss", u"Wed, 4 Jul 2001 12:08:56"),
        ("yyMMddHHmmssz", u"010704120856-07:00"),
        #("yyyy-MM-dd'T'HH:mm:ss.SSSz", u"2001-07-04T12:08:56.235-07:00"),
        ]
    for pattern, expected in tests:
        tester.startTest('date:format-date(%r, %r)' % (datetime, pattern))
        result = DateTime.FormatDate(None, datetime, pattern)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_FormatDate)


# date:week-in-month()
def test_WeekInMonth(tester):
    tests = [
        (u'2002-05-10T00:00:00+05:00', 2),      # xs:dateTime
        (u'2002-05-09T19:00:00Z', 2),           # xs:dateTime
        (u'2002-11-09T19:00:00', 2),            # xs:dateTime
        (u'2002-03-10+13:00', 2),               # xs:date
        (u'2002-06-09-11:00', 2),               # xs:date
        (u'2002-04-08', 2),                     # xs:date
        (u'12:20:00-05:00', number.nan),        # xs:time
        (u'17:20:00Z', number.nan),             # xs:time
        (u'24:00:00', number.nan),              # xs:time
        (u'1999-12Z', number.nan),              # xs:gYearMonth
        (u'1999-04', number.nan),               # xs:gYearMonth
        (u'1999-07:00', number.nan),            # xs:gYear
        (u'1999', number.nan),                  # xs:gYear
        (u'--08-14+14:00', number.nan),         # xs:gMonthDay
        (u'--09-14', number.nan),               # xs:gMonthDay
        (u'--07-11:00', number.nan),            # xs:gMonth
        (u'--10', number.nan),                  # xs:gMonth
        (u'---05Z', number.nan),                # xs:gDay
        (u'---09', number.nan),                 # xs:gDay
        # test case some edge cases
        (u'1969-12-30', 5),
        (u'1971-01-01', 1),
        (u'1979-12-31', 6),
        (u'1984-01-01', 1),
        (u'1991-12-30', 6),
        (u'1999-01-03', 1),
        (u'2012-12-31', 6),
        (u'2017-01-01', 1),
        (u'2029-01-01', 1),
        ]
    for datetime, expected in tests:
        tester.startTest("date:month-in-month('%s')" % datetime)
        result = DateTime.WeekInMonth(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_WeekInMonth)


# date:seconds()
def test_Seconds(tester):
    tests = [
        # durations
        ('P0DT0H0M0S', 0),
        ('P0DT0H0M59S', 59),
        ('P0DT0H1M0S', 60),
        ('P0DT0H59M59S', 3599),
        ('P0DT1H0M0S', 3600),
        ('P0DT23H59M59S', 86399),
        ('P1DT0H0M0S', 86400),
        # duration years and months are not allowed
        ('P60DT0H0M0S', 86400*60),
        ('P2M', number.nan),
        ('P400DT0H0M0S', 86400*400),
        ('P1Y1M4D', number.nan),
        # dateTime (difference from 1970-01-01T00:00:00Z
        ('1970-01-01T00:00:00Z', 0),
        ('1970-01-01T00:00:59Z', 59),
        ('1970-01-01T00:01:00Z', 60),
        ('1970-01-01T00:59:59Z', 3599),
        ('1970-01-01T01:00:00Z', 3600),
        ('1970-01-01T23:59:59Z', 86399),
        ('1970-01-02Z', 86400),
        ('1970-03-02Z', 86400*60),
        ('1971-02-05Z', 86400*400),
        ]
    for datetime, expected in tests:
        tester.startTest('date:seconds(%r)' % (datetime))
        result = DateTime.Seconds(None, datetime)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_Seconds)


# date:difference()
def test_Difference(tester):
    tests = [
        ('1969-01-01T00:00:00Z', '1970-01-01T00:00:00Z', 'P365D'),
        ('1969-01-01T00:00:00Z', '1970-01-01T00:00:59Z', 'P365DT59S'),
        ('1969-01-01T00:00:00Z', '1970-01-01T00:01:00Z', 'P365DT1M'),
        ('1969-01-01T00:00:00Z', '1970-01-01T00:59:59Z', 'P365DT59M59S'),
        ('1969-01-01T00:00:00Z', '1970-01-01T01:00:00Z', 'P365DT1H'),
        ('1969-01-01T00:00:00Z', '1970-01-01T23:59:59Z', 'P365DT23H59M59S'),
        ('1969-01-01T00:00:00Z', '1970-01-02Z', 'P366D'),
        ('1969-01-01T00:00:00Z', '1970-03-02Z', 'P425D'),
        ('1969-01-01T00:00:00Z', '1971-02-05Z', 'P765D'),
        ('1969-01-01T00:00:00Z', '1972-02Z', 'P3Y1M'),
        ('1969-01-01T00:00:00Z', '1973Z', 'P4Y'),

        ('1970-01-01T00:00:00Z', '1970-01-01T00:00:00Z', 'PT0S'),
        ('1970-01-01T00:00:00Z', '1970-01-01T00:00:59Z', 'PT59S'),
        ('1970-01-01T00:00:00Z', '1970-01-01T00:01:00Z', 'PT1M'),
        ('1970-01-01T00:00:00Z', '1970-01-01T00:59:59Z', 'PT59M59S'),
        ('1970-01-01T00:00:00Z', '1970-01-01T01:00:00Z', 'PT1H'),
        ('1970-01-01T00:00:00Z', '1970-01-01T23:59:59Z', 'PT23H59M59S'),
        ('1970-01-01T00:00:00Z', '1970-01-02Z', 'P1D'),
        ('1970-01-01T00:00:00Z', '1970-03-02Z', 'P60D'),
        ('1970-01-01T00:00:00Z', '1971-02-05Z', 'P400D'),
        ('1970-01-01T00:00:00Z', '1972-02Z', 'P2Y1M'),
        ('1970-01-01T00:00:00Z', '1973Z', 'P3Y'),

        ('1971-01-01T00:00:00Z', '1970-01-01T00:00:00Z', '-P365D'),
        ('1971-01-01T00:00:00Z', '1970-01-01T00:00:59Z', '-P364DT23H59M1S'),
        ('1971-01-01T00:00:00Z', '1970-01-01T00:01:00Z', '-P364DT23H59M'),
        ('1971-01-01T00:00:00Z', '1970-01-01T00:59:59Z', '-P364DT23H1S'),
        ('1971-01-01T00:00:00Z', '1970-01-01T01:00:00Z', '-P364DT23H'),
        ('1971-01-01T00:00:00Z', '1970-01-01T23:59:59Z', '-P364DT1S'),
        ('1971-01-01T00:00:00Z', '1970-01-02Z', '-P364D'),
        ('1971-01-01T00:00:00Z', '1970-03-02Z', '-P305D'),
        ('1971-01-01T00:00:00Z', '1971-02-05Z', 'P35D'),
        ('1971-01-01T00:00:00Z', '1972-02Z', 'P1Y1M'),
        ('1971-01-01T00:00:00Z', '1973Z', 'P2Y'),
        ]
    for start, end, expected in tests:
        tester.startTest('date:difference(%r, %r)' % (start, end))
        result = DateTime.Difference(None, start, end)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_Difference)


# date:add()
def test_Add(tester):
    tests = [
        ('1969-01-01T00:00:00Z', 'P365D', '1970-01-01T00:00:00Z'),
        ('1969-01-01T00:00:00Z', 'P365DT59S', '1970-01-01T00:00:59Z'),
        ('1969-01-01T00:00:00Z', 'P365DT1M', '1970-01-01T00:01:00Z'),
        ('1969-01-01T00:00:00Z', 'P365DT59M59S', '1970-01-01T00:59:59Z'),
        ('1969-01-01T00:00:00Z', 'P365DT1H', '1970-01-01T01:00:00Z'),
        ('1969-01-01T00:00:00Z', 'P365DT23H59M59S', '1970-01-01T23:59:59Z'),
        ('1969-01-01Z', 'P366D', '1970-01-02Z'),
        ('1969-01-01Z', 'P425D', '1970-03-02Z'),
        ('1969-01-01Z', 'P765D', '1971-02-05Z'),
        ('1969-01Z', 'P3Y1M', '1972-02Z'),
        ('1969Z', 'P4Y', '1973Z'),

        ('1970-01-01T00:00:00Z', 'PT0S', '1970-01-01T00:00:00Z'),
        ('1970-01-01T00:00:00Z', 'PT59S', '1970-01-01T00:00:59Z'),
        ('1970-01-01T00:00:00Z', 'PT1M', '1970-01-01T00:01:00Z'),
        ('1970-01-01T00:00:00Z', 'PT59M59S', '1970-01-01T00:59:59Z'),
        ('1970-01-01T00:00:00Z', 'PT1H', '1970-01-01T01:00:00Z'),
        ('1970-01-01T00:00:00Z', 'PT23H59M59S', '1970-01-01T23:59:59Z'),
        ('1970-01-01Z', 'P1D', '1970-01-02Z'),
        ('1970-01-01Z', 'P60D', '1970-03-02Z'),
        ('1970-01-01Z', 'P400D', '1971-02-05Z'),
        ('1970-01Z', 'P2Y1M', '1972-02Z'),
        ('1970Z', 'P3Y', '1973Z'),

        ('1971-01-01T00:00:00Z', '-P365D', '1970-01-01T00:00:00Z'),
        ('1971-01-01T00:00:00Z', '-P364DT23H59M1S', '1970-01-01T00:00:59Z'),
        ('1971-01-01T00:00:00Z', '-P364DT23H59M', '1970-01-01T00:01:00Z'),
        ('1971-01-01T00:00:00Z', '-P364DT23H1S', '1970-01-01T00:59:59Z'),
        ('1971-01-01T00:00:00Z', '-P364DT23H', '1970-01-01T01:00:00Z'),
        ('1971-01-01T00:00:00Z', '-P364DT1S', '1970-01-01T23:59:59Z'),
        ('1971-01-01Z', '-P364D', '1970-01-02Z'),
        ('1971-01-01Z', '-P305D', '1970-03-02Z'),
        ('1971-01-01Z', 'P35D', '1971-02-05Z'),
        ('1971-01Z', 'P1Y1M', '1972-02Z'),
        ('1971Z', 'P2Y', '1973Z'),

        ('2000-01', '-P3M', '1999-10'),
        ('2000-01-12', 'PT33H', '2000-01-13'),
        ('2000-01-12T12:13:14Z', 'P1Y3M5DT7H10M3.3S', '2001-04-17T19:23:17.3Z')
        ]


    for datetime, duration, expected in tests:
        tester.startTest('date:add(%r, %r)' % (datetime, duration))
        result = DateTime.Add(None, datetime, duration)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_Add)


# date:add-duration()
def test_AddDuration(tester):
    tests = [
        ('PT3S', 'PT7S', 'PT10S'),
        ('PT59S', 'PT1S', 'PT1M'),
        ('PT59M59S', 'PT1S', 'PT1H'),
        ('PT23H59M59S', 'PT1S', 'P1D'),
        # 30+D != 1M
        ('P33D', 'P1Y1M', 'P1Y1M33D'),
        ('P1M', '-P30D', '')
        ]
    for duration1, duration2, expected in tests:
        tester.startTest('date:add-duration(%r, %r)' % (duration1, duration2))
        result = DateTime.AddDuration(None, duration1, duration2)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_AddDuration)


# date:sum()
def test_Sum(tester):
    tests = [
        (['PT3S', 'PT7S'], 'PT10S'),
        (['PT59S', 'PT1S'], 'PT1M'),
        (['PT59M59S', 'PT1S'], 'PT1H'),
        (['PT23H59M59S', 'PT1S'], 'P1D'),
        # 30+D != 1M
        (['P33D', 'P1Y1M'], 'P1Y1M33D'),
        (['P1M', '-P30D'], ''),
        (['P1M', '-P30D', 'P30D'], 'P1M'),
        ]
    for durations, expected in tests:
        tester.startTest('date:sum(%r)' % (durations))
        result = DateTime.Sum(None, durations)
        tester.compare(expected, result)
        tester.testDone()
    return
TESTS.append(test_Sum)


# date:duration()
def test_Duration(tester):
    tests = [
        (0, u'PT0S'),
        (59, u'PT59S'),
        (60, u'PT1M'),
        (3599, u'PT59M59S'),
        (3600, u'PT1H'),
        (86399, u'PT23H59M59S'),
        (86400, u'P1D'),
        # Make sure that only days are returned, no months or years
        (86400*60, u'P60D'),
        (86400*400, u'P400D'),
        ]
    for seconds, expected in tests:
        tester.startTest('date:duration(%0.12g)' % (seconds))
        result = DateTime.Duration(None, seconds)
        tester.compare(expected, result)
        tester.testDone()
        # Test negatives as well (if not epoch, as it cannot be negative)
        if seconds:
            seconds *= -1
            expected = '-' + expected
            tester.startTest('date:duration(%0.12g)' % (seconds))
            result = DateTime.Duration(None, seconds)
            tester.compare(expected, result)
            tester.testDone()
    return
TESTS.append(test_Duration)


def Test(tester):
    tester.startGroup('Dates and Times')
    for test in TESTS:
        test(tester)
    tester.groupDone()
    return
