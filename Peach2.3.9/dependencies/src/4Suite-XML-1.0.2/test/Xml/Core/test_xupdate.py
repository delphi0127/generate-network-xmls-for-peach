from Ft.Lib import TestSuite
from Ft.Xml import XUpdate
from Ft.Xml import Domlette, InputSource
from Ft.Xml.Lib import TreeCompare
import cStringIO

# this first test is from the spec
# (http://www.xmldb.org/xupdate/xupdate-wd.html)
# "Example of Usage" section

src_1 = """\
<?xml version="1.0"?>
<addresses version="1.0">

  <address id="1">
    <fullname>Andreas Laux</fullname>
    <born day='1' month='12' year='1978'/>
    <town>Leipzig</town>
    <country>Germany</country>
  </address>

</addresses>
"""

xu_1 = """\
<?xml version="1.0"?>
<xupdate:modifications
  version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
>

  <xupdate:insert-after select="/addresses/address[1]" >

    <xupdate:element name="address">
      <xupdate:attribute name="id">2</xupdate:attribute>
      <fullname>Lars Martin</fullname>
      <born day='2' month='12' year='1974'/>
      <town>Leizig</town>
      <country>Germany</country>
    </xupdate:element>
  </xupdate:insert-after>

</xupdate:modifications>
"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<addresses version='1.0'>

  <address id='1'>
    <fullname>Andreas Laux</fullname>
    <born day='1' month='12' year='1978'/>
    <town>Leipzig</town>
    <country>Germany</country>
  </address><address id='2'><fullname>Lars Martin</fullname><born day='2' month='12' year='1974'/><town>Leizig</town><country>Germany</country></address>

</addresses>"""

src_2 = """\
<?xml version="1.0"?>
<addresses>
  <address>
    <town>Los Angeles</town>
  </address>
</addresses>
"""

xu_2 = """\
<?xml version="1.0"?>
<xupdate:modifications
  version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
>

  <xupdate:append select="/addresses" child="last()">
    <xupdate:element name="address">
      <town>San Francisco</town>
    </xupdate:element>
  </xupdate:append>

</xupdate:modifications>
"""

expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<addresses>
  <address>
    <town>Los Angeles</town>
  </address>
<address><town>San Francisco</town></address></addresses>"""

src_3 = """\
<?xml version="1.0"?>
<addresses>
  <address>
    <town>Los Angeles</town>
  </address>
  <address>
    <town>San Francisco</town>
  </address>
</addresses>
"""

xu_3 = """\
<?xml version="1.0"?>
<xupdate:modifications
  version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
>

  <xupdate:update select="/addresses/address[2]/town">
    New York
  </xupdate:update>

</xupdate:modifications>
"""

expected_3 = """<?xml version='1.0' encoding='UTF-8'?>
<addresses>
  <address>
    <town>Los Angeles</town>
  </address>
  <address>
    <town>
    New York
  </town>
  </address>
</addresses>"""

src_4 = src_3

xu_4 = """\
<?xml version="1.0"?>
<xupdate:modifications
  version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
>

  <xupdate:remove select="/addresses/address[1]"/>

</xupdate:modifications>
"""

expected_4 = """<?xml version='1.0' encoding='UTF-8'?>
<addresses>
__
  <address>
    <town>San Francisco</town>
  </address>
</addresses>""".replace('_', ' ')

src_5 = """<ftss:Container xmlns:ftss="http://xmlns.4suite.org/reserved">
  <ftss:Children/>
</ftss:Container>"""


xu_5 = """\
<?xml version="1.0"?>
<xupdate:modifications
  version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
  xmlns:ftss="http://xmlns.4suite.org/reserved"
  xmlns:xlink="http://www.w3.org/1999/xlink"
>
<xupdate:append select="(ftss:Repository | ftss:Container)/ftss:Children" child="last()">
    <ftss:ChildReference xlink:type="simple" xlink:actuate="onLoad" xlink:show="embed">
      <xupdate:attribute name='xlink:href'><xupdate:value-of select='concat($child-name,";metadata")'/></xupdate:attribute>
    </ftss:ChildReference>
  </xupdate:append>
</xupdate:modifications>
"""

expected_5 = """<?xml version='1.0' encoding='UTF-8'?>
<ftss:Container xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:ftss='http://xmlns.4suite.org/reserved'>\n  <ftss:Children><ftss:ChildReference xlink:href='FOO;metadata' xlink:type='simple' xlink:actuate='onLoad' xlink:show='embed'/></ftss:Children>\n</ftss:Container>"""


# this is from the spec
# "Append" section

src_6 = """<?xml version="1.0" encoding="utf-8"?>
<addresses>
  <address>
    <town>Los Angeles</town>
  </address>
</addresses>
"""

xu_6 = """<?xml version="1.0" encoding="utf-8"?>
<xupdate:modifications version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
>
 <xupdate:append select="/addresses" child="last()">
   <xupdate:element name="address">
     <town>San Francisco</town>
   </xupdate:element>
 </xupdate:append>
</xupdate:modifications>
"""

expected_6 = """<?xml version="1.0" encoding="UTF-8"?>
<addresses>
  <address>
    <town>Los Angeles</town>
  </address>
<address><town>San Francisco</town></address></addresses>
"""

# The following was posted on SourceForge as bug #704627
# (attributes were not being appended properly)

src_7 = "<?xml version='1.0'?><test><t id='t1'>one</t><t id='t2'>two</t></test>"

xu_7 = """<?xml version="1.0"?>
<xu:modifications version="1.0" xmlns:xu="http://www.xmldb.org/xupdate">
    <xu:append select="/test"><xu:attribute name="a1">a1v</xu:attribute></xu:append>
</xu:modifications>"""

expected_7 = """<?xml version="1.0" encoding="UTF-8"?>
<test a1="a1v"><t id="t1">one</t><t id="t2">two</t></test>"""


usecase_src = """<?xml version="1.0" encoding="UTF-8"?>
<addresses>

   <address id="1">
      <!--This is the users name-->
      <name>
         <first>John</first>
         <last>Smith</last>
      </name>
      <city>Houston</city>
      <state>Texas</state>
      <country>United States</country>
      <phone type="home">333-300-0300</phone>
      <phone type="work">333-500-9080</phone>
      <note><![CDATA[This is a new user]]></note>
   </address>

</addresses>"""

usecase_4 = """<?xml version="1.0" encoding="UTF-8"?>
<xupdate:modifications version="1.0" xmlns:xupdate="http://www.xmldb.org/xupdate">
   <xupdate:append select="/addresses/address[@id = 1]/phone[@type='work']">
      <xupdate:attribute name="extension">223</xupdate:attribute>
   </xupdate:append>
</xupdate:modifications>"""

usecase_expected_4 = """<?xml version="1.0" encoding="UTF-8"?>
<addresses>

   <address id="1">
      <!--This is the users name-->
      <name>
         <first>John</first>
         <last>Smith</last>
      </name>
      <city>Houston</city>
      <state>Texas</state>
      <country>United States</country>
      <phone type="home">333-300-0300</phone>
      <phone type="work" extension="223">333-500-9080</phone>
      <note><![CDATA[This is a new user]]></note>
   </address>

</addresses>"""

# rename tests based partly on SF bug #704627 and
# http://lists.fourthought.com/pipermail/4suite/2002-November/004602.html
#
xu_rename_src = """<?xml version="1.0" encoding="utf-8"?>
<addresses version="1.0">

  <address id="1">
    <fullname>Andreas Laux</fullname>
    <born day="1" month="12" year="1978"/>
    <town>Leipzig</town>
    <country>Germany</country>
  </address>

  <address id="2">
    <fullname>Heiko Smit</fullname>
    <born day="4" month="8" year="1970"/>
    <town>Berlin</town>
    <country>Germany</country>
  </address>

  <address id="3">
    <fullname>Vincent Q. Lu</fullname>
    <born day="9" month="9" year="1990"/>
    <town>Hong Kong</town>
    <country>China</country>
  </address>

  <address id="4">
    <fullname>Michelle Lambert</fullname>
    <born day="10" month="10" year="1958"/>
    <town>Toronto</town>
    <country>Canada</country>
  </address>

</addresses>"""

xu_rename = """<?xml version="1.0" encoding="UTF-8"?>
<xupdate:modifications version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
  xmlns:my="urn:bogus:myns">

  <!-- rename of an element -->
  <xupdate:rename select="/addresses/address[@id='1']/town">city</xupdate:rename>

  <!-- rename of an attribute -->
  <xupdate:rename select="/addresses/address[@id='1']/born/@year">annum</xupdate:rename>

  <!-- rename of document element -->
  <xupdate:rename select="/addresses">info</xupdate:rename>

  <!-- rename of multiple elements -->
  <xupdate:rename select="/*/address">data</xupdate:rename>

  <!-- rename of multiple attributes (1 per element) -->
  <xupdate:rename select="/*/*/@id[. > 1 and . &lt; 4]">num</xupdate:rename>

  <!-- rename of multiple attributes (all in same element) -->
  <xupdate:rename select="/*/*[@id='4']/born/@*[name()='day' or name()='month']">zzz</xupdate:rename>

  <!-- rename of renamed element -->
  <xupdate:rename select="/info">my:info</xupdate:rename>

  <!-- insert/append and rename of multiple elements -->
  <xupdate:insert-before select="/*/*[1]/born"><xupdate:element name="new-elem"/></xupdate:insert-before>
  <xupdate:insert-before select="/*/*[2]/born"><xupdate:element name="new-elem"/></xupdate:insert-before>
  <xupdate:insert-before select="/*/*[3]/born"><xupdate:element name="new-elem"/></xupdate:insert-before>
  <xupdate:insert-before select="/*/*[4]/born"><xupdate:element name="new-elem"/></xupdate:insert-before>
  <xupdate:rename select="/*/*/new-elem">my:new-elem</xupdate:rename>
  <xupdate:append select="/*/*" child="last()"><my:another-elem/></xupdate:append>
  <xupdate:rename select="/*/*/my:another-elem">my:other-elem</xupdate:rename>
  <xupdate:insert-after select="/*/*/my:other-elem"><xupdate:element name="my:foo"/></xupdate:insert-after>
</xupdate:modifications>"""

rename_expected = """<?xml version="1.0" encoding="UTF-8"?>
<my:info xmlns:my="urn:bogus:myns" version="1.0">

  <data id="1">
    <fullname>Andreas Laux</fullname>
    <my:new-elem/><born day="1" month="12" annum="1978"/>
    <city>Leipzig</city>
    <country>Germany</country>
  <my:other-elem/><my:foo/></data>

  <data num="2">
    <fullname>Heiko Smit</fullname>
    <my:new-elem/><born day="4" month="8" year="1970"/>
    <town>Berlin</town>
    <country>Germany</country>
  <my:other-elem/><my:foo/></data>

  <data num="3">
    <fullname>Vincent Q. Lu</fullname>
    <my:new-elem/><born day="9" month="9" year="1990"/>
    <town>Hong Kong</town>
    <country>China</country>
  <my:other-elem/><my:foo/></data>

  <data id="4">
    <fullname>Michelle Lambert</fullname>
    <my:new-elem/><born zzz="10" year="1958"/>
    <town>Toronto</town>
    <country>Canada</country>
  <my:other-elem/><my:foo/></data>

</my:info>
"""


# missing version attr
EXCEPTION_XUP_1 = """<?xml version="1.0"?>
<xupdate:modifications
  xmlns:xupdate="http://www.xmldb.org/xupdate"
>

  <xupdate:append select="/addresses" child="last()">
    <xupdate:element name="address">
      <town>San Francisco</town>
    </xupdate:element>
  </xupdate:append>

</xupdate:modifications>
"""

# missing select attr
EXCEPTION_XUP_2 = """<?xml version="1.0"?>
<xupdate:modifications
  version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
>

  <xupdate:append child="last()">
    <xupdate:element name="address">
      <town>San Francisco</town>
    </xupdate:element>
  </xupdate:append>

</xupdate:modifications>
"""

# invalid select
EXCEPTION_XUP_3 = """<?xml version="1.0"?>
<xupdate:modifications
  version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
>

  <xupdate:append select="/.." child="last()">
    <xupdate:element name="address">
      <town>San Francisco</town>
    </xupdate:element>
  </xupdate:append>

</xupdate:modifications>
"""

# syntax error
EXCEPTION_XUP_4 = """<?xml version="1.0"?>
<xupdate:modifications
  version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
>

  <xupdate:append select="!/addresses" child="last()">
    <xupdate:element name="address">
      <town>San Francisco</town>
    </xupdate:element>
  </xupdate:append>

</xupdate:modifications>
"""

# no "test" attr in xupdate:if
EXCEPTION_XUP_5 = """<?xml version="1.0"?>
<xupdate:modifications
  version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
>

  <xupdate:if>
    <xupdate:append select="/addresses" child="last()">
      <xupdate:element name="address">
        <town>San Francisco</town>
      </xupdate:element>
    </xupdate:append>
  </xupdate:if>

</xupdate:modifications>
"""

# unrecognized instruction
EXCEPTION_XUP_6 = """<?xml version="1.0"?>
<xupdate:modifications
  version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate"
>

  <xupdate:prepend select="/addresses" child="last()">
    <xupdate:element name="address">
      <town>San Francisco</town>
    </xupdate:element>
  </xupdate:prepend>

</xupdate:modifications>
"""

#-----------------------------------------------------------------------

xureader = XUpdate.Reader()

from urllib import quote
from Ft.Lib.Uri import OsPathToUri

def Test(tester):
    test_reader(tester, Domlette.NonvalParse)
    return

def test_reader(tester,srcReader):
    processor = XUpdate.Processor()

    # ------------------------------------------------------

    tester.startGroup('XUpdate instructions')
    for name, src, xuSrc, expected, vars_ in [
        ("XUpdate spec example 1", src_1, xu_1, expected_1, {}),
        ("Append", src_2, xu_2, expected_2, {}),
        ("Update", src_3, xu_3, expected_3, {}),
        ("Remove", src_4, xu_4, expected_4, {}),
        ("Attribute/Value-Of", src_5, xu_5, expected_5, {(None, 'child-name'):"FOO"}),
        ("XUpdate spec append example", src_6, xu_6, expected_6, {}),
        ("Append attribute 1", src_7, xu_7, expected_7, {}),
        ("XUpdate use case 4", usecase_src, usecase_4, usecase_expected_4, {}),
        ("Rename", xu_rename_src, xu_rename, rename_expected, {}),
        ]:
        tester.startTest(name)
        uri = OsPathToUri('xupdate-test-src-' + quote(name) + '.xml', attemptAbsolute=True)
        isrc = InputSource.DefaultFactory.fromString(src, uri)
        src = srcReader(isrc)
        uri = OsPathToUri('xupdate-test-xup-' + quote(name) + '.xml', attemptAbsolute=True)
        isrc = InputSource.DefaultFactory.fromString(xuSrc, uri)
        xu = xureader.fromSrc(isrc)

        processor.execute(src, xu, variables = vars_)
        st = cStringIO.StringIO()
        Domlette.Print(src, stream=st)

        tester.compare(expected, st.getvalue(),
                       func=TreeCompare.TreeCompare, diff=True)

        tester.testDone()

    tester.groupDone()

    tester.startGroup('XUpdate exceptions')
    uri = OsPathToUri('xupdate-test-src-2.xml', attemptAbsolute=True)
    isrc = InputSource.DefaultFactory.fromString(src_2, uri)
    src = srcReader(isrc)
    from Ft.Xml.XUpdate import XUpdateException
    for name, xuSrc, expected in [
        ('missing version attr', EXCEPTION_XUP_1, XUpdateException.NO_VERSION),
        ('missing select attr', EXCEPTION_XUP_2, XUpdateException.NO_SELECT),
        ('invalid select attr', EXCEPTION_XUP_3, XUpdateException.INVALID_SELECT),
        ('syntax error', EXCEPTION_XUP_4, XUpdateException.SYNTAX_ERROR),
        ('missing test attr', EXCEPTION_XUP_5, XUpdateException.NO_TEST),
        ('unrecognized instruction', EXCEPTION_XUP_6, XUpdateException.UNRECOGNIZED_INSTRUCTION),
        ]:
        tester.startTest(name)
        uri = OsPathToUri('xupdate-test-xup-' + quote(name) + '.xml', attemptAbsolute=True)
        isrc = InputSource.DefaultFactory.fromString(xuSrc, uri)
        xu = xureader.fromSrc(isrc)
        tester.testException(processor.execute, (src, xu), XUpdateException, {'errorCode': expected})
        tester.testDone()
    tester.groupDone()


    return
