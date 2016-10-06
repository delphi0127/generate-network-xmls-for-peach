from Xml.Xslt import test_harness

sheet_str_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
        <xsl:output method="html"/>

        <xsl:template match="/">
        <xsl:apply-templates/>
        </xsl:template>

        <xsl:template match="PARA">
                <p CLASS="dtp"><xsl:apply-templates/></p>
        </xsl:template>

        <xsl:template match="LINK">
                <a href="resolvterm?{@LINKEND}"><xsl:value-of select="."/></a>
        </xsl:template>

</xsl:stylesheet>
"""

xml_source_1 = """<PARA>This should have a trailing space <LINK LINKEND="foo">this should have no leading or trailing ws</LINK> this should have a leading space</PARA>"""

expected_1 = """<p CLASS='dtp'>This should have a trailing space <a href='resolvterm?foo'>this should have no leading or trailing ws</a> this should have a leading space</p>"""

sheet_2="""<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:output method="xml" indent="no" encoding="iso-8859-1"/>

  <xsl:template match="/">
    <result>
       <nbsp>&#160;</nbsp>
       <nbsps>&#160;&#160;&#160;</nbsps>
       <nbsptext>&#160;hello</nbsptext>
       <textnbsp>world&#160;</textnbsp>
       <lf>&#10;</lf>
       <lftext>&#10;foo</lftext>
       <textlf>bar&#10;</textlf>
       <tab>\x09</tab>
       <tabnbsp>\x09&#160;</tabnbsp>
       <tabtext>\x09tabbed</tabtext>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected_2= """<?xml version='1.0' encoding='iso-8859-1'?>
<result><nbsp>\xa0</nbsp><nbsps>\xa0\xa0\xa0</nbsps><nbsptext>\xa0hello</nbsptext><textnbsp>world\xa0</textnbsp><lf/><lftext>
foo</lftext><textlf>bar
</textlf><tab/><tabnbsp>\x09\xa0</tabnbsp><tabtext>\x09tabbed</tabtext></result>"""

def Test(tester):
    source = test_harness.FileInfo(string=xml_source_1)
    sheet = test_harness.FileInfo(string=sheet_str_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title="Whitespace Handling - trailing space in src doc")


    source = test_harness.FileInfo(string=xml_source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title="Whitespace Handling - nbsp, tab, lf in stylesheet")
    return
