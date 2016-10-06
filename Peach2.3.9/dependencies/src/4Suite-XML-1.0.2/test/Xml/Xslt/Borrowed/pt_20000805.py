#Paul Tchistopolskii <paul@qub.com> wonders whether Saxon or XT has a bug

from Xml.Xslt import test_harness


sheet_1 = """<xsl:stylesheet
xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version="1.0">
<xsl:output method="xml" indent="yes"/>

<xsl:template match="/">
<doc>
 <xsl:for-each select="/doc/*">
      <xsl:sort select="code"/>
      <xsl:copy-of select="."/>
 </xsl:for-each>
</doc>
</xsl:template>
</xsl:stylesheet>"""


source_1 = """<doc>
<a><code>A</code></a>
<b><code>-1</code></b>
<c><code>0</code></c>
</doc>"""


expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<doc>
  <b>
    <code>-1</code>
  </b>
  <c>
    <code>0</code>
  </c>
  <a>
    <code>A</code>
  </a>
</doc>"""


saxon_output = """<?xml version="1.0" encoding="utf-8"?>
<doc>
   <b>
      <code>-1</code>
   </b>
   <c>
      <code>0</code>
   </c>
   <a>
      <code>A</code>
   </a>
</doc>"""


#Note that all these sort orders are OK according to thhe spec's lenience
xt_output = """<?xml version="1.0" encoding="utf-8"?>
<doc>
<c>
<code>0</code>
</c>
<b>
<code>-1</code>
</b>
<a>
<code>A</code>
</a>
</doc>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
