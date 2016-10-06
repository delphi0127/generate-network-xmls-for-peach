from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:template match="customer">
    <wrapper>
    <customer id="{@id}" xmlns="http://spam.com">
      <xsl:element name="{substring-before(., ' ')}" namespace="http://eggs.com">Eggs</xsl:element>
      <name><xsl:value-of select="."/></name>
    </customer>
    </wrapper>
  </xsl:template>

</xsl:stylesheet>
"""

source_1 = """<customer id="uo">Uche Ogbuji</customer>"""

sheet_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:output method="html"/>

  <xsl:template match="/">
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>
"""

#source_1 = """<noescape>dummy</noescape>"""

expected_1 = """\
<?xml version='1.0' encoding='UTF-8'?>
<wrapper><customer id='uo' xmlns='http://spam.com'><Uche xmlns='http://eggs.com'>Eggs</Uche><name>Uche Ogbuji</name></customer></wrapper>"""

source_2 = """<foo/>"""

# makes sure empty text nodes are not created
sheet_2 = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

     <xsl:output indent="no" encoding="us-ascii"/>

     <xsl:template match="/">
       <result>
         <text>
           <xsl:text/>
         </text>
         <value>
           <xsl:value-of select="''"/>
         </value>
       </result>
     </xsl:template>

</xsl:stylesheet>"""

expected_2 = """<?xml version='1.0' encoding='us-ascii'?>
<result><text/><value/></result>"""


def Test(tester):

    tester.startGroup("Literal elements and text")

    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sty], expected_1,
                          title='test 1')

    source = test_harness.FileInfo(string=source_2)
    sty = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sty], expected_2,
                          title='test 2')

    tester.groupDone()

    return
