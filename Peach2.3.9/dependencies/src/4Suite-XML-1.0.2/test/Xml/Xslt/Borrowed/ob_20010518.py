#Oliver Becker <obecker@informatik.hu-berlin.de> wonders about namespace axis conformance

from Xml.Xslt import test_harness

sheet_1 = """\
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="el">
   <xsl:copy>
      <xsl:copy-of select="@*" />
      <xsl:attribute name="prefix:att2" 
                     namespace="uri2">bar</xsl:attribute>
   </xsl:copy>
</xsl:template>

</xsl:stylesheet>"""


source_1 = """\
<el xmlns:prefix="uri1" prefix:att="foo" />"""

expected_1 = """\
<?xml version='1.0' encoding='UTF-8'?>
<el xmlns:org.4suite.4xslt.ns0='uri2' xmlns:prefix='uri1' org.4suite.4xslt.ns0:att2='bar' prefix:att='foo'/>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
