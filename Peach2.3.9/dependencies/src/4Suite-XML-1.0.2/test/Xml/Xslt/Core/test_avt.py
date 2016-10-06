from Ft.Xml.Xslt import AttributeValueTemplate, XsltException, Error

def test_valid(tester):
    tests = [
        ('', ''),
        ('Senatus{{populisque}}romae', 'Senatus{populisque}romae'),
        ('Senatus{{{"populisque}}"}romae', 'Senatus{populisque}}romae'),
        ('{"{literal}"}', '{literal}'),
        ('{"{literal"}', '{literal'),
        ('{"literal}"}', 'literal}'),
        ('{"{{literal}}"}', '{{literal}}'),
        ('{"{{literal"}', '{{literal'),
        ('{"literal}}"}', 'literal}}'),
        ('{{{"literal"}', '{literal'),
        ('{{-{"literal"}', '{-literal'),
        ('{"literal"}}}', 'literal}'),
        ('{"literal"}-}}', 'literal-}'),
        ('{"100"}% {100}% {90+10}% 100% {"%"}1{0}0 %100', '100% 100% 100% 100% %100 %100'),
        ]

    tester.startGroup("Valid AVTs")
    for source, expected in tests:
        tester.startTest(source)
        try:
            avt = AttributeValueTemplate.AttributeValueTemplate(source)
        except Exception, exc:
            tester.exception('Unexpected exception: %s' % exc.__class__)
        else:
            tester.compare(expected, avt.evaluate(None))
        tester.testDone()
    tester.groupDone()
    return

def test_invalid(tester):
    tests = [
        '{}',               # no expression is error
        '{-{{"literal"}',   # '-{"literal"' is invalid Expr
        '{"literal"}}-}',   # '{"literal"} is expr; '}-}' is error
        '{{node()}',        # '{{node()' is literal, trailing '}' is error
        '{node()}}',        # '{node()}' is expr; trailing '}' is error
        '(id(@ref)/title}', # missing leading '{'
        '{(id(@ref)/title', # missing trailing '{'
        ]

    tester.startGroup("Invalid AVTs")
    for source in tests:
        tester.startTest(source)
        tester.testException(AttributeValueTemplate.AttributeValueTemplate,
                             (source,), XsltException,
                             {'errorCode' : Error.AVT_SYNTAX})
        tester.testDone()
    tester.groupDone()
    return

def Test(tester):
    test_valid(tester)
    test_invalid(tester)
    return
