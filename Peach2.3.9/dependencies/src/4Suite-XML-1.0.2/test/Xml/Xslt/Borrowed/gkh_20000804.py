#G. Ken Holman's <gkholman@CraneSoftwrights.com> node-set intersection and difference example

from Xml.Xslt import test_harness

sheet_and_source = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                 xmlns:data="ken"
                 version="1.0">

<xsl:output method="text"/>

<data:data>
   <item>1</item>
   <item>2</item>
   <item>3</item>
   <item>4</item>
   <item>5</item>
</data:data>

<xsl:template match="/">                         <!--root rule-->
   <xsl:variable name="ns1"
                 select="document('')//data:data/item[position()>1]"/>
   <xsl:variable name="ns2"
                 select="document('')//data:data/item[position()&lt;5]"/>
   <xsl:for-each select="$ns1[count(.|$ns2)=count($ns2)]">
     Intersection: <xsl:value-of select="."/>
   </xsl:for-each>
   <xsl:for-each select="(   $ns1[count(.|$ns2)!=count($ns2)]
                           | $ns2[count(.|$ns1)!=count($ns1)] )">
     Difference: <xsl:value-of select="."/>
   </xsl:for-each>
</xsl:template>

</xsl:stylesheet>"""


expected = """
     Intersection: 2
     Intersection: 3
     Intersection: 4
     Difference: 1
     Difference: 5"""


def Test(tester):
    source = test_harness.FileInfo(string=sheet_and_source)
    sheet = test_harness.FileInfo(string=sheet_and_source)
    test_harness.XsltTest(tester, source, [sheet], expected)
    return
    
