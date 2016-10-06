#Example from Michael Kay to ??? on 4 Feb 2000, with well-formedness corrections

from Xml.Xslt import test_harness

sheet_1 = """<xsl:transform
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 version="1.0"
>

<xsl:output method='text'/>

<xsl:variable name="pos">
  <xsl:for-each select="//element[descendant::y[.='z']][1]">
    <xsl:number/>
  </xsl:for-each>
</xsl:variable>

<xsl:template match="/">
result: <xsl:value-of select='$pos'/>
</xsl:template>

</xsl:transform>"""

sheet_2 = """<xsl:transform
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 version="1.0"
>

<xsl:output method='text'/>

<xsl:variable name="pos">
   <xsl:for-each select="//element">
       <xsl:if test="*[descendant::y[.='z']]">
           <xsl:value-of select="position()"/>
       </xsl:if>
   </xsl:for-each>
</xsl:variable>

<xsl:template match="/">
result: <xsl:value-of select='$pos'/>
</xsl:template>

</xsl:transform>"""

#This third approach actually by Senthil Vaiyapuri <senthil@portal.com> on 2000-02-04
sheet_3 = """<?xml version="1.0" standalone="yes"?> 
<xsl:stylesheet
      xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      version="1.0">
<xsl:output method="text"/>

<xsl:template match="element">
  <xsl:if test=".//y"> 
    <xsl:variable name="yvalue"><xsl:value-of select=".//y"/></xsl:variable>
     <xsl:if test="$yvalue = 'z'">
       <xsl:number count="element" format="1." level="any"/>
     </xsl:if>
  </xsl:if>
</xsl:template>
</xsl:stylesheet>
"""

source_1="""<?xml version="1.0"?>
<elementList>
    <element>
        <x>
            <y>a</y>
        </x>
    </element>
    <element>
        <x>
            <y>z</y>
        </x>
    </element>
</elementList>"""

expected_1 = """
result: 2"""
expected_2 = """
result: 2"""
expected_3 = """
    
    2.
"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='test 1')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='test 2')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='test 3')
    return
