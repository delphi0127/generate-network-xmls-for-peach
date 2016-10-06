#Tamito KAJIYAMA <kajiyama@grad.sccs.chukyo-u.ac.jp> caught us forgetting to encode comment and PI output

import sys
from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" encoding="iso-8859-1"/>

<xsl:template match="para">
<para><xsl:value-of select="."/></para>
</xsl:template>

<xsl:template match="note">
<xsl:comment><xsl:value-of select="."/></xsl:comment>
</xsl:template>

</xsl:stylesheet>"""

source_1 = """\
<?xml version='1.0' encoding='iso-8859-1'?>
<doc>
<para>H\344agen-Dazs</para>
<note>H\344agen-Dazs</note>
</doc>"""

expected_1 = """<?xml version='1.0' encoding='iso-8859-1'?>\012\012<para>H\344agen-Dazs</para>\012<!--H\344agen-Dazs-->\012"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
