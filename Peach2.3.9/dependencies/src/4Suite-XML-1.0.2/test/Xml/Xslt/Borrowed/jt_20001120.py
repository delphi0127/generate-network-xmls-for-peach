#Jeni Tennison <Jeni.Tennison@epistemics.co.uk> expores the world of NaN

from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

<xsl:template match="/">
   <xsl:variable name="NaN" select="number('abc')" />
   String value of NaN: <xsl:value-of select="$NaN" />
   String value of boolean value of NaN: <xsl:value-of select="boolean($NaN)" />
   String value of boolean value of string value of NaN: <xsl:value-of select="boolean(string($NaN))" />
   String value of numerical value of boolean value of NaN: <xsl:value-of select="number(boolean($NaN))" />
   String value of numerical value of boolean value of string value of NaN: <xsl:value-of select="number(boolean(string($NaN)))" />
</xsl:template>

</xsl:stylesheet>"""

source_1 = """<source/>"""

saxon_expected = """   String value of NaN: NaN
   String value of boolean value of NaN: false
   String value of boolean value of string value of NaN: true
   String value of numerical value of boolean value of NaN: 0
   String value of numerical value of boolean value of string value of NaN: 1
"""

expected_1 = """<?xml version="1.0" encoding="UTF-8"?>

   String value of NaN: NaN
   String value of boolean value of NaN: false
   String value of boolean value of string value of NaN: true
   String value of numerical value of boolean value of NaN: 0
   String value of numerical value of boolean value of string value of NaN: 1"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
