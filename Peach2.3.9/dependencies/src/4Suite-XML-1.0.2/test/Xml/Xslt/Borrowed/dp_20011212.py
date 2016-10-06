#Dave's Pawson's exsl:node-set problems

from Xml.Xslt import test_harness

sheet_1 = """\
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exslt="http://exslt.org/common"
  exclude-result-prefixes="exslt"
  version="1.0"
>

<xsl:template match="/">
  <xsl:variable name="smilFiles">
    <xsl:for-each select="//*[contains(@href,'smil')]">
     <xsl:copy-of select="."/>
    </xsl:for-each>
  </xsl:variable>
  <xsl:message><xsl:copy-of select="exslt:node-set($smilFiles)"/></xsl:message>

  <xsl:for-each select="exslt:node-set($smilFiles)/a">
    <ref title="{.}" src="{substring-before(@href,'#')}" id="{substring-before(@href,'.')}"/>
    </xsl:for-each>
</xsl:template>

</xsl:stylesheet>
"""

source_1 = '<h4 id="bajw_000e"><a href="bajw000E.smil#bajw_000e">Helen Sismore.</a></h4>'

expected_1 = """\
<?xml version='1.0' encoding='UTF-8'?>\n<ref title='Helen Sismore.' id='bajw000E' src='bajw000E.smil'/>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='RTF root nodes')
    return
