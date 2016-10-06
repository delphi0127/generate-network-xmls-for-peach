#See http://lists.fourthought.com/pipermail/4suite-dev/2002-September/000732.html
from Xml.Xslt import test_harness

SHEET_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="mb_20020907.xsl"/>

  <xsl:variable name="var1" select="'foo'"/>
  <xsl:variable name="var2" select="'bar'"/>
  <xsl:variable name="culprit" select="concat($var1,$var2)"/>

  <xsl:template match="/"/>

</xsl:transform>
"""

SHEET_2 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="var1" select="'foo'"/>
  <xsl:variable name="var2" select="'bar'"/>
  <xsl:variable name="culprit" select="concat($var1,$var2)"/>

  <xsl:template match="/"/>

</xsl:transform>
"""

EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n'

from Ft.Lib import Uri
INC_PATH = Uri.OsPathToUri('Xml/Xslt/Borrowed/etc/', attemptAbsolute=1)

def Test(tester):
    tester.startGroup("Import that overrides a var and uses multiple vars in the overridden def.")
    source = test_harness.FileInfo(string="<foo/>")
    sheet = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED,
                          stylesheetAltUris=[INC_PATH])

    source = test_harness.FileInfo(string="<foo/>")
    sheet = test_harness.FileInfo(string=SHEET_2)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED,
                          stylesheetAltUris=[INC_PATH])
    tester.groupDone()
    return

