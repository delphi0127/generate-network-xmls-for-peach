#Further analysis, by Warren Hedley <w.hedley@auckland.ac.nz> on 7 June 2000, of the XT bug report

from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

<xsl:template match="doc/div[last()=1]">
  <xsl:value-of select="." />
  <xsl:text> (</xsl:text>
  <xsl:value-of select="position()" />
  <xsl:text> - </xsl:text>
  <xsl:value-of select="last()" />
  <xsl:text>)
</xsl:text>
</xsl:template>

<xsl:template match="text()" />

</xsl:stylesheet>"""


source_1="""<?xml version="1.0" encoding="UTF-8"?>

<!DOCTYPE document>

<document>
  <doc>
    <div>doc1-div1</div>
    <div>doc1-div2</div>
  </doc>
  <doc>
    <div>doc2-div1</div>
  </doc>
  <doc>
    <div>doc3-div1</div>
    <div>doc3-div2</div>
    <div>doc3-div3</div>
  </doc>
</document>"""


expected_1 = """<?xml version="1.0" encoding="UTF-8"?>
doc2-div1 (2 - 3)
"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
