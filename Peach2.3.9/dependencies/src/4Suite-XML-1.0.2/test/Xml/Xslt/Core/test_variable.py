from Xml.Xslt import test_harness
from Ft.Xml.Xslt import XsltException, Error
from Ft.Xml.XPath import RuntimeException

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:n="http://spam.com"
  version="1.0"
>

  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE>Address Book</TITLE>
    </HEAD>
    <BODY>
    <TABLE><xsl:apply-templates/></TABLE>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:variable name='a'>1</xsl:variable>

  <xsl:variable name='width' select='100'></xsl:variable>

  <xsl:variable name='c'></xsl:variable>

  <xsl:template match="ENTRY">
        <!-- Make sure shadowing check isn't overzealous -->
        <xsl:param name='n:a' select='ok'/>
        <!-- Tests legal shadowing -->
        <xsl:variable name='a'>boo</xsl:variable>
        <xsl:element name='TR'>
        <xsl:apply-templates select='NAME'/>
        </xsl:element>
  </xsl:template>

  <xsl:template match="NAME">
    <xsl:variable name='d' select='.'></xsl:variable>
    <TD WIDTH='{$d}'>
      <B><xsl:apply-templates/></B>
    </TD>
  </xsl:template>

</xsl:stylesheet>
"""


sheet_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:param name='override' select='"abc"'/>
  <xsl:param name='list' select='foo'/>

  <xsl:template match="/">
    <doc>
      <overridden><xsl:value-of select='$override'/></overridden>
      <list><xsl:apply-templates select="$list"/></list>
    </doc>
  </xsl:template>

  <xsl:template match="text()">
    <item><xsl:value-of select="."/></item>
  </xsl:template>

</xsl:stylesheet>
"""


sheet_2a = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:x="urn:bogus:x"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

  <xsl:param name='x:override' select='"abc"'/>

  <xsl:template match="/">
      <overridden><xsl:value-of select='$x:override'/></overridden>
  </xsl:template>

</xsl:stylesheet>
"""


sheet_2b = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
xmlns:x="urn:bogus:x"
xmlns:y="urn:bogus:y"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

  <xsl:param name='x:override' select='"abc"'/>
  <xsl:param name='y:override' select='"abc"'/>

  <xsl:template match="/">
      <overridden1><xsl:value-of select='$x:override'/></overridden1>
      <overridden2><xsl:value-of select='$y:override'/></overridden2>
  </xsl:template>

</xsl:stylesheet>
"""


sheet_2c = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

  <xsl:param xmlns:x="urn:bogus:x" name='x:override' select='"abc"'/>
  <xsl:param xmlns:x="urn:bogus:xxx" name='x:override' select='"abc"'/>

  <xsl:template match="/">
    <overridden1><xsl:value-of xmlns:x="urn:bogus:x" select='$x:override'/></overridden1>
    <overridden2><xsl:value-of xmlns:x="urn:bogus:xxx" select='$x:override'/></overridden2>
  </xsl:template>

</xsl:stylesheet>
"""


sheet_3a = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:param name='a' select='"foo"'/>
  <xsl:variable name='b' select='concat($a, "bar")'/>

  <xsl:template match="/">
    <doc>
      <a><xsl:value-of select='$a'/></a>
      <b><xsl:value-of select='$b'/></b>
    </doc>
  </xsl:template>

</xsl:stylesheet>
"""


sheet_3b = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:param name='a' select='"foo"'/>
  <xsl:param name='b' select='concat($a, "bar")'/>

  <xsl:template match="/">
    <doc>
      <a><xsl:value-of select='$a'/></a>
      <b><xsl:value-of select='$b'/></b>
    </doc>
  </xsl:template>

</xsl:stylesheet>"""

sheet_3c = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:param name="color" select="'red'"/>
  <xsl:param name="type" select="'ink'"/>

  <xsl:param name="top-level-params">
    <p><xsl:value-of select="$color"/></p>
    <p><xsl:value-of select="$type"/></p>
  </xsl:param>

  <xsl:template match="/">
    <foo>
      <xsl:copy-of select="$top-level-params"/>
    </foo>
  </xsl:template>

</xsl:stylesheet>"""

sheet_3d = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:param name="color" select="'red'"/>
  <xsl:param name="type" select="'ink'"/>

  <xsl:variable name="top-level-params">
    <p><xsl:value-of select="$color"/></p>
    <p><xsl:value-of select="$type"/></p>
  </xsl:variable>

  <xsl:template match="/">
    <foo>
      <xsl:copy-of select="$top-level-params"/>
    </foo>
  </xsl:template>

</xsl:stylesheet>"""

sheet_4 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:param name='a' select='"foo"'/>
  <xsl:variable name='b'>
    <xsl:value-of select='$a'/>
  </xsl:variable>
  <xsl:variable name='c'>
    <x y='{$a}'/>
  </xsl:variable>
  <xsl:variable name='d'>
    <xsl:for-each select="/">
      <xsl:if test=".">
        <x y='{$a}'/>
      </xsl:if>
    </xsl:for-each>
  </xsl:variable>

  <xsl:template match="/">
    <doc>
      <a><xsl:value-of select='$a'/></a>
      <b><xsl:value-of select='$b'/></b>
      <c><xsl:copy-of select='$c'/></c>
      <d><xsl:copy-of select='$d'/></d>
    </doc>
  </xsl:template>

</xsl:stylesheet>
"""

sheet_5 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:template match="/">
    <xsl:variable name="a">
      <!-- OK because outer binding not yet visible -->
      <xsl:variable name="a" select="'foo'"/>
      <!-- inner binding now 'foo' -->
      <!-- now create value for outer binding -->
      <xsl:choose>
        <xsl:when test="$a = 'foo'">hello</xsl:when>
        <xsl:otherwise>world</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <!-- outer binding now visible; should be 'hello' -->
    <doc>
      <a><xsl:value-of select='$a'/></a>
    </doc>
  </xsl:template>

</xsl:stylesheet>
"""


#This is a global variable binding which depends on other global variable
#bindings by reference in an invoked template
sheet_6 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:variable name="a" select="1"/>

  <xsl:variable name="b">
    <a><xsl:value-of select='$a'/></a>
    <b>
      <xsl:apply-templates select='document("")/*/xsl:variable'/>
    </b>
  </xsl:variable>

  <xsl:template match="xsl:variable">
    <var>
      <a><xsl:value-of select='$a'/></a>
    </var>
  </xsl:template>

  <xsl:template match="/">
    <doc>
      <xsl:copy-of select='$b'/>
    </doc>
  </xsl:template>

</xsl:stylesheet>
"""


invalid_sheet_1 = """\
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:variable name='x' select='a'/>

  <xsl:template match="/">
    <xsl:variable name='x' select='b'/>
    <xsl:value-of select='$x'/>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="ENTRY">
    <xsl:variable name='x' select='c'/>
    <doc>
      <xsl:variable name='x' select='d'/>
      <xsl:value-of select='$x'/>
    </doc>
  </xsl:template>

</xsl:stylesheet>
"""


invalid_sheet_2 = """\
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:variable name='x' select='a'/>

  <xsl:template match="/">
    <xsl:variable name='x' select='b'/>
    <xsl:value-of select='$x'/>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="ENTRY">
    <xsl:variable name='x' select='c'/>
    <xsl:variable name='x' select='d'/>
    <doc>
      <xsl:value-of select='$x'/>
    </doc>
  </xsl:template>

</xsl:stylesheet>
"""


invalid_sheet_3 = """\
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:variable name='image-name' select='a'/>

  <xsl:template name="dummy">
    <xsl:param name="p1"/>
    <xsl:param name="p2" select="1"/>
    <xsl:variable name="image-name" select="''"/>
    <a href='{$image-name}'>
      <img height="24" width="32" border="0" src="{$image-name}.gif" name="{$image-name}"/>
    </a>
    <img height="24" width="32" border="0" src="{$image-name}.gif" name="{$image-name}"/>
    <xsl:variable name="image-name" select="'a'"/>
    <xsl:variable name="image-name" select="'b'"/>
    <img height="24" width="32" border="0" src="{$image-name}.gif" name="{$image-name}"/>
  </xsl:template>

</xsl:stylesheet>
"""

invalid_sheet_4 = """\
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:variable name='x' select='a'/>
  <xsl:variable name='x' select='b'/>

  <xsl:template match="/">
    <xsl:variable name='y' select='b'/>
    <xsl:value-of select='$x'/>
  </xsl:template>

</xsl:stylesheet>
"""


invalid_sheet_5 = """\
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:variable name='x' select='a'/>
  <xsl:param name='x' select='b'/>

  <xsl:template match="/">
    <xsl:variable name='y' select='b'/>
    <xsl:value-of select='$x'/>
  </xsl:template>

</xsl:stylesheet>
"""


invalid_sheet_6 = """\
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:param name='x' select='a'/>
  <xsl:param name='x' select='b'/>

  <xsl:template match="/">
    <xsl:variable name='y' select='b'/>
    <xsl:value-of select='$x'/>
  </xsl:template>

</xsl:stylesheet>
"""

invalid_sheet_7 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:template match="/">
    <!-- can't have both select and content -->
    <xsl:variable name="a" select="'hello'">world</xsl:variable>
    <doc>
      <a><xsl:value-of select='$a'/></a>
    </doc>
  </xsl:template>

</xsl:stylesheet>
"""

invalid_sheet_8 = """\
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:variable name='x' select='a'/>

  <xsl:template match="/">
    <xsl:variable name='x' select='b'/>
    <xsl:value-of select='$x'/>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template name="ENTRY">
    <xsl:variable name='x' select='c'/>
    <doc>
      <xsl:variable name='x' select='d'/>
      <xsl:value-of select='$x'/>
    </doc>
  </xsl:template>

</xsl:stylesheet>
"""

invalid_sheet_9 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:transform
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

<xsl:template match="/">
<xsl:variable name="invisible">Am I invisible?</xsl:variable>
<xsl:apply-templates select="." mode="another"/>
<xsl:call-template name="another"/>
</xsl:template>

<xsl:template match="*" mode="another">
apply-templates: <xsl:value-of select="$invisible"/>
</xsl:template>

<xsl:template name="another">
call-template: <xsl:value-of select="$invisible"/>
</xsl:template>

</xsl:transform>"""

# SourceForge bug #659626
invalid_sheet_10 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0">

  <xsl:variable name="foo">
    <xsl:call-template name="bar">
      <xsl:with-param name="path" select="'/a/b/c'"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:template match="/">
     foo: <xsl:value-of select="$foo"/>
    path: <xsl:value-of select="$path"/>
  </xsl:template>

  <xsl:template name="bar">
    <xsl:param name="path"/>
    <xsl:value-of select="translate($path,'abc','ABC')"/>
  </xsl:template>

</xsl:stylesheet>"""

# variation on previous
invalid_sheet_11 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0">

  <xsl:template match="/">
  <xsl:variable name="foo">
    <xsl:call-template name="bar">
      <xsl:with-param name="path" select="'/a/b/c'"/>
    </xsl:call-template>
  </xsl:variable>

     foo: <xsl:value-of select="$foo"/>
    path: <xsl:value-of select="$path"/>
  </xsl:template>

  <xsl:template name="bar">
    <xsl:param name="path"/>
    <xsl:value-of select="translate($path,'abc','ABC')"/>
  </xsl:template>

</xsl:stylesheet>"""


source_2 = """
<dummy/>
"""


expected_1 = """<HTML xmlns:n='http://spam.com'>
  <HEAD>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <TABLE>
      <TR>
        <TD WIDTH='Pieter Aaron'><B>Pieter Aaron</B></TD>
      </TR>
      <TR>
        <TD WIDTH='Emeka Ndubuisi'><B>Emeka Ndubuisi</B></TD>
      </TR>
      <TR>
        <TD WIDTH='Vasia Zhugenev'><B>Vasia Zhugenev</B></TD>
      </TR>
    </TABLE>
  </BODY>
</HTML>"""


expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<doc><overridden>xyz</overridden><list><item>a</item><item>b</item><item>c</item></list></doc>"""

expected_2a = """<?xml version="1.0" encoding="UTF-8"?>\n<overridden xmlns:x="urn:foo">xyz</overridden>"""

expected_2b = """<?xml version="1.0" encoding="UTF-8"?>\n<overridden1 xmlns:y="urn:bogus:y" xmlns:x="urn:bogus:x">xyz</overridden1><overridden2 xmlns:y="urn:bogus:y" xmlns:x="urn:bogus:x">abc</overridden2>"""

expected_2c = """<?xml version="1.0" encoding="UTF-8"?>\n<overridden1>xyz</overridden1><overridden2>abc</overridden2>"""

expected_3 = """<?xml version='1.0' encoding='UTF-8'?>
<doc><a>foo</a><b>foobar</b></doc>"""

expected_3c = """<?xml version='1.0' encoding='UTF-8'?>
<foo><p>red</p><p>ink</p></foo>"""

expected_3d = """<?xml version='1.0' encoding='UTF-8'?>
<foo><p>red</p><p>ink</p></foo>"""

expected_4 = """<?xml version='1.0' encoding='UTF-8'?>
<doc><a>foo</a><b>foo</b><c><x y='foo'/></c><d><x y='foo'/></d></doc>"""

expected_5 = """<?xml version='1.0' encoding='UTF-8'?>
<doc><a>hello</a></doc>"""

expected_6 = """<?xml version='1.0' encoding='UTF-8'?>
<doc><a>1</a><b><var><a>1</a></var><var><a>1</a></var></b></doc>"""


def Test(tester):

    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='Usage')


    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          topLevelParams={'override' : 'xyz',
                                          'list' : ['a', 'b', 'c']},
                          title="Top-level param override")


    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_2a)
    test_harness.XsltTest(tester, source, [sheet], expected_2a,
                          topLevelParams={'x:override' : 'xyz'},
                          title="Top-level param override using QName")


    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_2b)
    test_harness.XsltTest(tester, source, [sheet], expected_2b,
                          topLevelParams={'x:override' : 'xyz'},
                          title="Top-level param override using QName 2")


    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_2c)
    test_harness.XsltTest(tester, source, [sheet], expected_2c,
                          topLevelParams={('urn:bogus:x', u'override'): 'xyz'},
                          title="Top-level param override using QName with prefix ambiguity")


    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_3a)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title="Top-level variable depends on top-level param 1")


    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_3b)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title="Top-level param depends on top-level param 1")


    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_3c)
    test_harness.XsltTest(tester, source, [sheet], expected_3c,
                          title="Top-level param w/RTF depends on top-level param 1")


    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_3d)
    test_harness.XsltTest(tester, source, [sheet], expected_3d,
                          title="Top-level variable w/RTF depends on 2 top-level params 1")

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_4)
    test_harness.XsltTest(tester, source, [sheet], expected_4,
                          title="Top-level variable depends on top-level param 2")


    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_5)
    test_harness.XsltTest(tester, source, [sheet], expected_5,
                          title="Binding not visible until following sibling")


    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_6)
    test_harness.XsltTest(tester, source, [sheet], expected_6,
                          title="Global dependence through an applied template")


    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sheet = test_harness.FileInfo(string=invalid_sheet_1)
    test_harness.XsltTest(tester, source, [sheet], None,
                          exceptionCode=Error.ILLEGAL_SHADOWING,
                          title="Illegal shadowing 1")


    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sheet = test_harness.FileInfo(string=invalid_sheet_2)
    test_harness.XsltTest(tester, source, [sheet], None,
                          exceptionCode=Error.ILLEGAL_SHADOWING,
                          title="Illegal shadowing 2")


    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sheet = test_harness.FileInfo(string=invalid_sheet_3)
    test_harness.XsltTest(tester, source, [sheet], None,
                          exceptionCode=Error.ILLEGAL_SHADOWING,
                          title="Illegal shadowing 3")


    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sheet = test_harness.FileInfo(string=invalid_sheet_4)
    test_harness.XsltTest(tester, source, [sheet], None,
                          exceptionCode=Error.DUPLICATE_TOP_LEVEL_VAR,
                          title="Illegal shadowing 4")


    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sheet = test_harness.FileInfo(string=invalid_sheet_5)
    test_harness.XsltTest(tester, source, [sheet], None,
                          exceptionCode=Error.DUPLICATE_TOP_LEVEL_VAR,
                          title="Illegal shadowing 5")


    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sheet = test_harness.FileInfo(string=invalid_sheet_6)
    test_harness.XsltTest(tester, source, [sheet], None,
                          exceptionCode=Error.DUPLICATE_TOP_LEVEL_VAR,
                          title="Illegal shadowing 6")

    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sheet = test_harness.FileInfo(string=invalid_sheet_8)
    test_harness.XsltTest(tester, source, [sheet], None,
                          exceptionCode=Error.ILLEGAL_SHADOWING,
                          title="Illegal shadowing 7")

    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sheet = test_harness.FileInfo(string=invalid_sheet_7)
    test_harness.XsltTest(tester, source, [sheet], None,
                          exceptionCode=Error.VAR_WITH_CONTENT_AND_SELECT,
                          title="Illegal content when select attribute present")

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=invalid_sheet_9)
    test_harness.XsltTest(tester, source, [sheet], None,
                          exceptionClass=RuntimeException,
                          exceptionCode=RuntimeException.UNDEFINED_VARIABLE,
                          title="Visibility of variables across templates")

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=invalid_sheet_10)
    test_harness.XsltTest(tester, source, [sheet], None,
                          exceptionClass=RuntimeException,
                          exceptionCode=RuntimeException.UNDEFINED_VARIABLE,
                          title="Param visibility when evaluating top-level variable")

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=invalid_sheet_11)
    test_harness.XsltTest(tester, source, [sheet], None,
                          exceptionClass=RuntimeException,
                          exceptionCode=RuntimeException.UNDEFINED_VARIABLE,
                          title="Param visibility")
    return
