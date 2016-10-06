#From the XSLT spec: http://docs.local/REC-xslt-19991116.html#dt-literal-namespace-uri

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet
                version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:axsl="http://www.w3.org/1999/XSL/TransformAlias">

              <xsl:namespace-alias stylesheet-prefix="axsl" result-prefix="xsl"/>

              <xsl:template match="/">
                <axsl:stylesheet>
                  <xsl:apply-templates/>
                </axsl:stylesheet>
              </xsl:template>

              <xsl:template match="block">
                <axsl:template match="{.}">
                   <fo:block><axsl:apply-templates/></fo:block>
                </axsl:template>
              </xsl:template>

              </xsl:stylesheet>"""


source_1="""<elements>
              <block>p</block>
              <block>h1</block>
              <block>h2</block>
              <block>h3</block>
              <block>h4</block>
              </elements>"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet xmlns:fo='http://www.w3.org/1999/XSL/Format' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
              <xsl:template match='p'><fo:block><xsl:apply-templates/></fo:block></xsl:template>
              <xsl:template match='h1'><fo:block><xsl:apply-templates/></fo:block></xsl:template>
              <xsl:template match='h2'><fo:block><xsl:apply-templates/></fo:block></xsl:template>
              <xsl:template match='h3'><fo:block><xsl:apply-templates/></fo:block></xsl:template>
              <xsl:template match='h4'><fo:block><xsl:apply-templates/></fo:block></xsl:template>
              </xsl:stylesheet>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
