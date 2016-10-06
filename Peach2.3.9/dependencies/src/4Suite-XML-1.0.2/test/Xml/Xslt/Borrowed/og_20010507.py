# Oliver Graf <ograf@oli-ver-ena.de>:
# ft:output cdata-section-elements is not used

import os, tempfile
from Ft.Lib.Uri import OsPathToUri
from Xml.Xslt import test_harness

FILESTEM = tempfile.mktemp()
FILESTEM_URI = OsPathToUri(FILESTEM)

sheet_1 = """\
<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
    xmlns:exsl="http://exslt.org/common"
    extension-element-prefixes="exsl">

<xsl:output method="text" encoding="ISO-8859-1"/>

<xsl:template match="/">
  <xsl:variable name="file" select="'%s'"/>
  <exsl:document href="{$file}" method="xml" indent="yes" encoding="ISO-8859-1"
                 cdata-section-elements="str num">
    <datatree>
      <content><xsl:copy-of select="test/data/*"/></content>
      <what>test</what>
    </datatree>
  </exsl:document>
</xsl:template>

</xsl:stylesheet>"""%(FILESTEM_URI)

source_1 = """\
<?xml version="1.0" encoding="ISO-8859-1"?>

<test>
  <data>
    <num>1000</num>
    <str>test</str>
  </data>
</test>"""

expected_1 = """\
"""

file_expected_1 = """\
<?xml version="1.0" encoding="ISO-8859-1"?>
<datatree>
  <content>
    <num><![CDATA[1000]]></num>
    <str><![CDATA[test]]></str>
  </content>
  <what>test</what>
</datatree>"""


def Test(tester):
    if os.path.exists(FILESTEM):
        os.unlink(FILESTEM)

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)

    tester.startTest("Test File results")
    tester.compare(1, os.path.exists(FILESTEM))
    fileData = open(FILESTEM,'r').read()
    tester.compare(file_expected_1, fileData)
    tester.testDone()
    if os.path.exists(FILESTEM):
        os.unlink(FILESTEM)

    return
