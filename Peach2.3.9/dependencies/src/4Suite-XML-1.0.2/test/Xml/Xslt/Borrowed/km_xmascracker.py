#Michael Kay's Christmas Cracker.
#See 

from Xml.Xslt import test_harness

sheet_1 = """<a xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xsl:version="1.0">
<xsl:value-of select="*******************"/>
</a>"""

sheet_2 = """<a xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xsl:version="1.0">
<xsl:value-of select="* + * + * + * + * + * + * + * + * + *"/>
</a>"""

source_1 = """<q>2</q>"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<a>1024</a>"""

expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<a>20</a>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='test 1')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='test 2')
    return
