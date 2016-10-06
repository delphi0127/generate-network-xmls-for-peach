
"""
Mike Brown reported a problem with minidom and children nodes
"""

from Xml.Xslt import test_harness


source_1="""<?xml version="1.0" encoding="utf-8"?>
<docu><!--quotation--><t xml:lang="en">To be or not to be</t><?Question that-is-the?></docu>"""



sheet_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="text" indent="yes" encoding="us-ascii"/>

  <xsl:template match="/">
    <result>
      <xsl:apply-templates select="//node()"/>
    </result>
  </xsl:template>

  <xsl:template match="*">
    <xsl:text>Element: </xsl:text>
    <xsl:value-of select="name()"/>
    <xsl:call-template name="report"/>
    <xsl:apply-templates select="@*"/>
  </xsl:template>
  <xsl:template match="@*">
    <xsl:text>Attribute: </xsl:text>
    <xsl:value-of select="name()"/>
    <xsl:call-template name="report"/>
  </xsl:template>

  <xsl:template match="text()">
    <xsl:text>Text node: </xsl:text>
    <xsl:value-of select="."/>
    <xsl:call-template name="report"/>
  </xsl:template>

  <xsl:template match="comment()">
    <xsl:text>Comment: </xsl:text>
    <xsl:value-of select="."/>
    <xsl:call-template name="report"/>
  </xsl:template>

  <xsl:template match="processing-instruction()">
    <xsl:text>P.I. node: </xsl:text>
    <xsl:value-of select="."/>
    <xsl:call-template name="report"/>
  </xsl:template>

  <xsl:template name="report">
    <xsl:text>&#10;# of descendants: </xsl:text>
    <xsl:value-of select="count(descendant::node())"/>
    <xsl:text>&#10;-----------------------------&#10;</xsl:text>
  </xsl:template>

</xsl:stylesheet>
"""

expected = """Element: docu
# of descendants: 4
-----------------------------
Comment: quotation
# of descendants: 0
-----------------------------
Element: t
# of descendants: 1
-----------------------------
Attribute: xml:lang
# of descendants: 0
-----------------------------
Text node: To be or not to be
# of descendants: 0
-----------------------------
P.I. node: that-is-the
# of descendants: 0
-----------------------------
"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title="Test Descendants of different node types")
    return

