#From the XSLT spec: http://docs.local/REC-xslt-19991116.html#attribute-sets

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet
                version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format">

              <xsl:template match="/">
                <doc>
                  <xsl:apply-templates/>
                </doc>
              </xsl:template>

              <xsl:template match="chapter/heading">
                <fo:block quadding="start" xsl:use-attribute-sets="title-style">
                  <xsl:apply-templates/>
                </fo:block>
              </xsl:template>

              <xsl:attribute-set name="title-style">
                <xsl:attribute name="font-size">12pt</xsl:attribute>
                <xsl:attribute name="font-weight">bold</xsl:attribute>
              </xsl:attribute-set>

              </xsl:stylesheet>"""


source_1="""<chapter>
              <heading/>
              </chapter>"""


expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<doc xmlns:fo='http://www.w3.org/1999/XSL/Format'>
              <fo:block font-weight='bold' font-size='12pt' quadding='start'/>
              </doc>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
