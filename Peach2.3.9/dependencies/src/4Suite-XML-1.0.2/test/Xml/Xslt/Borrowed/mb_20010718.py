# Result tree fragments should have a root node. If you apply-templates to
# a fragment that has been converted to a node-set, the first template to
# fire should match the root node of the converted fragment. If there is
# no template matching this node, the built-in template, containing just
# xsl:apply-templates, will match. Parameters will not be passed from here.
#
# sheet_1 explicitly matches the root node of the fragment and mimics the
# behavior of the built-in template, but provides some extra output to
# indicate that it ran.
#
# sheet_2 lets the built-in template fire for the root node.
#
# In either case, the template that matches the children of the fragment's
# root node should not receive the parameter that was passed in the initial
# apply-templates.
#

from Xml.Xslt import test_harness

sheet_1 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exslt="http://exslt.org/common"
  exclude-result-prefixes="exslt">

  <xsl:output method="xml" indent="yes"/>

  <!--
    This template processes the root node of an arbitrary source tree
  -->
  <xsl:template match="/">

    <!-- a result tree fragment containing a root node and an element -->
    <xsl:variable name="myTree">
      <myElement/>
    </xsl:variable>

    <!--
      The output should be a myResult element that contains the result
      of processing the nodes in the $myTree fragment.
    -->
    <myResult>
      <xsl:apply-templates select="exslt:node-set($myTree)" mode="foo">
        <xsl:with-param name="myParameter" select="'hello world'"/>
      </xsl:apply-templates>
    </myResult>

  </xsl:template>

  <!-- This template processes the root node of the fragment -->
  <xsl:template match="/" mode="foo">
    <xsl:param name="myParameter"/>
    <note>
      <xsl:text>Processing the root node of the fragment. </xsl:text>
      <xsl:value-of select="$myParameter"/>
    </note>
    <xsl:apply-templates mode="foo"/> <!-- note we do not pass the parameter -->
  </xsl:template>

  <!-- This template processes the 'myElement' node of the fragment -->  
  <xsl:template match="myElement" mode="foo">
    <xsl:param name="myParameter"/>
    <note>
      <xsl:text>Processing the 'myElement' node of the fragment. </xsl:text>
      <xsl:value-of select="$myParameter"/>
    </note>
    <note>
      <xsl:text>This element has </xsl:text>
      <xsl:value-of select="count(ancestor::node())"/>
      <xsl:text> ancestor(s).</xsl:text>
    </note>
  </xsl:template>

</xsl:stylesheet>"""

expected_1 = """\
<?xml version='1.0' encoding='UTF-8'?>
<myResult>
  <note>Processing the root node of the fragment. hello world</note>
  <note>Processing the 'myElement' node of the fragment. </note>
  <note>This element has 1 ancestor(s).</note>
</myResult>"""

sheet_2 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exslt="http://exslt.org/common"
  exclude-result-prefixes="exslt">

  <xsl:output method="xml" indent="yes"/>

  <!--
    This template processes the root node of an arbitrary source tree
  -->
  <xsl:template match="/">

    <!-- a result tree fragment containing a root node and an element -->
    <xsl:variable name="myTree">
      <myElement/>
    </xsl:variable>

    <!--
      The output should be a myResult element that contains the result
      of processing the nodes in the $myTree fragment.
    -->
    <myResult>
      <xsl:apply-templates select="exslt:node-set($myTree)" mode="foo">
        <xsl:with-param name="myParameter" select="'hello world'"/>
      </xsl:apply-templates>
    </myResult>

  </xsl:template>

  <!-- This template processes the 'myElement' node of the fragment -->  
  <xsl:template match="myElement" mode="foo">
    <xsl:param name="myParameter"/>
    <note>
      <xsl:text>Processing the 'myElement' node of the fragment. </xsl:text>
      <xsl:value-of select="$myParameter"/>
    </note>
  </xsl:template>

</xsl:stylesheet>"""

expected_2 = """\
<?xml version='1.0' encoding='UTF-8'?>
<myResult>
  <note>Processing the 'myElement' node of the fragment. </note>
</myResult>"""


def Test(tester):
    source = test_harness.FileInfo(string=sheet_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='Case 1')

    source = test_harness.FileInfo(string=sheet_2)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='Case 2')
    return
