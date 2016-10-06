from Xml.Xslt import test_harness

sheet_1 = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:template match="/">
    <out>
      <xsl:apply-templates/>
    </out>
  </xsl:template>

  <xsl:template match="func">
    <one>
      <xsl:value-of select="ft:replace('X', ' ')"/>
    </one>
    <two>
      <xsl:value-of select="ft:replace('X', ' ', .)"/>
    </two>
  </xsl:template>
  
  <xsl:template match="elem">
    <three>
      <ft:replace substring='&quot;&#10;&quot;'>
        <newline/>
      </ft:replace>
    </three>
    <four>
      <ft:replace string='.' substring='&quot;&#10;&quot;'>
        <newline/>
      </ft:replace>
    </four>
  </xsl:template>
  
</xsl:stylesheet>
"""

source_1 = """\
<foo>
  <func>oneXsmallXstepXforXaXman</func>
  <elem>one
giant
leap
for
mankind</elem>
</foo>
"""


expected_1 = """\
<?xml version='1.0' encoding='UTF-8'?>\n<out>\n  <one>one small step for a man</one><two>one small step for a man</two>\n  <three>one<newline/>giant<newline/>leap<newline/>for<newline/>mankind<newline/></three><four>one<newline/>giant<newline/>leap<newline/>for<newline/>mankind<newline/></four>\n</out>"""


def Test(tester):
    tester.startGroup("basic ft:replace function and element")
    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sty], expected_1)
    tester.groupDone()

    return
