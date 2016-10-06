#Martin Sevigny's Saxon bug report, 29 Mar 2000

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="Record">
    <TestRecord>
      <xsl:apply-templates/>
    </TestRecord>
  </xsl:template>
  <xsl:template match="Field[@No='606']/Subfield[@No='x']">
    <GotAMatch><xsl:apply-templates/></GotAMatch>
  </xsl:template>
</xsl:stylesheet>"""


source_1="""<?xml version="1.0" ?>
<Record id='1'>
  <Field No="606">
    <Subfield No="x">Use</Subfield>
  </Field>
</Record>"""


expected_1="""<?xml version='1.0' encoding='UTF-8'?>
<TestRecord>
  
    <GotAMatch>Use</GotAMatch>
  
</TestRecord>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
