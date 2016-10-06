from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:strip-space elements='*'/>

  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE>Address Book</TITLE>
    </HEAD>
    <BODY>
    <TABLE><xsl:apply-templates/></TABLE>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="ENTRY">
        <xsl:element name='TR'>
        <xsl:apply-templates select='NAME'/>
        </xsl:element>
        <xsl:if test='not(position()=last())'><HR/></xsl:if>
  </xsl:template>

  <xsl:template match="NAME">
    <xsl:element name='TD'>
    <xsl:attribute name='ALIGN'>CENTER</xsl:attribute>
      <B><xsl:apply-templates/></B>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
"""


expected_1 = """<HTML>
  <HEAD>
    <META HTTP-EQUIV='Content-Type' CONTENT='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <TABLE>
      <TR>
        <TD ALIGN='CENTER'><B>Pieter Aaron</B></TD>
      </TR>
      <HR>
      <TR>
        <TD ALIGN='CENTER'><B>Emeka Ndubuisi</B></TD>
      </TR>
      <HR>
      <TR>
        <TD ALIGN='CENTER'><B>Vasia Zhugenev</B></TD>
      </TR>
    </TABLE>
  </BODY>
</HTML>"""


sheet_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:template match="/">
    <boo>
      <!-- true -->
      <xsl:if test='/'>
        ( <true/> )
      </xsl:if>
      <!-- false -->
      <xsl:if test='/..'>
        ( <false/> )
      </xsl:if>
    </boo>
  </xsl:template>

</xsl:stylesheet>
"""

source_2 = "<dummy/>"


expected_2 = "<?xml version='1.0' encoding='UTF-8'?>\n<boo>\n        ( <true/> )\n      </boo>"


def Test(tester):
    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sty = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sty], expected_1,
                          title='xsl:if')
    

    source = test_harness.FileInfo(string=source_2)
    sty = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sty], expected_2,
                          title="test text and element children of xsl:if")
    return
