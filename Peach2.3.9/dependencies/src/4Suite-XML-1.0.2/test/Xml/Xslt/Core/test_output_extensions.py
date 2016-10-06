from Xml.Xslt import test_harness
# BOM_UTF8 not available in Py2.2 codecs
#from codecs import BOM_UTF8

BOM_UTF8 = '\xef\xbb\xbf'

SHEET_1 = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
>

<xml:output ft:utf-bom="yes"/>

<xsl:template match="@*|node()">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>
</xsl:stylesheet>
"""


EXPECTED_1 = BOM_UTF8 + """<?xml version='1.0' encoding='UTF-8'?><foo/>"""


SOURCE_1 = "<foo/>"


def Test(tester):
    source = test_harness.FileInfo(string=SOURCE_1)
    sheet = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_1,
                          title='f:utf-bom')
    return

