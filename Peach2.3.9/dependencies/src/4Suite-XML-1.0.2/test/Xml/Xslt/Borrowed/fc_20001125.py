# -*- coding: ISO-8859-1 -*-
#Alex Reutter <areutter@spss.com> finds brokenness in text output method

import sys
from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0"
>

  <xsl:output encoding="UTF-8"/>
  
  <xsl:template match="Book">
    <html>
      <head>
        <title><xsl:value-of select="Title" /></title>
      </head>
      <body>
        <ul>
        <li><xsl:value-of select="Chapter" /></li>
        <li><xsl:value-of select="Chapter" /></li>
        </ul>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>"""

source_1 = """<?xml version="1.0"?>
<?xml-stylesheet href="book.html.xsl" type="text/xsl"?>
<!DOCTYPE Book [
<!ELEMENT Book (Title, Chapter+)>
<!ATTLIST Book Author CDATA #REQUIRED>
<!ELEMENT Title (#PCDATA)>
<!ELEMENT Chapter (#PCDATA)>
<!ATTLIST Chapter id CDATA #REQUIRED>
]>

<Book Author="³¯«Ø¾±">
 <Title>¤@¥»®Ñ</Title>
  <Chapter id="1">
    ³o¬O²Ä¤@³¹. &#24179;
  </Chapter>
  <Chapter id="2">
    ³o¬O²Ä¤G³¹. &#24179;
  </Chapter>
</Book>"""

source_2 = """<?xml version="1.0"?>\012<?xml-stylesheet href="book.html.xsl" type="text/xsl"?>\012<!DOCTYPE Book [\012<!ELEMENT Book (Title, Chapter+)>\012<!ATTLIST Book Author CDATA #REQUIRED>\012<!ELEMENT Title (#PCDATA)>\012<!ELEMENT Chapter (#PCDATA)>\012<!ATTLIST Chapter id CDATA #REQUIRED>\012]>\012\012<Book Author="\351\231\263\345\273\272\345\213\263">\012 <Title>\344\270\200\346\234\254\346\233\270</Title>\012  <Chapter id="1">\012    \351\200\231\346\230\257\347\254\254\344\270\200\347\253\240. &#24179;\012  </Chapter>\012  <Chapter id="2">\012    \351\200\231\346\230\257\347\254\254\344\272\214\347\253\240. &#24179;\012  </Chapter>\012</Book>"""
                 
expected_1 = expected_2 = """<html>\012  <head>\012    <META HTTP-EQUIV='Content-Type' CONTENT='text/html; charset=UTF-8'>\012    <title>\344\270\200\346\234\254\346\233\270</title>\012  </head>\012  <body>\012    <ul>\012      <li>\012    \351\200\231\346\230\257\347\254\254\344\270\200\347\253\240. \345\271\263\012  </li>\012      <li>\012    \351\200\231\346\230\257\347\254\254\344\270\200\347\253\240. \345\271\263\012  </li>\012    </ul>\012  </body>\012</html>"""


def Test(tester):
    tester.startTest("Checking for BIG5 codec")
    try:
        import codecs
        big5_decoder = codecs.getdecoder('big5')
    except LookupError:
        try:
            from encodings import big5
        except ImportError:
            tester.warning(
                "No BIG5 encoding support for case 1.  You can install \n"
                "BIG5 by downloading and installing ChineseCodes from\n"
                "ftp://python-codecs.sourceforge.net/pub/python-codecs/")
            tester.testDone()
            return
        else:
            big5_decode = big5.decode
    else:
        big5_decode = lambda s: big5_decoder(s)[0]
    tester.testDone()
            
    b5 = big5_decode(source_1)
    utf8 = b5.encode("utf-8")
        
    source = test_harness.FileInfo(string=utf8)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_2)
    return
    
