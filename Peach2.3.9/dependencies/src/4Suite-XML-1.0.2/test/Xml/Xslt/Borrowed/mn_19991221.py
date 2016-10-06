#Miloslav Nic <nicmila@vscht.cz>'s hack used in his on-line tutorials, with many corrections.  Posted 21 Dec 1999

from Xml.Xslt import test_harness

sheet_1 = """<xsl:transform
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 version="1.0"
>

<xsl:template match="text()">
<xsl:value-of select="translate(.,'{}','&lt;&gt;')"/>
</xsl:template>

<xsl:template match="/">
<xhtml><body>
<xsl:apply-templates/>
</body></xhtml>
</xsl:template>

<xsl:template match="description|doc">
<xsl:apply-templates/>
</xsl:template>

<xsl:template match="*">
<xsl:element name="{name()}"/>
<xsl:apply-templates/>
</xsl:template>

<xsl:template match="error">
<SPAN class="error"><xsl:apply-templates/></SPAN>
</xsl:template>
</xsl:transform>"""


source_1="""<demo type="notwf">
<description>Document with erroneous attributes</description>
<doc>
{errors}
        {wrong_char a<error>*</error>b = "23432"/}
        {mismatched_separator value = <error>"</error>12<error>'</error>/}
        {wrong_separator_type  value="aa<error>"</error>aa"/}
        {wrong_separator_type  value='bb<error>'</error>bb'/}
        {wrong_start <error>XML</error>-ID = "xml234"/}
{/errors}
</doc>
</demo>"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<xhtml><body><demo/>
Document with erroneous attributes

&lt;errors>
        &lt;wrong_char a<SPAN class='error'>*</SPAN>b = "23432"/>
        &lt;mismatched_separator value = <SPAN class='error'>"</SPAN>12<SPAN class='error'>'</SPAN>/>
        &lt;wrong_separator_type  value="aa<SPAN class='error'>"</SPAN>aa"/>
        &lt;wrong_separator_type  value='bb<SPAN class='error'>'</SPAN>bb'/>
        &lt;wrong_start <SPAN class='error'>XML</SPAN>-ID = "xml234"/>
&lt;/errors>

</body></xhtml>"""
#"'

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
