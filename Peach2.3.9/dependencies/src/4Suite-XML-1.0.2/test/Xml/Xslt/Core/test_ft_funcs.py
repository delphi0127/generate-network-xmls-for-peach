from Xml.Xslt import test_harness

SHEET_1 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="text"/>
  
  <xsl:template match="/">
    <xsl:variable name='matches' select="ft:search-re('([a-z])([0-9])', 'a1b2c3d')"/>
    <xsl:apply-templates select='$matches'/>
  </xsl:template>

  <xsl:template match="Match">
    <xsl:text>Match 1 groups:</xsl:text><xsl:apply-templates/><xsl:text>&#10;</xsl:text>
  </xsl:template>
  
  <xsl:template match="Group">
    <xsl:text> "</xsl:text><xsl:apply-templates/><xsl:text>"</xsl:text>
  </xsl:template>
  
</xsl:stylesheet>
"""

##from Eric van der Vlist
##preg_match_all("Call 555-1212 or 1-800-555-1212 or (612) 555-1313",
##"/\(? (\d{3})? \)? (?(1) [\-\s] ) \d{3}-\d{4}/x")

##would return a nodeset whose structure could be:
##<Match>
##  <Group></Group>
##  <Group></Group>
##  <Group>555-1212</Group>
##</Match>
##<Match>
##  <Group>1</Group>
##  <Group>-800-</Group>
##  <Group>5551212</Group>
##</Match>
##<Match>
##  <Group></Group>
##  <Group>(612) </Group>
##  <Group>555-1213</Group>
##</Match>

SHEET_2 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="text"/>
  
  <xsl:template match="/">
    <xsl:variable name='matches' select="ft:search-re('(1)?([(-]?\d{3}?[)-]?\s?)?(\d{3}-\d{4})', 'Call 555-1212 or 1-800-555-1212 or (612) 555-1313')"/>
    <xsl:apply-templates select='$matches'/>
  </xsl:template>

  <xsl:template match="Match">
    <xsl:text>Match 1 groups: "</xsl:text>
    <xsl:for-each select="Group">
      <xsl:apply-templates/>
    </xsl:for-each>
    <xsl:text>"&#10;</xsl:text>
  </xsl:template>
  
</xsl:stylesheet>
"""

SHEET_3 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="concat('amp &amp; lt &lt; gt &gt; quot &quot; apos ', &quot;&apos;&quot;)"/><xsl:text>&#10;</xsl:text>
    <xsl:value-of select="ft:escape-xml(concat('amp &amp; lt &lt; gt &gt; quot &quot; apos ', &quot;&apos;&quot;))"/>
  </xsl:template>

</xsl:stylesheet>
"""

SHEET_4 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="text"/>
  
  <xsl:template match="/">
    <xsl:for-each select="ft:split('1,2,3', ',')">
      <xsl:text>split </xsl:text><xsl:value-of select="."/><xsl:text>&#10;</xsl:text>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""

SHEET_5 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="ft:base-uri(/monty/python/spam/eggs[1])"/>
  </xsl:template>

</xsl:stylesheet>"""

SHEET_6 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:if test="ft:ends-with('file.xml', 'xml')">
      <xsl:text>true</xsl:text>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>"""

SHEET_7 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="ft:if(1 = 0, 'true', 'false')"/>
  </xsl:template>

</xsl:stylesheet>"""

SHEET_8 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="text"/>

  <xsl:template match="/letters">
    <xsl:value-of select="ft:join(*, '-')"/>
  </xsl:template>

</xsl:stylesheet>"""

SHEET_9 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:for-each select="ft:range(10, 13)">
      <xsl:value-of select="."/>
      <xsl:if test="not(position() = last())">
        <xsl:text>, </xsl:text>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>"""

SHEET_10 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="ft:resolve-url('s://ex/a/b', 'c/d')"/>
  </xsl:template>

</xsl:stylesheet>"""

SHEET_11 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="ft:sha-hash('foo')"/>
  </xsl:template>

</xsl:stylesheet>"""

source_1 = """<dummy/>"""

source_5 = "<monty xml:base='s://ex/a/b'><python><spam xml:base='c/d'><eggs/></spam></python></monty>"

source_8 = "<letters><letter>a</letter><letter>b</letter><letter>c</letter></letters>"

expected_1 = """Match 1 groups: "a" "1"
Match 1 groups: "b" "2"
Match 1 groups: "c" "3"
"""

expected_2 = """Match 1 groups: "555-1212"
Match 1 groups: "1-800-555-1212"
Match 1 groups: "(612) 555-1313"
"""

expected_3 = """\
amp & lt < gt > quot " apos '
amp &amp; lt &lt; gt &gt; quot " apos '\
"""

EXPECTED_4 = """split 1\nsplit 2\nsplit 3\n"""

EXPECTED_5 = "s://ex/a/c/d"

EXPECTED_6 = "true"

EXPECTED_7 = "false"

EXPECTED_8 = "a-b-c"

EXPECTED_9 = "10, 11, 12"

EXPECTED_10 = EXPECTED_5

EXPECTED_11 = "0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33"


def Test(tester):

    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sty], expected_1,
                          title="ft:search-re, simple REGEX")


    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=SHEET_2)
    test_harness.XsltTest(tester, source, [sty], expected_2,
                          title="ft:search-re, complex REGEX")


    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=SHEET_3)
    test_harness.XsltTest(tester, source, [sty], expected_3,
                          title="ft:escape-xml, text output")

    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=SHEET_4)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_4,
                          title="ft:split")

    source = test_harness.FileInfo(string=source_5)
    sty = test_harness.FileInfo(string=SHEET_5)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_5,
                          title="ft:base-uri")

    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=SHEET_6)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_6,
                          title="ft:ends-with")

    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=SHEET_7)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_7,
                          title="ft:if")

    source = test_harness.FileInfo(string=source_8)
    sty = test_harness.FileInfo(string=SHEET_8)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_8,
                          title="ft:join")

    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=SHEET_9)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_9,
                          title="ft:range")

    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=SHEET_10)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_10,
                          title="ft:resolve-url")

    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=SHEET_11)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_11,
                          title="ft:sha-hash")

    return

