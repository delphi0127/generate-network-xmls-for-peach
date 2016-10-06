#Based on Andy Turk's RTF FAQ (18 June 2000).  Interesting because of the fact that his RTF consists of a grove of attributes.  Note that his xsl:value-ofs had to be changed to xsl:copy-ofs
from Ft.Xml.Xslt import XsltException, Error
from Xml.Xslt import test_harness


#This one should bomb: implicit conversion from RTF to node-set
sheet_1 = """<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
>
  <xsl:strip-space elements="*"/>

  <xsl:template match="row">
    <xsl:variable name="attrs"><xsl:copy-of select="@*"/></xsl:variable>
    <tr>
      <xsl:for-each select="../column">
        <td>
          <xsl:for-each select="@*">
            <xsl:attribute name="{name()}"><xsl:value-of select="."/></xsl:attribute>
          </xsl:for-each>
          <xsl:for-each select="$attrs">
            <xsl:attribute name="{name()}"><xsl:value-of select="."/></xsl:attribute>
          </xsl:for-each>
        </td>
      </xsl:for-each>
    </tr>
  </xsl:template>
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates select='*'/>
    </docelem>
  </xsl:template>

</xsl:stylesheet>"""


#Do it the right way
sheet_2 = """<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
>
  <xsl:strip-space elements="*"/>

  <xsl:template match="row">
    <xsl:variable name="attrs" select="@*"/>
    <tr>
      <xsl:for-each select="../column">
        <td>
          <xsl:for-each select="@*">
            <xsl:attribute name="{name()}"><xsl:value-of select="."/></xsl:attribute>
          </xsl:for-each>
          <xsl:for-each select="$attrs">
            <xsl:attribute name="{name()}"><xsl:value-of select="."/></xsl:attribute>
          </xsl:for-each>
        </td>
      </xsl:for-each>
    </tr>
  </xsl:template>
  <xsl:template match='/'>
    <docelem><xsl:apply-templates select='*'/></docelem>
  </xsl:template>

</xsl:stylesheet>"""


#Do it by using the node-set extension
sheet_3 = """<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
  exclude-result-prefixes="exsl"
  version="1.0"
>
  <xsl:strip-space elements="*"/>

  <xsl:template match="row">
    <xsl:variable name="attrs"><xsl:copy-of select="@*"/></xsl:variable>
    <tr>
      <xsl:for-each select="../column">
        <td>
          <xsl:for-each select="@*">
            <xsl:attribute name="{name()}"><xsl:value-of select="."/></xsl:attribute>
          </xsl:for-each>
          <!--
            $attrs should be just an RTF document node at this point.
            We expect the for-each here to select an empty node-set.
          -->
          <xsl:for-each select="exsl:node-set($attrs)/@*">
            <xsl:attribute name="{name()}"><xsl:value-of select="."/></xsl:attribute>
          </xsl:for-each>
        </td>
      </xsl:for-each>
    </tr>
  </xsl:template>
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates select='*'/>
    </docelem>
  </xsl:template>

</xsl:stylesheet>"""


xml_source="""<matrix>
 <column c="1"/>
 <column c="2"/>
 <row r="1"/>
 <row r="2"/>
</matrix>
"""

expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<docelem><tr><td r='1' c='1'/><td r='1' c='2'/></tr><tr><td r='2' c='1'/><td r='2' c='2'/></tr></docelem>
"""

# RTFs cannot contain attribute/namespace nodes as
# immediate children
expected_3 = """<?xml version='1.0' encoding='UTF-8'?>
<docelem><tr><td c='1'/><td c='2'/></tr><tr><td c='1'/><td c='2'/></tr></docelem>
"""


def Test(tester):

    source = test_harness.FileInfo(string=xml_source)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], "",
                          exceptionCode=Error.INVALID_FOREACH_SELECT,
                          title='Invalid use of RTF')

    source = test_harness.FileInfo(string=xml_source)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title="RTF as variable")

    source = test_harness.FileInfo(string=xml_source)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title="Conversion with exsl:node-set")
    return
