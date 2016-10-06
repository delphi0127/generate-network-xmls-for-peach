from Ft.Xml.Lib.routines import FormatNumber

# decimal separator (.)
# grouping separator (,)
# infinity (Infinity)
# minus (-)
# not-a-number (NaN)
# percent (%)
# per-mille unichr(0x2030)
# zero digit (0)
# decimal digit (#)
# pattern separator (;)

decimal_format = ('.', ',', "Inf", '-', "Not-A-Number", '%', '?', '0', '#', ';')

g_tests = [(3.45,'#.##','3.45'),
           (-3.45, '#.##', '-3.45'),
           (3.45,'###.#####','3.45'),
           (3.45,'###.0000','3.4500'),
           (3.45,'###.##;#.##','3.45'),
           (-3.45,'###.##;(#.##)','(3.45)'),
           (3.45,'###.##;(#.##)','3.45'),
           (1234567.89,'######,###.##','1,234,567.89'),
           (1234567.901,'######,###.##','1,234,567.9'),
           (0.000008,'#0.00','0.00'),
           (.00256323814392,'0.00000','0.00256'),
           (0, '0.0', '0.0'),
           ]

def Test(tester):

    tester.startGroup("Format number")
    for num,format,exp in g_tests:
        tester.startTest("%s with %s" %(str(num),format))
        act = FormatNumber(num,format,decimal_format)
        tester.compare(exp,act)
        tester.testDone()
    tester.groupDone()
