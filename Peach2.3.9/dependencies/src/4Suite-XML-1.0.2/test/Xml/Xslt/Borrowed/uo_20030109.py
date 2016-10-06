from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ns="http://stuff.foo"
  exclude-result-prefixes="ns"
  >

  <xsl:import href="uo_20030109-1.xsl"/>

  <xsl:template match="/">
    <result><xsl:value-of select="ns:toUpperCase('Hello World')"/></result>
  </xsl:template>

</xsl:stylesheet>
"""

expected = "<?xml version='1.0' encoding='UTF-8'?>\n<result>HELLO WORLD</result>"

from Ft.Lib import Uri
INC_PATH = Uri.OsPathToUri('Xml/Xslt/Borrowed/etc/', attemptAbsolute=1)

def Test(tester):
    source = test_harness.FileInfo(string="<dummy/>")
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          stylesheetAltUris=[INC_PATH],
                          title='EXSLT functions defined in imported script')
    return
