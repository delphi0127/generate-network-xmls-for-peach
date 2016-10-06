#This source doc used to bomb cDomlette just on parse, as Uche found out

from Xml.Xslt import test_harness

sheet_1 = """\
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
>

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
"""

source_1 = """<?xml version='1.0'?>
<x xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include href="Xml/Core/include1.xml"/>
</x>
"""

source_2 = """<?xml version='1.0'?>
<x xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include href="Xml/Core/include2.xml"/>
</x>
"""

source_3 = """<?xml version='1.0'?>
<x xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include href="Xml/Core/include2.xml" parse='text'/>
</x>
"""

from Xml.Core.test_xinclude import expected_1, expected_2, expected_3

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='Case 1')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='Case 2')

    source = test_harness.FileInfo(string=source_3)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='Case 3')
    return
