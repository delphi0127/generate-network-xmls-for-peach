import os
from cStringIO import StringIO
from Xml.Xslt import test_harness
from Ft.Lib import Uri, Resolvers, Uuid
from Ft.Xml import __version__
from Ft.Xml.InputSource import DefaultFactory
from Ft.Xml.Lib import TreeCompare

# See XSLT 1.0 spec section 12.
# These are the functions that are tested:
#  document()
#  key() and xsl:key
#  format-number() and xsl:decimal-format
#  current()
#  unparsed-entity-uri()
#  generate-id()
#  system-property(), including these required properties:
#    system-property('xsl:version')
#    system-property('xsl:vendor')
#    system-property('xsl:vendor-url')


tests = []

DUMMY_XML_STR = "<dummy/>"
DUMMY_XML_URI = Uri.OsPathToUri(os.path.join(os.path.abspath(os.getcwd()),
                                Uuid.UuidAsString(Uuid.GenerateUuid())))

TEST_XML_STR = """<?xml version="1.0"?>
<doc>
  <elem a1="1" a2="6">one</elem>
  <elem a1="2" a2="4">two</elem>
  <elem a1="3" a2="2">three</elem>
</doc>"""
TEST_XML_URI = None  # (one will be generated)

TEST_DIR_URI_BASE = Uri.OsPathToUri(os.path.abspath(os.getcwd()))
if TEST_DIR_URI_BASE[-1] != '/':
    TEST_DIR_URI_BASE += '/'

f = open(os.path.normpath('Xml/Xslt/Core/addr_book1.xml'), 'r')
ADDR_BOOK_FILE_CONTENTS = f.read()
f.close()
del f


#----------------------------------------------------------------------
#
# system-property()
#
sheet_str = """<?xml version="1.0"?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  xmlns:env="http://xmlns.4suite.org/xslt/env-system-property"
  version="1.0"
>
  <xsl:template match="/">
    <xsl:value-of select="system-property('xsl:vendor')"/><xsl:text>&#10;</xsl:text>
    <xsl:value-of select="system-property('xsl:vendor-url')"/><xsl:text>&#10;</xsl:text>
    <xsl:value-of select="system-property('xsl:version')"/><xsl:text>&#10;</xsl:text>
  </xsl:template>

</xsl:transform>"""

expected = """<?xml version="1.0" encoding="UTF-8"?>
Fourthought Inc.
http://4Suite.org
1
"""

tests.append({'title': 'system-property(): required properties',
              'src': DUMMY_XML_STR,
              'src_uri': DUMMY_XML_URI,
              'sty': sheet_str,
              'sty_uri': None,
              'sty_params': None,
              'expected': expected,
              })


sheet_str = """<?xml version="1.0"?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  xmlns:env="http://xmlns.4suite.org/xslt/env-system-property"
  version="1.0"
>
  <xsl:template match="/">
    <xsl:value-of select="system-property('ft:version')"/><xsl:text>&#10;</xsl:text>
    <xsl:value-of select="system-property('env:PATH')"/><xsl:text>&#10;</xsl:text>
  </xsl:template>

</xsl:transform>"""

expected = """<?xml version="1.0" encoding="UTF-8"?>
%s
%s
""" % (__version__, os.environ.get('PATH', ''))

tests.append({'title': 'system-property(): vendor-specific properties',
              'src': DUMMY_XML_STR,
              'src_uri': DUMMY_XML_URI,
              'sty': sheet_str,
              'sty_uri': None,
              'sty_params': None,
              'expected': expected,
              })


#----------------------------------------------------------------------
#
# format-number() and xsl:decimal-format
#

sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="yes" encoding="us-ascii"/>

  <xsl:decimal-format name="european" decimal-separator=',' grouping-separator='.' />
  <xsl:decimal-format name="underscore-as-minus" minus-sign='_' />
  <xsl:decimal-format name="d-digit" digit="D" />
  <xsl:decimal-format name="carat-percent" percent="^" />
  <xsl:decimal-format name="carat-permille" per-mille="^" />
  <xsl:decimal-format name="arabic-indic-digits" zero-digit='&#x0660;' />
  <xsl:decimal-format name="vertbar-patternsep" pattern-separator="|" />

  <xsl:template match="/">
    <result>
      <!-- 5,351 -->
      <r><xsl:value-of select="format-number(5351,'#,###')"/></r>
      <!-- 5351.00 -->
      <r><xsl:value-of select="format-number(5351,'#.00')"/></r>
      <!-- 53.5100 -->
      <r><xsl:value-of select="format-number(53.51,'#.0000')"/></r>
      <!-- 0053.5100 -->
      <r><xsl:value-of select="format-number(53.51,'0000.0000')"/></r>
      <!-- 0053.51 -->
      <r><xsl:value-of select="format-number(53.51,'0000.####')"/></r>
      <!-- 53.6 -->
      <r><xsl:value-of select="format-number(53.56,'0.0')"/></r>
      <!-- 24.535,20 -->
      <r><xsl:value-of select="format-number(24535.2, '###.###,00', 'european')"/></r>
      <!-- NaN -->
      <r><xsl:value-of select="format-number('abc', '#,###')"/></r>
      <r><xsl:value-of select="format-number('', '#,###')"/></r>
      <!-- Infinity -->
      <r><xsl:value-of select="format-number(2 div 0, '#,###')"/></r>
      <!-- -5,351 -->
      <r><xsl:value-of select="format-number(-5351, '#,###')"/></r>
      <!-- -5,351 -->
      <r><xsl:value-of select="format-number(-5351, '#,###', 'underscore-as-minus')"/></r>
      <!-- (5,351) -->
      <r><xsl:value-of select="format-number(-5351,'###,###,###;(###,###,###)')"/></r>
      <!-- +5,351 -->
      <r><xsl:value-of select="format-number(5351,'+###,###,###;-###,###,###')"/></r>
      <!-- -5,351 -->
      <r><xsl:value-of select="format-number(-5351,'+###,###,###|-###,###,###','vertbar-patternsep')"/></r>
      <!-- 5,351 -->
      <r><xsl:value-of select="format-number(5351,'D,DDD', 'd-digit')"/></r>
      <!-- 12% -->
      <r><xsl:value-of select="format-number(0.12,'#00%')"/></r>
      <!-- 12^ -->
      <r><xsl:value-of select="format-number(0.115,'#00^','carat-percent')"/></r>
      <!-- 015&#x2030; or 015&#8240; -->
      <r><xsl:value-of select="format-number(0.015,'000&#x2030;')"/></r>
      <!-- 015^ -->
      <r><xsl:value-of select="format-number(0.015,'000^','carat-permille')"/></r>
      <!-- $12,345 -->
      <r><xsl:value-of select="format-number(12345,'$#0,000')"/></r>
      <!-- $12,345.00 -->
      <r><xsl:value-of select="format-number(12345,'$##,000.00')"/></r>
      <!-- $0,123.45 -->
      <r><xsl:value-of select="format-number(123.45,'$#0,000.00')"/></r>
      <!-- 012 -->
      <r><xsl:value-of select="format-number(12,'000')"/></r>
      <!-- &#x283C;&#x281A;&#x2801;&#x2803; or &#10300;&#10266;&#10241;&#10243; -->
      <r>012 in Braille: <xsl:value-of select="translate(format-number(12,'&#x283C;000'),'012345679','&#x281A;&#x2801;&#x2803;&#x2809;&#x2819;&#x2811;&#x280B;&#x281B;&#2813;&#x280A;')"/></r>
      <!-- &#x0660;&#x0661;&#x0662; or &#1632;&#1633;&#1634; -->
      <r>012 in Arabic-Indic digits: <xsl:value-of select="format-number(12,'&#x660;&#x660;&#x660;','arabic-indic-digits')"/></r>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected = """<?xml version="1.0" encoding="us-ascii"?>
<result>
  <r>5,351</r>
  <r>5351.00</r>
  <r>53.5100</r>
  <r>0053.5100</r>
  <r>0053.51</r>
  <r>53.6</r>
  <r>24.535,20</r>
  <r>NaN</r>
  <r>NaN</r>
  <r>Infinity</r>
  <r>-5,351</r>
  <r>_5,351</r>
  <r>(5,351)</r>
  <r>+5,351</r>
  <r>-5,351</r>
  <r>5,351</r>
  <r>12%</r>
  <r>12^</r>
  <r>015&#8240;</r>
  <r>015^</r>
  <r>$12,345</r>
  <r>$12,345.00</r>
  <r>$0,123.45</r>
  <r>012</r>
  <r>012 in Braille: &#10300;&#10266;&#10241;&#10243;</r>
  <r>012 in Arabic-Indic digits: &#1632;&#1633;&#1634;</r>
</result>"""

tests.append({'title': 'format-number() and xsl:decimal-format',
              'src': DUMMY_XML_STR,
              'src_uri': DUMMY_XML_URI,
              'sty': sheet_str,
              'sty_uri': None,
              'sty_params': None,
              'expected': expected,
              })


#----------------------------------------------------------------------
#
# current()
#
sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <xsl:apply-templates/>
    </result>
  </xsl:template>

  <xsl:template match="doc">
    <xsl:apply-templates select="elem">
      <xsl:sort select="@a1" order="descending"/>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="elem">
    <r>
      <xsl:value-of select="current()"/>
    </r>
  </xsl:template>

</xsl:stylesheet>"""

expected = """<?xml version="1.0" encoding="UTF-8"?>
<result>
  <r>three</r>
  <r>two</r>
  <r>one</r>
</result>"""

tests.append({'title': 'current() vs XSLT context',
              'src': TEST_XML_STR,
              'src_uri': TEST_XML_URI,
              'sty': sheet_str,
              'sty_uri': None,
              'sty_params': None,
              'expected': expected,
              })


sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <xsl:apply-templates/>
    </result>
  </xsl:template>

  <xsl:template match="doc">
    <xsl:apply-templates select="elem">
      <xsl:sort select="@a1" order="descending"/>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="elem">
    <r1>
      <xsl:value-of select="current()"/>
    </r1>
    <r2>
      <xsl:value-of select="/doc/elem[@a2=current()/@a1*2]"/>
    </r2>
  </xsl:template>

</xsl:stylesheet>"""

expected = """<?xml version="1.0" encoding="UTF-8"?>
<result>
  <r1>three</r1>
  <r2>one</r2>
  <r1>two</r1>
  <r2>two</r2>
  <r1>one</r1>
  <r2>three</r2>
</result>"""

tests.append({'title': 'current() vs XPath predicate context',
              'src': TEST_XML_STR,
              'src_uri': TEST_XML_URI,
              'sty': sheet_str,
              'sty_uri': None,
              'sty_params': None,
              'expected': expected,
              })


sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <xsl:apply-templates/>
    </result>
  </xsl:template>

  <xsl:template match="doc">
    <xsl:apply-templates select="elem[1]"/>
    <s><xsl:value-of select="current()"/></s>
    <xsl:apply-templates select="elem[2]"/>
    <s><xsl:value-of select="current()"/></s>
    <xsl:apply-templates select="elem[3]"/>
    <s><xsl:value-of select="current()"/></s>
  </xsl:template>

  <xsl:template match="elem">
    <r>
      <xsl:value-of select="current()"/>
    </r>
  </xsl:template>

</xsl:stylesheet>"""

expected =  '<?xml version="1.0" encoding="UTF-8"?>\n<result>\n  <r>one</r>\n  <s>\n  one\n  two\n  three\n</s>\n  <r>two</r>\n  <s>\n  one\n  two\n  three\n</s>\n  <r>three</r>\n  <s>\n  one\n  two\n  three\n</s>\n</result>'

tests.append({'title': 'current() vs XSLT context',
              'src': TEST_XML_STR,
              'src_uri': TEST_XML_URI,
              'sty': sheet_str,
              'sty_uri': None,
              'sty_params': None,
              'expected': expected,
              })


#----------------------------------------------------------------------
#
# document() only
#

sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:transform version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
 <xsl:output method="xml" encoding="utf-8"/>
 <xsl:template match="/">
  <xsl:copy-of select="document('')"/>
 </xsl:template>
</xsl:transform>"""

tests.append({'title': 'document() only: same-doc reference 1',
              'src': DUMMY_XML_STR,
              'src_uri': DUMMY_XML_URI,
              'sty': sheet_str,
              'sty_uri': None,
              'sty_params': None,
              'expected': sheet_str,
              })


sheet_uri = TEST_DIR_URI_BASE + 'document-func-same-doc-ref-2.xslt'

sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:transform version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
 <xsl:output method="xml" encoding="utf-8"/>
 <xsl:template match="/">
  <xsl:copy-of select="document('%s')"/>
 </xsl:template>
</xsl:transform>""" % sheet_uri

tests.append({'title': 'document() only: same-doc reference 2',
              'src': DUMMY_XML_STR,
              'src_uri': DUMMY_XML_URI,
              'sty': sheet_str,
              'sty_uri': sheet_uri,
              'sty_params': None,
              'expected': sheet_str,
              })


sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
 <xsl:output method="xml" encoding="utf-8"/>
 <xsl:template match="/">
  <xsl:copy-of select="document('Xml/Xslt/Core/addr_book1.xml')"/>
 </xsl:template>
</xsl:stylesheet>"""

sheet_uri = TEST_DIR_URI_BASE + 'document-func-external-doc-ref.xslt'

tests.append({'title': 'document() only: external XML file',
              'src': DUMMY_XML_STR,
              'src_uri': DUMMY_XML_URI,
              'sty': sheet_str,
              'sty_uri': sheet_uri,
              'sty_params': None,
              'expected': ADDR_BOOK_FILE_CONTENTS,
              })


sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
 <xsl:output method="xml" encoding="utf-8"/>
 <xsl:variable name="node" select="document('Xml/Xslt/Core/etc/null.xslt')"/>
 <xsl:template match="/">
  <xsl:copy-of select="document('../addr_book1.xml', $node)"/>
 </xsl:template>
</xsl:stylesheet>"""

sheet_uri = TEST_DIR_URI_BASE + 'document-func-base-uri-from-node.xslt'

tests.append({'title': 'document() only: file relative to base URI of a node',
              'src': DUMMY_XML_STR,
              'src_uri': DUMMY_XML_URI,
              'sty': sheet_str,
              'sty_uri': sheet_uri,
              'sty_params': None,
              'expected': ADDR_BOOK_FILE_CONTENTS,
              })


# This is also testing import precedence and variable scoping
sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:embedded="http://doesnt/matter">

 <xsl:import href="Xml/Xslt/Core/etc/document-func-import-test.xslt"/>

 <embedded:data>
   <Z/>
 </embedded:data>

 <xsl:template match="/">
   <xsl:element name="D">
     <xsl:apply-templates select="$node/*/embedded:data/*"/>
   </xsl:element>
 </xsl:template>

</xsl:stylesheet>"""

expected = """<?xml version="1.0" encoding="utf-8"?>
<D><A/><B/></D>
"""

sheet_uri = TEST_DIR_URI_BASE + 'document-func-across-imports.xslt'

tests.append({'title': 'document() only: imported stylesheet document',
              'src': DUMMY_XML_STR,
              'src_uri': DUMMY_XML_URI,
              'sty': sheet_str,
              'sty_uri': sheet_uri,
              'sty_params': None,
              'expected': expected,
              })


sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
 <xsl:output method="xml" encoding="utf-8"/>
 <xsl:template match="/">
  <xsl:copy-of select="document('urn:fourthought:Xml/Xslt/Core/addr_book1.xml')"/>
 </xsl:template>
</xsl:stylesheet>"""

sheet_uri = TEST_DIR_URI_BASE + 'document-func-with-custom-resolver.xsl'

# URN resolver class used for this test
class URNResolver(Resolvers.SchemeRegistryResolver):
    def __init__(self):
        Resolvers.SchemeRegistryResolver.__init__(self)
        self.handlers['urn'] = self.resolveURN
        self.supportedSchemes.append('urn')

    def resolveURN(self, uri, base=None):
        uriParts = uri.split(':')
        nid      = uriParts[1] # namespace ID
        nss      = uriParts[2] # namespace specific string
        f = open(os.path.normpath(nss), 'rb')
        st = f.read()
        f.close()
        return StringIO(st)

tests.append({'title': 'document() resolve URN via SchemeRegistryResolver',
              'src': DUMMY_XML_STR,
              'src_uri': DUMMY_XML_URI,
              'sty': sheet_str,
              'sty_uri': sheet_uri,
              'sty_params': None,
              'expected': ADDR_BOOK_FILE_CONTENTS,
              'resolver': URNResolver(),
              })

#----------------------------------------------------------------------
#
# generate-id() only
#
sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <!-- make sure multiple calls and order of calls don't matter -->
      <xsl:variable name="all-ids1">
        <xsl:for-each select="//node()">
          <id val="{.}"><xsl:value-of select="generate-id()"/></id>
        </xsl:for-each>
      </xsl:variable>
      <xsl:variable name="all-ids2">
        <xsl:for-each select="//node()">
          <xsl:sort select="." order="descending"/>
          <id val="{.}"><xsl:value-of select="generate-id()"/></id>
        </xsl:for-each>
      </xsl:variable>
      <!-- != means at least one string-value in first set is different than a string-value in the other. -->
      <!-- assumes exsl:node-set() and node-set comparisons work properly! -->
      <r>IDs are unique: <xsl:value-of select="not(exsl:node-set($all-ids1)/ids1 != exsl:node-set($all-ids2)/ids2)"/></r>
      <xsl:variable name="invalid-id">
        <xsl:for-each select="//node()">
          <xsl:if test="translate(substring(generate-id(),1,1),'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ','')">!</xsl:if>
          <xsl:if test="translate(substring(generate-id(),2),'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ','')">!</xsl:if>
        </xsl:for-each>
      </xsl:variable>
      <r>IDs are valid: <xsl:value-of select="not(string($invalid-id))"/></r>
      <r>IDs for context node don't vary: <xsl:value-of select="generate-id()=generate-id(/)=generate-id(.)"/></r>
      <r>ID for empty node-set is empty string: <xsl:value-of select="generate-id(/..)=''"/></r>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected = """<?xml version='1.0' encoding='UTF-8'?>
<result xmlns:exsl='http://exslt.org/common'>
  <r>IDs are unique: true</r>
  <r>IDs are valid: true</r>
  <r>IDs for context node don't vary: true</r>
  <r>ID for empty node-set is empty string: true</r>
</result>"""

tests.append({'title': 'generate-id() only',
              'src': TEST_XML_STR,
              'src_uri': TEST_XML_URI,
              'sty': sheet_str,
              'sty_uri': None,
              'sty_params': None,
              'expected': expected,
              })


#----------------------------------------------------------------------
#
# generate-id() and document()
#
sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <r>stylesheet root is unique: <xsl:value-of select="generate-id(document(''))=generate-id(document(''))"/></r>
      <r>external document root is unique: <xsl:value-of select="generate-id(document('Xml/Xslt/Core/addr_book1.xml'))=generate-id(document('Xml/Xslt/Core/addr_book1.xml'))"/></r>
      <r>stylesheet root != external non-stylesheet document root: <xsl:value-of select="generate-id(document('Xml/Xslt/Core/addr_book1.xml'))!=generate-id(document(''))"/></r>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

sheet_uri = TEST_DIR_URI_BASE + 'generate-id-vs-document-func-1.xsl'

expected = """<?xml version='1.0' encoding='UTF-8'?>
<result xmlns:exsl='http://exslt.org/common'>
  <r>stylesheet root is unique: true</r>
  <r>external document root is unique: true</r>
  <r>stylesheet root != external non-stylesheet document root: true</r>
</result>"""

tests.append({'title': 'generate-id() and document(): ID uniqueness',
              'src': DUMMY_XML_STR,
              'src_uri': DUMMY_XML_URI,
              'sty': sheet_str,
              'sty_uri': None,
              'sty_params': None,
              'expected': expected,
              })

# This test relies on RFC 2396-conformant URI resolution.
# Equivalent URIs must resolve to the same node with the same ID;
# documents must not be treated as unique when their URIs are equivalent.

source_uri = TEST_DIR_URI_BASE + 'Xml/Xslt/Core/dummy.xml'
sheet_uri  = TEST_DIR_URI_BASE + 'Xml/Xslt/Core/genid.xsl'
sheet_params = {
    u'src-uri': source_uri,
    u'sty-uri': sheet_uri,
}

expected = """<?xml version='1.0' encoding='us-ascii'?>
<results>
  <group>
    <title>source doc IDs</title>
    <test>ID of root node of source via XPath location path / is non-empty string</test>
    <result>true</result>
    <test>ID of root node of source via same-document URI reference relative to XPath location path / does not differ</test>
    <result>true</result>
    <test>ID of root node of source via relative URI ref does not differ</test>
    <result>true</result>
    <test>ID of root node of source via absolute URI ref does not differ</test>
    <result>true</result>
    <test>all of the above IDs are identical</test>
    <result>true</result>
    <test>ID of root node of source via file://localhost/ absolute URI ref does not differ</test>
    <result>true</result>
  </group>
  <group>
    <title>stylesheet IDs</title>
    <test>ID of root node of stylesheet via same-document URI reference is non-empty string</test>
    <result>true</result>
    <test>above ID differs from ID of root node of source via XPath location path /</test>
    <result>true</result>
    <test>ID of root node of stylesheet via relative URI ref does not differ</test>
    <result>true</result>
    <test>ID of root node of stylesheet via absolute URI ref does not differ</test>
    <result>true</result>
    <test>all of the above IDs are identical</test>
    <result>true</result>
    <test>ID of root node of stylesheet via file://localhost/ absolute URI ref does not differ</test>
    <result>true</result>
  </group>
  <group>
    <title>factors affecting results above</title>
    <test>generate-id() on empty node-set returns empty string</test>
    <result>true</result>
    <test>generate-id() on same node returns same results</test>
    <result>true</result>
    <test>generate-id() on different nodes returns different results</test>
    <result>true</result>
    <test>URIs given as src-uri and sty-uri are resolvable</test>
    <result>true</result>
    <test>given same URI reference, document() returns same node</test>
    <result>true</result>
    <test>given equivalent relative and absolute URI references, document() returns same node</test>
    <result>true</result>
    <test>URI given as src-uri parameter is recognized as URI of source doc fed to processor</test>
    <result>true</result>
    <test>URI given as sty-uri parameter is recognized as URI of stylesheet fed to processor</test>
    <result>true</result>
    <test>URI resolver treats file:/// and file://localhost/ same as per RFC 1738</test>
    <result>true</result>
  </group>
</results>"""

tests.append({'title': 'generate-id() and document(): ID consistency',
              'src': DUMMY_XML_STR,
              'src_uri': source_uri,
              'sty': None,
              'sty_uri': sheet_uri,
              'sty_params': sheet_params,
              'expected': expected,
              })


#----------------------------------------------------------------------
#
# unparsed-entity-uri()
#
xml_source = """<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE foo [
  <!NOTATION png SYSTEM "http://www.libpng.org/pub/png/">
  <!ENTITY obj0 SYSTEM "http://www.w3.org/Icons/WWW/w3c_home" NDATA png>
  <!ELEMENT foo (bar)>
  <!ELEMENT bar (#PCDATA)>
  <!ATTLIST bar
     logo ENTITY #IMPLIED
     desc CDATA #REQUIRED>
]>
<foo>
  <bar logo="obj0" desc="W3C logo"/>
</foo>"""

sheet_str = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <string>
        <xsl:value-of select="unparsed-entity-uri('obj0')"/>
      </string>
      <nodeset>
        <xsl:value-of select="unparsed-entity-uri(/foo/bar/@logo)"/>
      </nodeset>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected = """<?xml version='1.0' encoding='UTF-8'?>
<result>
  <string>http://www.w3.org/Icons/WWW/w3c_home</string>
  <nodeset>http://www.w3.org/Icons/WWW/w3c_home</nodeset>
</result>"""

tests.append({'title': 'unparsed-entity-uri()',
              'src': xml_source,
              'src_uri': None,
              'sty': sheet_str,
              'sty_uri': None,
              'sty_params': None,
              'expected': expected,
              })


del sheet_str, sheet_uri


def Test(tester):
    tests.reverse()
    while tests:
        d = tests.pop()
        test_title = d.get('title')
        source_str = d.get('src')
        source_uri = d.get('src_uri')
        if source_str:
            if source_uri:
                source = test_harness.FileInfo(string=source_str,
                                               baseUri=source_uri)
            else:
                source = test_harness.FileInfo(string=source_str)
        else:
            source = test_harness.FileInfo(uri=source_uri)

        sheet_str = d.get('sty')
        sheet_uri = d.get('sty_uri')
        if sheet_str:
            if sheet_uri:
                sheet = test_harness.FileInfo(string=sheet_str,
                                               baseUri=sheet_uri)
            else:
                sheet = test_harness.FileInfo(string=sheet_str)
        else:
            sheet = test_harness.FileInfo(uri=sheet_uri)

        params = d.get('sty_params') or {}
        expected = d.get('expected')
        resolver = d.get('resolver')
        if resolver:
            originalResolver = DefaultFactory.resolver
            DefaultFactory.resolver = URNResolver()

        test_harness.XsltTest(tester, source, [sheet], expected,
                              topLevelParams=params,
                              title=test_title)
        if resolver:
            DefaultFactory.resolver = originalResolver

    return
