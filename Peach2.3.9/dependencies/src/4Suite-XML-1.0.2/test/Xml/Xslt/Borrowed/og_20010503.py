#Oliver Graf <ograf@oli-ver-ena.de> has indentation probs with ft:write-file

import os, tempfile
from Ft.Lib.Uri import OsPathToUri
from Xml.Xslt import test_harness

BASENAME = tempfile.mktemp()
BASENAME_URI = OsPathToUri(BASENAME)

sheet_1 = """\
<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
    xmlns:exsl="http://exslt.org/common"
    extension-element-prefixes="exsl">

<xsl:output method="text" encoding="ISO-8859-1"/>

<xsl:template match="/">
  <xsl:apply-templates select="test/data"/>
</xsl:template>

<xsl:template match="data">
  <xsl:variable name="file" select="concat('%s',.,'.xml')"/>
  <exsl:document href="{$file}" method="xml" indent="yes" encoding="ISO-8859-1">
    <datatree>
      <name><xsl:value-of select="."/></name>
      <what>test</what>
    </datatree>
  </exsl:document>
</xsl:template>

</xsl:stylesheet>""" % BASENAME_URI


source_1 = """\
<?xml version="1.0" encoding="ISO-8859-1"?>

<test>
  <data>11</data>
  <data>12</data>
  <data>13</data>
  <data>14</data>
  <data>15</data>
</test>
"""

expected_1 = ""

file_expected = """<?xml version="1.0" encoding="ISO-8859-1"?>
<datatree>
  <name>%s</name>
  <what>test</what>
</datatree>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)

    for num in range(11,16):
        tester.startTest('File output - %d.xml' % num)
        file = '%s%d.xml' % (BASENAME, num)
        if os.path.exists(file):
            actual = open(file).read()
            os.unlink(file)
            tester.compare(file_expected % num, actual)
        else:
            tester.error("ft:write-file %d.xml doesn't exist" % num)
        tester.testDone()
    return
