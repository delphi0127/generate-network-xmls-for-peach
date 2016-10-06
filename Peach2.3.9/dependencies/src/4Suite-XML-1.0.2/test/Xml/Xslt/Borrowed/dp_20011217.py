#Dave's Pawson's identity transform problem

from Xml.Xslt import test_harness

source_1="""<elem xmlns="http:default.com" xmlns:foo="http://foo.com">
  <foo:child/>
</elem>"""


sheet_1="""<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
>
<!-- identity transforms. -->
<xsl:template match="*">
  <xsl:element name="{name(.)}" namespace="http://www.w3.org/1999/xhtml">
    <xsl:apply-templates select="@*" />
    <xsl:apply-templates />
    </xsl:element>
</xsl:template>


<xsl:template match="@*">
  <xsl:copy-of select="." />
</xsl:template>
</xsl:stylesheet>"""

sheet_2="""<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:foo="http://foo.com"
  version="1.0"
>
<!-- identity transforms. -->
<xsl:template match="*">
  <xsl:element name="{name(.)}" xmlns="http://www.w3.org/1999/xhtml">
    <xsl:apply-templates select="@*" />
    <xsl:apply-templates />
    </xsl:element>
</xsl:template>
<xsl:template match="@*">
  <xsl:copy-of select="." />
</xsl:template>
</xsl:stylesheet>"""


source_2="""<html>
    <head>
        <title>The TCS Review 2000/2001 - Working Together</title>
        <meta name="NCC:Format" content="Daisy 2.0"/>
        <meta name="NCC:Publisher" content="RNIB"/>
        <meta name="NCC:Identifier" content="UK:RNIB:6DCA50D0-E4E2-4472-A2DA-"/>
        <meta name="NCC:Charset" content="ISO-8859-1"/>
        <meta name="dc:title" content="The TCS Review 2000/2001 - Working Together"/>
        <meta name="dc:format" content="Daisy 2.0"/>
        <meta name="dc:creator" content="David Gordon - RNIB"/>
        <meta name="dc:subject" content="Factual"/>
        <meta name="ncc:narrator" content="mixed voices"/>
        <meta name="ncc:generator" content="LpStudioGen 1.5"/>
        <meta name="ncc:tocitems" content="70"/>
        <meta name="ncc:page-front" content="0"/>
        <meta name="ncc:page-normal" content="0"/>
        <meta name="ncc:page-special" content="0"/>
        <meta name="ncc:totaltime" content="01:23:19"/>
    </head>
</html>"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<elem xmlns='http://www.w3.org/1999/xhtml'>
  <foo:child xmlns:foo='http://www.w3.org/1999/xhtml'/>
</elem>"""

expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<elem xmlns='http://www.w3.org/1999/xhtml'>
  <foo:child xmlns:foo='http://foo.com'/>
</elem>"""

expected_3="""<?xml version='1.0' encoding='UTF-8'?>
<html xmlns='http://www.w3.org/1999/xhtml'>
    <head>
        <title>The TCS Review 2000/2001 - Working Together</title>
        <meta name='NCC:Format' content='Daisy 2.0'/>
        <meta name='NCC:Publisher' content='RNIB'/>
        <meta name='NCC:Identifier' content='UK:RNIB:6DCA50D0-E4E2-4472-A2DA-'/>
        <meta name='NCC:Charset' content='ISO-8859-1'/>
        <meta name='dc:title' content='The TCS Review 2000/2001 - Working Together'/>
        <meta name='dc:format' content='Daisy 2.0'/>
        <meta name='dc:creator' content='David Gordon - RNIB'/>
        <meta name='dc:subject' content='Factual'/>
        <meta name='ncc:narrator' content='mixed voices'/>
        <meta name='ncc:generator' content='LpStudioGen 1.5'/>
        <meta name='ncc:tocitems' content='70'/>
        <meta name='ncc:page-front' content='0'/>
        <meta name='ncc:page-normal' content='0'/>
        <meta name='ncc:page-special' content='0'/>
        <meta name='ncc:totaltime' content='01:23:19'/>
    </head>
</html>"""

def Test(tester):
    tester.startGroup("element with namespace attr")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='test 1')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='test 2')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='test 3')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='test 4')

    tester.groupDone()
    return
