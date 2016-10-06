########################################################################
# $Header: /var/local/cvsroot/4Suite/test/Xml/Xslt/Exslt/test_functions.py,v 1.1.4.1 2006/12/17 01:17:36 uogbuji Exp $
"""Tests for EXSLT Functions"""

from Xml.Xslt import test_harness

SOURCE_1 = """<?xml version="1.0"?><foo/>"""

SHEET_1 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:myns="http://stuff.foo"
  xmlns:func="http://exslt.org/functions"
  extension-element-prefixes="func"
  exclude-result-prefixes="myns">

  <xsl:output method="xml"/>

  <func:function name="myns:toUpperCase">
    <xsl:param name="stringToConvert"/>
    <func:result select="translate($stringToConvert,
                         'abcdefghijklmnopqrstuvwxyz',
                         'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>
  </func:function>

  <xsl:template match="/">
    <result><xsl:value-of select="myns:toUpperCase('Hello World')"/></result>
  </xsl:template>

</xsl:stylesheet>"""

EXPECTED_1 = """<?xml version="1.0" encoding="UTF-8"?>
<result>HELLO WORLD</result>"""

SHEET_2 = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:x="http://uche.ogbuji.net/dummy"
  xmlns:func="http://exslt.org/functions"
  extension-element-prefixes="func"
  version="1.0"
>

  <func:function name="x:count-elements">
    <xsl:for-each select="(//*)[1]">
      <func:result select="count(//*)" />
    </xsl:for-each>
  </func:function>

  <xsl:template match="/">
    <out>
      <xsl:value-of select="x:count-elements()" />
    </out>
  </xsl:template>

</xsl:stylesheet>
"""

SOURCE_2 = """\
<doc>
                              <section index="section1"
                                       index2="atr2val">
                                 <section index="subSection1.1">
                                    <p>Hello</p>
                                    <p>Hello again.</p>
                                 </section>
                              </section>
                              <section index="section2">
                                 <p>Hello2</p>
                                 <section index="subSection2.1">
                                    <p>Hello</p>
                                    <p>Hello again.</p>
                                 </section>
                                 <section index="subSection2.2">
                                    <p>Hello</p>
                                    <p>Hello again.</p>
                                 </section>
                                 <p>Hello2 again.</p>
                                 <section index="subSection2.3">
                                    <p>Hello</p>
                                    <p>Hello again.</p>
                                 </section>
                              </section>
                           </doc>
                           """
EXPECTED_2 = """<?xml version="1.0" encoding="UTF-8"?>
<out xmlns:x="http://uche.ogbuji.net/dummy">17</out>"""

# SF #707131
SOURCE_3 = "<?xml version='1.0'?><test>echo me</test>"

SHEET_3 = """<?xml version='1.0'?>
<xsl:transform version='1.0'
  xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
  xmlns:a='http://a' xmlns:b='http://b'
  exclude-result-prefixes='a b'>

  <xsl:include href='Xml/Xslt/Core/function-problem-a.xslt'/>
  <xsl:include href='Xml/Xslt/Core/function-problem-b.xslt'/>

  <xsl:template match='/'>
    <result>
      <xsl:value-of select='b:b-echo(a:a-echo(.))'/>
    </result>
  </xsl:template>
</xsl:transform>
"""

EXPECTED_3 = """<?xml version="1.0" encoding="UTF-8"?>
<result>echo me</result>"""


SOURCE_4 = """<doc><one/><two/></doc>"""

SHEET_4 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:transform version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:myns="http://stuff.foo"
  xmlns:exsl="http://exslt.org/common"
  xmlns:func="http://exslt.org/functions"
  xmlns:dyn="http://exslt.org/dynamic"
  extension-element-prefixes="func"
  exclude-result-prefixes="exsl dyn myns">

  <xsl:output method="xml"/>

  <func:function name="myns:toUpperCase">
    <xsl:param name="stringToConvert"/>
    <func:result select="translate($stringToConvert,
                         'abcdefghijklmnopqrstuvwxyz',
                         'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>
  </func:function>

  <xsl:template match="doc">
    <result>
      <xsl:apply-templates select="dyn:map(*, 'myns:toUpperCase(name())')"/>
    </result>
  </xsl:template>

  <xsl:template match="exsl:*">
    <xsl:element name='{local-name()}'>
      <xsl:value-of select="."/>
    </xsl:element>
  </xsl:template>

</xsl:transform>
"""

EXPECTED_4 = """<?xml version="1.0" encoding="UTF-8"?>
<result><string>ONE</string><string>TWO</string></result>"""


def Test(tester):
    tester.startGroup('Functions')

    source = test_harness.FileInfo(string=SOURCE_1)
    sheet = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_1,
                          title='test 1')

    source = test_harness.FileInfo(string=SOURCE_2)
    sheet = test_harness.FileInfo(string=SHEET_2)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_2,
                          title='test 2')

    source = test_harness.FileInfo(string=SOURCE_3)
    sheet = test_harness.FileInfo(string=SHEET_3)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_3,
                          title='test 3')

    source = test_harness.FileInfo(string=SOURCE_4)
    sheet = test_harness.FileInfo(string=SHEET_4)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_4,
                          title='func:function invoked from dynamic function')

    tester.groupDone()
    return

