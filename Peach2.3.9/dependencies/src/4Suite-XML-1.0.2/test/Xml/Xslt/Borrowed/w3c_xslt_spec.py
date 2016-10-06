# W3C XSLT source and stylesheet

from Xml.Xslt import test_harness

import os
expected_file = os.path.join(os.path.dirname(__file__),
                             'REC-xslt-19991116.html')

def Test(tester):
    source = test_harness.FileInfo(uri='Xml/Xslt/Borrowed/REC-xslt-19991116.xml')
    sheet = test_harness.FileInfo(uri='Xml/Xslt/Borrowed/w3c-xmlspec.xslt')
    
    f = open(expected_file)
    expected= f.read()
    f.close()
    test_harness.XsltTest(tester, source, [sheet], expected)
    return

