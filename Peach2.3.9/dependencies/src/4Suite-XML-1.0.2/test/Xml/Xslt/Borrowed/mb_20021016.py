# Just some general recursion stress tests:
# 1. Ackermann's Function
# 2. Fibonacci Numbers

import sys
from Ft import MAX_PYTHON_RECURSION_DEPTH
sys.setrecursionlimit(MAX_PYTHON_RECURSION_DEPTH)

from Xml.Xslt import test_harness

source_1 = """<dummy/>"""

sty_1 = """<?xml version="1.0" encoding="utf-8"?>
<!--

  Ackermann's function
  http://pweb.netcom.com/~hjsmith/Ackerman/AckeWhat.html

  1. If x = 0 then  A(x, y) = y + 1
  2. If y = 0 then  A(x, y) = A(x-1, 1)
  3. Otherwise,     A(x, y) = A(x-1, A(x, y-1))

  A(3,4) = 125
  A(3,5) = 253
  A(3,6) = 509; template called 172233 times, nested up to 511 calls deep
  A(3,7) will call the template 693964 times (good luck)

-->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="text" indent="no"/>

  <xsl:param name="x" select="3"/>
  <xsl:param name="y" select="6"/>

  <xsl:template match="/">
    <xsl:value-of select="concat('A(',$x,',',$y,') = ')"/>
    <xsl:variable name="c" select="0"/>
    <xsl:call-template name="A">
      <xsl:with-param name="x" select="$x"/>
      <xsl:with-param name="y" select="$y"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="A">
    <xsl:param name="x" select="0"/>
    <xsl:param name="y" select="0"/>
    <xsl:choose>
      <xsl:when test="$x = 0">
        <xsl:value-of select="$y + 1"/>
      </xsl:when>
      <xsl:when test="$y = 0">
        <xsl:call-template name="A">
          <xsl:with-param name="x" select="$x - 1"/>
          <xsl:with-param name="y" select="1"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="A">
          <xsl:with-param name="x" select="$x - 1"/>
          <xsl:with-param name="y">
            <xsl:call-template name="A">
              <xsl:with-param name="x" select="$x"/>
              <xsl:with-param name="y" select="$y - 1"/>
            </xsl:call-template>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>"""

expected_1 = """A(3,4) = 125"""

sty_2 = """<?xml version="1.0" encoding="utf-8"?>
<!--

  Fibonacci Numbers

  if n = 0, f(n) = 0
  if n = 1, f(n) = 1
  otherwise, f(n) = f(n-2) + f(n-1)

  tail-recursive version based on Scheme code by
  Ben Gum and John David Stone, at
  http://www.math.grin.edu/~gum/courses/151/readings/tail-recursion.xhtml
        
-->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="text" indent="no"/>

  <xsl:param name="n" select="100"/>

  <xsl:template match="/">
    <xsl:value-of select="concat('f(',$n,') = ')"/>
    <xsl:call-template name="fibo">
      <xsl:with-param name="n" select="$n"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="fibo">
    <xsl:param name="n" select="0"/>
    <xsl:call-template name="fibo-guts">
      <xsl:with-param name="current" select="0"/>
      <xsl:with-param name="next" select="1"/>
      <xsl:with-param name="remaining" select="$n"/>
    </xsl:call-template>
  </xsl:template>
    
  <xsl:template name="fibo-guts">
    <xsl:param name="current" select="0"/>
    <xsl:param name="next" select="0"/>
    <xsl:param name="remaining" select="0"/>
    <xsl:choose>
      <xsl:when test="$remaining = 0">
        <xsl:value-of select="$current"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="fibo-guts">
          <xsl:with-param name="current" select="$next"/>
          <xsl:with-param name="next" select="$current + $next"/>
          <xsl:with-param name="remaining" select="$remaining - 1"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>"""

expected_2 = "f(100) = 354224848179261997056"

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sty_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          topLevelParams={'x': 3, 'y': 4},
                          title="Ackermann's Function")

    sheet = test_harness.FileInfo(string=sty_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title="Fibonacci Numbers")
    return
