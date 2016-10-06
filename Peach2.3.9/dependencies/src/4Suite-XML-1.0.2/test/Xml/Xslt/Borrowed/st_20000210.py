#From Steve Tinney's word-count templates, 10 Feb 2000

from Xml.Xslt import test_harness

sheet_1 = """<?xml version='1.0'?>
<!-- wctest.xsl -->
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="text"/>
<xsl:include href="Xml/Xslt/Borrowed/wc-nt.xslt"/>

<xsl:variable name="nwords">
  <xsl:call-template name="word-count">
    <xsl:with-param name="in" select="/"/>
  </xsl:call-template>
</xsl:variable>

<xsl:template match="/">
  Word count = <xsl:value-of select="$nwords"/>
</xsl:template>

</xsl:stylesheet>"""


sheet_2 = """<?xml version='1.0'?>
<!-- wctest.xsl -->
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="text"/>
<xsl:include href="Xml/Xslt/Borrowed/wc.xslt"/>

<xsl:variable name="nwords">
  <xsl:call-template name="word-count">
    <xsl:with-param name="in" select="/"/>
  </xsl:call-template>
</xsl:variable>

<xsl:template match="/">
  Word count = <xsl:value-of select="$nwords"/>
</xsl:template>

</xsl:stylesheet>"""


source_1="""<test><a> a a </a><b>b<one>1</one><two>2</two></b></test>"""

expected_1="""
  Word count = 5"""
expected_2="""
  Word count = 5"""

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
