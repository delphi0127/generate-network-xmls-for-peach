import time, calendar
from Ft.Lib import Time

def utcTupleToLocal8601(utctuple):
    loc_tuple = time.localtime(calendar.timegm(utctuple))
    if loc_tuple[8] == 1:
        offset_secs = time.altzone
    else:
        offset_secs = time.timezone
    if offset_secs == 0:
        offset_str = 'Z'
    else:
        offset_str = '%+03d:%02d' % (-offset_secs / 3600, abs(offset_secs) % 60)
    return time.strftime('%Y-%m-%dT%H:%M:%S' + offset_str, loc_tuple)


def test_instance(tester):

    tester.startGroup("Test DateTime Instance")

    tester.startGroup("Test Seconds")

    tester.startTest('10s + 5ms')
    d = Time.DT(0,0,0,0,0,10,5,0,"",0,0)
    tester.compare(10,d.second())
    tester.compare(5,d.milliSecond())
    tester.testDone()

    tester.startTest('10s + 5001ms')
    d = Time.DT(0,0,0,0,0,10,5001,0,"",0,0)
    tester.compare(15,d.second())
    tester.compare(1,d.milliSecond())
    tester.testDone()

    tester.groupDone()

    tester.startGroup("Test Minutes")

    tester.startTest("1m 0s")
    d = Time.DT(0,0,0,0,1,0,0,0,"",0,0)
    tester.compare(1,d.minute())
    tester.compare(1,d.minute(local=1))
    tester.testDone()

    tester.startTest("1m 0s, offset 20m")
    d = Time.DT(0,0,0,0,1,0,0,0,"",0,20)
    tester.compare(1,d.minute())
    tester.compare(21,d.minute(local=1))
    tester.testDone()

    tester.startTest("1m 65s, offset 20m")
    d = Time.DT(0,0,0,0,1,65,0,0,"",0,20)
    tester.compare(2,d.minute())
    tester.compare(22,d.minute(local=1))
    tester.compare(5,d.second())
    tester.testDone()

    tester.groupDone()

    tester.startGroup("Test Hour")

    tester.startTest("1h 0m")
    d = Time.DT(0,0,0,1,0,0,0,0,"",0,0)
    tester.compare(1,d.hour())
    tester.compare(1,d.hour(local=1))
    tester.testDone()

    tester.startTest("1h 0m, offset -2h")
    d = Time.DT(0,0,0,1,0,0,0,0,"",-2,0)
    tester.compare(1,d.hour())
    tester.compare(23,d.hour(local=1))
    tester.testDone()

    tester.startTest("10h 125m, offset -15h 65m")
    d = Time.DT(0,0,0,10,125,0,0,0,"",-15,65)
    tester.compare(12,d.hour())
    tester.compare(22,d.hour(local=1))
    tester.compare(5,d.minute())
    tester.compare(10,d.minute(local=1))
    tester.testDone()

    tester.groupDone()

    tester.startGroup("Time Zones")

    tester.startTest("0h 0m, offset -6h, summer")
    d = Time.DT(0,0,0,0,0,0,0,1,"",-6,0)
    tester.compare("MDT",d.tzName())
    tester.compare(-6,d.tzHourOffset())
    tester.compare(0,d.tzMinuteOffset())
    tester.compare(18,d.hour(local=1))
    tester.compare(0,d.hour())
    tester.testDone()

    tester.startTest("0h 0m, offset -6h, winter")
    d = Time.DT(0,0,0,0,0,0,0,0,"",-6,0)
    tester.compare("CST",d.tzName())
    tester.compare(-6,d.tzHourOffset())
    tester.compare(0,d.tzMinuteOffset())
    tester.compare(18,d.hour(local=1))
    tester.compare(0,d.hour())
    tester.testDone()

    tester.startTest("0h 0m, offset -7h, summer")
    d = Time.DT(0,0,0,0,0,0,0,1,"",-7,0)
    tester.compare("PDT",d.tzName())
    tester.compare(-7,d.tzHourOffset())
    tester.compare(0,d.tzMinuteOffset())
    tester.compare(17,d.hour(local=1))
    tester.compare(0,d.hour())
    tester.testDone()

    tester.startTest("0h 0m, offset -7h, winter")
    d = Time.DT(0,0,0,0,0,0,0,0,"",-7,0)
    tester.compare("MST",d.tzName())
    tester.compare(-7,d.tzHourOffset())
    tester.compare(0,d.tzMinuteOffset())
    tester.compare(17,d.hour(local=1))
    tester.compare(0,d.hour())
    tester.testDone()

    tester.groupDone()

    tester.startGroup("Test Date")

    tester.startTest("Y2001, M1, D1")
    d = Time.DT(2001,1,1,0,0,0,0,0,"",0,0)
    tester.compare(2001,d.year())
    tester.compare(1,d.month())
    tester.compare(1,d.day())
    tester.compare(1,d.day(local=1))
    tester.testDone()

    tester.startTest("Y2001, M2, D1, 1h, offset -2h")
    d = Time.DT(2001,2,1,1,0,0,0,0,"",-2,0)
    tester.compare(2001,d.year())
    tester.compare(2,d.month())
    tester.compare(1,d.month(local=1))
    tester.compare(1,d.day())
    tester.compare(31,d.day(local=1))
    tester.compare(23,d.hour(local=1))
    tester.testDone()

    tester.startTest("Y2001, M2, D1, 33h")
    d = Time.DT(2001,2,1,33,0,0,0,0,"",0,0)
    tester.compare(2001,d.year())
    tester.compare(2,d.month())
    tester.compare(2,d.day())
    tester.compare(9,d.hour())
    tester.testDone()

    tester.startTest("Y2000, M2, D30")
    d = Time.DT(2000,2,30,00,0,0,0,0,"",0,0)
    tester.compare(2000,d.year())
    tester.compare(3,d.month())
    tester.compare(1,d.day())
    tester.testDone()

    tester.startTest("Y2001, M2, D30")
    d = Time.DT(2001,2,30,00,0,0,0,0,"",0,0)
    tester.compare(2001,d.year())
    tester.compare(3,d.month())
    tester.compare(2,d.day())
    tester.testDone()

    tester.groupDone()

    tester.groupDone()


def test_iso(tester):
    tester.startGroup("ISO Time Parser")

    for i,h,m,s,ms in [("T232050",23,20,50,0),
                       ("23:20:50",23,20,50,0),
                       ("T23:20:50",23,20,50,0),
                       ("T2320",23,20,0,0),
                       ("T23:20",23,20,0,0),
                       ("23:20",23,20,0,0),
                       ("T23",23,0,0,0),
                       ("T232050,5",23,20,50,500),
                       ("T232050.5",23,20,50,500),
                       ("T23:20:50,5",23,20,50,500),
                       ("T23:20:50.5",23,20,50,500),
                       ("23:20:50,5",23,20,50,500),
                       ("23:20:50.5",23,20,50,500),
                       ("T2320,9",23,20,54,0),
                       ("T2320.9",23,20,54,0),
                       ("T23:20,9",23,20,54,0),
                       ("T23:20.9",23,20,54,0),
                       ("23:20,9",23,20,54,0),
                       ("23:20.9",23,20,54,0),
                       ("T23,3",23,18,0,0),
                       ("T23.3",23,18,0,0),
                       ("T-2050",None,20,50,0),
                       ("T-20:50",None,20,50,0),
                       ("T-20",None,20,0,0),
                       ("T--50",None,None,50,0),
                       ("T11,3",11,18,0,0),
                       ("T11.3",11,18,0,0),
                       ("T-20,9",None,20,54,0),
                       ("T-20.9",None,20,54,0),
                       ("T-2050,5",None,20,50,500),
                       ("T-2050.5",None,20,50,500),
                       ("T-20:50,5",None,20,50,500),
                       ("T-20:50.5",None,20,50,500),
                       ("T--50,5",None,None,50,500),
                       ("T--50.5",None,None,50,500),
                       ("T000000",0,0,0,0),
                       ("T00:00:00",0,0,0,0),
                       ("T240000",0,0,0,0),
                       ("T24:00:00",0,0,0,0),

                      ]:
        tester.startTest(i)
        d = Time.FromISO8601(i)
        if h is None:
            h = time.localtime()[3]
        if m is None:
            m = time.localtime()[4]
        tester.compare(h,d.hour())
        tester.compare(m,d.minute())
        tester.compare(s,d.second())
        tester.compare(ms,d.milliSecond())
        tester.testDone()


    tester.groupDone()


    tester.startGroup("ISO Time and TZ Parser")

    for i,h,m,s,tzh,tzm,lh,lm in [("232030Z",23,20,30,0,0,23,20),
                                  ("T232030Z",23,20,30,0,0,23,20),
                                  ("23:20:30Z",23,20,30,0,0,23,20),
                                  ("T23:20:30Z",23,20,30,0,0,23,20),
                                  ("2320Z",23,20,0,0,0,23,20),
                                  ("23:20Z",23,20,0,0,0,23,20),
                                  ("T2320Z",23,20,0,0,0,23,20),
                                  ("T23:20Z",23,20,0,0,0,23,20),
                                  ("23Z",23,0,0,0,0,23,0),
                                  ("T23Z",23,0,0,0,0,23,0),
                                  ("T152746+0130",13,57,46,1,30,15,27),
                                  ("T152746+01",14,27,46,1,00,15,27),
                                  ("T15:27:46+01:30",13,57,46,1,30,15,27),
                                  ("T15:27:46+01",14,27,46,1,00,15,27),
                                  ("152746+0130",13,57,46,1,30,15,27),
                                  ("152746+01",14,27,46,1,00,15,27),
                                  ("15:27:46+01:30",13,57,46,1,30,15,27),
                                  ("15:27:46+01",14,27,46,1,00,15,27),
                                  ("T152746-0530",20,57,46,-5,-30,15,27),
                                  ("152746-0530",20,57,46,-5,-30,15,27),
                                  ("T15:27:46-05:30",20,57,46,-5,-30,15,27),
                                  ("15:27:46-05:30",20,57,46,-5,-30,15,27),
                                  ("T152746-05",20,27,46,-5,0,15,27),
                                  ("152746-05",20,27,46,-5,0,15,27),
                                  ("T15:27:46-05",20,27,46,-5,0,15,27),
                                  ("15:27:46-05",20,27,46,-5,0,15,27),

                                  ]:
        tester.startTest(i)
        d = Time.FromISO8601(i)
        tester.compare(h,d.hour())
        tester.compare(m,d.minute())
        tester.compare(s,d.second())
        #tester.compare(tzh,d.tzHourOffset())
        #tester.compare(tzm,d.tzMinuteOffset())
        #tester.compare(lh,d.hour(local=1))
        #tester.compare(lm,d.minute(local=1))
        tester.testDone()
    tester.groupDone()


    tester.startGroup("ISO Date Parser")

    for i,y,m,d in [("19850412",1985,4,12),
                    ("1985-04-12",1985,4,12),
                    ("1985-04",1985,4,1),
                    ("1985",1985,1,1),
                    ("1900",1900,1,1),
                    ("850412",2085,04,12),
                    ("85-04-12",2085,04,12),
                    ("-8504",2085,04,1),
                    ("-85-04",2085,04,1),
                    ("-85",2085,01,1),
                    ("--0412",None,04,12),
                    ("--04-12",None,04,12),
                    ("--04",None,04,1),
                    ("---12",None,None,12),
                    ]:

        tester.startTest(i)
        dt = Time.FromISO8601(i)
        now = time.localtime()
        if y is None:
            y = now[0]
        if m is None:
            m = now[1]

        tester.compare(y,dt.year())
        tester.compare(m,dt.month())
        tester.compare(d,dt.day())
        tester.testDone()

    tester.groupDone()

    tester.startGroup("ISO Ordinal Date Parser")

    for i,y,m,d in [("1985102",1985,4,12),
                    ("1985-102",1985,4,12),
                    ("85102",2085,04,12),
                    ("85-102",2085,04,12),
                    (calendar.isleap(time.localtime()[0])
                      and "-103" or "-102",None,04,12),
                    ]:

        tester.startTest(i)
        dt = Time.FromISO8601(i)
        now = time.localtime()
        if y is None:
            y = now[0]
        if m is None:
            m = now[1]

        tester.compare(y,dt.year())
        tester.compare(m,dt.month())
        tester.compare(d,dt.day())
        tester.testDone()

    tester.groupDone()

    tester.startGroup("ISO Week Date Parser")

    for i,y,m,d in [("1985W155",1985,4,12),
                    ("1985-W15-5",1985,4,12),
                    ("1985W15",1985,4,8),
                    ("1985-W15",1985,4,8),
                    ("85W155",2085,04,13),
                    ("85-W15-5",2085,04,13),
                    ("85W15",2085,04,9),
                    ("85-W15",2085,04,9),
                    ("-5W155",2005,04,15),
                    ("-5-W15-5",2005,04,15),
# date of week 15, day 5 varies from year to year
#                    ("-W155",None,04,13),
#                    ("-W15-5",None,04,13),
#                    ("-W15",None,04,9),
#                    ("-W15",None,04,9),
                    ]:

        tester.startTest(i)
        dt = Time.FromISO8601(i)
        now = time.localtime()
        if y is None:
            y = now[0]
        if m is None:
            m = now[1]

        tester.compare(y,dt.year())
        tester.compare(m,dt.month())
        tester.compare(d,dt.day())
        tester.testDone()

    tester.groupDone()


    tester.startGroup("ISO Combined Date Parser")

    for i,y,m,d,h,min,s,ms,tzh,tzm,ld,lh,lm in [("19850412T101530",1985,4,12,10,15,30,0,0,0,12,10,15),
                                                ("19850412T1015",1985,4,12,10,15,0,0,0,0,12,10,15),
                                                ("19850412T10",1985,4,12,10,0,0,0,0,0,12,10,0),
                                                ("1985-04-12T10:15:30",1985,4,12,10,15,30,0,0,0,12,10,15),
                                                ("1985-04-12T10:15",1985,4,12,10,15,0,0,0,0,12,10,15),
                                                ("1985-04-12T10",1985,4,12,10,0,0,0,0,0,12,10,0),
                                                ("1985102T23:50:30",1985,4,12,23,50,30,0,0,0,12,23,50),
                                                ("1985102T23:50",1985,4,12,23,50,0,0,0,0,12,23,50),
                                                ("1985102T23",1985,4,12,23,0,0,0,0,0,12,23,0),
                                                ("1985-102T23:50:30",1985,4,12,23,50,30,0,0,0,12,23,50),
                                                ("1985-102T23:50",1985,4,12,23,50,0,0,0,0,12,23,50),
                                                ("1985-102T23",1985,4,12,23,0,0,0,0,0,12,23,0),
                                                ("1985W155T235030",1985,4,12,23,50,30,0,0,0,12,23,50),
                                                ("1985W155T2350",1985,4,12,23,50,0,0,0,0,12,23,50),
                                                ("1985W155T23",1985,4,12,23,0,0,0,0,0,12,23,0),
                                                ("1985-W15-5T23:50:30",1985,4,12,23,50,30,0,0,0,12,23,50),
                                                ("1985-W15-5T23:50",1985,4,12,23,50,0,0,0,0,12,23,50),
                                                ("1985-W15-5T23",1985,4,12,23,0,0,0,0,0,12,23,0),
                                                #Some with TZ
                                                ("1985-04-12T10:15:30,5+03:30",1985,4,12,6,45,30,500,3,30,12,10,15),

                                                ]:

        tester.startTest(i)
        dt = Time.FromISO8601(i)
        tester.compare(y,dt.year())
        tester.compare(m,dt.month())
        tester.compare(d,dt.day())
        tester.compare(h,dt.hour())
        tester.compare(min,dt.minute())
        tester.compare(s,dt.second())
        tester.compare(ms,dt.milliSecond())
        tester.compare(tzh,dt.tzHourOffset())
        tester.compare(tzm,dt.tzMinuteOffset())
        tester.compare(ld,dt.day(local=1))
        tester.compare(lh,dt.hour(local=1))
        tester.compare(lm,dt.minute(local=1))
        tester.testDone()

    tester.groupDone()



def test_rfc822(tester):
    tester.startGroup("RFC 822 Parsing")


    for i,y,m,d,h,min,s,ms,tzh,tzm,ld,lh,lm in [("Thu, Jan 4 2001 09:15:39 MDT",
                                                 2001,
                                                 1,
                                                 4,
                                                 15,
                                                 15,
                                                 39,
                                                 0,
                                                 -6,
                                                 0,
                                                 4,
                                                 9,
                                                 15),
                                                ("Tue, May 18 1999 13:45:50 GMT",
                                                 1999,
                                                 5,
                                                 18,
                                                 13,
                                                 45,
                                                 50,
                                                 0,
                                                 0,
                                                 0,
                                                 18,
                                                 13,
                                                 45),
                                                ]:

        tester.startTest(i)
        dt = Time.FromRFC822(i)
        tester.compare(y,dt.year())
        tester.compare(m,dt.month())
        tester.compare(d,dt.day())
        tester.compare(h,dt.hour())
        tester.compare(min,dt.minute())
        tester.compare(s,dt.second())
        tester.compare(ms,dt.milliSecond())
        tester.compare(tzh,dt.tzHourOffset())
        tester.compare(tzm,dt.tzMinuteOffset())
        tester.compare(ld,dt.day(local=1))
        tester.compare(lh,dt.hour(local=1))
        tester.compare(lm,dt.minute(local=1))
        tester.testDone()


    tester.groupDone()


def test_serialize(tester):

    tester.startGroup("ISO Time Serializer")
    for i,o,ol in [("T10:30:50","T10:30:50Z","T10:30:50Z"),
                   ("T10:30:50+0130","T09:00:50Z","T10:30:50+01:30"),
                   ("T10:30:50,5+0130","T09:00:50,5Z","T10:30:50,5+01:30"),
                   ]:
        tester.startTest(i)
        dt = Time.FromISO8601(i)
        e = dt.asISO8601Time()
        tester.compare(o,e)
        e = dt.asISO8601Time(local=1)
        tester.compare(ol,e)
        tester.testDone()
    tester.groupDone()

    tester.startGroup("ISO Date Serializer")
    for i,o in [("20011217","2001-12-17"),
                ("20010133","2001-02-02"),
                ]:
        tester.startTest(i)
        dt = Time.FromISO8601(i)
        e = dt.asISO8601Date()
        tester.compare(o,e)
        e = dt.asISO8601Date(local=1)
        tester.compare(o,e)
        tester.testDone()
    tester.groupDone()


    tester.startGroup("ISO Date Time Serializer")
    for i,o,ol in [("20011217T10:30:50","2001-12-17T10:30:50Z","2001-12-17T10:30:50Z"),
                   ("20011217T10:30:50+0130","2001-12-17T09:00:50Z","2001-12-17T10:30:50+01:30"),
                   ]:
        tester.startTest(i)
        dt = Time.FromISO8601(i)
        e = dt.asISO8601DateTime()
        tester.compare(o,e)
        e = dt.asISO8601DateTime(local=1)
        tester.compare(ol,e)
        tester.testDone()
    tester.groupDone()

    tester.startGroup("RFC822 Date Time Serializer")
    for i,o,ol in [("Thu, 04 Jan 2001 09:15:39 MDT","Thu, 04 Jan 2001 15:15:39 GMT","Thu, 04 Jan 2001 09:15:39 MDT"),
                   ("Fri, 05 Jan 2001 09:15:39 GMT","Fri, 05 Jan 2001 09:15:39 GMT","Fri, 05 Jan 2001 09:15:39 GMT"),
                   ]:
        tester.startTest(i)
        dt = Time.FromRFC822(i)
        e = dt.asRFC822DateTime()
        tester.compare(o,e)
        e = dt.asRFC822DateTime(local=1)
        tester.compare(ol,e)
        tester.testDone()
    tester.groupDone()


def test_python_tuple(tester):

    tester.startGroup("Python time tuple")
    for i,o in [((2001,12,17,13,15,30,0,0,-1),"2001-12-17T13:15:30Z"),
                ((2000,1,33,13,15,30,0,0,-1),"2000-02-02T13:15:30Z"),
               ]:
        tester.startTest(repr(i))

        ol = utcTupleToLocal8601(i)
        dt = Time.FromPythonTimeTuple(i)
        e = dt.asISO8601DateTime()
        tester.compare(o,e)
        e = dt.asISO8601DateTime(local=1)
        tester.compare(ol,e)
        e = dt.asPythonTimeTuple()

        tester.testDone()
    tester.groupDone()

    tester.startTest("Python time")
    t = time.time()
    dt = Time.FromPythonTime(t)
    test = time.gmtime(t)

    tester.compare(dt.year(),test[0])
    tester.compare(dt.month(),test[1])
    tester.compare(dt.day(),test[2])
    tester.compare(dt.hour(),test[3])
    tester.compare(dt.minute(),test[4])
    tester.compare(dt.second(),test[5])
    tester.testDone()
    return


def Test(tester):
    test_instance(tester)
    test_iso(tester)
    test_rfc822(tester)
    test_serialize(tester)
    test_python_tuple(tester)
