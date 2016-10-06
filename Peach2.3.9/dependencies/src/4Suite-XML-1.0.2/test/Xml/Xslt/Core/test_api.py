from Xml.Xslt import test_harness
from Ft.Lib import Uri
import os


from Ft.Xml.InputSource import DefaultFactory
from Ft.Xml.Xslt.Processor import Processor

stylesheet_string = '''<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
<xsl:template match="/">
  <xsl:variable name="foo"
select="text()"/>
</xsl:template>
</xsl:stylesheet>
'''
source_string = '<doc/>'

EXPECTED_1 = """<?xml version="1.0" encoding="UTF-8"?>\n"""


def Test(tester):
    # We don't use test_harness.XsltTest and friends because they hide away
    # the API details we're testing in this module.
    # See http://bugs.4suite.org/641693

    tester.startGroup("Test multiple stylesheet invokation")
    xp = Processor()
    xp.appendStylesheet(DefaultFactory.fromString(stylesheet_string,
                                                  uri="data:ss"))
    result1 = xp.run(DefaultFactory.fromString(source_string,
                                     uri="data:src1"))
    result2 = xp.run(DefaultFactory.fromString(source_string,
                                     uri="data:src2"))
    tester.compare(result1, EXPECTED_1)
    tester.compare(result2, EXPECTED_1)
    tester.groupDone()
    return
