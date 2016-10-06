from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
version="1.0">
<xsl:template match="@*|node()">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>
</xsl:stylesheet>
"""


expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<?xml-stylesheet href="addr_book1.xsl" type="text/xml"?>
<ADDRBOOK>
    <ENTRY ID='pa'>
        <NAME>Pieter Aaron</NAME>
        <ADDRESS>404 Error Way</ADDRESS>
        <PHONENUM DESC='Work'>404-555-1234</PHONENUM>
        <PHONENUM DESC='Fax'>404-555-4321</PHONENUM>
        <PHONENUM DESC='Pager'>404-555-5555</PHONENUM>
        <EMAIL>pieter.aaron@inter.net</EMAIL>
    </ENTRY>
    <ENTRY ID='en'>
        <NAME>Emeka Ndubuisi</NAME>
        <ADDRESS>42 Spam Blvd</ADDRESS>
        <PHONENUM DESC='Work'>767-555-7676</PHONENUM>
        <PHONENUM DESC='Fax'>767-555-7642</PHONENUM>
        <PHONENUM DESC='Pager'>800-SKY-PAGEx767676</PHONENUM>
        <EMAIL>endubuisi@spamtron.com</EMAIL>
    </ENTRY>
    <ENTRY ID='vz'>
        <NAME>Vasia Zhugenev</NAME>
        <ADDRESS>2000 Disaster Plaza</ADDRESS>
        <PHONENUM DESC='Work'>000-987-6543</PHONENUM>
        <PHONENUM DESC='Cell'>000-000-0000</PHONENUM>
        <EMAIL>vxz@magog.ru</EMAIL>
    </ENTRY>
</ADDRBOOK>"""

sheet_2 = """\
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
version="1.0">

<xsl:template match="foo">
  <xsl:copy/>
</xsl:template>

</xsl:stylesheet>"""

source_2 = """\
<foo a="1" b="2">
  <?foobar baz?>
  <bar/>
</foo>
"""

expected_2 = """<?xml version="1.0" encoding="UTF-8"?>
<foo/>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='xsl:copy')


    source = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xml')
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title="Identity transform")
    return
