########################################################################
# $Header: /var/local/cvsroot/4Suite/test/Xml/Xslt/Exslt/test_dynamic.py,v 1.1.2.6 2006/10/30 22:43:22 mbrown Exp $
"""Tests for EXSLT Dynamic"""

from Xml.Xslt import test_harness

TESTS = []

SOURCE = """<doc><otu id='1'/><abuo id='2'/><ato id='3'/><ano id='4'/></doc>"""

# dyn:evaluate()
def test_evaluate1(tester):
    TRANSFORM = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dyn="http://exslt.org/dynamic"
  exclude-result-prefixes="dyn"
  version="1.0"
>

  <xsl:template match="doc">
    <result>
      <xsl:for-each select="*">
        <num>
          <xsl:value-of select="dyn:evaluate(concat('name(/doc/*[', position(), '])'))"/>
        </num>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:transform>
"""

    EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<result><num>otu</num><num>abuo</num><num>ato</num><num>ano</num></result>'

    source = test_harness.FileInfo(string=SOURCE)
    transform = test_harness.FileInfo(string=TRANSFORM)
    test_harness.XsltTest(tester, source, [transform], EXPECTED,
                          title='dyn:evaluate()')
    return

TESTS.append(test_evaluate1)

def test_evaluate2(tester):
    TRANSFORM = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dyn="http://exslt.org/dynamic"
  exclude-result-prefixes="dyn"
  version="1.0"
>

  <xsl:template match="doc">
    <result>
      <xsl:for-each select="*">
        <num>
          <xsl:value-of select="dyn:evaluate(/..)"/>
        </num>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:transform>
"""

    EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<result><num/><num/><num/><num/></result>'

    source = test_harness.FileInfo(string=SOURCE)
    transform = test_harness.FileInfo(string=TRANSFORM)
    test_harness.XsltTest(tester, source, [transform], EXPECTED,
                          title='dyn:evaluate() with invalid XPath expr')
    return

TESTS.append(test_evaluate2)


# dyn:map()
def test_map1(tester):
    TRANSFORM = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dyn="http://exslt.org/dynamic"
  exclude-result-prefixes="dyn"
  version="1.0"
>

  <xsl:template match="doc">
    <result>
      <xsl:for-each select="dyn:map(*, '@id')">
        <num>
          <xsl:value-of select="."/>
        </num>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:transform>
"""

    EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<result><num>1</num><num>2</num><num>3</num><num>4</num></result>'

    source = test_harness.FileInfo(string=SOURCE)
    transform = test_harness.FileInfo(string=TRANSFORM)
    test_harness.XsltTest(tester, source, [transform], EXPECTED,
                          title='dyn:map()')
    return

TESTS.append(test_map1)

SOURCE2 = """<doc><otu>1</otu><abuo>2</abuo><ato>3</ato><ano>4</ano></doc>"""


def test_map2(tester):

    TRANSFORM = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dyn="http://exslt.org/dynamic"
  exclude-result-prefixes="dyn"
  version="1.0"
>

  <xsl:template match="doc">
    <result>
      <xsl:for-each select="dyn:map(*, 'string(.)')">
        <num>
          <xsl:copy-of select="."/>
        </num>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:transform>
"""

    EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<result><num><exsl:string xmlns:exsl="http://exslt.org/common">1</exsl:string></num><num><exsl:string xmlns:exsl="http://exslt.org/common">2</exsl:string></num><num><exsl:string xmlns:exsl="http://exslt.org/common">3</exsl:string></num><num><exsl:string xmlns:exsl="http://exslt.org/common">4</exsl:string></num></result>'

    source = test_harness.FileInfo(string=SOURCE2)
    transform = test_harness.FileInfo(string=TRANSFORM)
    test_harness.XsltTest(tester, source, [transform], EXPECTED,
                          title='dyn:map() w/string expr')
    return

TESTS.append(test_map2)


def test_map3(tester):

    TRANSFORM = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dyn="http://exslt.org/dynamic"
  exclude-result-prefixes="dyn"
  version="1.0"
>

  <xsl:template match="doc">
    <result>
      <xsl:for-each select="dyn:map(*, 'number(.)')">
        <num>
          <xsl:copy-of select="."/>
        </num>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:transform>
"""

    EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<result><num><exsl:number xmlns:exsl="http://exslt.org/common">1</exsl:number></num><num><exsl:number xmlns:exsl="http://exslt.org/common">2</exsl:number></num><num><exsl:number xmlns:exsl="http://exslt.org/common">3</exsl:number></num><num><exsl:number xmlns:exsl="http://exslt.org/common">4</exsl:number></num></result>'

    source = test_harness.FileInfo(string=SOURCE2)
    transform = test_harness.FileInfo(string=TRANSFORM)
    test_harness.XsltTest(tester, source, [transform], EXPECTED,
                          title='dyn:map() w/numeric expr')
    return

TESTS.append(test_map3)

def test_map4(tester):

    TRANSFORM = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dyn="http://exslt.org/dynamic"
  exclude-result-prefixes="dyn"
  version="1.0"
>

  <xsl:template match="doc">
    <result>
      <xsl:for-each select="dyn:map(*, '. > 2')">
        <num>
          <xsl:copy-of select="."/>
        </num>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:transform>
"""

    EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<result><num><exsl:boolean xmlns:exsl="http://exslt.org/common"/></num><num><exsl:boolean xmlns:exsl="http://exslt.org/common"/></num><num><exsl:boolean xmlns:exsl="http://exslt.org/common">true</exsl:boolean></num><num><exsl:boolean xmlns:exsl="http://exslt.org/common">true</exsl:boolean></num></result>'

    source = test_harness.FileInfo(string=SOURCE2)
    transform = test_harness.FileInfo(string=TRANSFORM)
    test_harness.XsltTest(tester, source, [transform], EXPECTED,
                          title='dyn:map() w/boolean expr')
    return

TESTS.append(test_map4)


def test_map5(tester):

    INVALID_EXPRS = ['', '%', 'not()']

    TRANSFORM = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dyn="http://exslt.org/dynamic"
  exclude-result-prefixes="dyn"
  version="1.0"
>

  <xsl:template match="doc">
    <result>
      <xsl:for-each select="dyn:map(*, '%s')">
        <num>
          <xsl:copy-of select="."/>
        </num>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:transform>
"""

    EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<result/>'

    for invalid_expr in INVALID_EXPRS:
        source = test_harness.FileInfo(string=SOURCE2)
        transform = test_harness.FileInfo(string=TRANSFORM % invalid_expr)
        test_harness.XsltTest(tester, source, [transform], EXPECTED,
                              title="dyn:map() w/invalid expr %r" % invalid_expr)
    return

TESTS.append(test_map5)


def test_map6(tester):
    MAP6_SRC = """<?xml version="1.0" encoding="UTF-8"?>
<foo>
  <minutes_to_override>
    <duration>0</duration>
    <duration>15</duration>
    <duration>30</duration>
  </minutes_to_override>
  <comma>,</comma>
</foo>"""

    TRANSFORM = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dynamic="http://exslt.org/dynamic"
  exclude-result-prefixes="dynamic">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <xsl:variable name="data" select="/foo/minutes_to_override/duration"/>
    <r><xsl:value-of select="dynamic:map($data, 'concat(., substring( /foo/comma, 1 div (position()!=last()) ))')"/></r>
  </xsl:template>

</xsl:stylesheet>"""

    EXPECTED = """<?xml version="1.0" encoding="UTF-8"?>
<r>0,15,30</r>"""

    source = test_harness.FileInfo(string=MAP6_SRC)
    transform = test_harness.FileInfo(string=TRANSFORM)
    test_harness.XsltTest(tester, source, [transform], EXPECTED,
                          title="dyn:map() w/var and nested func")
    return

TESTS.append(test_map6)


# dyn:closure()
#FIXME: Not a very good test: exercises closure logic, but not dynamic expression evaluation
def test_closure(tester):
    TRANSFORM = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dyn="http://exslt.org/dynamic"
  exclude-result-prefixes="dyn"
  version="1.0"
>

  <xsl:template match="doc">
    <result>
      <xsl:for-each select="dyn:closure(*, '*[@x]')">
        <node>
          <xsl:value-of select="@x"/>
        </node>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:transform>
"""

    SOURCE2 = """<doc><a x='1'><e x='2'/></a><b x='3'><f/></b><c><g x='4'/></c><d x='5'><h x='6'/></d></doc>"""

    EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<result><node>2</node><node>4</node><node>6</node></result>'

    source = test_harness.FileInfo(string=SOURCE2)
    transform = test_harness.FileInfo(string=TRANSFORM)
    test_harness.XsltTest(tester, source, [transform], EXPECTED,
                          title='dyn:closure()')
    return

TESTS.append(test_closure)
    

def Test(tester):
    tester.startGroup('EXSLT Dynamic module')
    for test in TESTS:
        test(tester)
    tester.groupDone()
    return

