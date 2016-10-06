#Example from David Carlisle to John Lam on 25 Feb 2000, with well-formedness and XSLT semantics corrections

from Xml.Xslt import test_harness

sheet_1 = """<total
  xsl:version="1.0"
  xsl:exclude-result-prefixes="exsl"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
>

<xsl:variable name="x">
  <xsl:for-each select="x/thing">
    <a><xsl:value-of select="quantity * price"/></a>
  </xsl:for-each>
</xsl:variable>

<xsl:value-of select="sum(exsl:node-set($x)/*)"/>

</total>
"""


source_1="""<x>
<thing><quantity> 1</quantity><price> 2</price></thing>
<thing><quantity> 4</quantity><price> 5</price></thing>
<thing><quantity> 3</quantity><price>10</price></thing>
<thing><quantity> 2</quantity><price> 1</price></thing>
</x>
"""


expected_1="""<?xml version='1.0' encoding='UTF-8'?>
<total>54</total>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
