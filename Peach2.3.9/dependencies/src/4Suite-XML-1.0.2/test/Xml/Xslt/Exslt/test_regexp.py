########################################################################
# $Header: /var/local/cvsroot/4Suite/test/Xml/Xslt/Exslt/test_regexp.py,v 1.2 2005/12/28 02:38:18 jkloth Exp $
"""Tests for EXSLT Regular Expressions"""

from Xml.Xslt import test_harness

SOURCE = """<?xml version='1.0'?>
<doc>Is this EXSLT? No. no</doc>
"""

TESTS = []

# regexp:match()
def test_Match(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:regexp="http://exslt.org/regular-expressions"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:for-each select="regexp:match('http://www.bayes.co.uk/xml/index.xml', 
                                       '(\w+):\/\/([^/:]+)(:\d*)?([^# ]*)')">
      <xsl:text>Part </xsl:text>
      <xsl:value-of select="position()"/> = <xsl:value-of select="."/>
      <xsl:text>&#10;</xsl:text>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = """\
Part 1 = http://www.bayes.co.uk/xml/index.xml
Part 2 = http
Part 3 = www.bayes.co.uk
Part 4 =\x20
Part 5 = /xml/index.xml
"""
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='regexp:match() non-global match')

    # global match
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:regexp="http://exslt.org/regular-expressions"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:for-each select="regexp:match('This is a test string', '(\w+)', 'g')">
      <xsl:text>Part </xsl:text>
      <xsl:value-of select="position()"/> = <xsl:value-of select="."/>
      <xsl:text>&#10;</xsl:text>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = """\
Part 1 = This
Part 2 = is
Part 3 = a
Part 4 = test
Part 5 = string
"""
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='regexp:match() global')

    # global, case-insensitive match
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:regexp="http://exslt.org/regular-expressions"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:for-each select="regexp:match('This is a test string', '([a-z])+',
                                       'gi')">
      <xsl:text>Part </xsl:text>
      <xsl:value-of select="position()"/> = <xsl:value-of select="."/>
      <xsl:text>&#10;</xsl:text>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = """\
Part 1 = This
Part 2 = is
Part 3 = a
Part 4 = test
Part 5 = string
"""
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='regexp:match() global, case-insensitive')
    return
TESTS.append(test_Match)


# regexp:replace()
def test_Replace(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:regexp="http://exslt.org/regular-expressions"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="regexp:replace(., 'no', 'g', 'yes!!!')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "Is this EXSLT? No. yes!!!"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='regexp:replace() global')

    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:regexp="http://exslt.org/regular-expressions"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="regexp:replace(., 'no', 'gi', 'yes!!!')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "Is this EXSLT? yes!!!. yes!!!"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='regexp:replace() global, case-insensitive')
    return
TESTS.append(test_Replace)


# regexp:test()
def test_Test(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:regexp="http://exslt.org/regular-expressions"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="regexp:test(., 'no', 'g')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "true"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='regexp:test() global')

    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:regexp="http://exslt.org/regular-expressions"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="regexp:test(., 'exslt', 'gi')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "true"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='regexp:test() global, case-insensitive')
    return
TESTS.append(test_Test)


def Test(tester):
    tester.startGroup('Regular Expressions')
    for test in TESTS:
        test(tester)
    tester.groupDone()
    return
