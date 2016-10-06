from Xml.Xslt import test_harness
from Ft.Xml.Xslt import Error

source_1 = """<?xml version="1.0" encoding="utf-8"?><dummy/>"""

# An element enables forwards-compatible mode for itself, its
# attributes, its descendants and their attributes if either it is an
# xsl:stylesheet element whose version attribute is not equal to 1.0,
# or it is a literal result element that has an xsl:version attribute
# whose value is not equal to 1.0. [...]
#
# If an element is processed in forwards-compatible mode, then:

# if it is a top-level element and XSLT 1.0 does not allow such
# elements as top-level elements, then the element must be ignored
# along with its content;
#

# stylesheet version 1.0;
# top-level literal result element version 3.0, in no namespace;
# expected result: element is ignored (i.e., without the xsl:version > 1.0,
# it would trigger an exception as per XSLT 1.0 sec. 2.2, but since it has
# the xsl:version > 1.0, it matches the rule quoted above, and will be
# ignored. It's still visible in the document, though.)
sheet_1a = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes"/>
  <greeting xsl:version="3.0">hello</greeting>
  <xsl:template match="/">
    <result><xsl:value-of select="document('')/*/greeting"/></result>
  </xsl:template>
</xsl:stylesheet>"""

expected_1a = """<?xml version="1.0" encoding="UTF-8"?>
<result>hello</result>"""


# stylesheet version 1.0
# top-level literal result element with no version info, in no namespace
# (should raise an exception per XSLT 1.0 sec. 2.2)
sheet_1b = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes"/>
  <greeting>hello</greeting>
  <xsl:template match="/">
    <result/>
  </xsl:template>
</xsl:stylesheet>"""

expected_1b = None


# stylesheet version 1.0
# top-level literal result element version 1.0, in no namespace
# (same as previous test, but version is explicit;
#  should still raise an exception per XSLT 1.0 sec. 2.2)
sheet_1c = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes"/>
  <greeting xsl:version="1.0">hello</greeting>
  <xsl:template match="/">
    <result/>
  </xsl:template>
</xsl:stylesheet>"""

expected_1c = None


# stylesheet version 3.0
# top-level literal result element version 1.0, in no namespace
# (it disables forwards-compatible processing for itself,
#  so it should still raise an exception per XSLT 1.0 sec. 2.2)
sheet_1d = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="3.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes"/>
  <greeting xsl:version="1.0">hello</greeting>
  <xsl:template match="/">
    <result/>
  </xsl:template>
</xsl:stylesheet>"""

expected_1d = None


# stylesheet version 3.0
# top-level literal result element w/no version, in no namespace
# (should be ignored / no error)
sheet_1e = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="3.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes"/>
  <greeting>hello</greeting>
  <xsl:template match="/">
    <result><xsl:value-of select="document('')/*/greeting"/></result>
  </xsl:template>
</xsl:stylesheet>"""

expected_1e = """<?xml version="1.0" encoding="UTF-8"?>
<result>hello</result>"""


# forwards-compatible processing example from the spec
sheet_2 = """<xsl:stylesheet version="1.1" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <xsl:choose>
      <xsl:when test="system-property('xsl:version') >= 1.1">
        <xsl:exciting-new-1.1-feature/>
      </xsl:when>
      <xsl:otherwise>
        <html>
        <head>
          <title>XSLT 1.1 required</title>
        </head>
        <body>
          <p>Sorry, this stylesheet requires XSLT 1.1.</p>
        </body>
        </html>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>"""

expected_2 = """<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    <title>XSLT 1.1 required</title>
  </head>
  <body>
    <p>Sorry, this stylesheet requires XSLT 1.1.</p>
  </body>
</html>"""

sheet_3 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="/">
    <!--
      literal result element version = 1.0;
      fallback instruction is noop.
    -->
    <result xsl:version="1.0">
      <xsl:fallback>fallback</xsl:fallback>
    </result>
  </xsl:template>
</xsl:stylesheet>"""

expected_3 = """<?xml version="1.0" encoding="UTF-8"?>
<result/>"""

sheet_4 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="/">
    <!--
      literal result element version != 1.0;
      element is not instantiated;
      no error must be signaled.
    -->
    <result xsl:version="3.0">
      <xsl:choose>
        <xsl:when test="false()">
          <xsl:perform-magic>We do magic<xsl:fallback>Sorry, we don't do magic</xsl:fallback></xsl:perform-magic>
        </xsl:when>
        <xsl:otherwise>hello world</xsl:otherwise>
      </xsl:choose>
    </result>
  </xsl:template>
</xsl:stylesheet>"""

expected_4 = """<?xml version="1.0" encoding="UTF-8"?>
<result>hello world</result>"""

sheet_5 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="/">
    <!--
      literal result element version != 1.0;
      fallback must be performed;
    -->
    <result xsl:version="3.0">
      <xsl:perform-magic>We do magic<xsl:fallback>Sorry, we don't do magic</xsl:fallback></xsl:perform-magic>
    </result>
  </xsl:template>
</xsl:stylesheet>"""

expected_5 = """<?xml version="1.0" encoding="UTF-8"?>
<result>Sorry, we don't do magic</result>"""

sheet_6 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="/">
    <!--
      literal result element version != 1.0;
      fallback must be performed;
      since no fallback child, error must be signaled.
    -->
    <result xsl:version="3.0">
      <xsl:perform-magic/>
    </result>
  </xsl:template>
</xsl:stylesheet>"""

expected_6 = None

def Test(tester):
    tester.startGroup('forwards-compatible processing')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1a)
    test_harness.XsltTest(tester, source, [sheet], expected_1a,
                          title='1.0 sty w/non-1.0 top-level elem')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1b)
    test_harness.XsltTest(tester, source, [sheet], expected_1b,
                          exceptionCode=Error.ILLEGAL_ELEMENT_CHILD,
                          title='1.0 sty w/implicit 1.0 illegal top-level elem')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1c)
    test_harness.XsltTest(tester, source, [sheet], expected_1c,
                          exceptionCode=Error.ILLEGAL_ELEMENT_CHILD,
                          title='1.0 sty w/explicit 1.0 illegal top-level elem')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1d)
    test_harness.XsltTest(tester, source, [sheet], expected_1d,
                          exceptionCode=Error.ILLEGAL_ELEMENT_CHILD,
                          title='3.0 sty w/explicit 1.0 illegal top-level elem')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1e)
    test_harness.XsltTest(tester, source, [sheet], expected_1e,
                          title='3.0 sty w/3.0 top-level elem illegal in 1.0')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='forwards-compatible example from XSLT 1.0 spec')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='1.0 literal result elem w/fallback')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_4)
    test_harness.XsltTest(tester, source, [sheet], expected_4,
                          title='uninstantiated non-1.0 literal result elem')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_5)
    test_harness.XsltTest(tester, source, [sheet], expected_5,
                          title='non-1.0 literal result elem w/fallback')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_6)
    test_harness.XsltTest(tester, source, [sheet], expected_6,
                          exceptionCode=Error.FWD_COMPAT_WITHOUT_FALLBACK,
                          title='non-1.0 literal result elem w/o fallback')

    tester.groupDone()
    return
