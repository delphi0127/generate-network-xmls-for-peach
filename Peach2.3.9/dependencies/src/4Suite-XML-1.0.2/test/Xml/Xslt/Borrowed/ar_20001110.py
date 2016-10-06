#Alex Reutter <areutter@spss.com> finds brokenness in text output method
from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
<xsl:output method="text"/>

<xsl:template match="/source">
<xsl:text><![CDATA[<MML><Include "format.mml"></MML>]]></xsl:text>
<xsl:apply-templates/></xsl:template>

</xsl:stylesheet>"""

source_1 = """<source/>"""

expected_1 = '<MML><Include "format.mml"></MML>'


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='text output method bug')
    return
