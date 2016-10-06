from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="mb_20020527-1.xsl"/>

  <xsl:template name="i">
    <foo>import.xsl</foo>
  </xsl:template>

</xsl:stylesheet>
"""

expected = """<?xml version="1.0" encoding="UTF-8"?>\n<out><foo>import.xsl</foo></out>"""

from Ft.Lib import Uri
INC_PATH = Uri.OsPathToUri('Xml/Xslt/Borrowed/etc/', attemptAbsolute=1)

def Test(tester):
    source = test_harness.FileInfo(string="<foo/>")
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          stylesheetAltUris=[INC_PATH],
                          title="Nested imports with names that clash across import precedence")
    return

