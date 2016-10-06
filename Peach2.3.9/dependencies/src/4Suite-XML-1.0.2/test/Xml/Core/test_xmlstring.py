from Ft.Xml.Lib import XmlString

_TESTS = [
    (XmlString.SplitQName, [('foo', (None, 'foo')),
                            ('foo:bar', ('foo', 'bar')),
                            ('foo:bar:baz', ('foo', 'bar:baz')),
                            ]),

    (XmlString.XmlStrStrip, [('\r\nfoo\t ', 'foo')]),
    (XmlString.XmlStrRStrip, [('\r\nfoo\t ', '\r\nfoo')]),
    (XmlString.XmlStrLStrip, [('\r\nfoo\t ', 'foo\t ')]),
     ]           

#Exception integrity (i.e. no core dumps)
#XmlStrStrip(None) used to dump core
_EXCEPTION_TESTS = [
    (XmlString.XmlStrStrip, [((None,), TypeError, 'NoneType')]),
    (XmlString.XmlStrRStrip, [((None,), TypeError, 'NoneType')]),
    (XmlString.XmlStrLStrip, [((None,), TypeError, 'NoneType')]),
]


def Test(tester):

    tester.startGroup("XML String Functions")

    for func, tests in _TESTS:
        for source, expected in tests:
            tester.startTest('%s(%r)' % (func.__name__, source))
            tester.compare(expected, func(source))
            tester.testDone()

    for func, tests in _EXCEPTION_TESTS:
        for args, exc, type_str in tests:
            tester.startTest('Exception case: %s(%r) -> %s' % (func.__name__, args[0], exc))
            tester.testException(func, args, exc, {'msg': "argument must be unicode or string, %.80s found."%type_str})
            tester.testDone()

    tester.groupDone()
    return
