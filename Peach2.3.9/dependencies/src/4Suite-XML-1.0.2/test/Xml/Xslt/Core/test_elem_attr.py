from Xml.Xslt import test_harness

dummy_src = """<?xml version="1.0"?><dummy/>"""

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

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
  </xsl:template>

  <xsl:template match="NAME">
    <xsl:element name='TD'>
    <xsl:attribute name='ALIGN'>CENTER</xsl:attribute>
      <B><xsl:apply-templates/></B>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
"""

sheet_2 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <!-- should be in explicitly specified namespace --> 
      <xsl:element name="xse-ns" namespace="http://foo/bar"/>
      <xsl:element name="xse-empty-ns" namespace=""/>
      <!-- should be in default namespace (empty) -->
      <xsl:element name="xse"/>
      <lre-ns xmlns="http://stuff">
        <!-- should be in explicitly specified namespace -->   
        <xsl:element name="xse-ns" namespace="http://foo/bar"/>
        <xsl:element name="xse-empty-ns" namespace=""/>
        <!-- should be in http://stuff namespace -->                                                           
        <xsl:element name="xse"/>
      </lre-ns>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

sheet_3 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>   

  <xsl:template match="/">
    <result>
      <lre>
        <xsl:attribute name="att">foo</xsl:attribute>
        <!-- should be in explicitly specified namespace -->
        <xsl:attribute name="att-ns" namespace="http://crud">foo</xsl:attribute>
        <xsl:attribute name="att-empty-ns" namespace="">foo</xsl:attribute>
      </lre>
      <lre xmlns="http://stuff">
        <!-- ns should be none/empty; should *not* inherit http://stuff -->
        <xsl:attribute name="att">foo</xsl:attribute>
        <!-- should be in explicitly specified namespace -->
        <xsl:attribute name="att-ns" namespace="http://crud">foo</xsl:attribute>
        <xsl:attribute name="att-empty-ns" namespace="">foo</xsl:attribute>
      </lre>
      <lre xmlns:pre="http://prefix">
        <!-- ns should the one bound to pre: -->
        <xsl:attribute name="pre:att">foo</xsl:attribute>
        <!-- explicit namespace should override the one bound to pre: -->
        <xsl:attribute name="pre:att-ns" namespace="http://crud">foo</xsl:attribute>
        <xsl:attribute name="pre:att-empty-ns" namespace="">foo</xsl:attribute>
      </lre>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

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
      <TR>
        <TD ALIGN='CENTER'><B>Emeka Ndubuisi</B></TD>
      </TR>
      <TR>
        <TD ALIGN='CENTER'><B>Vasia Zhugenev</B></TD>
      </TR>
    </TABLE>
  </BODY>
</HTML>"""

expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<result><xse-ns xmlns='http://foo/bar'/><xse-empty-ns/><xse/><lre-ns xmlns='http://stuff'><xse-ns xmlns='http://foo/bar'/><xse-empty-ns xmlns=''/><xse/></lre-ns></result>"""

expected_3 = """<?xml version='1.0' encoding='UTF-8'?>
<result><lre xmlns:org.4suite.4xslt.ns0='http://crud' att-empty-ns='foo' att='foo' org.4suite.4xslt.ns0:att-ns='foo'/><lre xmlns='http://stuff' xmlns:org.4suite.4xslt.ns0='http://crud' att-empty-ns='foo' att='foo' org.4suite.4xslt.ns0:att-ns='foo'/><lre xmlns:org.4suite.4xslt.ns0='http://crud' xmlns:pre='http://prefix' pre:att='foo' att-empty-ns='foo' org.4suite.4xslt.ns0:att-ns='foo'/></result>"""

def Test(tester):

    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sty = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sty], expected_1,
                          title="xsl:element and xsl:attribute instantiation")


    source = test_harness.FileInfo(string=dummy_src)
    sty = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sty], expected_2,
                          title="xsl:element with namespaces")


    source = test_harness.FileInfo(string=dummy_src)
    sty = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sty], expected_3,
                          title="xsl:attribute with namespaces")
    return
