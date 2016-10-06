# -*- coding: iso-8859-1 -*-
#See http://lists.fourthought.com/pipermail/4suite/2002-July/003976.html et seq.
from Xml.Xslt import test_harness

SHEET_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html"/>
  <xsl:template match="/">
    <html>
      <head/>
      <body name="{.}"/>
    </html>
  </xsl:template>
</xsl:stylesheet>
"""

SHEET_2 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html"/>
  <xsl:template match="/">
    <html>
      <head/>
      <body background="{.}"/>
    </html>
  </xsl:template>
</xsl:stylesheet>
"""

SHEET_3 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="ISO-8859-1"/>
  <xsl:template match="/">
    <link title="{.}"></link>
  </xsl:template>
</xsl:stylesheet>
"""

SHEET_4 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <link title="{.}"></link>
  </xsl:template>
</xsl:stylesheet>
"""

SOURCE_1 = """<?xml version="1.0" encoding="ISO-8859-1"?>
<test>Baron Münchausen</test>
"""

EXPECTED_1 = "<html>\n  <head>\n    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>\n  </head>\n  <body name='Baron M&uuml;nchausen'></body>\n</html>"


EXPECTED_2 = "<html>\n  <head>\n    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>\n  </head>\n  <body background='Baron M%C3%BCnchausen'></body>\n</html>"


EXPECTED_3 = """<?xml version="1.0" encoding="ISO-8859-1"?>\n<link title='Baron Münchausen'></link>"""


EXPECTED_4 = """<?xml version="1.0" encoding="UTF-8"?>\n<link title='Baron M\xC3\xBCnchausen'></link>"""


def Test(tester):
    source = test_harness.FileInfo(string=SOURCE_1)
    sheet = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_1,
                          title=("ISO-8859-1 input emitted in an HTML "
                                 "attribute."),
                          )

    sheet = test_harness.FileInfo(string=SHEET_2)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_2,
                          title=("ISO-8859-1 input emitted in an HTML URI "
                                 "attribute."),
                          )

    sheet = test_harness.FileInfo(string=SHEET_3)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_3,
                          title=("ISO-8859-1 input emitted in an XML attribute"
                                 " as ISO-8859-1."),
                          )

    sheet = test_harness.FileInfo(string=SHEET_4)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_4,
                          title=("ISO-8859-1 input emitted in an XML attribute"
                                 " as UTF-8."),
                          )
    return

