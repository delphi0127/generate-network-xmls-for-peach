# Prior to development of this test, 4XSLT was not properly determining the
# string-value for elements in a node-set that was generated from a result
# tree fragment with exslt:node-set. Only text node children of the elements
# were picked up; other text node descendants were not. This was fixed by a
# minor patch to Ft/Xslt/RtfWriter.py.

from Xml.Xslt import test_harness

source_1 = """\
<?xml version="1.0"?>
<foo/>"""

sheet_1 = """\
<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exslt="http://exslt.org/common"
>
  <xsl:output method="text"/>
  <xsl:variable name="tree">
    <x id="0">foo</x>
    <x id="1">foo<y/>bar</x>
    <x id="2">
      <y>hello world</y>
    </x>
    <x id="3">      <y/>
    </x>
    <x id="4">
      <y>
        <z>hrrmmmm</z>
      </y>
    </x>
  </xsl:variable>
  <xsl:variable name="all-non-empty-x" select="exslt:node-set($tree)/*[string()]"/>

  <xsl:template match="/">
    <xsl:for-each select="$all-non-empty-x">
      <xsl:text>current element: '</xsl:text>
      <xsl:value-of select="name()"/>
      <xsl:text>' with id '</xsl:text>
      <xsl:value-of select="@id"/>
      <xsl:text>'&#10;</xsl:text>
      <xsl:text>string-value: '</xsl:text>
      <xsl:value-of select="."/>
      <xsl:text>'&#10;--------------------&#10;</xsl:text>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>"""

expected_1 = """\
current element: 'x' with id '0'
string-value: 'foo'
--------------------
current element: 'x' with id '1'
string-value: 'foobar'
--------------------
current element: 'x' with id '2'
string-value: 'hello world'
--------------------
current element: 'x' with id '4'
string-value: 'hrrmmmm'
--------------------
"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title="string-value test on node-set from exslt:node-set()")
    return
