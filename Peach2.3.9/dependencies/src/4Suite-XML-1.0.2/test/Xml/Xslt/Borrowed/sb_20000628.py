#Steve Brown <prospect@flex.com.au> on 28 July 2000 posted what he felt was a bug in Xalan.  David Carlisle later confirmed it was a bug pointing out the correct output from XT

from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

<xsl:template match="list">
    <xsl:apply-templates select="item[@include='yes']"/>
</xsl:template>

<xsl:template match="item">
    *<xsl:value-of select="@a"/>*
    position = <xsl:value-of select="position()"/>
    last = <xsl:value-of select="last()"/>
</xsl:template>

</xsl:stylesheet>"""


source_1 = """<?xml version="1.0"?>
<list>
    <item a="1" include="yes"/>
    <item a="2" include="no"/>
    <item a="3" include="no"/>
    <item a="4" include="no"/>
    <item a="5" include="yes"/>
    <item a="6" include="yes"/>
    <item a="7" include="yes"/>
</list>"""


expected_1 = """<?xml version="1.0" encoding="UTF-8"?>

    *1*
    position = 1
    last = 4
    *5*
    position = 2
    last = 4
    *6*
    position = 3
    last = 4
    *7*
    position = 4
    last = 4"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
