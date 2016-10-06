########################################################################
# $Header: /var/local/cvsroot/4Suite/test/Xml/Xslt/Exslt/test_strings.py,v 1.2 2005/12/28 02:38:18 jkloth Exp $
"""Tests for EXSLT Strings"""

from Xml.Xslt import test_harness

from Ft.Xml.Xslt.Exslt import Strings

SOURCE = """<?xml version='1.0'?>
<doc>Is this EXSLT? No. no</doc>
"""

TESTS = []

# str:align()
def test_Align(tester):
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
   <xsl:value-of select="str:align(., '------------------------------',
                                   'left')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "Is this EXSLT? No. no---------"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='str:align() left')

    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
   <xsl:value-of select="str:align(., '  ', 'right')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "Is"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='str:align() right')

    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
   <xsl:value-of select="str:align(., '---------------------------',
                                   'center')"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    expected = "---Is this EXSLT? No. no---"
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='str:align() center')
    return
TESTS.append(test_Align)


# str:concat()
def test_Concat(tester):
    src = """\
<a>
  <c>Is this EXSLT? No. no</c>
  <c>Is this EXSLT? No. no</c>
  <c>Is this EXSLT? No. no</c>
</a>
"""
    sty = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/a">
    <xsl:value-of select="str:concat(c)"/>
  </xsl:template>

</xsl:stylesheet>
"""
    source = test_harness.FileInfo(string=src)
    sheet = test_harness.FileInfo(string=sty)
    expected = "Is this EXSLT? No. no" * 3
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='str:concat()')
    return
TESTS.append(test_Concat)


# str:decode-uri()
def test_DecodeUri(tester):
    sty = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings"
  extension-element-prefixes="str"
>

  <xsl:output method="text" encoding="iso-8859-1"/>

  <xsl:template match="/">
    <xsl:value-of select="str:decode-uri(
      'http://www.example.com/my%20r%C3%A9sum%C3%A9.html', 'utf-8')"/>
  </xsl:template>

</xsl:stylesheet>"""

    expected = "http://www.example.com/my r\xe9sum\xe9.html"

    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='str:decode-uri() UTF-8')

    sty = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings"
  extension-element-prefixes="str"
>

  <xsl:output method="text" encoding="utf-8"/>

  <xsl:template match="/">
    <xsl:value-of select="str:decode-uri(
      'http://www.example.com/my%20r%E9sum%E9.html', 'iso-8859-1')"/>
  </xsl:template>

</xsl:stylesheet>"""

    expected = "http://www.example.com/my r\xc3\xa9sum\xc3\xa9.html"

    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='str:decode-uri() ISO-8859-1')
    return
TESTS.append(test_DecodeUri)


# str:endcode-uri()
def test_EncodeUri(tester):
    strings = { 0: u'hello world',
                1: u'hello%20world',
                2: u'1 & 2 are < 3',
                3: u'100% OK?',
                4: u'\u00a1Hola!',
                5: u'\u4eca\u65e5\u306f',
              }

    encodings = { 1: u'utf-8',
                  2: u'iso-8859-1',
                  3: u'utf-16le',
                }

    escape_res = { 1: u'true()',
                   0: u'false()',
                 }

    expected = { #(str, encoding, escape_reserved): expected
                 (0, 1, 0): u'hello%20world',
                 (0, 1, 1): u'hello%20world',
                 (0, 2, 0): u'hello%20world',
                 (0, 2, 1): u'hello%20world',
                 (0, 3, 0): u'hello%20world',
                 (0, 3, 1): u'hello%20world',
                 (1, 1, 0): u'hello%20world',
                 (1, 1, 1): u'hello%20world',
                 (1, 2, 0): u'hello%20world',
                 (1, 2, 1): u'hello%20world',
                 (1, 3, 0): u'hello%20world',
                 (1, 3, 1): u'hello%20world',
                 (2, 1, 0): u'1%20&%202%20are%20%3C%203',
                 (2, 1, 1): u'1%20%26%202%20are%20%3C%203',
                 (2, 2, 0): u'1%20&%202%20are%20%3C%203',
                 (2, 2, 1): u'1%20%26%202%20are%20%3C%203',
                 (2, 3, 0): u'1%20&%202%20are%20%3C%203',
                 (2, 3, 1): u'1%20%26%202%20are%20%3C%203',
                 (3, 1, 0): u'100%25%20OK?',
                 (3, 1, 1): u'100%25%20OK%3F',
                 (3, 2, 0): u'100%25%20OK?',
                 (3, 2, 1): u'100%25%20OK%3F',
                 (3, 3, 0): u'100%25%20OK?',
                 (3, 3, 1): u'100%25%20OK%3F',
                 (4, 1, 0): u'%C2%A1Hola!',
                 (4, 1, 1): u'%C2%A1Hola!',
                 (4, 2, 0): u'%A1Hola!',
                 (4, 2, 1): u'%A1Hola!',
                 (4, 3, 0): u'%A1%00Hola!',
                 (4, 3, 1): u'%A1%00Hola!',
                 (5, 1, 0): u'%E4%BB%8A%E6%97%A5%E3%81%AF',
                 (5, 1, 1): u'%E4%BB%8A%E6%97%A5%E3%81%AF',
                 (5, 2, 0): u'%3F%3F%3F',
                 (5, 2, 1): u'%3F%3F%3F',
                 (5, 3, 0): u'%CA%4E%E5%65%6F%30',
                 (5, 3, 1): u'%CA%4E%E5%65%6F%30',
               }
    for s_key in strings.keys():
        s = strings[s_key]
        for enc_key in encodings.keys():
            encoding = encodings[enc_key]
            for esc_key in escape_res.keys():
                escape = escape_res[esc_key]
                test_title = u"str:encode-uri(%r, %s, '%s')" % (s, escape, encoding)
                tester.startTest(test_title)
                if expected.has_key((s_key, enc_key, esc_key)):
                    expected_str = expected[(s_key, enc_key, esc_key)]
                    result = Strings.EncodeUri(None, s, esc_key, encoding)
                    tester.compare(expected_str, result)
                else:
                    tester.warning('Not tested; expected result unknown')
                tester.testDone()
    return
TESTS.append(test_EncodeUri)


# str:padding()
def test_Padding(tester):
    sty = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings"
  extension-element-prefixes="str"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:copy-of select="str:padding(20, '---4567----23----890----------')"/>
    <xsl:text>&#10;</xsl:text>
    <xsl:value-of select="."/>
    <xsl:text>&#10;</xsl:text>
    <xsl:copy-of select="str:padding(10, '+-+')"/>
  </xsl:template>

</xsl:stylesheet>"""

    expected = """\
---4567----23----890
Is this EXSLT? No. no
+-++-++-++"""

    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='str:padding()')
    return
TESTS.append(test_Padding)


# str:replace()
def test_Replace(tester):
    sty1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
  xmlns:str="http://exslt.org/strings"
  extension-element-prefixes="exsl str">

  <xsl:output method="xml" indent="yes"/>

  <xsl:include href="Xml/Xslt/Core/str.replace.function.xsl"/>
  <xsl:include href="Xml/Xslt/Core/str.replace.template.xsl"/>

  <xsl:template match="/">
    <result>
      <!-- just strings -->
      <func>
        <xsl:copy-of select="str:replace('kill me','ll','ss')"/>
      </func>
      <efun>
        <xsl:copy-of select="str:replacef('kill me','ll','ss')"/>
      </efun>
      <tmpl>
        <xsl:call-template name="str:replacet">
          <xsl:with-param name="string" select="'kill me'" />
          <xsl:with-param name="search" select="'ll'" />
          <xsl:with-param name="replace" select="'ss'" />
        </xsl:call-template>
      </tmpl>

      <func>
        <xsl:copy-of select="str:replace('ha-ha silly','ha','bye')"/>
      </func>
      <efun>
        <xsl:copy-of select="str:replacef('ha-ha silly','ha','bye')"/>
      </efun>
      <tmpl>
        <xsl:call-template name="str:replacet">
          <xsl:with-param name="string" select="'ha-ha silly'" />
          <xsl:with-param name="search" select="'ha'" />
          <xsl:with-param name="replace" select="'bye'" />
        </xsl:call-template>
      </tmpl>

      <func>
        <xsl:copy-of select="str:replace('ha-ha silly','boo','bye')"/>
      </func>
      <efun>
        <xsl:copy-of select="str:replacef('ha-ha silly','boo','bye')"/>
      </efun>
      <tmpl>
        <xsl:call-template name="str:replacet">
          <xsl:with-param name="string" select="'ha-ha silly'" />
          <xsl:with-param name="search" select="'boo'" />
          <xsl:with-param name="replace" select="'bye'" />
        </xsl:call-template>
      </tmpl>

      <!-- getting fancy -->
      <xsl:variable name="s" select="'four score and seven years ago, our forefathers'"/>
      <xsl:variable name="search">
        <substring>e</substring>
        <substring>seven</substring>
        <substring>our</substring>
        <substring>the</substring>
      </xsl:variable>
      <xsl:variable name="searchNodes" select="exsl:node-set($search)/node()"/>
      <xsl:variable name="replace">
        <E/>
        <xsl:comment>HI</xsl:comment>
        <xsl:text>OO</xsl:text>
      </xsl:variable>
      <xsl:variable name="replNodes" select="exsl:node-set($replace)/node()"/>
      <func>
        <xsl:copy-of select="str:replace($s,$searchNodes,$replNodes)"/>
      </func>
      <efun>
        <xsl:copy-of select="str:replacef($s,$searchNodes,$replNodes)"/>
      </efun>
      <tmpl>
        <xsl:call-template name="str:replacet">
          <xsl:with-param name="string" select="$s" />
          <xsl:with-param name="search" select="$searchNodes" />
          <xsl:with-param name="replace" select="$replNodes" />
        </xsl:call-template>
      </tmpl>

      <!-- exceptional empty string case -->
      <xsl:variable name="replace2">
        <br/>
      </xsl:variable>
      <xsl:variable name="replNodes2" select="exsl:node-set($replace2)/node()"/>
      <func>
        <xsl:copy-of select="str:replace($s,'',$replNodes2)"/>
      </func>
      <efun>
        <xsl:copy-of select="str:replacef($s,'',$replNodes2)"/>
      </efun>
      <tmpl>
        <xsl:call-template name="str:replacet">
          <xsl:with-param name="string" select="$s" />
          <xsl:with-param name="search" select="''" />
          <xsl:with-param name="replace" select="$replNodes2" />
        </xsl:call-template>
      </tmpl>

      <!-- attrs and namespace nodes in replacements are treated as empty strings -->
      <xsl:variable name="replace3">
        <foo bar="baz"/>
      </xsl:variable>
      <xsl:variable name="replNodes3" select="exsl:node-set($replace3)/foo/@bar"/>
      <func>
        <xsl:copy-of select="str:replace($s,'years',$replNodes3)"/>
      </func>
      <efun>
        <xsl:copy-of select="str:replacef($s,'years',$replNodes3)"/>
      </efun>
      <tmpl>
        <xsl:call-template name="str:replacet">
          <xsl:with-param name="string" select="$s" />
          <xsl:with-param name="search" select="'years'" />
          <xsl:with-param name="replace" select="$replNodes3" />
        </xsl:call-template>
      </tmpl>


      <!-- string to node -->
      <xsl:variable name="s3" select="'line one&#10;line two&#10;line three'"/>
      <func>
        <xsl:copy-of select="str:replace($s3,'&#10;',$replNodes2)"/>
      </func>
      <efun>
        <xsl:copy-of select="str:replacef($s3,'&#10;',$replNodes2)"/>
      </efun>
      <tmpl>
        <xsl:call-template name="str:replacet">
          <xsl:with-param name="string" select="$s3" />
          <xsl:with-param name="search" select="'&#10;'" />
          <xsl:with-param name="replace" select="$replNodes2" />
        </xsl:call-template>
      </tmpl>
<oleg>
 <xsl:variable name="srch">
   <substr>$name</substr>
   <substr>$id</substr>
 </xsl:variable>
 <xsl:variable name="repl-rtf">
   <name>phd</name>
   <id>1234</id>
 </xsl:variable>
 <xsl:variable name="repl" select="exsl:node-set($repl-rtf)/node()"/>
 <xsl:copy-of select="str:replace('Patient: $name ($id)',$srch,$repl)"/>
</oleg>

    </result>
  </xsl:template>

</xsl:stylesheet>"""

    expected1 = """<?xml version="1.0" encoding="UTF-8"?>
<result>
  <func>kiss me</func>
  <efun>kiss me</efun>
  <tmpl>kiss me</tmpl>
  <func>bye-bye silly</func>
  <efun>bye-bye silly</efun>
  <tmpl>bye-bye silly</tmpl>
  <func>ha-ha silly</func>
  <efun>ha-ha silly</efun>
  <tmpl>ha-ha silly</tmpl>
  <func>fOO scor<E/> and <!--HI--> y<E/>ars ago, OO for<E/>fars</func>
  <efun>fOO scor<E/> and <!--HI--> y<E/>ars ago, OO for<E/>fars</efun>
  <tmpl>fOO scor<E/> and <!--HI--> y<E/>ars ago, OO for<E/>fars</tmpl>
  <func>four score and seven years ago, our forefathers</func>
  <efun>four score and seven years ago, our forefathers</efun>
  <tmpl>four score and seven years ago, our forefathers</tmpl>
  <func>four score and seven  ago, our forefathers</func>
  <efun>four score and seven  ago, our forefathers</efun>
  <tmpl>four score and seven  ago, our forefathers</tmpl>
  <func>line one<br/>line two<br/>line three</func>
  <efun>line one<br/>line two<br/>line three</efun>
  <tmpl>line one<br/>line two<br/>line three</tmpl>
  <oleg>Patient: $name ($id)</oleg>
</result>"""

    sty2 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings"
  exclude-result-prefixes="str">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <one>
        <xsl:value-of select="str:replace('ha-ha silly','ha','bye')"/>
      </one>
      <two>
        <xsl:value-of select="str:replace('ha-ha silly','boo','bye')"/>
      </two>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

    expected2 = """<?xml version="1.0" encoding="UTF-8"?>
<result>
  <one>bye-bye silly</one>
  <two>ha-ha silly</two>
</result>"""

    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty1)
    test_harness.XsltTest(tester, source, [sheet], expected1,
                          title='str:replace() 1')

    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty2)
    test_harness.XsltTest(tester, source, [sheet], expected2,
                          title='str:replace() 2')
    return
TESTS.append(test_Replace)


# str:split()
def test_Split(tester):
    sty1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <one>
        <xsl:copy-of select="str:split('a, simple, string',', ')"/>
      </one>
      <two>
        <xsl:copy-of select="str:split('date math str')"/>
      </two>
      <three>
        <xsl:copy-of select="str:split('foo','')"/>
      </three>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

    expected1 = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:str="http://exslt.org/strings">
  <one>
    <token>a</token>
    <token>simple</token>
    <token>string</token>
  </one>
  <two>
    <token>date</token>
    <token>math</token>
    <token>str</token>
  </two>
  <three>
    <token>f</token>
    <token>o</token>
    <token>o</token>
  </three>
</result>"""

    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty1)
    test_harness.XsltTest(tester, source, [sheet], expected1,
                          title='str:split()')
    return
TESTS.append(test_Split)


# str:tokenize()
def test_Tokenize(tester):
    sty = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings"
  extension-element-prefixes="str"
>

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <one>
        <xsl:copy-of select="str:tokenize('2001-06-03T11:40:23', '-T:')"/>
      </one>
      <two>
        <xsl:copy-of select="str:tokenize('date math str')"/>
      </two>
      <three>
        <xsl:copy-of select="str:tokenize('foo', '')"/>
      </three>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

    expected = """<?xml version="1.0" encoding="UTF-8"?>
<result>
  <one>
    <token>2001</token>
    <token>06</token>
    <token>03</token>
    <token>11</token>
    <token>40</token>
    <token>23</token>
  </one>
  <two>
    <token>date</token>
    <token>math</token>
    <token>str</token>
  </two>
  <three>
    <token>f</token>
    <token>o</token>
    <token>o</token>
  </three>
</result>
"""

    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=sty)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='str:tokenize()')
    return
TESTS.append(test_Tokenize)


def Test(tester):
    tester.startGroup('Strings')
    for test in TESTS:
        test(tester)
    tester.groupDone()
    return
