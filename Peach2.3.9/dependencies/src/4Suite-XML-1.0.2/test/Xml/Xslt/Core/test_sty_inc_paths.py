import os
from Xml.Xslt import test_harness

sheet_1 = """<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:import href="null.xslt"/>
</xsl:transform>
"""

sheet_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:variable name='spam' select='"original"'/>
  <xsl:import href='Xml/Xslt/Core/addr_book3.xsl'/>

</xsl:stylesheet>
"""

expected_1 = """<?xml version="1.0" encoding="UTF-8"?>\n"""
from Ft.Lib import Uri
INC_PATH = Uri.UriToOsPath('Xml/Xslt/Core/etc/', attemptAbsolute=1)
INC_PATH = Uri.OsPathToUri(INC_PATH)

def Test(tester):
    source = test_harness.FileInfo(string="<foo/>")
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          stylesheetAltUris=[INC_PATH],
                          title="xsl:import using alternative stylesheet URIs")
    return

