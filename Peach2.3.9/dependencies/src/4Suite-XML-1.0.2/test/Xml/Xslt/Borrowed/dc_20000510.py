#David Carlisle's <> Grammatical Decorator example, 10 May 2000

from Xml.Xslt import test_harness

source_1 = """  <exp>
      <add-exp>
        <add-exp>
          <mult-exp>
            <primary-exp>
              <literal value="2"/>
            </primary-exp>
          </mult-exp>
        </add-exp>
        <op-add/>
        <mult-exp>
          <primary-exp>
            <literal value="3"/>
          </primary-exp>
        </mult-exp>
      </add-exp>
    </exp>"""


sheet_1 = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0"
                >

<xsl:output method="xml" indent="yes"/>


<xsl:template match="add-exp[op-add]" mode="value">
<xsl:variable name="x">
<xsl:apply-templates select="*[1]" mode="value"/>
</xsl:variable>
<xsl:variable name="y">
<xsl:apply-templates select="*[3]" mode="value"/>
</xsl:variable>
<xsl:value-of select="$x + $y"/>
</xsl:template>

<xsl:template match="add-exp[op-sub]" mode="value">
<xsl:variable name="x">
<xsl:apply-templates select="*[1]" mode="value"/>
</xsl:variable>
<xsl:variable name="y">
<xsl:apply-templates select="*[3]" mode="value"/>
</xsl:variable>
<xsl:value-of select="$x - $y"/>
</xsl:template>


<xsl:template match="primary-exp[op-mult]" mode="value">
<xsl:variable name="x">
<xsl:apply-templates select="*[1]" mode="value"/>
</xsl:variable>
<xsl:variable name="y">
<xsl:apply-templates select="*[3]" mode="value"/>
</xsl:variable>
<xsl:value-of select="$x * $y"/>
</xsl:template>


<xsl:template match="literal" mode="value">
<xsl:value-of select="number(@value)"/>
</xsl:template>

<xsl:template match="*" mode="value">
<xsl:apply-templates select="*" mode="value"/>
</xsl:template>

<xsl:template match="*">
<xsl:copy>
<xsl:attribute name="value">
<xsl:apply-templates select="." mode="value"/>
</xsl:attribute>
<xsl:apply-templates/>
</xsl:copy>
</xsl:template>

<xsl:template match="op-add|op-sub|op-mult">
<xsl:copy>
<xsl:apply-templates/>
</xsl:copy>
</xsl:template>


</xsl:stylesheet>
"""

              
expected_1="""<?xml version='1.0' encoding='UTF-8'?>
<exp value='5'>
      <add-exp value='5'>
        <add-exp value='2'>
          <mult-exp value='2'>
            <primary-exp value='2'>
              <literal value='2'/>
            </primary-exp>
          </mult-exp>
        </add-exp>
        <op-add/>
        <mult-exp value='3'>
          <primary-exp value='3'>
            <literal value='3'/>
          </primary-exp>
        </mult-exp>
      </add-exp>
    </exp>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
