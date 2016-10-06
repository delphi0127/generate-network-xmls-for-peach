
"""
Mike Brown reported a problem with minidom and children nodes
"""

from Xml.Xslt import test_harness


source_1="""<?xml version="1.0" encoding="utf-8"?>
<doc>
<elem xmlns:unused="urn:uuu000"/>
<elem xmlns="urn:sss111"/>
<y:elem xmlns:y="urn:yyyy222"/>
</doc>"""



sheet_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="xml" indent="no"/>

<xsl:template match="/">
<result xmlns:new="urn:added-by-stylesheet">
<xsl:text>&#10;</xsl:text>
<r>total nodes: <xsl:value-of select="count(//node()
|//node()/namespace::node())"/></r>
<xsl:text>&#10;</xsl:text>
<r>copy:&#10;<xsl:copy-of select="."/></r>
</result>
</xsl:template>

</xsl:stylesheet>
"""

expected = """<?xml version="1.0" encoding="utf-8"?>
<result xmlns:new="urn:added-by-stylesheet">
<r>total nodes: 15</r>
<r>copy:
<doc>
<elem xmlns:unused="urn:uuu000"/>
<elem xmlns="urn:sss111"/>
<y:elem xmlns:y="urn:yyyy222"/>
</doc></r></result>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='Descendants of different node types')
    return

