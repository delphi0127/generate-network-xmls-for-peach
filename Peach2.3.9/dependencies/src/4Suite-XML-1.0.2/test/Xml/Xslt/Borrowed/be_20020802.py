from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="junk">Some Junk
</xsl:template>
</xsl:stylesheet>
"""
        
source_1 = """<?xml version="1.0"?>
<?xml-stylesheet version="1.0" type="text/xsl" href="junk.xsl"?>
<!DOCTYPE junk [ <!ELEMENT junk ANY> ]>
<junk>Blah</junk>
"""

source_2 = """<?xml version="1.0"?>
<!DOCTYPE junk [ <!ELEMENT junk ANY> ]>
<junk>Just some text </junk>
"""

source_3 = """<?xml version="1.0"?>
<!DOCTYPE junk [ <!ELEMENT junk (morejunk)><!ELEMENT morejunk ANY> ]>
<junk><morejunk>Still more junk</morejunk></junk>
"""

expected_1 = """<?xml version="1.0" encoding="UTF-8"?>\nSome Junk\n"""


def Test(tester):
    tester.startGroup("Bill Ellridge had trouble with validation")

    source = test_harness.FileInfo(string=source_1, validate=1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1, ignorePis=0)

    source = test_harness.FileInfo(string=source_2, validate=1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)

    source = test_harness.FileInfo(string=source_3, validate=1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)

    tester.groupDone()
    return

