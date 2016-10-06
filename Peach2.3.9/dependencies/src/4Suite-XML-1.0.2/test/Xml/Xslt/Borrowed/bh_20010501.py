#Brent Hendricks <brentmh@ece.rice.edu> spots an import precedence problem

##I've been looking at the 4suite package (4xslt in particular).  Let me
##first say that so far I am impressed with its speed and adherance to
##the XSLT spec.

##I did find a bug, however, regarding import precedence.  Suppose you
##have an "outer" stylesheets that imports two "inner" stylesheets as in
##the following:

##<xsl:import href="inner1.xsl"/>
##<xsl:import href="inner2.xsl"/>

##According to the XSLT spec, elements in inner2 should have a higher
##import precedence than elements in inner1.  It appears to me that
##4xslt is giving elements in inner2 a *lower* precedence.

##I'm attaching an example that demonstrates this behavior.  Both
##inner1.xsl and inner2.xsl match the document tag in test.xml.  inner1
##outputs the word "Failure" and inner2 outputs the word "Success".
##outer.xsl imports inner1 and then inner2.

##When you apply outer.xsl to test.xml with 4xslt, you will get the word
##"Failure" indicating that the template in inner1 was applied.  The
##expected behavior is to see the word "Success" indicating that the
##template inner2 was applied.


from Xml.Xslt import test_harness

sheet_1 = """\
<?xml version= "1.0"?>
                            
<xsl:stylesheet
  version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="Xml/Xslt/Borrowed/bh_20010501-inner1.xslt"/>
  <xsl:import href="Xml/Xslt/Borrowed/bh_20010501-inner2.xslt"/>

  <xsl:output omit-xml-declaration="yes"/>

  <xsl:template match="/">
    <xsl:apply-templates/>
  </xsl:template>
  
</xsl:stylesheet>
"""

source_1 = "<document/>"


expected_1 = """
    Success
  """


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='import/variable problems')
    return
