#Olivier Cayrol <olivier.cayrol@logilab.fr> reports xsl:text bug
#See https://sourceforge.net/bugs/?func=detailbug&bug_id=123172&group_id=6473

from Xml.Xslt import test_harness

sheet_1 = """\
<?xml version="1.0" encoding="ISO-8859-1" standalone="yes" ?> 

                            <xsl:stylesheet 
                            xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                            version="1.0" 
                            > 

                            <xsl:output method="html" encoding="ISO-8859-1"/> 

                            <xsl:template match="/"> 
                            <html> 
                            <head> 
                            <title>Address Book Test</title> 
                            </head> 
                            <body> 
                            <xsl:apply-templates/> 
                            </body> 
                            </html> 
                            </xsl:template> 
                            <xsl:template match="addressbook"> 
                            <p>My friends are: 
                            <ul> 
                            <xsl:apply-templates/> 
                            </ul> 
                            </p> 
                            </xsl:template> 

                            <xsl:template match="entry"> 
                            <li> 
                            <xsl:value-of select="firstname"/><xsl:text> </xsl:text> 
                            <xsl:value-of select="lastname"/> 
                            </li> 
                            </xsl:template> 

                            </xsl:stylesheet>"""


source_1 = """\
<?xml version="1.0" standalone="yes"?> 

                            <!DOCTYPE addressbook > 

                            <addressbook> 
                            <entry> 
                            <firstname>Alexandre</firstname> 
                            <lastname>FAYOLLE</lastname> 
                            </entry> 
                            <entry> 
                            <firstname>Nicolas</firstname> 
                            <lastname>CHAUVAT</lastname> 
                            </entry> 
                            </addressbook>"""

expected_1 = """\
<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=ISO-8859-1'>
    <title>Address Book Test</title>
  </head>
  <body>
    <p>My friends are: 
                            <ul>
        <li>Alexandre FAYOLLE</li>
        <li>Nicolas CHAUVAT</li>
      </ul>
    </p>
  </body>
</html>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
