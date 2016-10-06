#Uche Ogbuji tries a substitute reader

# jkloth 2002-09-26:
#   Removed unused substitute reader code as this is now done through
#   InputSources and is tested in other locations (not to mention the code
#   was *really* out of date)

from Xml.Xslt import test_harness

sheet_1 = """\
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:output method='text'/>

  <xsl:template match = "/">
    <xsl:value-of select='name(/*)'/>
    <xsl:text>&#10;</xsl:text>
    <xsl:value-of select='name(document("http://4suite.org/4Suite.xsa")/*)'/>
    <xsl:text>&#10;</xsl:text>
  </xsl:template>

</xsl:stylesheet>"""

source_1 = "<spam/>"

expected_1 = "spam\nxsa\n"

def Test(tester):
    tester.startTest("Connect to Internet")
    import urllib
    try:
        if not tester.offline:
            urllib.urlopen('http://fourthought.com/')
        else:
            raise IOError
    except IOError:
        tester.warning("Unable to connect to internet")
        tester.testDone()
        return
    tester.testDone()

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='document() with ext. URI (requires Internet access)')
    return
