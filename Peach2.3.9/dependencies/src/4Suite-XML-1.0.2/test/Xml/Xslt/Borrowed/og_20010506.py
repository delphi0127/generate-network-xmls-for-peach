#Oliver Graf <ograf@oli-ver-ena.de> spotted illegal side-effects on params

from Xml.Xslt import test_harness

sheet_1 = """\
<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output method="text" encoding="ISO-8859-1"/>

<xsl:param name="what" select="'this'"/>

<xsl:template match="/">
  <xsl:apply-templates select="test">
        <xsl:with-param name="what" select="concat($what,',root')"/>
  </xsl:apply-templates>
</xsl:template>

<xsl:template match="test">
  <xsl:param name="what" select="''"/>
  <xsl:apply-templates select="data">
        <xsl:with-param name="what" select="concat($what,',test')"/>
  </xsl:apply-templates>
  <xsl:apply-templates select="data">
        <xsl:with-param name="what" select="concat($what,',rerun')"/>
  </xsl:apply-templates>
</xsl:template>

<xsl:template match="data">
  <xsl:param name="what" select="''"/>
  <xsl:value-of select="."/>
  <xsl:text> </xsl:text>
  <xsl:value-of select="$what"/>
  <xsl:text>
</xsl:text>
</xsl:template>

</xsl:stylesheet>"""


source_1 = """\
<?xml version="1.0" encoding="ISO-8859-1"?>

<test>
  <data>11</data>
  <data>12</data>
  <data>13</data>
  <data>14</data>
  <data>15</data>
</test>
"""

expected_1 = """\
11 this,root,test
12 this,root,test
13 this,root,test
14 this,root,test
15 this,root,test
11 this,root,rerun
12 this,root,rerun
13 this,root,rerun
14 this,root,rerun
15 this,root,rerun
"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
