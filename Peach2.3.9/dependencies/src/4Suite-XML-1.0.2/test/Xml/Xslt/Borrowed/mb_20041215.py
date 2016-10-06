# See 

from Xml.Xslt import test_harness

SRC_1 = """\
<z:foo xmlns:z="planetz">sometext<bar>moretext</bar></z:foo>"""

SRC_2 = """\
<z:foo xmlns:z="planetz" a="b">sometext<bar>moretext</bar></z:foo>"""

SHEET_1 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:f="http://xmlns.4suite.org/ext"
  extension-element-prefixes="f">

  <xsl:output method="xml" encoding="us-ascii" indent="yes"/>
  
  <xsl:key name="foo" match="node()" use="."/>

  <xsl:template match="/">
    <f:dump-keys force-update="yes"/>
  </xsl:template>

</xsl:stylesheet>
"""

SHEET_2 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:f="http://xmlns.4suite.org/ext"
  extension-element-prefixes="f">

  <xsl:output method="xml" encoding="us-ascii" indent="yes"/>
  
  <xsl:key name="foo" match="*" use="."/>

  <xsl:template match="/">
    <f:dump-keys force-update="yes"/>
  </xsl:template>

</xsl:stylesheet>
"""

SHEET_3 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:f="http://xmlns.4suite.org/ext"
  extension-element-prefixes="f">

  <xsl:output method="xml" encoding="us-ascii" indent="yes"/>
  
  <xsl:key name="foo" match="@*|*" use="."/>

  <xsl:template match="/">
    <f:dump-keys force-update="yes"/>
  </xsl:template>

</xsl:stylesheet>
"""

SHEET_4 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:f="http://xmlns.4suite.org/ext"
  extension-element-prefixes="f">

  <xsl:output method="xml" encoding="us-ascii" indent="yes"/>
  
  <xsl:key name="foo" match="node()" use="."/>
  <xsl:key name="bar" match="*" use="."/>

  <xsl:template match="/">
    <f:dump-keys force-update="yes"/>
  </xsl:template>

</xsl:stylesheet>
"""

SHEET_5 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:f="http://xmlns.4suite.org/ext"
  xmlns:z="planetz"
  extension-element-prefixes="f">

  <xsl:output method="xml" encoding="us-ascii" indent="yes"/>
  
  <xsl:key name="foo" match="node()" use="."/>
  <xsl:key name="bar" match="z:*" use="."/>

  <xsl:template match="/">
    <f:dump-keys force-update="yes"/>
  </xsl:template>

</xsl:stylesheet>
"""

SHEET_6 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:f="http://xmlns.4suite.org/ext"
  xmlns:z="planetz"
  extension-element-prefixes="f">

  <xsl:output method="xml" encoding="us-ascii" indent="yes"/>
  
  <xsl:key name="foo" match="node()|@*" use="."/>
  <xsl:key name="bar" match="*" use="."/>

  <xsl:template match="/">
    <f:dump-keys force-update="yes"/>
  </xsl:template>

</xsl:stylesheet>
"""

EXPECTED_1_1 = """\
<?xml version="1.0" encoding="us-ascii"?>
<zz:KeyDump xmlns:zz="http://xmlns.4suite.org/reserved">
  <zz:Key name="foo">
    <zz:MatchSet value="sometextmoretext">
      <z:foo xmlns:z="planetz">sometext<bar>moretext</bar>
      </z:foo>
    </zz:MatchSet>
    <zz:MatchSet value="sometext">sometext</zz:MatchSet>
    <zz:MatchSet value="moretext">
      <bar xmlns:z="planetz">moretext</bar>moretext</zz:MatchSet>
  </zz:Key>
</zz:KeyDump>"""

EXPECTED_1_2 = """\
<?xml version="1.0" encoding="us-ascii"?>
<zz:KeyDump xmlns:zz="http://xmlns.4suite.org/reserved">
  <zz:Key name="foo">
    <zz:MatchSet value="sometextmoretext">
      <z:foo xmlns:z="planetz" a="b">sometext<bar>moretext</bar>
      </z:foo>
    </zz:MatchSet>
    <zz:MatchSet value="sometext">sometext</zz:MatchSet>
    <zz:MatchSet value="moretext">
      <bar xmlns:z="planetz">moretext</bar>moretext</zz:MatchSet>
  </zz:Key>
</zz:KeyDump>"""

EXPECTED_2_2 = """\
<?xml version="1.0" encoding="us-ascii"?>
<zz:KeyDump xmlns:zz="http://xmlns.4suite.org/reserved">
  <zz:Key name="foo">
    <zz:MatchSet value="sometextmoretext">
      <z:foo xmlns:z="planetz" a="b">sometext<bar>moretext</bar>
      </z:foo>
    </zz:MatchSet>
    <zz:MatchSet value="moretext">
      <bar xmlns:z="planetz">moretext</bar>
    </zz:MatchSet>
  </zz:Key>
</zz:KeyDump>"""
    
EXPECTED_3_2 = """\
<?xml version="1.0" encoding="us-ascii"?>
<zz:KeyDump xmlns:zz="http://xmlns.4suite.org/reserved">
  <zz:Key name="foo">
    <zz:MatchSet value="sometextmoretext">
      <z:foo xmlns:z="planetz" a="b">sometext<bar>moretext</bar>
      </z:foo>
    </zz:MatchSet>
    <zz:MatchSet value="b">
      <!--Attribute: a=b-->
    </zz:MatchSet>
    <zz:MatchSet value="moretext">
      <bar xmlns:z="planetz">moretext</bar>
    </zz:MatchSet>
  </zz:Key>
</zz:KeyDump>"""

EXPECTED_4_2 = """\
<?xml version="1.0" encoding="us-ascii"?>
<zz:KeyDump xmlns:zz="http://xmlns.4suite.org/reserved">
  <zz:Key name="foo">
    <zz:MatchSet value="sometextmoretext">
      <z:foo xmlns:z="planetz" a="b">sometext<bar>moretext</bar>
      </z:foo>
    </zz:MatchSet>
    <zz:MatchSet value="sometext">sometext</zz:MatchSet>
    <zz:MatchSet value="moretext">
      <bar xmlns:z="planetz">moretext</bar>moretext</zz:MatchSet>
  </zz:Key>
  <zz:Key name="bar">
    <zz:MatchSet value="sometextmoretext">
      <z:foo xmlns:z="planetz" a="b">sometext<bar>moretext</bar>
      </z:foo>
    </zz:MatchSet>
    <zz:MatchSet value="moretext">
      <bar xmlns:z="planetz">moretext</bar>
    </zz:MatchSet>
  </zz:Key>
</zz:KeyDump>"""

EXPECTED_5_2 = """\
<?xml version="1.0" encoding="us-ascii"?>
<zz:KeyDump xmlns:zz="http://xmlns.4suite.org/reserved">
  <zz:Key name="foo">
    <zz:MatchSet value="sometextmoretext">
      <z:foo xmlns:z="planetz" a="b">sometext<bar>moretext</bar>
      </z:foo>
    </zz:MatchSet>
    <zz:MatchSet value="sometext">sometext</zz:MatchSet>
    <zz:MatchSet value="moretext">
      <bar xmlns:z="planetz">moretext</bar>moretext</zz:MatchSet>
  </zz:Key>
  <zz:Key name="bar">
    <zz:MatchSet value="sometextmoretext">
      <z:foo xmlns:z="planetz" a="b">sometext<bar>moretext</bar>
      </z:foo>
    </zz:MatchSet>
  </zz:Key>
</zz:KeyDump>"""

EXPECTED_6_2 = """\
<?xml version="1.0" encoding="us-ascii"?>
<zz:KeyDump xmlns:zz="http://xmlns.4suite.org/reserved">
  <zz:Key name="foo">
    <zz:MatchSet value="sometextmoretext">
      <z:foo xmlns:z="planetz" a="b">sometext<bar>moretext</bar>
      </z:foo>
    </zz:MatchSet>
    <zz:MatchSet value="b">
      <!--Attribute: a=b-->
    </zz:MatchSet>
    <zz:MatchSet value="sometext">sometext</zz:MatchSet>
    <zz:MatchSet value="moretext">
      <bar xmlns:z="planetz">moretext</bar>moretext</zz:MatchSet>
  </zz:Key>
  <zz:Key name="bar">
    <zz:MatchSet value="sometextmoretext">
      <z:foo xmlns:z="planetz" a="b">sometext<bar>moretext</bar>
      </z:foo>
    </zz:MatchSet>
    <zz:MatchSet value="moretext">
      <bar xmlns:z="planetz">moretext</bar>
    </zz:MatchSet>
  </zz:Key>
</zz:KeyDump>"""


def Test(tester):
    source = test_harness.FileInfo(string=SRC_1)
    sheet = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_1_1,
                          title='xsl:key with match="node()"')

    source = test_harness.FileInfo(string=SRC_2)
    sheet = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_1_2,
                          title='xsl:key with match="node() and some attributes"')

    source = test_harness.FileInfo(string=SRC_2)
    sheet = test_harness.FileInfo(string=SHEET_2)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_2_2,
                          title='xsl:key with match="*"')

    source = test_harness.FileInfo(string=SRC_2)
    sheet = test_harness.FileInfo(string=SHEET_3)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_3_2,
                          title='xsl:key with match="*@|*"')

    source = test_harness.FileInfo(string=SRC_2)
    sheet = test_harness.FileInfo(string=SHEET_4)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_4_2,
                          title='xsl:key with match="node() and *"')

    source = test_harness.FileInfo(string=SRC_2)
    sheet = test_harness.FileInfo(string=SHEET_5)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_5_2,
                          title='xsl:key with match="node() and z:*"')

    source = test_harness.FileInfo(string=SRC_2)
    sheet = test_harness.FileInfo(string=SHEET_6)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_6_2,
                          title='xsl:key with match="node() and z:*"')
    return

