########################################################################
# $Header: /var/local/cvsroot/4Suite/test/Xml/Xslt/Exslt/test_sets.py,v 1.2 2005/02/14 21:45:02 jkloth Exp $
"""Tests for EXSLT Sets"""

from Xml.Xslt import test_harness

SOURCE = "<dummy/>"

TESTS = []

# set:difference()
def test_Difference(tester):
    sty = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:set="http://exslt.org/sets"
  xmlns:x="http://uche.ogbuji.net/dummy"
  version="1.0"
>

  <xsl:output method="text"/>

  <x:spam/>
  <x:eggs/>

  <xsl:variable name='self' select="document('')/*"/>

  <xsl:template match="/">
    <xsl:variable name='result' select='set:difference($self/x:*, $self/x:spam)'/>
    <xsl:value-of select='count($result)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='name($result)'/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "1 x:eggs"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='set:difference()')
    return
TESTS.append(test_Difference)


# set:distinct()
def test_Distinct(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:set="http://exslt.org/sets"
  xmlns:x="http://uche.ogbuji.net/dummy"
  version="1.0"
>

  <xsl:output method="text"/>

  <x:node pos='1'>spam</x:node>
  <x:node pos='2'>eggs</x:node>
  <x:node pos='3'>spam</x:node>

  <xsl:variable name='self' select='document("")/*'/>

  <xsl:template match="/">
    <xsl:variable name='result' select='set:distinct($self/x:*)'/>
    <xsl:value-of select='count($result)'/>
    <xsl:for-each select='$result'>
      <xsl:text> </xsl:text>
      <xsl:value-of select='@pos'/>
      <xsl:value-of select='text()'/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "2 1spam 2eggs"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='set:distinct()')
    return
TESTS.append(test_Distinct)


# set:has-same-node()
def test_HasSameNode(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:set="http://exslt.org/sets"
  xmlns:x="http://uche.ogbuji.net/dummy"
  version="1.0"
>

  <xsl:output method="text"/>

  <x:spam/>
  <x:eggs/>

  <xsl:variable name='self' select='document("")/*'/>
  <xsl:variable name='empty' select='/parent::*'/>

  <xsl:template match="/">
    <xsl:variable name='r1' select='set:has-same-node($self/x:*, $self/x:spam)'/>
    <xsl:choose>
      <xsl:when test='$r1'>
        <xsl:text>works</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>broken</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text> </xsl:text>
    <xsl:variable name='r2' select='set:has-same-node($self/x:*, $empty)'/>
    <xsl:choose>
      <xsl:when test='$r2'>
        <xsl:text>broken</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>works</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "works works"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='set:has-same-node()')
    return
TESTS.append(test_HasSameNode)


# set:intersection()
def test_Intersection(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:set="http://exslt.org/sets"
  xmlns:x="http://uche.ogbuji.net/dummy"
  version="1.0"
>

  <xsl:output method="text"/>

  <x:spam/>
  <x:eggs/>

  <xsl:variable name='self' select='document("")/*'/>
  <xsl:variable name='empty' select='/parent::*'/>

  <xsl:template match="/">
    <xsl:variable name='result' select='set:intersection($self/x:*, $self/x:spam)'/>
    <xsl:value-of select='count($result)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='name($result)'/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "1 x:spam"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='set:intersection()')
    return
TESTS.append(test_Intersection)


# set:leading()
def test_Leading(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:set="http://exslt.org/sets"
  xmlns:x="http://uche.ogbuji.net/dummy"
  version="1.0"
>

  <xsl:output method="text"/>

  <x:spam/>
  <x:eggs/>
  <x:bread/>
  <x:eggs/>
  <x:spam/>

  <xsl:variable name='self' select='document("")/*'/>

  <xsl:template match="/">
  <xsl:variable name='result' select='set:leading($self/x:*, "name()=&apos;x:bread&apos;")'/>
    <xsl:value-of select='count($result)'/>
    <xsl:for-each select='$result'>
      <xsl:text> </xsl:text>
      <xsl:value-of select='name()'/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "0"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='set:leading()')
    return
TESTS.append(test_Leading)


# set:trailing()
def test_Trailing(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:set="http://exslt.org/sets"
  xmlns:x="http://uche.ogbuji.net/dummy"
  version="1.0"
>

  <xsl:output method="text"/>

  <x:spam/>
  <x:eggs/>
  <x:bread/>
  <x:eggs/>
  <x:spam/>

  <xsl:variable name='self' select='document("")/*'/>

  <xsl:template match="/">
  <xsl:variable name='result' select='set:trailing($self/x:*, "name()=&apos;x:bread&apos;")'/>
    <xsl:value-of select='count($result)'/>
    <xsl:for-each select='$result'>
      <xsl:text> </xsl:text>
      <xsl:value-of select='name()'/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "0"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='set:trailing()')
    return
TESTS.append(test_Trailing)


def Test(tester):
    tester.startGroup('Sets')
    for test in TESTS:
        test(tester)
    tester.groupDone()
    return
