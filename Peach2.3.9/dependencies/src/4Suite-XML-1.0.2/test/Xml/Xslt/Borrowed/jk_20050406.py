#See http://bugs.4suite.org/1180509
import tempfile, os
from Ft.Lib import Uri
from Xml.Xslt import test_harness

SHEET_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:exsl="http://exslt.org/common"
extension-element-prefixes="exsl"
exclude-result-prefixes="exsl">

<xsl:output method="html" indent="no"/>

<xsl:param name="URL" select="'%s'"/>

<xsl:template match="/">
<exsl:document href="{$URL}"
method ="html"
version ="-//W3C//DTD XHTML 1.1//EN"

doctype-public="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"
indent="%s">
<html>
<head>
<title>test</title>
</head>
<body>
<p>hello world</p>
</body>
</html>
</exsl:document>
</xsl:template>

</xsl:stylesheet>"""


EXPECTED = ""

EXPECTED_FILE_1 = '<!DOCTYPE html PUBLIC "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n<html><head><meta content="text/html; charset=iso-8859-1" http-equiv="Content-Type"><title>test</title></head><body><p>hello world</p></body></html>'

EXPECTED_FILE_2 = '<!DOCTYPE html PUBLIC "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n<html>\n  <head>\n    <meta content="text/html; charset=iso-8859-1" http-equiv="Content-Type">\n    <title>test</title>\n  </head>\n  <body>\n    <p>hello world</p>\n  </body>\n</html>'

def Test(tester):
    tester.startGroup('EXSLT exsl:document and indent')

    fname = tempfile.mktemp()
    furi = Uri.OsPathToUri(fname)

    source = test_harness.FileInfo(string="<dummy/>")
    sheet = test_harness.FileInfo(string=SHEET_1%(furi, "no"))

    test_harness.XsltTest(tester, source, [sheet], EXPECTED,
                          title='run transform')
    tester.startTest("With indent='no'")
    tester.compare(True, os.path.exists(fname))
    file = open(fname, 'r')
    fcontent = file.read()
    file.close()
    tester.compare(EXPECTED_FILE_1, fcontent)
    os.unlink(fname)
    tester.testDone()

    fname = tempfile.mktemp()
    furi = Uri.OsPathToUri(fname)

    source = test_harness.FileInfo(string="<dummy/>")
    sheet = test_harness.FileInfo(string=SHEET_1%(furi, "yes"))

    test_harness.XsltTest(tester, source, [sheet], EXPECTED,
                          title='run transform')
    tester.startTest("With indent='yes'")
    tester.compare(True, os.path.exists(fname))
    file = open(fname, 'r')
    fcontent = file.read()
    file.close()
    tester.compare(EXPECTED_FILE_2, fcontent)
    os.unlink(fname)
    tester.testDone()

    tester.groupDone()

    return

