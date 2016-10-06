from Xml.Xslt import test_harness

import os
from Ft.Lib import Uri
from Ft.Xml.XPath import RuntimeException

BASE = os.getcwd()
if BASE[-1] != os.sep:
    BASE += os.sep
BASE = Uri.OsPathToUri(BASE)


SHEET_2 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:variable name="sty-doc" select="document('')"/>

  <xsl:key name='name' match='*' use='name()'/>

  <xsl:template match="/">
    <xsl:for-each select=".">
      Entries from keys: <xsl:value-of select="count(key('name', 'ENTRY'))"/>
      Template from keys: <xsl:value-of select="count(key('name', 'xsl:template'))"/>
    </xsl:for-each>
    <xsl:for-each select="$sty-doc">
      Entries from keys: <xsl:value-of select="count(key('name', 'ENTRY'))"/>
      Template from keys: <xsl:value-of select="count(key('name', 'xsl:template'))"/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""


SHEET_3 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:x="http://spam.com"
>

  <xsl:output method="text"/>

  <xsl:key name='k1' match='xsl:*' use='name()'/>
  <xsl:key name='k2' match='x:*' use='@id'/>

  <x:grail id="ein"/>
  <x:grail id="zwo"/>
  <x:knicht id="drei"/>
  <x:knicht id="vier"/>

  <xsl:template match="/">
    <xsl:for-each select="document('')">
    Entries from key 1: <xsl:copy-of select="count(key('k1', 'xsl:template'))"/>
    Entries from key 2: <xsl:copy-of select="count(key('k2', 'drei'))"/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""


SHEET_3a = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:x="http://spam.com"
>

  <xsl:import href="Xml/Xslt/Core/etc/test-key-import-error.xslt"/>

  <x:grail id="ein"/>
  <x:grail id="zwo"/>
  <x:knicht id="drei"/>
  <x:knicht id="vier"/>

  <xsl:template match="/">
    Entries from key 1: <xsl:value-of select="count(key('k1', 'pa'))"/>
    <xsl:for-each select="document('')">
    Entries from key 2: <xsl:copy-of select="count(key('k2', 'drei'))"/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""


SHEET_4 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>

  <xsl:import href="Xml/Xslt/Core/etc/test-key-import-1.xslt"/>
  <xsl:output method="text"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="/">
    Entries from key 1: <xsl:value-of select="count(key('k1', 'pa'))"/>
    <xsl:for-each select="$sty-doc">
    Entries from key 2: <xsl:copy-of select="count(key('k2', 'drei'))"/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""


SHEET_5 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>

  <xsl:include href="Xml/Xslt/Core/etc/test-key-import-1.xslt"/>
  <xsl:output method="text"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="/">
    Entries from key 1: <xsl:value-of select="count(key('k1', 'pa'))"/>
    <xsl:for-each select="$sty-doc">
    Entries from key 2: <xsl:copy-of select="count(key('k2', 'drei'))"/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""


SHEET_6 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>

  <xsl:import href="Xml/Xslt/Core/etc/test-key-import-1.xslt"/>
  <!-- creates a silly key which indexes all ENTRY elements in the doc as 'pa'
       just to be different from the key in the import with the same name -->
  <xsl:key name='k1' match='ENTRY' use="'pa'"/>

  <xsl:output method="text"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="/">
    Entries from key 1: <xsl:value-of select="count(key('k1', 'pa'))"/>
    <xsl:for-each select="$sty-doc">
    Entries from key 2: <xsl:copy-of select="count(key('k2', 'drei'))"/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
"""


SHEET_7 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:x="http://spam.com/x"
>

  <xsl:output method="xml"/>
  <xsl:strip-space elements="*"/>
  <xsl:variable name="sty-doc" select="document('')"/>

  <xsl:key name='k1' match='x:*' use='local-name()'/>
  <xsl:key name='k1' match='x:*' use='@id'/>

  <x:vier id="ein"/>
  <x:drei id="zwo"/>
  <x:zwo id="drei"/>
  <x:ein id="vier"/>

  <xsl:template match="/">
    <result>
      <xsl:for-each select="$sty-doc">
        <xsl:copy-of select="key('k1', 'drei')"/>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:stylesheet>
"""

SRC_7 = """<?xml version="1.0" encoding="utf-8"?><dummy/>"""


SHEET_8 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:x="http://spam.com/x"
  xmlns:y="http://spam.com/y"
>

  <xsl:output method="xml"/>
  <xsl:strip-space elements="*"/>
  <xsl:variable name="sty-doc" select="document('')"/>

  <xsl:key name='k1' match='x:*' use='@id'/>
  <xsl:key name='k1' match='y:*' use='@id'/>

  <x:vier id="ein"/>
  <x:drei id="zwo"/>
  <x:zwo id="drei"/>
  <x:ein id="vier"/>
  <y:vier id="ein"/>
  <y:drei id="zwo"/>
  <y:zwo id="drei"/>
  <y:ein id="vier"/>

  <xsl:template match="/">
    <result>
      <xsl:for-each select="$sty-doc">
        <xsl:copy-of select="key('k1', 'drei')"/>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:stylesheet>
"""


SHEET_9 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:x="http://spam.com/x"
  xmlns:y="http://spam.com/y"
>

  <xsl:import href="Xml/Xslt/Core/etc/test-key-import-2.xslt"/>
  <xsl:output method="xml"/>
  <xsl:strip-space elements="*"/>
  <xsl:variable name="sty-doc" select="document('')"/>

  <xsl:key name='k1' match='x:*' use='@id'/>

  <x:vier id="ein"/>
  <x:drei id="zwo"/>
  <x:zwo id="drei"/>
  <x:ein id="vier"/>
  <y:vier id="ein"/>
  <y:drei id="zwo"/>
  <y:zwo id="drei"/>
  <y:ein id="vier"/>

  <xsl:template match="/">
    <result>
      <xsl:for-each select="$sty-doc">
        <xsl:copy-of select="key('k1', 'drei')"/>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:stylesheet>
"""



EXPECTED_1 = """<HTML>
  <HEAD>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <H1>Tabulate just the Names</H1>
    <TABLE>
      <TR>
        <TD ALIGN='CENTER'><B ID='pieter.aaron@inter.net'>Pieter Aaron</B></TD>
      </TR>
      <TR>
        <TD ALIGN='CENTER'><B ID='endubuisi@spamtron.com'>Emeka Ndubuisi</B></TD>
      </TR>
      <TR>
        <TD ALIGN='CENTER'><B ID='vxz@magog.ru'>Vasia Zhugenev</B></TD>
      </TR>
    </TABLE>
  </BODY>
</HTML>"""


EXPECTED_2 = """\
<?xml version="1.0" encoding="UTF-8"?>

      Entries from keys: 3
      Template from keys: 0
      Entries from keys: 0
      Template from keys: 1"""


EXPECTED_3 = """
    Entries from key 1: 1
    Entries from key 2: 1"""


EXPECTED_6 = """
    Entries from key 1: 3
    Entries from key 2: 1"""


EXPECTED_7 = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:x="http://spam.com/x"><x:drei xmlns:xsl="http://www.w3.org/1999/XSL/Transform" id="zwo"/><x:zwo xmlns:xsl="http://www.w3.org/1999/XSL/Transform" id="drei"/></result>"""


EXPECTED_8 = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:x="http://spam.com/x" xmlns:y="http://spam.com/y"><x:zwo xmlns:xsl="http://www.w3.org/1999/XSL/Transform" id="drei"/><y:zwo xmlns:xsl="http://www.w3.org/1999/XSL/Transform" id="drei"/></result>"""

EXPECTED_9 = EXPECTED_8

SHEET_URI = BASE + 'sheet_string'


def Test(tester):
    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sty = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book_keyed.xsl")
    test_harness.XsltTest(tester, source, [sty], EXPECTED_1,
                          title="Basic keys test")

    sty = test_harness.FileInfo(string=SHEET_2)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_2,
                          title="Keys shifting with context doc")

    sty = test_harness.FileInfo(string=SHEET_3)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_3,
                          title="Keys using patterns of form ns:*")

    sty = test_harness.FileInfo(string=SHEET_3a)
    test_harness.XsltTest(tester, source, [sty], None,
                          exceptionClass=RuntimeException,
                          exceptionCode=RuntimeException.UNDEFINED_PREFIX,
                          title="Keys using patterns of form ns:*")

    sheet = test_harness.FileInfo(string=SHEET_4, baseUri=SHEET_URI)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_3,
                          title='Imported keys')

    sheet = test_harness.FileInfo(string=SHEET_5, baseUri=SHEET_URI)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_3,
                          title='Included keys')

    tester.startGroup("Keys with same name")

    source = test_harness.FileInfo(string=SRC_7)
    sheet = test_harness.FileInfo(string=SHEET_7, baseUri=SHEET_URI)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_7,
                          title='Different values')

    source = test_harness.FileInfo(string=SRC_7)
    sheet = test_harness.FileInfo(string=SHEET_8, baseUri=SHEET_URI)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_8,
                          title='Matching different nodes')

    tester.startGroup("Keys with different import precedence")

    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sheet = test_harness.FileInfo(string=SHEET_6, baseUri=SHEET_URI)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_6,
                          title='Different values')

    source = test_harness.FileInfo(string=SRC_7)
    sheet = test_harness.FileInfo(string=SHEET_9, baseUri=SHEET_URI)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_9,
                          title='Matching different nodes')

    tester.groupDone()
    tester.groupDone()

    return
