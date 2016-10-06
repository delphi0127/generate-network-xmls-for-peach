#Exercise some uniquification/grouping tricks

from Xml.Xslt import test_harness

sheet_1 = """\
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
>

  <xsl:key name='k' match='datum' use='.'/>

  <xsl:template match="data">
    <data>
      <xsl:copy-of select='datum[generate-id(.)=generate-id(key("k",.)[1])]'/>
    </data>
  </xsl:template>

</xsl:stylesheet>
"""

sheet_2 = """\
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
>

  <xsl:key name='k' match='datum' use='.'/>

  <xsl:template match="data">
    <xsl:variable name="unique" select='datum[generate-id(.)=generate-id(key("k",.)[1])]'/>
    <data>
      <xsl:apply-templates select="$unique"/>
    </data>
  </xsl:template>

  <xsl:template match="datum">
    <xsl:copy>
      <xsl:value-of select="."/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
"""

source_1 = """\
<?xml version='1.0'?>
<data>
  <datum>one</datum>
  <datum>two</datum>
  <datum>three</datum>
  <datum>one</datum>
  <datum>three</datum>
  <datum>two</datum>
  <datum>two</datum>
  <datum>one</datum>
</data>
"""

source_2 = source_1

source_x = """\
<?xml version='1.0'?>
<data>
  <datum p='1'>one</datum>
  <datum p='2'>two</datum>
  <datum p='3'>three</datum>
  <datum p='1'>ein</datum>
  <datum p='3'>drei</datum>
  <datum p='1'>un</datum>
  <datum p='2'>zwo</datum>
  <datum p='1'>otu</datum>
</data>
"""

expected_1 = """\
<?xml version='1.0' encoding='UTF-8'?>
<data><datum>one</datum><datum>two</datum><datum>three</datum></data>"""

expected_2 = expected_1


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='generate-id/key techniques, case 1')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='generate-id/key techniques, case 2')
    return
