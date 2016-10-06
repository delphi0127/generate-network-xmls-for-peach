from Xml.Xslt import test_harness

SHEET_1 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  xmlns:ns="urn:bogus:dummy:"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:template match="/">
    <doc>
    <ft:uri-to-element uri='urn:bogus:dummy:spam'
                       default-name='x:Unknown'
                       default-namespace='urn:bogus:dummy:'>
    </ft:uri-to-element>
    <ft:uri-to-element uri='urn:bogus:nonce:spam'
                       default-name='x:Unknown'
                       default-namespace='urn:bogus:dummy:'>
    </ft:uri-to-element>
    </doc>
  </xsl:template>

</xsl:stylesheet>
"""

SOURCE_1 = """<dummy/>"""

EXPECTED_1 = """<?xml version="1.0" encoding="UTF-8"?>\n<doc xmlns:ns="urn:bogus:dummy:"><ns:spam/><x:Unknown xmlns:x="urn:bogus:dummy:"/></doc>
"""


def Test(tester):
    source = test_harness.FileInfo(string=SOURCE_1)
    sty = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_1,
                          title="ft:uri-to-element")

    return

