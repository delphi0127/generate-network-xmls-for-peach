import re

from Ft.Xml.Xslt import XsltException, Error
from Xml.Xslt import test_harness

from Ft.Xml.Xslt.XmlWriter import DEFAULT_GENERATED_PREFIX

# an unsophisticated comparer of XML strings that just checks to see if
# both strings have the same set of substrings that look like attributes.
_attrPattern = re.compile(r'[\w:]+="[^"]+"')
def _cmp_rawattrs(a, b):
    a_attrs = _attrPattern.findall(a)
    b_attrs = _attrPattern.findall(b)
    a_attrs.sort()
    b_attrs.sort()
    return a_attrs != b_attrs


source_1 = """<dummy/>"""


sheet_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <xsl:attribute name="foo">bar</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected_1 = """<?xml version="1.0" encoding="UTF-8"?>
<result foo="bar"/>"""


sheet_2 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <xsl:if test="true()">
        <xsl:attribute name="foo">bar</xsl:attribute>
      </xsl:if>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected_2 = """<?xml version="1.0" encoding="UTF-8"?>
<result foo="bar"/>"""


# "xsl:attribute with namespace"
sheet_3 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <xsl:attribute name="foo" namespace="http://some-ns/">bar</xsl:attribute>
      <xsl:attribute name="y:foo" namespace="http://some-other-ns/">bar</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected_3 = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:%(gp)s0="http://some-ns/" xmlns:y="http://some-other-ns/" %(gp)s0:foo="bar" y:foo="bar"/>"""%{'gp': DEFAULT_GENERATED_PREFIX}


sheet_4 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <!-- duplicate attrs override previous -->
      <xsl:attribute name="foo">bar</xsl:attribute>
      <xsl:attribute name="foo">baz</xsl:attribute>
      <xsl:attribute name="foo">maz</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected_4 = """<?xml version="1.0" encoding="UTF-8"?>
<result foo="maz"/>"""


sheet_5 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result foo="bar">
      <!-- duplicate attrs override previous -->
      <xsl:attribute name="foo">baz</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected_5 = """<?xml version="1.0" encoding="UTF-8"?>
<result foo="baz"/>"""



sheet_6 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <xsl:attribute name="foo">bar</xsl:attribute>
      <!-- duplicate attrs override previous -->
      <!-- we use xsl:if to obscure it a bit -->
      <xsl:if test="true()">
        <xsl:attribute name="foo">baz</xsl:attribute>
      </xsl:if>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected_6 = """<?xml version="1.0" encoding="UTF-8"?>
<result foo="baz"/>"""


#"adding attributes with the same expanded-name 4"
sheet_7 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <!-- duplicate attrs override previous -->
      <xsl:attribute name="foo" namespace="http://some-ns/">bar</xsl:attribute>
      <xsl:attribute name="x:foo" xmlns:x="http://some-ns/">baz</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected_7 = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:org.4suite.4xslt.ns0="http://some-ns/" org.4suite.4xslt.ns0:foo="baz"/>"""


# "adding attributes with the same expanded-name 5"
sheet_8 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result x:foo="bar" xmlns:x="http://some-ns/">
      <!-- duplicate attrs override previous -->
      <xsl:attribute name="foo" namespace="http://some-ns/">baz</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected_8 = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:x="http://some-ns/" x:foo="baz"/>"""


sheet_9 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <!-- linefeed must be serialized as &#10; -->
      <xsl:attribute name="a">x
y</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected_9 = """<?xml version="1.0" encoding="UTF-8"?>
<result a="x&#10;y"/>"""


sheet_10 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <!-- if an attribute prefix would be xmlns, it must be changed to something else -->
      <xsl:attribute name="xmlns:foo" namespace="http://some-ns/">bar</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected_10 = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:%(gp)s0="http://some-ns/" %(gp)s0:foo="bar"/>"""%{'gp': DEFAULT_GENERATED_PREFIX}


# "attributes in various namespaces"
sheet_11 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <!-- correct results are indicated in the attribute values -->
      <xsl:attribute name="foo">local-name foo, no namespace, no prefix</xsl:attribute>
      <xsl:attribute name="in-empty-ns" namespace="">local-name in-empty-ns, no namespace, no prefix</xsl:attribute>
      <xsl:attribute name="in-foo-ns" namespace="http://foo-ns/">local-name in-foo-ns, namespace http://foo-ns/, generated prefix</xsl:attribute>
      <xsl:attribute name="pre:foo" xmlns:pre="http://ns-for-pre/">local-name foo, namespace http://ns-for-pre/, preferred prefix pre</xsl:attribute>
      <xsl:attribute name="pre:bar" xmlns:pre="http://ns-for-pre/" namespace="http://explicit-ns/">local-name bar, namespace http://explicit-ns/, generated prefix</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""


expected_11 = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:pre="http://ns-for-pre/" xmlns:%(gp)s0="http://foo-ns/" xmlns:%(gp)s1="http://explicit-ns/" %(gp)s1:bar="local-name bar, namespace http://explicit-ns/, generated prefix" foo="local-name foo, no namespace, no prefix" in-empty-ns="local-name in-empty-ns, no namespace, no prefix" pre:foo="local-name foo, namespace http://ns-for-pre/, preferred prefix pre" %(gp)s0:in-foo-ns="local-name in-foo-ns, namespace http://foo-ns/, generated prefix"/>"""%{'gp': DEFAULT_GENERATED_PREFIX}


sheet_12 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <!-- the element should be in the http://foo-ns/ namespace. -->
    <!-- the element *may*, but most likely won't, bear the same generated prefix as the in-foo-ns attribute. -->
    <result xmlns="http://foo-ns/">
      <!-- A default namespace is in scope, but this does not affect the value of 'name' in xsl:attribute. -->
      <!-- in-foo-ns attribute does not inherit the default namespace. It *must* have a prefix, bound to http://foo-ns/ -->
      <xsl:attribute name="foo">local-name foo, no namespace, no prefix</xsl:attribute>
      <xsl:attribute name="in-empty-ns" namespace="">local-name in-empty-ns, no namespace, no prefix</xsl:attribute>
      <xsl:attribute name="in-foo-ns" namespace="http://foo-ns/">local-name in-foo-ns, namespace http://foo-ns/, generated prefix</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""

expected_12 = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns="http://foo-ns/" xmlns:%(gp)s0="http://foo-ns/" foo="local-name foo, no namespace, no prefix" in-empty-ns="local-name in-empty-ns, no namespace, no prefix" %(gp)s0:in-foo-ns="local-name in-foo-ns, namespace http://foo-ns/, generated prefix"/>"""%{'gp': DEFAULT_GENERATED_PREFIX}


# "attributes in empty and in-scope default namespaces"
sheet_13 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <!-- element should be in http://foo-ns/ namespace, retaining prefix foo -->
    <foo:result xmlns:foo="http://foo-ns/">
      <xsl:attribute name="foo">local-name foo, no namespace, no prefix</xsl:attribute>
      <xsl:attribute name="in-empty-ns" namespace="">local-name in-empty-ns, no namespace, no prefix</xsl:attribute>
      <xsl:attribute name="in-foo-ns" namespace="http://foo-ns/">local-name in-foo-ns, namespace http://foo-ns/, prefix foo</xsl:attribute>
    </foo:result>
  </xsl:template>

</xsl:stylesheet>"""

# it's technically OK for the in-foo-ns attr to have a
# generated prefix, but it really should re-use the foo.
#
expected_13 = """<?xml version="1.0" encoding="UTF-8"?>
<foo:result xmlns:foo="http://foo-ns/" foo="local-name foo, no namespace, no prefix" in-empty-ns="local-name in-empty-ns, no namespace, no prefix" foo:in-foo-ns="local-name in-foo-ns, namespace http://foo-ns/, prefix foo"/>"""


sheet_14 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <!-- element should be in http://foo-ns/ namespace, retaining prefix foo -->
    <pre:result xmlns:pre="http://foo-ns/">
      <xsl:attribute name="in-foo-ns" namespace="http://foo-ns/">local-name in-foo-ns, namespace http://foo-ns/, prefix pre</xsl:attribute>
      <xsl:attribute name="pre:bar" xmlns:pre="http://ns-for-pre/" namespace="http://explicit-ns/">local-name bar, namespace http://explicit-ns/, generated prefix</xsl:attribute>
    </pre:result>
  </xsl:template>

</xsl:stylesheet>"""

# the bar attribute must have a generated prefix.
# it's technically OK for the in-foo-ns attr to have a
# generated prefix, but it really should re-use the pre.
#
expected_14 = """<?xml version="1.0" encoding="UTF-8"?>
<pre:result xmlns:pre="http://foo-ns/" xmlns:%(gp)s0="http://explicit-ns/" pre:in-foo-ns="local-name in-foo-ns, namespace http://foo-ns/, prefix pre" %(gp)s0:bar="local-name bar, namespace http://explicit-ns/, generated prefix"/>"""%{'gp': DEFAULT_GENERATED_PREFIX}


sheet_e1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <xsl:text>hello world</xsl:text>
      <!-- error: children added to element before attribute (recovery optional) -->
      <xsl:attribute name="att">foo</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""


sheet_e2 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <!-- error: adding attribute to non-element (recovery optional) -->
    <xsl:attribute name="att">foo</xsl:attribute>
  </xsl:template>

</xsl:stylesheet>"""


sheet_e3 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <xsl:attribute name="foo">
        <!-- error: creating non-text in attribute (recovery optional) -->
        <xsl:comment>uh-oh</xsl:comment>
      </xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""


sheet_e4 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <!-- error: creating attribute with illegal name 'xmlns' (recovery optional) -->
      <xsl:attribute name="{concat('xml','ns')}">http://some-ns/</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""


sheet_e5 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <!-- error: creating attribute with illegal name (recovery optional) -->
      <xsl:attribute name="99foo">bar</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""


sheet_nre1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="no"/>

  <xsl:template match="/">
    <result>
      <!-- error: illegal namespace name (Namespaces in XML restriction) -->
      <!-- XPath relies on Namespaces in XML, XSLT relies on XPath -->
      <xsl:attribute name="foo" namespace="http://www.w3.org/XML/1998/namespace">bar</xsl:attribute>
      <xsl:attribute name="baz" namespace="http://www.w3.org/2000/xmlns/">maz</xsl:attribute>
    </result>
  </xsl:template>

</xsl:stylesheet>"""



def Test(tester):

    tester.startGroup("xsl:attribute")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title="xsl:attribute as child of literal result element")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title="xsl:attribute as child of xsl:if child of l.r.e.")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title="xsl:attribute with namespace")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_4)
    test_harness.XsltTest(tester, source, [sheet], expected_4,
                          title="adding attributes with the same expanded-name 1")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_5)
    test_harness.XsltTest(tester, source, [sheet], expected_5,
                          title="adding attributes with the same expanded-name 2")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_6)
    test_harness.XsltTest(tester, source, [sheet], expected_6,
                          title="adding attributes with the same expanded-name 3")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_7)
    test_harness.XsltTest(tester, source, [sheet], expected_7,
                          title="adding attributes with the same expanded-name 4")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_8)
    test_harness.XsltTest(tester, source, [sheet], expected_8,
                          title="adding attributes with the same expanded-name 5")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_9)
    test_harness.XsltTest(tester, source, [sheet], expected_9,
                          title="serialization of linefeed in attribute value")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_10)
    test_harness.XsltTest(tester, source, [sheet], expected_10,
                          title="substitution of xmlns prefix in attribute name")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_11)
    test_harness.XsltTest(tester, source, [sheet], expected_11,
                          title="attributes in various namespaces")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_12)
    test_harness.XsltTest(tester, source, [sheet], expected_12,
                          title="attributes in empty and in-scope default namespaces")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_13)
    test_harness.XsltTest(tester, source, [sheet], expected_13,
                          title="attributes in empty and in-scope non-default namespaces")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_14)
    test_harness.XsltTest(tester, source, [sheet], expected_14,
                          title="attributes in in-scope namespaces and with dup prefixes")

    tester.groupDone()

    tester.startGroup("recoverable xsl:attribute errors")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_e1)
    test_harness.XsltTest(tester, source, [sheet], source_1,
                          exceptionCode=Error.ATTRIBUTE_ADDED_TOO_LATE,
                          title="adding attribute after non-attributes")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_e2)
    test_harness.XsltTest(tester, source, [sheet], source_1,
                          exceptionCode=Error.ATTRIBUTE_ADDED_TO_NON_ELEMENT,
                          title="adding attribute to non-element")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_e3)
    test_harness.XsltTest(tester, source, [sheet], source_1,
                          exceptionCode=Error.NONTEXT_IN_ATTRIBUTE,
                          title="creating non-text during xsl:attribute instantiation")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_e4)
    test_harness.XsltTest(tester, source, [sheet], source_1,
                          exceptionCode=Error.BAD_ATTRIBUTE_NAME,
                          title="illegal attribute name ('xmlns')")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_e5)
    test_harness.XsltTest(tester, source, [sheet], source_1,
                          exceptionCode=Error.INVALID_QNAME_ATTR,
                          title="illegal attribute name (non-QName)")

    tester.groupDone()

    tester.startGroup("non-recoverable xsl:attribute errors")

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_nre1)
    test_harness.XsltTest(tester, source, [sheet], source_1,
                          exceptionCode=Error.INVALID_NS_URIREF_ATTR,
                          title="illegal namespace URI")

    tester.groupDone()

    return
