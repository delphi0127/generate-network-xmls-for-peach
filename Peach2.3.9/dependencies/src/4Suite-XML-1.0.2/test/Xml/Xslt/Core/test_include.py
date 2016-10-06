import cStringIO

from Ft.Lib.Uri import OsPathToUri
from Ft.Xml.InputSource import InputSourceFactory, DefaultFactory
from Ft.Xml.Xslt import XsltException, Error
from Ft.Xml.Xslt.Processor import Processor

from Xml.Xslt import test_harness

#-----------------------------------------------------------------------
# General test: a duplicate template at a higher priority
# should override the original. Other included templates
# should work.
#
sheet_str_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:include href='Xml/Xslt/Core/addr_book1.xsl'/>

  <xsl:template match='PHONENUM' priority='10'>
    <xsl:element name='p'>
      <xsl:attribute name='align'>center</xsl:attribute>
      <xsl:value-of select='@DESC'/><xsl:text>: </xsl:text>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
"""

expected_1 = """<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <title>Address Book</title>
  </head>
  <body>
    <h1>Tabulate Just Names and Phone Numbers</h1>
    <table>
      <tr>
        <td align='center'><b>Pieter Aaron</b></td>
        <td>
          <p align='center'>Work: 404-555-1234</p>
          <p align='center'>Fax: 404-555-4321</p>
          <p align='center'>Pager: 404-555-5555</p>
        </td>
      </tr>
      <tr>
        <td align='center'><b>Emeka Ndubuisi</b></td>
        <td>
          <p align='center'>Work: 767-555-7676</p>
          <p align='center'>Fax: 767-555-7642</p>
          <p align='center'>Pager: 800-SKY-PAGEx767676</p>
        </td>
      </tr>
      <tr>
        <td align='center'><b>Vasia Zhugenev</b></td>
        <td>
          <p align='center'>Work: 000-987-6543</p>
          <p align='center'>Cell: 000-000-0000</p>
        </td>
      </tr>
    </table>
  </body>
</html>"""

#-----------------------------------------------------------------------
# A stylesheet cannot include itself directly.
#
STY_CIRC = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:include href="self-include.xsl"/>

</xsl:stylesheet>"""

#-----------------------------------------------------------------------
# A stylesheet cannot include itself indirectly.
#
STY_CIRC_A = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:include href="circ-B.xsl"/>

</xsl:stylesheet>"""

STY_CIRC_B = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:include href="circ-A.xsl"/>

</xsl:stylesheet>"""

#-----------------------------------------------------------------------
# The same stylesheet can be included twice, as long as it doesn't
# include itself indirectly, but it will have duplicate definitions.
#
# In these examples, the only thing being defined is a match template,
# which is a recoverable error (it may be overlooked and the last
# template defined will be used).

STY_MATCH_DEF_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template match="/">first</xsl:template>

</xsl:stylesheet>"""

STY_MATCH_DEF_2 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template match="/">last</xsl:template>

</xsl:stylesheet>"""

STY_DUP_INCLUDE_MATCH = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="text"/>
  <xsl:include href="match-def-2.xsl"/>
  <xsl:include href="match-def-2.xsl"/>

</xsl:stylesheet>"""

STY_DUP_MATCH = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="text"/>
  <xsl:include href="match-def-1.xsl"/>
  <xsl:include href="match-def-2.xsl"/>

</xsl:stylesheet>"""


#-----------------------------------------------------------------------
# The same stylesheet can be included twice, but will have
# duplicate definitions.
#
# In this example, the duplicate definitions are global vars,
# which is an error that must be flagged.

STY_VAR_DEF = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="a" select="'hello'"/>
  <xsl:variable name="a" select="'world'"/>

</xsl:stylesheet>"""

STY_DUP_INCLUDE_VAR = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:include href="var-def.xsl"/>
  <xsl:include href="var-def.xsl"/>

</xsl:stylesheet>"""

#-----------------------------------------------------------------------
# The same stylesheet can be included twice, but will have
# duplicate definitions.
#
# In this example, the duplicate definitions are named templates,
# which is an error that must be flagged.

STY_NAMED_DEF = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template name="einstein">hello universe</xsl:template>

</xsl:stylesheet>"""

STY_DUP_INCLUDE_NAMED = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="text"/>
  <xsl:include href="named-def.xsl"/>
  <xsl:include href="named-def.xsl"/>

</xsl:stylesheet>"""

#-----------------------------------------------------------------------
# Indirect inclusion example from the XSLT 1.0 spec.
#
# B includes A: OK
# C includes A: OK
# D includes B and C: not circular, but A is included twice,
#   so there will be duplicate definitions (an error)

STY_A = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- this is stylesheet A -->
  <xsl:output method="text"/>
  <xsl:template match="/">hello world</xsl:template>

</xsl:stylesheet>"""

STY_B = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- this is stylesheet B -->
  <xsl:include href="A.xsl"/>

</xsl:stylesheet>"""

STY_C = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- this is stylesheet C -->
  <xsl:include href="A.xsl"/>

</xsl:stylesheet>"""

STY_D = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- this is stylesheet D -->
  <xsl:include href="B.xsl"/>
  <xsl:include href="C.xsl"/>

</xsl:stylesheet>"""

STY_IDENTITY = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>"""

STY_XINC = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="text" />

  <xsl:template match="/">
    <xsl:variable name="content"><xi:include xmlns:xi="http://www.w3.org/2001/XInclude" parse="text" href="content.ent"/></xsl:variable>
    <xsl:choose>
      <xsl:when test="string($content)">The XInclude was processed. Here is the text:&#10;<xsl:value-of select="$content"/></xsl:when>
      <xsl:otherwise>The XInclude was not processed.</xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>"""

XINC_CONTENT = """hello world"""

XINC_EXPECTED_1 = """The XInclude was processed. Here is the text:
hello world"""

XINC_EXPECTED_2 = """The XInclude was not processed."""

STY_CIRC_XINC = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:xi="http://www.w3.org/2001/XInclude">

  <xsl:variable name="circular-include">
    <xi:include href="circ-xinclude.xsl"/>
  </xsl:variable>

</xsl:stylesheet>"""

DUMMY_XML = """<?xml version="1.0" encoding="utf-8"?><dummy/>"""

from Ft.Lib.Uri import FtUriResolver
class TestResolver(FtUriResolver):

    def resolve(self, uri, baseUri=None):
        if uri.endswith('self-include.xsl'):
            return cStringIO.StringIO(STY_CIRC)
        elif uri.endswith('circ-A.xsl'):
            return cStringIO.StringIO(STY_CIRC_A)
        elif uri.endswith('circ-B.xsl'):
            return cStringIO.StringIO(STY_CIRC_B)
        elif uri.endswith('dup-include-match.xsl'):
            return cStringIO.StringIO(STY_DUP_INCLUDE_MATCH)
        elif uri.endswith('dup-match.xsl'):
            return cStringIO.StringIO(STY_DUP_MATCH)
        elif uri.endswith('dup-include-named.xsl'):
            return cStringIO.StringIO(STY_DUP_INCLUDE_NAMED)
        elif uri.endswith('dup-include-var.xsl'):
            return cStringIO.StringIO(STY_DUP_INCLUDE_VAR)
        elif uri.endswith('match-def-1.xsl'):
            return cStringIO.StringIO(STY_MATCH_DEF_1)
        elif uri.endswith('match-def-2.xsl'):
            return cStringIO.StringIO(STY_MATCH_DEF_2)
        elif uri.endswith('named-def.xsl'):
            return cStringIO.StringIO(STY_NAMED_DEF)
        elif uri.endswith('var-def.xsl'):
            return cStringIO.StringIO(STY_VAR_DEF)
        elif uri.endswith('identity.xsl'):
            return cStringIO.StringIO(STY_IDENTITY)
        elif uri.endswith('xinc.xsl'):
            return cStringIO.StringIO(STY_XINC)
        elif uri.endswith('A.xsl'):
            return cStringIO.StringIO(STY_A)
        elif uri.endswith('B.xsl'):
            return cStringIO.StringIO(STY_B)
        elif uri.endswith('C.xsl'):
            return cStringIO.StringIO(STY_C)
        elif uri.endswith('D.xsl'):
            return cStringIO.StringIO(STY_D)
        elif uri.endswith('content.ent'):
            return cStringIO.StringIO(XINC_CONTENT)
        elif uri.endswith('circ-xinclude.xsl'):
            return cStringIO.StringIO(STY_CIRC_XINC)
        else:
            raise ValueError("can't resolve %s" % uri)


def Test(tester):

    source = test_harness.FileInfo(uri="Xml/Xslt/Core/addr_book1.xml")
    sty = test_harness.FileInfo(string=sheet_str_1)
    test_harness.XsltTest(tester, source, [sty], expected_1,
                          title='xsl:include')

    styfactory = InputSourceFactory(resolver=TestResolver())

    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri=OsPathToUri('self-include.xsl'))
    test_harness.XsltTest(tester, source, [sty], None,
                          title='circular xsl:include (direct)',
                          exceptionCode=Error.CIRCULAR_INCLUDE,
                          stylesheetInputFactory=styfactory)

    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri=OsPathToUri('circ-A.xsl'))
    test_harness.XsltTest(tester, source, [sty], None,
                          title='circular xsl:include (indirect)',
                          exceptionCode=Error.CIRCULAR_INCLUDE,
                          stylesheetInputFactory=styfactory)

    # conflicting match templates can raise an exception or produce a result
    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri=OsPathToUri('dup-include-match.xsl'))
    test_harness.XsltTest(tester, source, [sty], 'last',
                          title='non-circular duplicate include of match templates (direct)',
                          exceptionCode=Error.MULTIPLE_MATCH_TEMPLATES,
                          stylesheetInputFactory=styfactory)

    # conflicting match templates can raise an exception or produce a result
    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri=OsPathToUri('dup-match.xsl'))
    test_harness.XsltTest(tester, source, [sty], 'last',
                          title='include of conflicting match templates (direct)',
                          exceptionCode=Error.MULTIPLE_MATCH_TEMPLATES,
                          stylesheetInputFactory=styfactory)

    # conflicting match templates can raise an exception or produce a result
    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri=OsPathToUri('D.xsl'))
    test_harness.XsltTest(tester, source, [sty], 'hello world',
                          title='non-circular duplicate include of match templates (indirect)',
                          exceptionCode=Error.MULTIPLE_MATCH_TEMPLATES,
                          stylesheetInputFactory=styfactory)

    # dup named templates must raise exception
    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri=OsPathToUri('dup-include-named.xsl'))
    test_harness.XsltTest(tester, source, [sty], None,
                          title='non-circular duplicate include of named templates (direct)',
                          exceptionCode=Error.DUPLICATE_NAMED_TEMPLATE,
                          stylesheetInputFactory=styfactory)

    # dup top-level vars must raise exception
    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri=OsPathToUri('dup-include-var.xsl'))
    test_harness.XsltTest(tester, source, [sty], None,
                          title='non-circular duplicate include of top-level vars (direct)',
                          exceptionCode=Error.DUPLICATE_TOP_LEVEL_VAR,
                          stylesheetInputFactory=styfactory)

    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri=OsPathToUri('xinc.xsl'),
                                processIncludes=True)
    test_harness.XsltTest(tester, source, [sty], XINC_EXPECTED_1,
                          title='process XInclude in stylesheet',
                          stylesheetInputFactory=styfactory)

    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri=OsPathToUri('xinc.xsl'),
                                processIncludes=False)
    test_harness.XsltTest(tester, source, [sty], XINC_EXPECTED_2,
                          title='ignore XInclude in stylesheet',
                          stylesheetInputFactory=styfactory)

    source = test_harness.FileInfo(string=DUMMY_XML)
    sty = test_harness.FileInfo(uri=OsPathToUri('circ-xinclude.xsl'),
                                processIncludes=True)
    test_harness.XsltTest(tester, source, [sty], None,
                          title='circular include from XInclude',
                          exceptionCode=Error.STYLESHEET_PARSE_ERROR,
                          stylesheetInputFactory=styfactory)
    return
