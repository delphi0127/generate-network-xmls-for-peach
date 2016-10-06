#Sebastian Pierre's problem with xsl:number and multiple

from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?> 
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="Document">
        <html><body>
        <h1>XSL Numbering test</h1>
        <blockquote>
            <xsl:apply-templates select="*"/>
        </blockquote>
        </body></html>
    </xsl:template>
    
    <xsl:template match="Topic|Section">
        <p>For <xsl:value-of select="name"/> '<xsl:value-of select="@name"/>':
            <ul>
                <li>'single' number = <xsl:number level="single"/></li>
                <li>'multiple' number = <xsl:number level="multiple" format='1.'/></li>
                <li>'any' number = <xsl:number level="any"/></li>
            </ul>
        </p>
        <xsl:apply-templates select="*"/>
    </xsl:template>
    
</xsl:stylesheet>"""

source_1 = """<?xml version="1.0"?>

<Document>

        <Topic>
                <Section name="1">
                <p>Blah</p>
                <p>Blah</p>
                <p>Blah</p>
                        <Section name="1.a">
                        <p>Nojasdsa</p>
                                <Section name="1.a.a">
                                <p>BKjasda</p>
                                </Section>
                                <Section name="1.a.b">
                                <p>BKjasda</p>
                                </Section>
                        </Section>
                        <Section name="1.b">
                                <p>kjhkdsfsdfd</p>
                        </Section>
                </Section>
                <p>Blah</p>
                <p>Blah</p>
                <p>Blah</p>
                <Section name="2">
                        <p>Blah</p>
                </Section>
        </Topic>

        <Topic>
                <p>Blah</p>
                <Section name="1">
                <p>Blah</p>
                </Section>
        </Topic>
        
</Document>"""

expected_1 = """<html>
  <body>
    <h1>XSL Numbering test</h1>
    <blockquote>
      <p>For  '':
            <ul>
          <li>'single' number = 1</li>
          <li>'multiple' number = 1.</li>
          <li>'any' number = 1</li>
        </ul>
      </p>
      <p>For  '1':
            <ul>
          <li>'single' number = 1</li>
          <li>'multiple' number = 1.</li>
          <li>'any' number = 1</li>
        </ul>
      </p>BlahBlahBlah
      <p>For  '1.a':
        <ul>
          <li>'single' number = 1</li>
          <li>'multiple' number = 1.1.</li>
          <li>'any' number = 2</li>
        </ul>
      </p>Nojasdsa
      <p>For  '1.a.a':
        <ul>
          <li>'single' number = 1</li>
          <li>'multiple' number = 1.1.1.</li>
          <li>'any' number = 3</li>
        </ul>
      </p>BKjasda
      <p>For  '1.a.b':
        <ul>
          <li>'single' number = 2</li>
          <li>'multiple' number = 1.1.2.</li>
          <li>'any' number = 4</li>
        </ul>
      </p>BKjasda
      <p>For  '1.b':
        <ul>
          <li>'single' number = 2</li>
          <li>'multiple' number = 1.2.</li>
          <li>'any' number = 5</li>
        </ul>
      </p>kjhkdsfsdfdBlahBlahBlah
      <p>For  '2':
        <ul>
          <li>'single' number = 2</li>
          <li>'multiple' number = 2.</li>
          <li>'any' number = 6</li>
        </ul>
      </p>Blah                
      <p>For  '':
        <ul>
          <li>'single' number = 2</li>
          <li>'multiple' number = 2.</li>
          <li>'any' number = 2</li>
        </ul>
      </p>Blah
      <p>For  '1':
        <ul>
          <li>'single' number = 1</li>
          <li>'multiple' number = 1.</li>
          <li>'any' number = 7</li>
        </ul>
      </p>Blah
    </blockquote>
  </body>
</html>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
