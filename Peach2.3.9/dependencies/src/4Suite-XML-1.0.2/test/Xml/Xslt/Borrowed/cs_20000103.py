#"Carl Soane" <csoane@ix.netcom.com> offres an example of format-number

from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/TR/REC-html40">

<xsl:output method="html"/>


<xsl:template match="/">
<HTML>
<BODY>
  <xsl:apply-templates select="Numbers"/>
</BODY>
</HTML>
</xsl:template>

<xsl:template match="Numbers">
 <b><xsl:value-of select="format-number(Num, '#,###,###.###')"/></b>
 <br/>
</xsl:template>

</xsl:stylesheet>"""

source_1 = """<?xml version="1.0"?>
<Numbers>
    <Num>
     123456.7890
    </Num>
</Numbers>"""

# the empty 'br' is in XML syntax because it's not in the null namespace
expected_1 = """<HTML xmlns='http://www.w3.org/TR/REC-html40'>
  <BODY>
    <b>123,456.789</b>
    <br/>
  </BODY>
</HTML>"""
#"

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
