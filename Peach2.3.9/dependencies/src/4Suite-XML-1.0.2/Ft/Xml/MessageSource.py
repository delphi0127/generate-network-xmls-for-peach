########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/MessageSource.py,v 1.13 2006/02/04 00:06:36 jkloth Exp $
"""
Localizable message strings

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft import TranslateMessage as _
from Ft.Xml import ReaderException, XIncludeException

XINCLUDE = {
    XIncludeException.MISSING_HREF : _('Missing or empty href attribute'),
    XIncludeException.INVALID_PARSE_ATTR : _(
    'Invalid value %r for parse attribute'),
    XIncludeException.TEXT_XPOINTER : _(
    'xpointer attribute forbidden for parse="text"'),
    XIncludeException.FRAGMENT_IDENTIFIER : _(
    'Fragment identifier not allowed in URI %r; use the xpointer attribute'),
    XIncludeException.UNSUPPORTED_XPOINTER : _(
    'Unsupported XPointer %r'),
    XIncludeException.INCLUDE_IN_INCLUDE :_(
    'xi:include has an xi:include child'),
    XIncludeException.FALLBACK_NOT_IN_INCLUDE : _(
    'xi:fallback is not the child of an xi:include'),
    XIncludeException.MULTIPLE_FALLBACKS : _(
    'xi:include with multiple xi:fallback children'),
    }

READER = {
    # Fatal errors
    ReaderException.SYNTAX_ERROR: _("syntax error"),
    ReaderException.NO_ELEMENTS: _("no element found"),
    ReaderException.INVALID_TOKEN: _("not well-formed (invalid token)"),
    ReaderException.UNCLOSED_TOKEN: _("unclosed token"),
    ReaderException.PARTIAL_CHAR: _("partial character"),
    ReaderException.TAG_MISMATCH: _("mismatched tag"),
    ReaderException.DUPLICATE_ATTRIBUTE: _("duplicate attribute"),
    ReaderException.JUNK_AFTER_DOCUMENT_ELEMENT: _("junk after document element"),
    ReaderException.ILLEGAL_PARAM_ENTITY_REF: _("illegal parameter entity reference"),
    ReaderException.UNDEFINED_ENTITY: _("undefined entity"),
    ReaderException.RECURSIVE_ENTITY_REF: _("recursive entity reference"),
    ReaderException.ASYNC_ENTITY: _("asynchronous entity"),
    ReaderException.BAD_CHAR_REF: _("reference to invalid character number"),
    ReaderException.BINARY_ENTITY_REF: _("reference to binary entity"),
    ReaderException.ATTRIBUTE_EXTERNAL_ENTITY_REF: _("reference to external entity in attribute"),
    ReaderException.MISPLACED_XML_PI: _("XML or text declaration not at start of entity"),
    ReaderException.UNKNOWN_ENCODING: _("unknown encoding"),
    ReaderException.INCORRECT_ENCODING: _("encoding specified in XML declaration is incorrect"),
    ReaderException.UNCLOSED_CDATA_SECTION: _("unclosed CDATA section"),
    ReaderException.EXTERNAL_ENTITY_HANDLING: _("error in processing external entity reference"),
    ReaderException.NOT_STANDALONE: _("document is not standalone"),
    ReaderException.ENTITY_DECLARED_IN_PE: _("entity declared in parameter entity"),
    ReaderException.UNBOUND_PREFIX: _("unbound prefix"),
    ReaderException.UNDECLARED_PREFIX: _("must not undeclare prefix"),
    ReaderException.INCOMPLETE_PE: _("incomplete markup in parameter entity"),
    ReaderException.INVALID_XML_DECL: _("XML declaration not well-formed"),
    ReaderException.INVALID_TEXT_DECL: _("text declaration not well-formed"),
    ReaderException.INVALID_PUBLICID: _("illegal character(s) in public id"),
    ReaderException.RESERVED_PREFIX_XML: _("reserved prefix (xml) must not be undeclared or bound to another namespace name"),
    ReaderException.RESERVED_PREFIX_XMLNS: _("reserved prefix (xmlns) must not be declared or undeclared"),
    ReaderException.RESERVED_NAMESPACE_URI: _("prefix must not be bound to one of the reserved namespace names"),

    # -- Validity Errors -----------------------------------------------------

    ReaderException.MISSING_DOCTYPE: _("Missing document type declaration"),
    ReaderException.INVALID_ELEMENT: _("Element '%(element)s' not allowed here"),
    ReaderException.ROOT_ELEMENT_MISMATCH: _("Document root element '%(element)s' does not match declared root element"),
    ReaderException.UNDECLARED_ELEMENT: _("Element '%(element)s' not declared"),
    ReaderException.INCOMPLETE_ELEMENT: _("Element '%(element)s' ended before all required elements found"),
    ReaderException.INVALID_TEXT: _("Character data not allowed in the content of element '%(element)s'"),
    ReaderException.UNDECLARED_ATTRIBUTE: _("Attribute '%(attr)s' not declared"),
    ReaderException.DUPLICATE_ID: _("ID '%(id)s' appears more than once"),
    ReaderException.UNDECLARED_ENTITY: _("Entity '%(entity)s' not declared"),
    ReaderException.INVALID_ENTITY: _("Entity '%(entity)s' is not an unparsed entity"),
    ReaderException.UNDECLARED_NOTATION: _("Notation '%(notation)s' not declared"),
    ReaderException.MISSING_ATTRIBUTE: _("Missing required attribute '%(attr)s'"),
    ReaderException.UNDEFINED_ID: _("IDREF referred to non-existent ID '%(id)s'"),
    ReaderException.DUPLICATE_ELEMENT_DECL: _("Element '%(element)s' declared more than once"),
    ReaderException.DUPLICATE_ID_DECL: _("Only one ID attribute allowed on each element type"),
    ReaderException.ID_ATTRIBUTE_DEFAULT: _("ID attributes cannot have a default value"),
    ReaderException.XML_SPACE_DECL: _("xml:space must be declared an enumeration type"),
    ReaderException.XML_SPACE_VALUES: _("xml:space must have exactly one or both of the values 'default' and 'preserve'"),
    ReaderException.INVALID_NAME_VALUE: _("Value of '%(attr)s' attribute is not a valid name"),
    ReaderException.INVALID_NAME_SEQ_VALUE: _("Value of '%(attr)s' attribute is not a valid name sequence"),
    ReaderException.INVALID_NMTOKEN_VALUE: _("Value of '%(attr)s' attribute is not a valid name token"),
    ReaderException.INVALID_NMTOKEN_SEQ_VALUE: _("Value of '%(attr)s' attribute is not a valid name token sequence"),
    ReaderException.INVALID_ENUM_VALUE: _("'%(value)s in not an allowed value for the '%(attr)s' attribute"),
    ReaderException.ATTRIBUTE_UNDECLARED_NOTATION: _("Notation attribute '%(attr)s' uses undeclared notation '%(notation)s'"),
    ReaderException.ENTITY_UNDECLARED_NOTATION: _(""),

    # -- Warnings ------------------------------------------------------------

    ReaderException.ATTRIBUTES_WITHOUT_ELEMENT: _("Attribute list for undeclared element '%(element)s'"),
    ReaderException.ATTRIBUTE_DECLARED: _("Attribute '%(attr)s' already declared"),
    ReaderException.ENTITY_DECLARED: _("Entity '%(entity)s' already declared"),

    # -- Miscellaneous -------------------------------------------------------

    ReaderException.XML_PARSE_ERROR: _('XML parse error in %r at line %d, column %d: %s'),
    ReaderException.RECURSIVE_PARSE_ERROR: _("Recursive parsing of '%(uri)s'"),
    }
