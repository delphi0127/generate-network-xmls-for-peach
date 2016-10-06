from Ft.Xml.Xslt import XsltException, Error
from Xml.Xslt import test_harness

source_1 = """<foo>dummy</foo>"""



"""
ValueOfElement.py:            raise XsltException(Error.VALUEOF_MISSING_SELECT)
WhenElement.py                raise XsltException(Error.WHEN_MISSING_TEST)
"""



apply_templates_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates>
      <foo/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates>
      <xsl:apply-templates/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_3 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates>
      <xsl:sort select='.'/>
      <foo/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_4 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates>
      <xsl:sort select='.'/>
      <xsl:apply-templates/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_5 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates>
      <xsl:with-param name='foo' select='.'/>
      <foo/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_6 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates>
      <xsl:with-param name='foo' select='.'/>
      <xsl:apply-templates/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_7 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates>
      <xsl:with-param name='foo' select='.'/>
      <xsl:sort select='.'/>
      <foo/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_8 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates>
      <xsl:with-param name='foo' select='.'/>
      <xsl:sort select='.'/>
      <xsl:apply-templates/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_9 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates select='foo'>
      <foo/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_10 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates select='foo'>
      <xsl:apply-templates/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_11 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates select='foo'>
      <xsl:sort select='.'/>
      <foo/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_12 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates select='foo'>
      <xsl:sort select='.'/>
      <xsl:apply-templates/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_13 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates select='foo'>
      <xsl:with-param name='foo' select='.'/>
      <foo/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_14 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates select='foo'>
      <xsl:with-param name='foo' select='.'/>
      <xsl:apply-templates/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_15 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates select='foo'>
      <xsl:with-param name='foo' select='.'/>
      <xsl:sort select='.'/>
      <foo/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

apply_templates_16 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:apply-templates select='foo'>
      <xsl:with-param name='foo' select='.'/>
      <xsl:sort select='.'/>
      <xsl:apply-templates/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

attribute_set_template_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:attribute-set/>
</xsl:stylesheet>
"""

attribute_set_template_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:attribute-set name='foo'>
    <foo/>
  </xsl:attribute-set>
</xsl:stylesheet>
"""

attribute_set_template_3 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:attribute-set name='foo'>
    <xsl:apply-templates/>
  </xsl:attribute-set>
</xsl:stylesheet>
"""

attribute_set_template_4 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:attribute-set name='foo' use-attribute-sets='bar'/>
  <xsl:template match='/'>
    <xsl:element name='dummy' use-attribute-sets='foo'/>
  </xsl:template>
</xsl:stylesheet>
"""

avt_template_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <TABLE WIDTH='{'/>
  </xsl:template>
</xsl:stylesheet>
"""

avt_template_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <TABLE WIDTH='{{}'/>
  </xsl:template>
</xsl:stylesheet>
"""

avt_template_3 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <TABLE WIDTH='}'/>
  </xsl:template>
</xsl:stylesheet>
"""

call_template_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:call-template name='foo'>
      <foo/>
    </xsl:call-template>
  </xsl:template>
</xsl:stylesheet>
"""

call_template_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:call-template name='foo'>
      <xsl:apply-templates/>
    </xsl:call-template>
  </xsl:template>
</xsl:stylesheet>
"""

choose_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:choose>
      <foo/>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
"""

choose_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:choose>
      <xsl:apply-templates/>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
"""

choose_3 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:choose/>
  </xsl:template>
</xsl:stylesheet>
"""

choose_4 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:choose>
      <xsl:otherwise/>
      <xsl:when test='foo'/>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
"""

choose_5 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:choose>
      <xsl:when test='foo'/>
      <xsl:otherwise/>
      <xsl:otherwise/>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
"""

copy_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:attribute-set name='foo'/>
  <xsl:template match='/*'>
    <xsl:copy use-attribute-sets='bar'/>
  </xsl:template>
</xsl:stylesheet>
"""

copy_of_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/*'>
    <xsl:copy-of/>
  </xsl:template>
</xsl:stylesheet>
"""

element_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:attribute-set name='foo'/>
  <xsl:template match='/'>
    <xsl:element name='foo' use-attribute-sets='bar'/>
  </xsl:template>
</xsl:stylesheet>
"""

literal_element_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:attribute-set name='foo'/>
  <xsl:template match='/*'>
    <TABLE xsl:use-attribute-sets='bar'/>
  </xsl:template>
</xsl:stylesheet>
"""

message_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <xsl:message terminate='yes'/>
  </xsl:template>
</xsl:stylesheet>
"""

message_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:message terminate='no'/>
  <xsl:template match='/'>
    <foo/>
  </xsl:template>
</xsl:stylesheet>
"""

namespace_alias_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
<xsl:namespace-alias result-prefix="xsl"/>
  <xsl:template match='/'>
    <xsl:apply-templates select='/|*'>
      <xsl:sort order='foo'/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

namespace_alias_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
<xsl:namespace-alias stylesheet-prefix="axsl"/>
  <xsl:template match='/'>
    <xsl:apply-templates select='/|*'>
      <xsl:sort order='foo'/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

number_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <xsl:number level='foo'/>
  </xsl:template>
</xsl:stylesheet>
"""

number_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <xsl:number grouping-separator=',' grouping-size='A'/>
  </xsl:template>
</xsl:stylesheet>
"""

number_3 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <xsl:number letter-value='foo'/>
  </xsl:template>
</xsl:stylesheet>
"""

number_4 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <xsl:number format='?'/>
  </xsl:template>
</xsl:stylesheet>
"""

sort_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <xsl:apply-templates select='/|*'>
      <xsl:sort data-type='foo'/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

sort_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <xsl:apply-templates select='/|*'>
      <xsl:sort case-order='foo'/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

sort_3 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <xsl:apply-templates select='/|*'>
      <xsl:sort order='foo'/>
    </xsl:apply-templates>
  </xsl:template>
</xsl:stylesheet>
"""

stylesheet_reader_1 = """<?xml version="1.0"?>
<xsl:foo xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <xsl:apply-templates/>
  </xsl:template>
</xsl:foo>
"""

stylesheet_reader_2 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <xsl:foo/>
  </xsl:template>
</xsl:stylesheet>
"""

stylesheet_reader_3 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match='/'>
    <xsl:foo/>
  </xsl:template>
</xsl:stylesheet>
"""

stylesheet_reader_4 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template foo='/'/>
</xsl:stylesheet>
"""

stylesheet_reader_5 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="foo"
version="1.0">
  <xsl:template match='/'/>
</xsl:stylesheet>
"""

stylesheet_reader_6 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'/>
  <foo/>
</xsl:stylesheet>
"""

template_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/' priority='foo'/>
</xsl:stylesheet>
"""

text_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match='/'>
    <xsl:text><Foo/></xsl:text>
  </xsl:template>
</xsl:stylesheet>
"""

value_of_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:value-of/>
  </xsl:template>
</xsl:stylesheet>
"""

when_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:template match="/">
    <xsl:choose>
      <xsl:when/>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
"""



#"

errors = [('Illegal apply-templates child 1', apply_templates_1, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 2', apply_templates_2, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 3', apply_templates_3, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 4', apply_templates_4, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 5', apply_templates_5, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 6', apply_templates_6, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 7', apply_templates_7, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 8', apply_templates_8, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 9', apply_templates_9, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 10', apply_templates_10, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 11', apply_templates_11, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 12', apply_templates_12, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 13', apply_templates_13, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 14', apply_templates_14, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 15', apply_templates_15, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal apply-templates child 16', apply_templates_16, Error.ILLEGAL_ELEMENT_CHILD),

          ('attribute-set requires name', attribute_set_template_1, Error.MISSING_REQUIRED_ATTRIBUTE),
          ('Illegal attribute-set with child 1', attribute_set_template_2, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal attribute-set with child 2', attribute_set_template_3, Error.ILLEGAL_ELEMENT_CHILD),
          ('Undefined attribute-set', attribute_set_template_4, Error.UNDEFINED_ATTRIBUTE_SET),

          ('invalid attribute value template 1', avt_template_1, Error.INVALID_AVT),
          ('invalid attribute value template 2', avt_template_2, Error.INVALID_AVT),
          ('invalid attribute value template 3', avt_template_3, Error.INVALID_AVT),

          ('Illegal call-template child 1', call_template_1, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal call-template child 2', call_template_2, Error.ILLEGAL_ELEMENT_CHILD),

          ('Illegal choose child 1', choose_1, Error.ILLEGAL_ELEMENT_CHILD),
          ('Illegal choose child 2', choose_2, Error.ILLEGAL_ELEMENT_CHILD),
          ('choose requires when child', choose_3, Error.CHOOSE_REQUIRES_WHEN),
          ('choose with when after otherwise', choose_4, Error.ILLEGAL_CHOOSE_CHILD),
          ('choose with multiple otherwise', choose_5, Error.ILLEGAL_CHOOSE_CHILD),

          ('copy invalid use name', copy_1, Error.UNDEFINED_ATTRIBUTE_SET),

          ('copy-of missing select', copy_of_1, Error.MISSING_REQUIRED_ATTRIBUTE),

          ('element invalid use name', element_1, Error.UNDEFINED_ATTRIBUTE_SET),

          ('literal element invalid use name', literal_element_1, Error.UNDEFINED_ATTRIBUTE_SET),

          ('message terminate', message_1, Error.STYLESHEET_REQUESTED_TERMINATION),
          ('message as top-level element', message_2, Error.ILLEGAL_ELEMENT_CHILD),

          ('Invalid namespace alias 1', namespace_alias_1, Error.MISSING_REQUIRED_ATTRIBUTE),
          ('Invalid namespace alias 2', namespace_alias_2, Error.MISSING_REQUIRED_ATTRIBUTE),

          ('Illegal number level value', number_1, Error.INVALID_ATTR_CHOICE),
          ('Illegal number grouping size value', number_2, Error.INVALID_NUMBER_ATTR),
          ('Illegal number letter value', number_3, Error.INVALID_ATTR_CHOICE),
          ('Illegal number format value', number_4, Error.ILLEGAL_NUMBER_FORMAT_VALUE),

          ('Illegal sort data-type value', sort_1, Error.INVALID_ATTR_CHOICE),
          ('Illegal sort case-order value', sort_2, Error.INVALID_ATTR_CHOICE),
          ('Illegal sort order value', sort_3, Error.INVALID_ATTR_CHOICE),

          ('stylesheet illegal root', stylesheet_reader_1, Error.XSLT_ILLEGAL_ELEMENT),
          ('stylesheet illegal element', stylesheet_reader_2, Error.XSLT_ILLEGAL_ELEMENT),
          ('stylesheet missing version', stylesheet_reader_3, Error.MISSING_REQUIRED_ATTRIBUTE),
          ('stylesheet illegal attribute', stylesheet_reader_4, Error.ILLEGAL_NULL_NAMESPACE_ATTR),
          ('stylesheet missing version', stylesheet_reader_5, Error.LITERAL_RESULT_MISSING_VERSION),
          ('stylesheet illegal child', stylesheet_reader_6, Error.ILLEGAL_ELEMENT_CHILD),

          ('Illegal template priority', template_1, Error.INVALID_NUMBER_ATTR),

          ('illegal text child', text_1, Error.ILLEGAL_ELEMENT_CHILD),
          
          ('value-of missing select', value_of_1, Error.MISSING_REQUIRED_ATTRIBUTE),
          
          ('when missing test', when_1, Error.MISSING_REQUIRED_ATTRIBUTE),
          ]

expected = """<?xml version='1.0' encoding='UTF-8'?>\
<foo/>"""

def Test(tester):

    for name, sheet, errorCode in errors:
        source = test_harness.FileInfo(string=source_1)
        sheet = test_harness.FileInfo(string=sheet)
        test_harness.XsltTest(tester, source, [sheet], None,
                              exceptionCode=errorCode, title=name)
    return

