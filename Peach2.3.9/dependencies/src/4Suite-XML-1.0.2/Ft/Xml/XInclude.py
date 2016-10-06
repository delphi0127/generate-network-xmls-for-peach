########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XInclude.py,v 1.12 2005/04/12 06:33:33 mbrown Exp $
"""
XInclude processing

XInclude processing is normally controlled via the Domlette reader APIs
and is implemented within Domlette itself. This module just provides
constants and classes to support XInclude processing.

XInclude is defined at http://www.w3.org/TR/xinclude

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

# this list intentionally excludes deprecated functionality
__all__ = ['XINCLUDE_NAMESPACE',
           'NONNORMATIVE_SCHEMA_FOR_XINCLUDE_ELEMENT',
           'g_errorMessages']

XINCLUDE_NAMESPACE = u'http://www.w3.org/2001/XInclude'

NONNORMATIVE_SCHEMA_FOR_XINCLUDE_ELEMENT = """<?xml version="1.0" encoding="utf-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns:xi="http://www.w3.org/2001/XInclude"
           targetNamespace="http://www.w3.org/2001/XInclude"
           finalDefault="extension">

  <xs:element name="include" type="xi:includeType" />

  <xs:complexType name="includeType" mixed="true">
    <xs:choice minOccurs='0' maxOccurs='unbounded' >
      <xs:element ref='xi:fallback' />
      <xs:any namespace='##other' processContents='lax' />
      <xs:any namespace='##local' processContents='lax' />
    </xs:choice>
    <xs:attribute name="href" use="optional" type="xs:anyURI"/>
    <xs:attribute name="parse" use="optional" default="xml"
                  type="xi:parseType" />
    <xs:attribute name="xpointer" use="optional" type="xs:string"/>
    <xs:attribute name="encoding" use="optional" type="xs:string"/>
    <xs:attribute name="accept" use="optional" type="xs:string"/>
    <xs:attribute name="accept-language" use="optional" type="xs:string"/>
    <xs:anyAttribute namespace="##other" processContents="lax"/>
  </xs:complexType>

  <xs:simpleType name="parseType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="xml"/>
      <xs:enumeration value="text"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:element name="fallback" type="xi:fallbackType" />

  <xs:complexType name="fallbackType" mixed="true">
    <xs:choice minOccurs="0" maxOccurs="unbounded">
      <xs:element ref="xi:include"/>
      <xs:any namespace="##other" processContents="lax"/>
      <xs:any namespace="##local" processContents="lax"/>
    </xs:choice>
    <xs:anyAttribute namespace="##other" processContents="lax" />
  </xs:complexType>

</xs:schema>"""


import warnings

def ProcessIncludesFromUri(uri, validate=0):
    """
    DEPRECATED - The Ft.Xml.Domlette readers expand XIncludes by default.
    """
    warnings.warn("ProcessIncludesFromUri() is deprecated",
                  DeprecationWarning, 2)
    if validate:
        from Ft.Xml.Domlette import ValidatingReader as reader
    else:
        from Ft.Xml.Domlette import NonvalidatingReader as reader
    return reader.parseUri(uri)

def ProcessIncludesFromString(string, uri='', validate=0):
    """
    DEPRECATED - The Ft.Xml.Domlette readers expand XIncludes by default.
    """
    warnings.warn("ProcessIncludesFromString() is deprecated",
                  DeprecationWarning, 2)
    if validate:
        from Ft.Xml.Domlette import ValidatingReader as reader
    else:
        from Ft.Xml.Domlette import NonvalidatingReader as reader
    return reader.parseString(string, uri)

def ProcessIncludesFromSource(inputSource, validate=0):
    """
    DEPRECATED - The Ft.Xml.Domlette readers expand XIncludes by default.
    """
    warnings.warn("ProcessIncludesFromSource() is deprecated",
                  DeprecationWarning, 2)
    if validate:
        from Ft.Xml.Domlette import ValidatingReader as reader
    else:
        from Ft.Xml.Domlette import NonvalidatingReader as reader
    return reader.parse(inputSource)

