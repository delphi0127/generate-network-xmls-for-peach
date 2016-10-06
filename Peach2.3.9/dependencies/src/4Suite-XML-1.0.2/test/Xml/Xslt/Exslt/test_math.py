########################################################################
# $Header: /var/local/cvsroot/4Suite/test/Xml/Xslt/Exslt/test_math.py,v 1.3 2005/12/28 02:38:18 jkloth Exp $
"""Tests for EXSLT Math"""

from Xml.Xslt import test_harness

SOURCE = """<?xml version='1.0'?>
<x:items xmlns:x='http://uche.ogbuji.net/dummy'>
  <x:spam>2</x:spam>
  <x:eggs>12.0</x:eggs>
  <x:bread>100</x:bread>
</x:items>
"""

TESTS = []

# math:max()
def test_Max(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  xmlns:common="http://exslt.org/common"
  xmlns:x="http://uche.ogbuji.net/dummy"
  version="1.0"
>

  <xsl:output method="text"/>

  <x:spam>2</x:spam>
  <x:eggs>12.0</x:eggs>
  <x:bread>100</x:bread>

  <xsl:variable name='self' select='document("")/*'/>

  <xsl:template match="/">
    <xsl:variable name='result' select='math:max($self/x:*)'/>
    <xsl:value-of select='common:object-type($result)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='$result'/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "number 100"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:max()')
    return
TESTS.append(test_Max)


# math:min()
def test_Min(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  xmlns:common="http://exslt.org/common"
  xmlns:x="http://uche.ogbuji.net/dummy"
  version="1.0"
>

  <xsl:output method="text"/>

  <x:spam>2</x:spam>
  <x:eggs>12.0</x:eggs>
  <x:bread>100</x:bread>

  <xsl:variable name='self' select='document("")/*'/>

  <xsl:template match="/">
    <xsl:variable name='result' select='math:min($self/x:*)'/>
    <xsl:value-of select='common:object-type($result)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='$result'/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "number 2"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:min()')
    return
TESTS.append(test_Min)


# math:highest()
def test_Highest(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  xmlns:common="http://exslt.org/common"
  xmlns:x="http://uche.ogbuji.net/dummy"
  version="1.0"
>

  <xsl:output method="text"/>

  <x:spam>2</x:spam>
  <x:bread>100</x:bread>
  <x:eggs>12.0</x:eggs>

  <xsl:variable name='self' select='document("")/*'/>

  <xsl:template match="/">
    <xsl:variable name='result' select='math:highest($self/x:*)'/>
    <xsl:value-of select='name($result)'/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "x:bread"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:highest()')
    return
TESTS.append(test_Highest)


# math:lowest()
def test_Lowest(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  xmlns:common="http://exslt.org/common"
  xmlns:x="http://uche.ogbuji.net/dummy"
  version="1.0"
>

  <xsl:output method="text"/>

  <x:spam>2</x:spam>
  <x:bread>100</x:bread>
  <x:eggs>12.0</x:eggs>

  <xsl:variable name='self' select='document("")/*'/>

  <xsl:template match="/">
    <xsl:variable name='result' select='math:lowest($self/x:*)'/>
    <xsl:value-of select='name($result)'/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "x:spam"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:lowest()')
    return
TESTS.append(test_Lowest)


# math:abs()
def test_Abs(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select='math:abs(1)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:abs(-1)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:abs(0)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:abs(-0)'/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "1 1 0 0"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:abs()')
    return
TESTS.append(test_Abs)


# math:sqrt()
def test_Sqrt(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select='math:sqrt(4)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:sqrt(-4)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:sqrt(1)'/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "2 0 1"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:sqrt()')
    return
TESTS.append(test_Sqrt)


# math:power()
def test_Power(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select='math:power(2, 2)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:power(2, -1)'/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "4 0.5"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:power()')
    return
TESTS.append(test_Power)


# math:constant()
def test_Constant(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select='math:constant("PI", 4)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:constant("E", 4)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:constant("SQRRT2", 4)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:constant("LN2", 4)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:constant("LN10", 4)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:constant("LOG2E", 4)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:constant("SQRT1_2", 4)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='math:constant("spam", 4)'/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "3.1416 2.7183 1.4142 0.6931 2.3026 1.4427 0.7071 NaN"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:constant()')
    return
TESTS.append(test_Constant)


# math:log()
def test_Log(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="format-number(math:log(2), '0.####')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:log(10), '0.####')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "0.6932 2.3026"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:log()')
    return
TESTS.append(test_Log)


# math:random()
def test_Random(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:variable name="n" select="math:random()"/>
    <xsl:value-of select='$n >= 0 and 1 > $n'/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "true"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:random()')
    return
TESTS.append(test_Random)


# math:sin()
def test_Sin(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:variable name='PI' select='math:constant("PI", 20)'/>
    <xsl:value-of select="format-number(math:sin(0), '#')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:sin($PI div 2), '#')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:sin($PI), '#')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:sin(-$PI div 2), '#')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "0 1 0 -1"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:sin()')
    return
TESTS.append(test_Sin)


# math:cos()
def test_Cos(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:variable name='PI' select='math:constant("PI", 20)'/>
    <xsl:value-of select="format-number(math:cos(0), '#')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:cos($PI div 2), '#')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:cos($PI), '#')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:cos(-$PI div 2), '#')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "1 0 -1 0"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:cos()')
    return
TESTS.append(test_Cos)


# math:tan()
def test_Tan(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:variable name='PI' select='math:constant("PI", 20)'/>
    <xsl:value-of select="format-number(math:tan(0), '#')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:tan($PI div 4), '#')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:tan(-$PI div 4), '#')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "0 1 -1"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:tan()')
    return
TESTS.append(test_Tan)


# math:asin()
def test_ASin(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:variable name='PI' select='math:constant("PI", 20)'/>
    <xsl:value-of select="format-number(math:asin(0), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:asin(1), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:asin(-1), '#.###')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "0 1.571 -1.571"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:asin()')
    return
TESTS.append(test_ASin)


# math:acos()
def test_ACos(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:variable name='PI' select='math:constant("PI", 20)'/>
    <xsl:value-of select="format-number(math:acos(0), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:acos(-1), '#.###')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "1.571 3.142"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:acos()')
    return
TESTS.append(test_ACos)


# math:atan()
def test_ATan(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="format-number(math:atan(0), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:atan(1), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:atan(-1), '#.###')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "0 0.785 -0.785"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:atan()')
    return
TESTS.append(test_ATan)


# math:atan2()
def test_ATan2(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="format-number(math:atan2(0.5, 0.5), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:atan2(-0.5, -0.5), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:atan2(5, 5), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:atan2(10, 20), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:atan2(-5, -5), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:atan2(-10, 10), '#.###')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "0.785 -2.356 0.785 0.464 -2.356 -0.785"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:atan2()')
    return
TESTS.append(test_ATan2)


# math:exp()
def test_Exp(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://exslt.org/math"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:value-of select="format-number(math:exp(1), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:exp(-1), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:exp(5), '#.###')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="format-number(math:exp(10), '#.###')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "2.718 0.368 148.413 22026.466"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='math:exp()')
    return
TESTS.append(test_Exp)


def Test(tester):
    tester.startGroup('Math')
    for test in TESTS:
        test(tester)
    tester.groupDone()
    return
