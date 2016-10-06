# At the time this test was developed, 4XSLT treated "ns1 != ns2" the same
# as "not(ns1 = ns2)" when evaluated in a predicate.
#
# The expected behavior is as follows:
#
# ns1 = ns2
#   true if any node in ns1 has the same string-value as any node in ns2
#
# ns1 != ns2
#   true if any node in ns1 has a different string-value than any node in ns2
#
# not(ns1 = ns2)
#   true if no node in ns1 has the same string-value as any node in ns2
#

from Xml.Xslt import test_harness

source_1 = """\
<?xml version="1.0" encoding="utf-8"?>
<foo>
  <set1>
    <x>hello</x>
    <x>world</x>
  </set1>
  <set2>
    <y>world</y>
    <y>bazaar</y>
  </set2>
  <set3>
    <z>totally</z>
    <z>different</z>
  </set3>
</foo>"""

sheet_1 = """\
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="/">

    <xsl:variable name="set1" select="/foo/set1/*"/>
    <xsl:variable name="set2" select="/foo/set2/*"/>
    <xsl:variable name="set3" select="/foo/set3/*"/>

    <result>

      <r><xsl:value-of select="concat('set1 = set1: ',$set1=$set1)"/></r>
      <r><xsl:value-of select="concat('set2 = set2: ',$set2=$set2)"/></r>
      <r><xsl:value-of select="concat('set3 = set3: ',$set3=$set3)"/></r>
      <r><xsl:value-of select="concat('set1 = set2: ',$set1=$set2)"/></r>
      <r><xsl:value-of select="concat('set1 = set3: ',$set1=$set3)"/></r>
      <r><xsl:value-of select="concat('set2 = set3: ',$set2=$set3)"/></r>
      <r><xsl:value-of select="concat('set1 != set1: ',$set1 != $set1)"/></r>
      <r><xsl:value-of select="concat('set2 != set2: ',$set2 != $set2)"/></r>
      <r><xsl:value-of select="concat('set3 != set3: ',$set3 != $set3)"/></r>
      <r><xsl:value-of select="concat('set1 != set2: ',$set1 != $set2)"/></r>
      <r><xsl:value-of select="concat('set1 != set3: ',$set1 != $set3)"/></r>
      <r><xsl:value-of select="concat('set2 != set3: ',$set2 != $set3)"/></r>
      <r><xsl:value-of select="concat('not(set1 = set1): ',not($set1 = $set1))"/></r>
      <r><xsl:value-of select="concat('not(set2 = set2): ',not($set2 = $set2))"/></r>
      <r><xsl:value-of select="concat('not(set3 = set3): ',not($set3 = $set3))"/></r>
      <r><xsl:value-of select="concat('not(set1 = set2): ',not($set1 = $set2))"/></r>
      <r><xsl:value-of select="concat('not(set1 = set3): ',not($set1 = $set3))"/></r>
      <r><xsl:value-of select="concat('not(set2 = set3): ',not($set2 = $set3))"/></r>

    </result>

  </xsl:template>
</xsl:stylesheet>"""

expected_1 = """\
<?xml version="1.0" encoding="utf-8"?>
<result>
  <r>set1 = set1: true</r>
  <r>set2 = set2: true</r>
  <r>set3 = set3: true</r>
  <r>set1 = set2: true</r>
  <r>set1 = set3: false</r>
  <r>set2 = set3: false</r>
  <r>set1 != set1: true</r>
  <r>set2 != set2: true</r>
  <r>set3 != set3: true</r>
  <r>set1 != set2: true</r>
  <r>set1 != set3: true</r>
  <r>set2 != set3: true</r>
  <r>not(set1 = set1): false</r>
  <r>not(set2 = set2): false</r>
  <r>not(set3 = set3): false</r>
  <r>not(set1 = set2): false</r>
  <r>not(set1 = set3): true</r>
  <r>not(set2 = set3): true</r>
</result>"""

sheet_2 = """\
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="/">

    <xsl:variable name="set1" select="/foo/set1"/>
    <xsl:variable name="set2" select="/foo/set2"/>
    <xsl:variable name="set3" select="/foo/set3"/>

    <result>

      <r><xsl:copy-of select="$set1/x[. != $set2/y]"/></r>
      <r><xsl:copy-of select="$set1/x[. != $set3/z]"/></r>
      <r><xsl:copy-of select="$set2/y[. != $set1/x]"/></r>
      <r><xsl:copy-of select="$set2/y[. != $set3/z]"/></r>
      <r><xsl:copy-of select="$set3/z[. != $set1/x]"/></r>
      <r><xsl:copy-of select="$set3/z[. != $set2/y]"/></r>

    </result>

  </xsl:template>
</xsl:stylesheet>"""

expected_2 = """\
<?xml version="1.0" encoding="utf-8"?>
<result>
  <r>
    <x>hello</x>
    <x>world</x>
  </r>
  <r>
    <x>hello</x>
    <x>world</x>
  </r>
  <r>
    <y>world</y>
    <y>bazaar</y>
  </r>
  <r>
    <y>world</y>
    <y>bazaar</y>
  </r>
  <r>
    <z>totally</z>
    <z>different</z>
  </r>
  <r>
    <z>totally</z>
    <z>different</z>
  </r>
</result>"""

sheet_3 = """\
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="/">

    <xsl:variable name="set1" select="/foo/set1"/>
    <xsl:variable name="set2" select="/foo/set2"/>
    <xsl:variable name="set3" select="/foo/set3"/>

    <result>

      <r><xsl:copy-of select="$set1/x[not(. = $set2/y)]"/></r>
      <r><xsl:copy-of select="$set1/x[not(. = $set3/z)]"/></r>
      <r><xsl:copy-of select="$set2/y[not(. = $set1/x)]"/></r>
      <r><xsl:copy-of select="$set2/y[not(. = $set3/z)]"/></r>
      <r><xsl:copy-of select="$set3/z[not(. = $set1/x)]"/></r>
      <r><xsl:copy-of select="$set3/z[not(. = $set2/y)]"/></r>

    </result>

  </xsl:template>
</xsl:stylesheet>"""

expected_3 = """\
<?xml version="1.0" encoding="utf-8"?>
<result>
  <r>
    <x>hello</x>
  </r>
  <r>
    <x>hello</x>
    <x>world</x>
  </r>
  <r>
    <y>bazaar</y>
  </r>
  <r>
    <y>world</y>
    <y>bazaar</y>
  </r>
  <r>
    <z>totally</z>
    <z>different</z>
  </r>
  <r>
    <z>totally</z>
    <z>different</z>
  </r>
</result>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    xtest = test_harness.XsltTest(tester, source, [sheet], expected_1,
                                  title='Case 1')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                                  title='Case 2')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                                  title='Case 3')
    return
