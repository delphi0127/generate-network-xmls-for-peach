from Xml.Xslt import test_harness

sheet_str = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:template match="/">
    <MEMO>
    <xsl:processing-instruction name='xml-stylesheet'>href="memo.css" type="text/css"</xsl:processing-instruction>
    <TITLE><xsl:value-of select='/document/title'/></TITLE>
    <xsl:apply-templates/>
    </MEMO>
  </xsl:template>

  <xsl:template match="paragraph">
    <PARA>
      <xsl:apply-templates/>
    </PARA>
  </xsl:template>

  <xsl:template match="product">
    <xsl:element name='PROD'>
    <xsl:attribute name='href'><xsl:value-of select='code'/></xsl:attribute>
    <xsl:value-of select='name'/>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>"""

xml_source = """<?xml version="1.0"?>
<document> 
    <description>Memo</description> 
    <title>Re: Widget 404 Request</title> 
    <paragraph> 
        We need 5 of 
           <product> 
              <code>00808</code> 
              <name>Widget 404</name> 
              <description>Gee-gaw and doo-dad</description> 
           </product> 
         to send out to reviewers this week. 
    </paragraph> 
</document>  
"""

expected = """<?xml version='1.0' encoding='UTF-8'?>
<MEMO><?xml-stylesheet href="memo.css" type="text/css"?><TITLE>Re: Widget 404 Request</TITLE> 
    Memo 
    Re: Widget 404 Request 
    <PARA> 
        We need 5 of 
           <PROD href='00808'>Widget 404</PROD> 
         to send out to reviewers this week. 
    </PARA> 
</MEMO>"""


def Test(tester):
    source = test_harness.FileInfo(string=xml_source)
    sheet = test_harness.FileInfo(string=sheet_str)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title="xsl:processing-instruction")
    return
