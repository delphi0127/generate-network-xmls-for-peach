from Ft.Xml.Xslt import Error
from Xml.Xslt import test_harness
from Ft.Lib import Uri
import os

base = os.getcwd()
if base[-1] != os.sep:
    base += os.sep
base = Uri.OsPathToUri(base)

SHEET_1 = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
  >

  <xsl:import href="Xml/Xslt/Core/test-apply-imports-1.xslt"/>

  <xsl:template match="example">
    <div style="border: solid red">
      <xsl:apply-imports/>
    </div>
  </xsl:template>

</xsl:stylesheet>
"""

SHEET_URI = base + 'sheet_string'

SOURCE_1 = "<example>This is an example</example>"

EXPECTED_1 = """\
<?xml version='1.0' encoding='UTF-8'?>
<div style="border: solid red"><pre>This is an example</pre></div>"""

SHEET_2a = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
  >

  <xsl:import href="Xml/Xslt/Core/test-apply-imports-2.xslt"/>

  <xsl:template match="doc">
    <body>
      <xsl:apply-imports/>
    </body>
  </xsl:template>

  <xsl:template match="*">
    <unknown-element><xsl:value-of select="name()"/></unknown-element>
  </xsl:template>

</xsl:stylesheet>
"""

SOURCE_2 = "<doc><example>This is an example<inconnu/></example></doc>"

EXPECTED_2a = """\
<?xml version="1.0" encoding="UTF-8"?>\n<body><div style="border: solid red"><unknown-element>example</unknown-element></div></body>"""

SHEET_2b = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
  >

  <xsl:import href="Xml/Xslt/Core/test-apply-imports-2.xslt"/>

  <xsl:template match="doc">
    <body>
      <xsl:apply-imports>
        <xsl:with-param name="border-style" select="'dotted'"/>
      </xsl:apply-imports>
    </body>
  </xsl:template>

  <xsl:template match="*">
    <unknown-element><xsl:value-of select="name()"/></unknown-element>
  </xsl:template>

</xsl:stylesheet>
"""

SHEET_2c = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:f="http://xmlns.4suite.org/ext"
  version="1.0"
  extension-element-prefixes="f"
  >

  <xsl:import href="Xml/Xslt/Core/test-apply-imports-2.xslt"/>

  <xsl:template match="doc">
    <body>
      <f:apply-imports/>
    </body>
  </xsl:template>

  <xsl:template match="*">
    <unknown-element><xsl:value-of select="name()"/></unknown-element>
  </xsl:template>

</xsl:stylesheet>
"""

EXPECTED_2c = EXPECTED_2a

SHEET_2d = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:f="http://xmlns.4suite.org/ext"
  version="1.0"
  extension-element-prefixes="f"
  >

  <xsl:import href="Xml/Xslt/Core/test-apply-imports-2.xslt"/>

  <xsl:template match="doc">
    <body>
      <f:apply-imports>
        <xsl:with-param name="border-style" select="'dotted'"/>
      </f:apply-imports>
    </body>
  </xsl:template>

  <xsl:template match="*">
    <unknown-element><xsl:value-of select="name()"/></unknown-element>
  </xsl:template>

</xsl:stylesheet>
"""

EXPECTED_2d = """\
<?xml version="1.0" encoding="UTF-8"?>\n<body><div style="border: dotted red"><unknown-element>example</unknown-element></div></body>"""


def Test(tester):
    source = test_harness.FileInfo(string=SOURCE_1)
    sheet = test_harness.FileInfo(string=SHEET_1, baseUri=SHEET_URI)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_1,
                          title='xsl:apply-imports 1')

    source = test_harness.FileInfo(string=SOURCE_2)
    sheet = test_harness.FileInfo(string=SHEET_2a, baseUri=SHEET_URI)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_2a,
                          title='xsl:apply-imports 2')

    source = test_harness.FileInfo(string=SOURCE_2)
    sheet = test_harness.FileInfo(string=SHEET_2b, baseUri=SHEET_URI)
    test_harness.XsltTest(tester, source, [sheet], None,
                          title='xsl:apply-imports 2 with params',
                          exceptionCode=Error.ILLEGAL_ELEMENT_CHILD,
                          )
    source = test_harness.FileInfo(string=SOURCE_2)
    sheet = test_harness.FileInfo(string=SHEET_2c, baseUri=SHEET_URI)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_2c,
                          title='f:apply-imports')

    source = test_harness.FileInfo(string=SOURCE_2)
    sheet = test_harness.FileInfo(string=SHEET_2d, baseUri=SHEET_URI)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_2d,
                          title='f:apply-imports with params')
    return
