# At the time of this writing, 4xslt was not correctly determining the
# string-value of a root node. Also, when pDomlette was being used,
# a traceback would be generated when referencing a root node in an
# attribute value template.

from Xml.Xslt import test_harness

source_1 = """\
<?xml version="1.0"?>
<foo><bar>hello</bar><baz> world</baz></foo>"""

sheet_1 = """\
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <rootnode stringvalue="{.}"/>
  </xsl:template>

</xsl:stylesheet>"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<rootnode stringvalue='hello world'/>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='namespace copy-through')
    return
