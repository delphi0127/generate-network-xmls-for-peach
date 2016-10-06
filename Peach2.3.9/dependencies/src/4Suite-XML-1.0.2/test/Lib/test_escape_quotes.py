def Test(tester):

    from Ft.Lib.DbUtil import EscapeQuotes

    for i,out in [('hello','hello'),
                  ("he'llo",r"he\'llo"),
                  ("he'll'o",r"he\'ll\'o"),
                  ("'hello'",r"\'hello\'"),
                  ("'","\\'"),
                  (r"hhh\\hhhh",r"hhh\\\\hhhh"),
                  (r"\\",r"\\\\"),
                  (r"'\\''\\'\\'",r"\'\\\\\'\'\\\\\'\\\\\'"),
                  (None,r""),
                   ]:
        tester.startTest(repr(i))
        e = EscapeQuotes(i)
        tester.compare(out,e)
        tester.testDone()

