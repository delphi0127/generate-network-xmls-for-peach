#Dieter Maurer <dieter@handshake.de> reports problems with xsl:import and variables

from Xml.Xslt import test_harness
from Ft.Xml.Xslt import XsltException, Error

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version='1.0'>

  <xsl:import href="Xml/Xslt/Borrowed/dm_20010506.xslt"/>

  <xsl:variable name="section.autolabel" select="1" />
  <xsl:variable name="html.stylesheet">book.xsl</xsl:variable>
  <xsl:variable name="html.stylesheet.type">text/css</xsl:variable>
    
</xsl:stylesheet>"""

expected = """\
<html>\n    START\n    <link type='text/css' rel='stylesheet' href='book.xsl'>\n    END\n    </html>"""


sheet_2 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version='1.0'>

  <xsl:import href="Xml/Xslt/Borrowed/dm_20010506.xslt"/>

  <xsl:param name="section.autolabel" select="1" />
  <xsl:param name="html.stylesheet">book.xsl</xsl:param>
  <xsl:param name="html.stylesheet.type">text/css</xsl:param>

</xsl:stylesheet>"""


error_sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version='1.0'>

  <xsl:include href="Xml/Xslt/Borrowed/dm_20010506.xslt"/>

  <xsl:variable name="section.autolabel" select="1" />
  <xsl:variable name="html.stylesheet">book.xsl</xsl:variable>
  <xsl:variable name="html.stylesheet.type">text/css</xsl:variable>

</xsl:stylesheet>"""


error_sheet_2 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version='1.0'>

  <xsl:include href="Xml/Xslt/Borrowed/dm_20010506.xslt"/>

  <xsl:param name="section.autolabel" select="1" />
  <xsl:param name="html.stylesheet">book.xsl</xsl:param>
  <xsl:param name="html.stylesheet.type">text/css</xsl:param>

</xsl:stylesheet>"""


def Test(tester):
    source = test_harness.FileInfo(string="<ignored/>")

    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='Import with variables')

    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='Import with params')

    sheet = test_harness.FileInfo(string=error_sheet_1)
    test_harness.XsltTest(tester, source, [sheet], "",
                          exceptionCode=Error.DUPLICATE_TOP_LEVEL_VAR,
                          title='Include with variables')

    sheet = test_harness.FileInfo(string=error_sheet_2)
    test_harness.XsltTest(tester, source, [sheet], "",
                          exceptionCode=Error.DUPLICATE_TOP_LEVEL_VAR,
                          title='Include with params')
    return
