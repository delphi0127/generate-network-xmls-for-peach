# expat2domlette.c seems to get confused about xmlns attributes,
# like which part is the localName and which part is the prefix.

from Xml.Xslt import test_harness

source_1 = """\
<?xml version="1.0"?>
<foobar/>"""

sheet_1 = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0"
xmlns:ss="urn:wonky"
>
  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <results/>
  </xsl:template>

</xsl:stylesheet>"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<results xmlns:ss="urn:wonky"/>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='namespace copy-through')
    return
