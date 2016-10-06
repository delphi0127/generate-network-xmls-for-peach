#Example from David Carlisle to ??? on 10 Feb 2000, with well-formedness corrections
#With a few added variations for more testing

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 version="1.0"
>

<xsl:template match="/a">
  <foo><xsl:value-of select="translate(.,'&#10; ','')"/></foo>
</xsl:template>

</xsl:stylesheet>"""


source_1="""<?xml version="1.0"?>
<a>
1 2
3 4
5 6
</a>"""


expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<foo>123456</foo>"""


#Note: this one is tricky.  We have the default namespace in exclude-result
#So it shouldn't appear, right?  Wrong.  The literal result element output
#by the template is actually in the http://duncan.com ns by virtue of default
#So it must be declared as such in the output.

sheet_2 = """<xsl:stylesheet
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:boo="http://banquo.com"
 xmlns="http://duncan.com"
 exclude-result-prefixes='#default boo'
 version="1.0"
>

<xsl:template match="/boo:a">
  <foo><xsl:value-of select="translate(.,'&#10; ','')"/></foo>
</xsl:template>

</xsl:stylesheet>"""


source_2 = """<?xml version="1.0"?>
<boo:a xmlns:boo="http://banquo.com">
1 2
3 4
5 6
</boo:a>"""


expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<foo xmlns='http://duncan.com'>123456</foo>"""


sheet_3 = """<xsl:stylesheet
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:boo="http://banquo.com"
 xmlns="http://duncan.com"
 version="1.0"
>

<xsl:template match="/boo:a">
  <foo><xsl:value-of select="translate(.,'&#10; ','')"/></foo>
</xsl:template>

</xsl:stylesheet>"""


source_3 = """<?xml version="1.0"?>
<boo:a xmlns:boo="http://banquo.com">
1 2
3 4
5 6
</boo:a>"""


expected_3 = """<?xml version='1.0' encoding='UTF-8'?>
<foo xmlns:boo='http://banquo.com' xmlns='http://duncan.com'>123456</foo>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='test 1')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='test 2')

    source = test_harness.FileInfo(string=source_3)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='test 3')
    return
