from Xml.Xslt import test_harness
from Ft.Xml.Xslt import XsltException, Error

simple_sheet_str = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='text()'/>
  <xsl:template match='item'>
    <xsl:value-of select='.'/>
  </xsl:template>
</xsl:stylesheet>
"""

select_sheet_str = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates select='data/item[@in]'/>
    </docelem>
  </xsl:template>
  <xsl:template match='text()'/>
  <xsl:template match='item'>
    <xsl:value-of select='.'/>
  </xsl:template>
</xsl:stylesheet>
"""

select_attr_sheet_str = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates select='data/item/@in'/>
    </docelem>
  </xsl:template>
  <xsl:template match='text()'/>
  <xsl:template match='@*[. = "1"]'>!</xsl:template>
</xsl:stylesheet>
"""

sort_sheet_str = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='data'>
    <xsl:apply-templates>
      <xsl:sort select='.'/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match='text()'/>
  <xsl:template match='item'>
    <xsl:value-of select='.'/>
  </xsl:template>
</xsl:stylesheet>
"""

param_sheet_str = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='data'>
    <xsl:apply-templates>
      <xsl:with-param name='foo' select='1'/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match='text()'/>
  <xsl:template match='item'>
    <xsl:param name='foo'/>
    <xsl:value-of select='concat($foo,.)'/>
  </xsl:template>
</xsl:stylesheet>
"""

sort_param_sheet_str = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='data'>
    <xsl:apply-templates>
      <xsl:sort select='.'/>
      <xsl:with-param name='foo' select='1'/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match='text()'/>
  <xsl:template match='item'>
    <xsl:param name='foo'/>
    <xsl:value-of select='concat($foo,.)'/>
  </xsl:template>
</xsl:stylesheet>
"""


select_sort_sheet_str = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='data'>
    <xsl:apply-templates select='item[@in]'>
      <xsl:sort select='.'/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match='text()'/>
  <xsl:template match='item'>
    <xsl:value-of select='.'/>
  </xsl:template>
</xsl:stylesheet>
"""

select_param_sheet_str = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='data'>
    <xsl:apply-templates select='item[@in]'>
      <xsl:with-param name='foo' select='1'/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match='text()'/>
  <xsl:template match='item'>
    <xsl:param name='foo'/>
    <xsl:value-of select='concat($foo,.)'/>
  </xsl:template>
</xsl:stylesheet>
"""

select_sort_param_sheet_str = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match='/'>
    <docelem>
      <xsl:apply-templates/>
    </docelem>
  </xsl:template>
  <xsl:template match='data'>
    <xsl:apply-templates select='item[@in]'>
      <xsl:sort select='.'/>
      <xsl:with-param name='foo' select='1'/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match='text()'/>
  <xsl:template match='item'>
    <xsl:param name='foo'/>
    <xsl:value-of select='concat($foo,.)'/>
  </xsl:template>
</xsl:stylesheet>
"""

source_str_start = """<?xml version = "1.0"?>
<data>
"""
source_str_middle = """ <item>b</item>
 <item in='1'>a</item>
 <item>d</item>
 <item in='1'>c</item>
"""
source_str_end = """</data>
"""

MULTIPLIER = 50

source_str = source_str_start + source_str_middle*MULTIPLIER + source_str_end

simple_expected = """<?xml version='1.0' encoding='UTF-8'?>\n<docelem>"""+"""badc"""*MULTIPLIER + "</docelem>"
select_expected = """<?xml version='1.0' encoding='UTF-8'?>\n<docelem>"""+"""ac"""*MULTIPLIER+"</docelem>"
select_attr_expected = """<?xml version='1.0' encoding='UTF-8'?>\n<docelem>"""+"""!"""*MULTIPLIER*2+"""</docelem>"""
sort_expected = """<?xml version='1.0' encoding='UTF-8'?>\n<docelem>"""+"""a"""*MULTIPLIER + """b"""*MULTIPLIER + """c"""*MULTIPLIER + """d"""*MULTIPLIER+"</docelem>"
param_expected = """<?xml version='1.0' encoding='UTF-8'?>\n<docelem>"""+"""1b1a1d1c"""*MULTIPLIER+"</docelem>"
sort_param_expected = """<?xml version='1.0' encoding='UTF-8'?>\n<docelem>"""+"""1a"""*MULTIPLIER + """1b"""*MULTIPLIER + """1c"""*MULTIPLIER + """1d"""*MULTIPLIER+"</docelem>"
select_sort_expected = """<?xml version='1.0' encoding='UTF-8'?>\n<docelem>"""+"""a"""*MULTIPLIER + """c"""*MULTIPLIER+"</docelem>"
select_param_expected = """<?xml version='1.0' encoding='UTF-8'?>\n<docelem>"""+"""1a1c"""*MULTIPLIER+"</docelem>"
select_sort_param_expected = """<?xml version='1.0' encoding='UTF-8'?>\n<docelem>"""+"""1a"""*MULTIPLIER + """1c"""*MULTIPLIER+"</docelem>"

tests = [('Empty',simple_sheet_str,simple_expected),
         ('Empty using sort',sort_sheet_str,sort_expected),
         ('Empty using with-param',param_sheet_str,param_expected),
         ('Empty using sort and with-param',sort_param_sheet_str,sort_param_expected),
         ('Select',select_sheet_str,select_expected),
         ('Select of attributes',select_attr_sheet_str,select_attr_expected),
         ('Select using sort',select_sort_sheet_str,select_sort_expected),
         ('Select using with-param',select_param_sheet_str,select_param_expected),
         ('Select using sort and with-param',select_sort_param_sheet_str,select_sort_param_expected),
         ]

# Testing to ensure apply-templates applies to a node-set.
# If it's not a node-set, a particular XsltException is generated.
#
source_1="""<?xml version="1.0"?>
<foo/>"""

invalid_sheet_1="""<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <xsl:variable name="fragment">
      <foo>hello</foo>
      <foo>world</foo>
    </xsl:variable>
    <!-- should produce a fatal error in XSLT 1.0 -->
    <xsl:apply-templates select="$fragment" mode="foo"/>
  </xsl:template>

  <xsl:template match="/" mode="foo">
    <result>
      <xsl:apply-templates mode="foo"/>
    </result>
  </xsl:template>

  <xsl:template match="foo" mode="foo">
    <bar>
      <xsl:value-of select="."/>
    </bar>
  </xsl:template>

</xsl:stylesheet>"""

invalid_sheet_2="""<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <xsl:apply-templates select="'why is a string here?'"/>
  </xsl:template>

</xsl:stylesheet>"""

expected_1=""

def Test(tester):
    for (title, xsltSrc, expected) in tests:
        source = test_harness.FileInfo(string=source_str)
        sheet = test_harness.FileInfo(string=xsltSrc)
        test_harness.XsltTest(tester, source, [sheet], expected, title=title)

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=invalid_sheet_1)
    test_harness.XsltTest(tester, source, [sheet], "",
                          exceptionCode=Error.ILLEGAL_APPLYTEMPLATE_NODESET,
                          title='Select invalid node-set 1'),

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=invalid_sheet_2)
    test_harness.XsltTest(tester, source, [sheet], "",
                          exceptionCode=Error.ILLEGAL_APPLYTEMPLATE_NODESET,
                          title='Select invalid node-set 2'),
    return
