########################################################################
# $Header: /var/local/cvsroot/4Suite/test/Xml/Xslt/Exslt/test_common.py,v 1.5 2005/10/09 02:09:26 mbrown Exp $
"""Tests for EXSLT Common"""

from Xml.Xslt import test_harness

import tempfile, os
from Ft.Lib import Uri

SRC1 = """<dummy/>"""

SRC2 = """\
<?xml version="1.0"?>
<foo>
  <a/>
  <b/>
  <c/>
</foo>"""

TESTS = []

# exsl:node-set()
def test_NodeSet(tester):
    sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:variable name='spam'>
      <eggs/>
    </xsl:variable>
    <xsl:value-of select='count(exsl:node-set($spam)/*)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='name(exsl:node-set($spam)/*)'/>
  </xsl:template>

</xsl:stylesheet>
"""

    expected_1 = '1 eggs'

    # 4XSLT used to die a horrible death when computing the union of
    # two node-sets that were created with exslt:node-set().
    sheet_2 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0"
xmlns:exsl="http://exslt.org/common"
exclude-result-prefixes="exsl">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">

    <xsl:variable name="rtf1">
      <a/><b/><c/>
    </xsl:variable>

    <xsl:variable name="rtf2">
      <x/><y/><z/>
    </xsl:variable>

    <xsl:variable name="set1" select="$rtf1"/>
    <xsl:variable name="set2" select="$rtf2"/>

    <results>
      <xsl:variable name="rtf-union" select="exsl:node-set($rtf1)|exsl:node-set($rtf2)"/>
      <result info="$rtf1">
        <xsl:copy-of select="$rtf1"/>
      </result>
      <result info="$rtf2">
        <xsl:copy-of select="$rtf2"/>
      </result>
      <result info="$rtf-union">
        <xsl:for-each select="$rtf-union/*">
          <xsl:sort select="local-name()"/>
          <xsl:copy/>
        </xsl:for-each>
      </result>
    </results>

  </xsl:template>

</xsl:stylesheet>"""

    expected_2 = """<?xml version="1.0" encoding="UTF-8"?>
<results>
  <result info="$rtf1">
    <a/>
    <b/>
    <c/>
  </result>
  <result info="$rtf2">
    <x/>
    <y/>
    <z/>
  </result>
  <result info="$rtf-union">
    <a/>
    <b/>
    <c/>
    <x/>
    <y/>
    <z/>
  </result>
</results>"""

    sheet_3 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0"
xmlns:exsl="http://exslt.org/common"
exclude-result-prefixes="exsl">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">

    <xsl:variable name="rtf1">
      <a/><b/><c/>
    </xsl:variable>

    <xsl:variable name="rtf2">
      <x/><y/><z/>
    </xsl:variable>

    <xsl:variable name="set1" select="exsl:node-set($rtf1)"/>
    <xsl:variable name="set2" select="exsl:node-set($rtf2)"/>

    <results>
      <xsl:variable name="set-union" select="$set1|$set2"/>
      <result info="$set1">
        <xsl:copy-of select="$set1"/>
      </result>
      <result info="$set2">
        <xsl:copy-of select="$set2"/>
      </result>
      <result info="$set-union">
        <xsl:for-each select="$set-union/*">
          <xsl:sort select="local-name()"/>
          <xsl:copy/>
        </xsl:for-each>
      </result>
    </results>

  </xsl:template>

</xsl:stylesheet>"""

    expected_3 = """<?xml version="1.0" encoding="UTF-8"?>
<results>
  <result info="$rtf1">
    <a/>
    <b/>
    <c/>
  </result>
  <result info="$rtf2">
    <x/>
    <y/>
    <z/>
  </result>
  <result info="$set-union">
    <a/>
    <b/>
    <c/>
    <x/>
    <y/>
    <z/>
  </result>
</results>"""

    sheet_4 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0"
xmlns:exsl="http://exslt.org/common"
exclude-result-prefixes="exsl">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">

    <xsl:variable name="rtf2">
      <x/><y/><z/>
    </xsl:variable>

    <xsl:variable name="set1" select="/foo/*"/>
    <xsl:variable name="set2" select="exsl:node-set($rtf2)"/>

    <results>
      <xsl:variable name="set-union" select="$set1|$set2"/>
      <result info="$set1">
        <xsl:copy-of select="$set1"/>
      </result>
      <result info="$set2">
        <xsl:copy-of select="$set2"/>
      </result>
      <result info="$set-union">
        <xsl:for-each select="$set-union|$set-union/*">
          <xsl:sort select="local-name()"/>
          <xsl:copy/>
        </xsl:for-each>
      </result>
    </results>

  </xsl:template>

</xsl:stylesheet>"""

    expected_4 = expected_3

    sheet_5 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0"
xmlns:exsl="http://exslt.org/common"
exclude-result-prefixes="exsl">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <xsl:variable name="set" select="exsl:node-set('foo')"/>
    <results>
      <!-- make sure it's not a root or element node with a text node child -->
      <result>
        <xsl:copy-of select="$set/node()"/>
      </result>
      <result nodes="count($set)">
        <xsl:copy-of select="$set"/>
      </result>
    </results>
  </xsl:template>

</xsl:stylesheet>"""

    expected_5 = """<?xml version="1.0" encoding="UTF-8"?>
<results><result/><result nodes="1">foo</result></results>"""

    source = test_harness.FileInfo(string=SRC1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='exsl:node-set()')

    source = test_harness.FileInfo(string=SRC1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='exsl:node-set() union 1')

    source = test_harness.FileInfo(string=SRC1)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='exsl:node-set() union 2')

    source = test_harness.FileInfo(string=SRC2)
    sheet = test_harness.FileInfo(string=sheet_4)
    test_harness.XsltTest(tester, source, [sheet], expected_4,
                          title='exsl:node-set() union 3')

    source = test_harness.FileInfo(string=SRC2)
    sheet = test_harness.FileInfo(string=sheet_5)
    test_harness.XsltTest(tester, source, [sheet], expected_5,
                          title='exsl:node-set() on string arg')
    return
TESTS.append(test_NodeSet)


# exsl:object-type()
def test_ObjectType(tester):
    sheet_1 = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
  version="1.0"
>

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:variable name='spam'>
      <eggs/>
    </xsl:variable>
    <xsl:value-of select='exsl:object-type($spam)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='exsl:object-type(.)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='exsl:object-type("1")'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='exsl:object-type(1)'/>
    <xsl:text> </xsl:text>
    <xsl:value-of select='exsl:object-type(1=1)'/>
  </xsl:template>

</xsl:stylesheet>
"""

    expected_1 = "RTF node-set string number boolean"

    source = test_harness.FileInfo(string=SRC1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='exsl:object-type()')
    return
TESTS.append(test_ObjectType)


# <exsl:document>
def test_Document(tester):
    sty = """\
<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
    xmlns:exsl="http://exslt.org/common"
    extension-element-prefixes="exsl">

<xsl:output method="xml" indent="yes" encoding="ISO-8859-1"/>

<xsl:param name="filebase"/>
<xsl:param name="method"/>
<xsl:param name="indent"/>

<xsl:template match="/">
  <xsl:apply-templates select="test"/>
</xsl:template>

<xsl:template match="test">
  <testout>
    <xsl:apply-templates select="data"/>
  </testout>
</xsl:template>

<xsl:template match="data">
  <xsl:variable name="file" select="concat($filebase, ., '.xml')"/>
  <datafile>
    <xsl:text>Writing data file </xsl:text>
    <xsl:value-of select="."/>
  </datafile>
  <exsl:document href="{$file}"
                 method="{$method}"
                 indent="{$indent}"
                 encoding="ISO-8859-1">
    <datatree>
      <name><xsl:value-of select="."/></name>
      <what>test</what>
    </datatree>
  </exsl:document>
</xsl:template>

</xsl:stylesheet>"""

    src = """\
<?xml version="1.0" encoding="ISO-8859-1"?>

<test>
  <data>11</data>
  <data>12</data>
  <data>13</data>
  <data>14</data>
  <data>15</data>
</test>
"""

    expected = """<?xml version="1.0" encoding="ISO-8859-1"?>
<testout>
  <datafile>Writing data file 11</datafile>
  <datafile>Writing data file 12</datafile>
  <datafile>Writing data file 13</datafile>
  <datafile>Writing data file 14</datafile>
  <datafile>Writing data file 15</datafile>
</testout>"""

    file_xml_indented = """<?xml version="1.0" encoding="ISO-8859-1"?>
<datatree>
  <name>%s</name>
  <what>test</what>
</datatree>"""

    file_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<datatree><name>%s</name><what>test</what></datatree>"""

    file_html_indented = """<datatree>
  <name>%s</name>
  <what>test</what>
</datatree>"""

    file_html = """<datatree><name>%s</name><what>test</what></datatree>"""

    tester.startGroup("exsl:document")

    fileName = tempfile.mktemp()
    fileUri = Uri.OsPathToUri(fileName)

    source = test_harness.FileInfo(string=src)
    sheet = test_harness.FileInfo(string=sty)
    for method, indent, file_expected in (('xml', 'yes', file_xml_indented),
                                          ('xml', 'no', file_xml),
                                          ('html', 'yes', file_html_indented),
                                          ('html', 'no', file_html)):
        title="Using method='%s', indent='%s'" % (method, indent)
        test_harness.XsltTest(tester, source, [sheet], expected,
                              topLevelParams={'filebase' : fileUri,
                                              'method' : method,
                                              'indent' : indent},
                              title=title)
        tester.startTest("Checking output documents")
        for data in range(11, 16):
            file_name = '%s%d.xml' % (fileName, data)
            tester.compare(True, os.path.exists(file_name))
            file = open(file_name, 'r')
            fileData = file.read()
            file.close()
            tester.compare(file_expected % data, fileData)
            if os.path.exists(file_name):
                os.unlink(file_name)

        tester.testDone()

    #--------
    title = ('cdata-section-elements in secondary document')

    src = """<data>document.write('&lt;p&gt;foo &amp; bar&lt;/p&gt;')</data>"""

    sty = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
  xmlns:xhtml="http://www.w3.org/1999/xhtml"
  extension-element-prefixes="exsl">

  <xsl:output %(main)s/>

  <xsl:template match="/">
    <html>
      <head>
        <title>test</title>
      </head>
      <body>
        <h1>test</h1>
        <script type="text/javascript">
          <xsl:value-of select="data"/>
        </script>
        <exsl:document href="%(outfile)s" %(secondary)s>
          <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
            <head>
              <script type="text/javascript">
                <xsl:value-of select="data"/>
              </script>
            </head>
            <body>
              <xsl:value-of select="data"/>
            </body>
          </html>
        </exsl:document>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>"""

    expected = """<html xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <head>
    <meta content="text/html; charset=iso-8859-1" http-equiv="Content-Type">
    <title>test</title>
  </head>
  <body>
    <h1>test</h1><script type="text/javascript">document.write('<p>foo & bar</p>')</script></body>
</html>"""

    expected_filedata = """<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:xhtml="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en"><head><script type="text/javascript"><![CDATA[document.write('<p>foo & bar</p>')]]></script></head><body>document.write('&lt;p&gt;foo &amp; bar&lt;/p&gt;')</body></html>"""
    fileName = tempfile.mktemp()
    fileUri = Uri.OsPathToUri(fileName)
    main = 'method="html" indent="yes" encoding="iso-8859-1"'
    secondary = 'method="xml" encoding="utf-8" indent="no" doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" cdata-section-elements="xhtml:script"'
    sheet_str = sty % {'main': main, 'secondary': secondary, 'outfile': fileUri}
    source = test_harness.FileInfo(string=src)
    sheet = test_harness.FileInfo(string=sheet_str)
    test_harness.XsltTest(tester, source, [sheet], expected, title=title)
    tester.compare(True, os.path.exists(fileName))
    file = open(fileName, 'r')
    fileData = file.read()
    file.close()
    tester.compare(expected_filedata, fileData)
    if os.path.exists(fileName):
        os.unlink(fileName)

    title = 'cdata-section-elements in main document only'
    fileName = tempfile.mktemp()
    fileUri = Uri.OsPathToUri(fileName)
    main = 'method="html" indent="yes" encoding="iso-8859-1" cdata-section-elements="xhtml:script"'
    secondary = 'method="xml" encoding="utf-8" indent="no" doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"'
    sheet_str = sty % {'main': main, 'secondary': secondary, 'outfile': fileUri}
    source = test_harness.FileInfo(string=src)
    sheet = test_harness.FileInfo(string=sheet_str)
    test_harness.XsltTest(tester, source, [sheet], expected, title=title)
    expected_filedata = """<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:xhtml="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en"><head><script type="text/javascript">document.write('&lt;p&gt;foo &amp; bar&lt;/p&gt;')</script></head><body>document.write('&lt;p&gt;foo &amp; bar&lt;/p&gt;')</body></html>"""
    file = open(fileName, 'r')
    fileData = file.read()
    file.close()
    tester.compare(expected_filedata, fileData)
    if os.path.exists(fileName):
        os.unlink(fileName)

    tester.groupDone()
    return

TESTS.append(test_Document)


def Test(tester):
    tester.startGroup('Common')
    for test in TESTS:
        test(tester)
    tester.groupDone()
    return
