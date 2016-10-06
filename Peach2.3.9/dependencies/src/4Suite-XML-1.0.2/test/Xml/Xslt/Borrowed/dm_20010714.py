#Dieter Maurer <dieter@handshake.de> reports problems with xsl:text and pre tag output

from Xml.Xslt import test_harness

sheet_1 = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version='1.0'>

  <xsl:output method="html"/>
  <xsl:strip-space elements="*"/>
  
  <xsl:template match="/">
    <html><xsl:apply-templates/></html>
  </xsl:template>

  <xsl:template match="cmdsynopsis/command[1]">
    <xsl:call-template name="inline.monoseq"/>
    <xsl:text> </xsl:text>
  </xsl:template>

  <xsl:template name="inline.monoseq">
    <tt>if</tt>
  </xsl:template>

</xsl:stylesheet>"""

source_1 = """\
<cmdsynopsis sepchar=" ">
  <command>if</command>
  <arg choice="plain" rep="norepeat">true_body</arg>
  <text> ... </text>
</cmdsynopsis>"""


expected_1 = """\
<html><tt>if</tt> true_body ... </html>"""


sheet_2 = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version='1.0'>

  <xsl:output method="xml"/>
  <xsl:strip-space elements="*"/>
  
  <xsl:template match="/">
    <html><xsl:apply-templates/></html>
  </xsl:template>

  <xsl:template match="cmdsynopsis/command[1]">
    <xsl:call-template name="inline.monoseq"/>
    <xsl:text> </xsl:text>
  </xsl:template>

  <xsl:template name="inline.monoseq">
    <tt>if</tt>
  </xsl:template>

</xsl:stylesheet>"""

source_2 = """\
<cmdsynopsis sepchar=" ">
  <command>if</command>
  <arg choice="plain" rep="norepeat">true_body</arg>
  <text> ... </text>
</cmdsynopsis>"""


expected_2 = """\
<?xml version='1.0' encoding='UTF-8'?>
<html><tt>if</tt> true_body ... </html>"""


sheet_3 = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version='1.0'>

  <xsl:output method="html"/>
  
  <xsl:template match="/">
    <html>
    <head><title>Hello</title></head>
    <body><p>
      <pre>
Testing
Testing
123
      </pre>
    </p></body>
    </html>
  </xsl:template>

</xsl:stylesheet>"""

source_3 = "<dummy/>"

expected_3 = """\
<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <title>Hello</title>
  </head>
  <body>
    <p>
      <pre>\nTesting\nTesting\n123\n      </pre>
    </p>
  </body>
</html>"""



def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='xsl:text in html mode')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='xsl:text in xml mode')

    source = test_harness.FileInfo(string=source_3)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='problems with PRE tag')
    return

