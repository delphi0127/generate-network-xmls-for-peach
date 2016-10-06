"""
Behavior of node copy to result tree
"""

from Xml.Xslt import test_harness


SOURCE_1="""<?xml version="1.0" encoding="UTF-8"?>
<books>
    <book id="1">
        <title>Code Generation in Action</title>
        <author><first>Jack</first><last>Herrington</last></author>
        <publisher>Manning</publisher>
    </book>
    <book id="2">
        <title>PHP Hacks</title>
        <author><first>Jack</first><last>Herrington</last></author>
        <publisher>O'Reilly</publisher>
    </book>
    <book id="3">
        <title>Podcasting Hacks</title>
        <author><first>Jack</first><last>Herrington</last></author>
        <publisher>O'Reilly</publisher>
    </book>
</books>
"""


SHEET_1 = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
    xmlns:func="http://exslt.org/functions"
    xmlns:str="http://exslt.org/strings"
    xmlns:js="http://muttmansion.com"
    extension-element-prefixes="func">
    
  <xsl:output method="text" />

  <func:function name="js:escape">
    <xsl:param name="text"/>
    <func:result select='str:replace($text, "&apos;", "\&apos;")'/>
  </func:function>

  <xsl:template match="/">
var g_books = [
<xsl:apply-templates/>
];
  </xsl:template>

  <xsl:template match="book">
<xsl:if test="position() > 1">,</xsl:if> {
id: <xsl:value-of select="@id" />,
name: '<xsl:value-of select="js:escape(title)"/>',
first: '<xsl:value-of select="js:escape(author/first)"/>',
last: '<xsl:value-of select="js:escape(author/last)"/>',
publisher: '<xsl:value-of select="js:escape(publisher)"/>'
}
  </xsl:template>

</xsl:transform>
"""


SHEET_2 = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
    xmlns:func="http://exslt.org/functions"
    xmlns:regex="http://exslt.org/regular-expressions"
    xmlns:js="http://muttmansion.com"
    extension-element-prefixes="func">
    
  <xsl:output method="text" />

  <func:function name="js:escape">
    <xsl:param name="text"/>
    <func:result select='regex:replace($text, "&apos;", "g", "\&apos;")'/>
  </func:function>

  <xsl:template match="/">
var g_books = [
<xsl:apply-templates/>
];
  </xsl:template>

  <xsl:template match="book">
<xsl:if test="position() > 1">,</xsl:if> {
id: <xsl:value-of select="@id" />,
name: '<xsl:value-of select="js:escape(title)"/>',
first: '<xsl:value-of select="js:escape(author/first)"/>',
last: '<xsl:value-of select="js:escape(author/last)"/>',
publisher: '<xsl:value-of select="js:escape(publisher)"/>'
}
  </xsl:template>

</xsl:transform>
"""


EXPECTED_1 = "\nvar g_books = [\n\n    , {\nid: 1,\nname: 'Code Generation in Action',\nfirst: 'Jack',\nlast: 'Herrington',\npublisher: 'Manning'\n}\n  \n    , {\nid: 2,\nname: 'PHP Hacks',\nfirst: 'Jack',\nlast: 'Herrington',\npublisher: 'O\\'Reilly'\n}\n  \n    , {\nid: 3,\nname: 'Podcasting Hacks',\nfirst: 'Jack',\nlast: 'Herrington',\npublisher: 'O\\'Reilly'\n}\n  \n\n];\n  "


def Test(tester):
    source = test_harness.FileInfo(string=SOURCE_1)
    sheet = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_1,
                          title="EXSLT str:replace within func:function")

    source = test_harness.FileInfo(string=SOURCE_1)
    sheet = test_harness.FileInfo(string=SHEET_2)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_1,
                          title="EXSLT regex:replace within func:function")
    return

