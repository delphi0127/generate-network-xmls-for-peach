# Kamel Howard reported difficulty using "current()" in a place
# where "." would have sufficed. See
# http://lists.fourthought.com/pipermail/4suite/2003-September/012215.html

from Xml.Xslt import test_harness

SRC_1 = """<?xml version="1.0" encoding="utf-8"?>
<data>
  <stuff>
    <files>
      <file name="three" num="3"/>
      <file name="four" num="4"/>
    </files>
    <morefiles>
      <file name="one" num="1"/>
      <file name="two" num="2"/>
    </morefiles>
  </stuff>
  <otherstuff>
    <file name="six" num="6"/>
    <file name="five" num="5"/>
  </otherstuff>
</data>"""

SHEET_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes" encoding="us-ascii"/>
  <xsl:template match="data">
    <table>
      <xsl:for-each select="current()//file">
      <xsl:sort select="@num" order="ascending" case-order="lower-first" data-type="number"/>
        <tr>
          <th align="left"><xsl:value-of select="@num"/></th>
          <td width="99%"><xsl:value-of select="@name"/></td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>
</xsl:stylesheet>"""

EXPECTED_1 = """<?xml version="1.0" encoding="us-ascii"?>
<table>
  <tr>
    <th align="left">1</th>
    <td width="99%">one</td>
  </tr>
  <tr>
    <th align="left">2</th>
    <td width="99%">two</td>
  </tr>
  <tr>
    <th align="left">3</th>
    <td width="99%">three</td>
  </tr>
  <tr>
    <th align="left">4</th>
    <td width="99%">four</td>
  </tr>
  <tr>
    <th align="left">5</th>
    <td width="99%">five</td>
  </tr>
  <tr>
    <th align="left">6</th>
    <td width="99%">six</td>
  </tr>
</table>
"""

def Test(tester):
    source = test_harness.FileInfo(string=SRC_1)
    sheet = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_1,
                          title='current() instead of .')
