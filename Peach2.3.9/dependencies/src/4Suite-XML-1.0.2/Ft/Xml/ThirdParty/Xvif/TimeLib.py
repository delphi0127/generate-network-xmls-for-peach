import re

try:
    from datetime import time, datetime
except:
    pass

#Regexen from Mark Nottingham (http://www.mnot.net/python/isodate.py)
DATETIME_PAT = re.compile(r"""
    (?P<year>\d{4,4})
    (?:
        -
        (?P<month>\d{1,2})
        (?:
            -
            (?P<day>\d{1,2})
            (?:
                T
                (?P<hour>\d{1,2})
                :
                (?P<minute>\d{1,2})
                (?:
                    :
                    (?P<second>\d{1,2})
                    (?:
                        \.
                        (?P<fract_second>\d+)?
                    )?
                )?
                (?:
                    Z
                    |
                    (?:
                        (?P<tz_sign>[+-])
                        (?P<tz_hour>\d{1,2})
                        :
                        (?P<tz_min>\d{2,2})
                    )
                )
            )?
        )?
    )?
$""", re.VERBOSE)


TIME_PAT = re.compile(r"""
                (?P<hour>\d{1,2})
                :
                (?P<minute>\d{1,2})
                (?:
                    :
                    (?P<second>\d{1,2})
                    (?:
                        \.
                        (?P<fract_second>\d+)?
                    )?
                )?
                (?:
                    Z
                    |
                    (?:
                        (?P<tz_sign>[+-])
                        (?P<tz_hour>\d{1,2})
                        :
                        (?P<tz_min>\d{2,2})
                    )
                )
$""", re.VERBOSE)


def parse_isodate(st):
    """
    st - string or Unicode with ISO 8601 date
    """
    m = DATETIME_PAT.match(st)
    if not m:
        return None
    gd = m.groupdict('0')
    #FIXME: does not handle time zones
    dt = datetime(int(gd['year']),
                  int(gd['month']) or 1,
                  int(gd['day']) or 1,
                  int(gd['hour']),
                  int(gd['minute']),
                  int(gd['second']),
                  int(float(u'.' + gd['fract_second'])*1000000),
                  )
    return dt


def parse_isotime(st):
    """
    st - string or Unicode with ISO 8601 time
    """
    m = TIME_PAT.match(st)
    if not m:
        return None
    gd = m.groupdict('0')
    #FIXME: does not handle time zones
    t = time(int(gd['hour']),
             int(gd['minute']),
             int(gd['second']),
             int(float(u'.' + gd['fract_second'])*1000000),
             )
    return t
