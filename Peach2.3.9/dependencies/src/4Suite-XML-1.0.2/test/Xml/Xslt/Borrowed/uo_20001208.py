#Uche Ogbuji exercises format-number on Brad Marshall's behalf

from Xml.Xslt import test_harness

sheet_1 = """\
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:template match = "/">
    <xsl:value-of select='format-number(10000000000.75 + 10000000000.50, "##.##")'/>
  </xsl:template>

</xsl:stylesheet>"""

#"
source_1 = "<spam/>"


expected_1 = """<?xml version="1.0" encoding="UTF-8"?>
20000000001.25"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
