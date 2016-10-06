from Xml.Xslt import test_harness

sheet_str_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:output method="html"/>

  <xsl:template match="/">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="noescape">
    <html><p><xsl:text disable-output-escaping='yes'>&amp;nbsp;</xsl:text></p></html>
  </xsl:template>

</xsl:stylesheet>
"""

xml_source_1 = """<noescape>dummy</noescape>"""

expected_1 = """<html>
  <p>&nbsp;</p>
</html>"""


def Test(tester):
    source = test_harness.FileInfo(string=xml_source_1)
    sheet = test_harness.FileInfo(string=sheet_str_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title="Disable Output Escaping")
    return
