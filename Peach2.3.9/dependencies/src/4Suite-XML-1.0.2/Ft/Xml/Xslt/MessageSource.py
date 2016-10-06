########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/MessageSource.py,v 1.37 2005/04/03 06:47:13 jkloth Exp $
"""
XSLT error codes and messages

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft import TranslateMessage as _

POSITION_INFO = _('In stylesheet %s, line %s, column %s:\n%s')

EXPRESSION_POSITION_INFO = _('In stylesheet %s, line %s, column %s in "%s":\n'
                             '%s')

XSLT_EXPRESSION_POSITION_INFO = _('%s\n'
                                  'The error occurred in the expression "%s".')

BUILTIN_TEMPLATE_WITH_PARAMS = _('Built-in template invoked with params that '
                                 'will be ignored. This message will only '
                                 'appear once per transform.')

TEMPLATE_CONFLICT_LOCATION = _('In stylesheet %s, line %s, column %s, pattern %s')

# for xsl:message output
DEFAULT_MESSAGE_PREFIX = _('STYLESHEET MESSAGE:\n')
DEFAULT_MESSAGE_SUFFIX = _('\nEND STYLESHEET MESSAGE\n')

class Error:
    # internal errors
    #INTERNAL_ERROR = 1

    # xsl:stylesheet
    NO_STYLESHEET = 20
    #STYLESHEET_MISSING_VERSION = 21
    LITERAL_RESULT_MISSING_VERSION = 22
    STYLESHEET_PARSE_ERROR = 23
    SOURCE_PARSE_ERROR = 24
    #XSL_STYLESHEET_NOT_DOCELEM = 25
    #TOP_LEVEL_ELEM_WITH_NULL_NS = 26
    XSLT_ILLEGAL_ELEMENT = 27
    #STYLESHEET_ILLEGAL_ROOT = 28
    CIRCULAR_VAR = 29
    DUPLICATE_TOP_LEVEL_VAR = 30
    DUPLICATE_NAMESPACE_ALIAS = 31

    # misc element validation
    ILLEGAL_ELEMENT_CHILD = 50
    ILLEGAL_TEXT_CHILD_PARSE = 51
    UNDEFINED_PREFIX = 52

    # misc attribute validation
    MISSING_REQUIRED_ATTRIBUTE = 70
    ILLEGAL_NULL_NAMESPACE_ATTR = 71
    ILLEGAL_XSL_NAMESPACE_ATTR = 72
    INVALID_ATTR_CHOICE = 73
    INVALID_CHAR_ATTR = 74
    INVALID_NUMBER_ATTR = 75
    INVALID_NS_URIREF_ATTR = 76
    INVALID_ID_ATTR = 77
    INVALID_QNAME_ATTR = 78
    INVALID_NCNAME_ATTR = 79
    INVALID_PREFIX_ATTR = 80
    INVALID_NMTOKEN_ATTR = 81
    QNAME_BUT_NOT_NCNAME = 82
    AVT_SYNTAX = 83
    AVT_EMPTY = 84
    INVALID_AVT = 85
    INVALID_PATTERN = 86
    INVALID_EXPRESSION = 87
    #PATTERN_SYNTAX = 88
    #PATTERN_SEMANTIC = 89

    # xsl:apply-imports
    APPLYIMPORTS_WITH_NULL_CURRENT_TEMPLATE = 100

    # xsl:import and xsl:include
    ILLEGAL_IMPORT = 110
    #IMPORT_NOT_FOUND = 111
    INCLUDE_NOT_FOUND = 112
    CIRCULAR_INCLUDE = 113

    # xsl:choose, xsl:when and xsl:otherwise
    ILLEGAL_CHOOSE_CHILD = 120
    CHOOSE_REQUIRES_WHEN = 121
    #CHOOSE_WHEN_AFTER_OTHERWISE = 122
    #CHOOSE_MULTIPLE_OTHERWISE = 123
    #WHEN_MISSING_TEST = 124

    # xsl:call-template
    #ILLEGAL_CALLTEMPLATE_CHILD = 130
    NAMED_TEMPLATE_NOT_FOUND = 131

    # xsl:template
    #ILLEGAL_TEMPLATE_PRIORITY = 140
    MULTIPLE_MATCH_TEMPLATES = 141
    DUPLICATE_NAMED_TEMPLATE = 142

    # xsl:attribute
    ATTRIBUTE_ADDED_TOO_LATE = 150
    #ATTRIBUTE_MISSING_NAME = 151
    ATTRIBUTE_ADDED_TO_NON_ELEMENT = 152
    NONTEXT_IN_ATTRIBUTE = 153
    BAD_ATTRIBUTE_NAME = 154

    # xsl:element
    UNDEFINED_ATTRIBUTE_SET = 160

    # xsl:for-each
    INVALID_FOREACH_SELECT = 170

    # xsl:value-of
    #VALUEOF_MISSING_SELECT = 180

    # xsl:copy-of
    #COPYOF_MISSING_SELECT = 190

    # xsl:text
    ILLEGAL_TEXT_CHILD = 200

    # xsl:apply-template
    #ILLEGAL_APPLYTEMPLATE_CHILD = 210
    #ILLEGAL_APPLYTEMPLATE_MODE = 211
    ILLEGAL_APPLYTEMPLATE_NODESET = 212

    # xsl:attribute-set
    #ILLEGAL_ATTRIBUTESET_CHILD = 220
    #ATTRIBUTESET_REQUIRES_NAME = 221
    CIRCULAR_ATTRIBUTE_SET = 222

    # xsl:param and xsl:variable
    #ILLEGAL_PARAM = 230
    #ILLEGAL_PARAM_PARENT = 231
    ILLEGAL_SHADOWING = 232
    VAR_WITH_CONTENT_AND_SELECT = 233

    # xsl:message
    #ILLEGAL_MESSAGE_PARENT = 240
    STYLESHEET_REQUESTED_TERMINATION = 241

    # xsl:processing-instruction
    ILLEGAL_XML_PI = 250
    NONTEXT_IN_PI = 251

    # xsl:output
    UNKNOWN_OUTPUT_METHOD = 260

    # xsl:decimal-format
    DUPLICATE_DECIMAL_FORMAT = 270
    UNDEFINED_DECIMAL_FORMAT = 271

    # xsl:sort
    #ILLEGAL_SORT_DATA_TYPE_VALUE = 280
    #ILLEGAL_SORT_CASE_ORDER_VALUE = 281
    #ILLEGAL_SORT_ORDER_VALUE = 282

    # xsl:number
    #ILLEGAL_NUMBER_GROUPING_SIZE_VALUE = 290
    #ILLEGAL_NUMBER_LEVEL_VALUE = 291
    #ILLEGAL_NUMBER_LETTER_VALUE = 292
    ILLEGAL_NUMBER_FORMAT_VALUE = 293
    UNSUPPORTED_NUMBER_LANG_VALUE = 294
    UNSUPPORTED_NUMBER_LETTER_FOR_LANG = 295

    # xsl:namespace-alias
    #INVALID_NAMESPACE_ALIAS = 300

    # xsl:comment
    NONTEXT_IN_COMMENT = 310

    # xsl:fallback and forwards-compatible processing
    FWD_COMPAT_WITHOUT_FALLBACK = 320
    UNKNOWN_EXTENSION_ELEMENT = 321

    # built-in functions and XSLT-specific extension functions
    DOC_FUNC_EMPTY_NODESET = 1000
    UNKNOWN_NODE_BASE_URI = 1001
    #KEY_WITH_RTF_CONTEXT = 1002
    #WRONG_NUMBER_OF_ARGUMENTS = 2000
    WRONG_ARGUMENT_TYPE = 2001
    INVALID_QNAME_ARGUMENT = 2002

    # EXSLT messages use 3000-3999; see Exslt/MessageSource.py

    # built-in output methods
    RESTRICTED_OUTPUT_VIOLATION = 7000

    #FEATURE_NOT_SUPPORTED = 9999


g_errorMessages = {

    # internal errors
    #Error.INTERNAL_ERROR: _('There is an internal bug in 4Suite. '
    #    'Please make a post to the 4Suite mailing list to report this error '
    #    'message to the developers. Include platform details and info about '
    #    'how to reproduce the error. Info about the mailing list is at '
    #    'http://lists.fourthought.com/mailman/listinfo/4suite. '
    #    'The error code to report is: %s'),

    # xsl:stylesheet
    Error.NO_STYLESHEET: _('No stylesheets to process.'),
    #Error.STYLESHEET_MISSING_VERSION: _('Stylesheet "%s", document root element must have a version attribute.  (see XSLT 1.0 sec. 2.2)'),
    Error.LITERAL_RESULT_MISSING_VERSION: _('Document root element must have a xsl:version attribute.  (see XSLT 1.0 sec. 2.3).'),
    Error.STYLESHEET_PARSE_ERROR: _('Error parsing stylesheet (%s): %s'),
    Error.SOURCE_PARSE_ERROR: _('Error parsing source document (%s): %s'),
    #Error.XSL_STYLESHEET_NOT_DOCELEM: _('An xsl:stylesheet or xsl:transform element must be the document element.'),
    #Error.TOP_LEVEL_ELEM_WITH_NULL_NS: _(''),
    Error.XSLT_ILLEGAL_ELEMENT: _("Illegal element '%s' in XSLT Namespace (see XSLT 1.0 sec. 2.1)."),
    #Error.STYLESHEET_ILLEGAL_ROOT: _('Illegal Document Root Element "%s" (see XSLT 1.0 sec. 2.2).'),
    Error.CIRCULAR_VAR: _('Circular variable reference error (see XSLT 1.0 sec. 11.4) for variable or parameter: (%s, %s)'),
    Error.DUPLICATE_TOP_LEVEL_VAR: _('Top level variable %s has duplicate definitions with the same import precedence.  (see XSLT 1.0 sec. 11)'),
    Error.DUPLICATE_NAMESPACE_ALIAS: _('The namespace for "%s" has duplicate namespace aliases defined with the same import precedence.  (see XSLT 1.0 sec. 2.6.2)'),

    # misc element validation
    Error.ILLEGAL_ELEMENT_CHILD: _("Illegal child '%s' within element '%s'"),
    Error.ILLEGAL_TEXT_CHILD_PARSE: _("Illegal literal text %s within element '%s'"),
    Error.UNDEFINED_PREFIX: _("Undefined namespace prefix '%s'"),

    # misc attribute validation
    Error.MISSING_REQUIRED_ATTRIBUTE: _("Element '%s' missing required attribute '%s'"),
    Error.ILLEGAL_NULL_NAMESPACE_ATTR: _("Illegal null-namespace attribute '%s' on element '%s'."),
    Error.ILLEGAL_XSL_NAMESPACE_ATTR: _("Illegal xsl-namespace attribute '%s' on element '%s'."),
    Error.INVALID_ATTR_CHOICE: _("Illegal attribute value '%s', must be one of '%s'"),
    Error.INVALID_CHAR_ATTR: _("Invalid char attribute value '%s'"),
    Error.INVALID_NUMBER_ATTR: _("Invalid number attribute value '%s'"),
    Error.INVALID_NS_URIREF_ATTR: _("'%s' is not a valid namespace name (see Namespaces in XML erratum NE05)"),
    Error.INVALID_ID_ATTR: _("Invalid ID attribute value '%s'"),
    Error.INVALID_QNAME_ATTR: _("Invalid QName attribute value '%s'"),
    Error.INVALID_NCNAME_ATTR: _("Invalid NCName attribute value '%s'"),
    Error.INVALID_PREFIX_ATTR: _("Invalid prefix attribute value '%s'"),
    Error.INVALID_NMTOKEN_ATTR: _("Invalid NMTOKEN attribute value '%s'"),
    Error.QNAME_BUT_NOT_NCNAME: _("QName allowed but not NCName, '%s' found"),
    Error.AVT_SYNTAX: _('Unbalanced curly braces ({}) in attribute value template. (see XSLT 1.0 sec. 7.6.2)'),
    Error.AVT_EMPTY: _('No expression in attribute value template.'),
    Error.INVALID_AVT: _('Malformed attribute value template: "%s" in the element at %s, line %s, column %s\n  %s'),
    Error.INVALID_PATTERN: _('Malformed pattern: "%s" in the element at %s, line %s, column %s\n  %s'),
    Error.INVALID_EXPRESSION: _('Malformed expression: "%s" in the element at %s, line %s, column %s\n  %s'),
    #Error.PATTERN_SYNTAX: _('Syntax error in pattern at location %s (XPattern production number: %d).'),
    #Error.PATTERN_SEMANTIC: _('Parse tree error in pattern at location %s (XPattern production number: %d, error type: %s, error value: %s, traceback:\n%s'),

    # xsl:apply-imports
    Error.APPLYIMPORTS_WITH_NULL_CURRENT_TEMPLATE: _('apply-imports used where there is no current template.  (see XSLT Spec)'),

    # xsl:import and xsl:include
    Error.ILLEGAL_IMPORT: _('xsl:import is not allowed here (xsl:import must be at top level and precede all other XSLT top-level instructions).  (see XSLT 1.0 sec. 2.6.2)'),
    #Error.IMPORT_NOT_FOUND: _(''),
    Error.INCLUDE_NOT_FOUND: _('Unable to open imported or included stylesheet "%s", using base URI "%s", or all base URIs in the include PATH'),
    Error.CIRCULAR_INCLUDE: _('Stylesheet %s may not be included or imported more than once (see XSLT 1.0 sec. 2.6)'),

    # xsl:choose, xsl:when and xsl:otherwise
    Error.ILLEGAL_CHOOSE_CHILD: _('FIXME'),
    Error.CHOOSE_REQUIRES_WHEN: _('"choose" must have at least one "when" child (see XSLT 1.0 sec. 9.2)'),
    #Error.CHOOSE_WHEN_AFTER_OTHERWISE: _('"choose" cannot have "when" child after "otherwise" child (see XSLT 1.0 sec. 9.2)'),
    #Error.CHOOSE_MULTIPLE_OTHERWISE: _('"choose" only allowed one "otherwise" child (see XSLT 1.0 sec. 9.2)'),
    #Error.WHEN_MISSING_TEST: _('xsl:when requires "test" attribute (see XSLT 1.0 sec. 9.2)'),

    # xsl:call-template
    #Error.ILLEGAL_CALLTEMPLATE_CHILD: _('call-template child must be with-param., (see XSLT 1.0 sec. 6)'),
    Error.NAMED_TEMPLATE_NOT_FOUND: _('Named template "%s" invoked but not defined.'),

    # xsl:template
    #Error.ILLEGAL_TEMPLATE_PRIORITY: _('Invalid priority value for template. (see XSLT 1.0 sec. 5.5)'),
    Error.MULTIPLE_MATCH_TEMPLATES:
    _('Multiple templates matching node %r.  (see XSLT 1.0 sec. 5.5).\n'
      'Conflicting template locations:\n%s'),
    Error.DUPLICATE_NAMED_TEMPLATE:
    _("Named template '%s' already defined with same import precedence"),

    # xsl:attribute
    Error.ATTRIBUTE_ADDED_TOO_LATE: _('Children were added to element before xsl:attribute instantiation. (see XSLT 1.0 sec. 7.1.3)'),
    #Error.ATTRIBUTE_MISSING_NAME: _('xsl:attribute missing required name attribute. (see XSLT 1.0 sec. 7.1.3)'),
    Error.ATTRIBUTE_ADDED_TO_NON_ELEMENT: _('xsl:attribute attempted to add attribute to non-element. (see XSLT 1.0 sec. 7.1.3)'),
    Error.NONTEXT_IN_ATTRIBUTE: _('Nodes other than text nodes created during xsl:attribute instantiation. (see XSLT 1.0 sec. 7.1.3)'),
    Error.BAD_ATTRIBUTE_NAME: _('An attribute cannot be created with name %s. (see XSLT 1.0 sec. 7.1.3)'),

    # xsl:element
    Error.UNDEFINED_ATTRIBUTE_SET: _('Undefined attribute set (%s)'),

    # xsl:for-each
    Error.INVALID_FOREACH_SELECT: _('"select" attribute of "for-each" must evaluate to a node set (see XSLT 1.0 sec. 8)'),

    # xsl:value-of
    #Error.VALUEOF_MISSING_SELECT: _('Empty "value-of" requires "select" attribute (see XSLT 1.0 sec. 7.6.1)'),

    # xsl:copy-of
    #Error.COPYOF_MISSING_SELECT: _('Empty "copy-of" requires "select" attribute (see XSLT 1.0 sec. 11.3)'),

    # xsl:text
    Error.ILLEGAL_TEXT_CHILD: _('xsl:text cannot have any child elements" (see XSLT 1.0 sec. 7.2)'),

    # xsl:apply-templates
    #Error.ILLEGAL_APPLYTEMPLATE_CHILD: _('apply-templates child must be with-param or sort. (see XSLT Spec 5.4)'),
    #Error.ILLEGAL_APPLYTEMPLATE_MODE: _('apply-templates mode must be a QName. (see XSLT Spec 5.4)'),
    Error.ILLEGAL_APPLYTEMPLATE_NODESET: _('apply-templates must apply to a node-set.'),

    # xsl:attribute-set
    #Error.ILLEGAL_ATTRIBUTESET_CHILD: _('xsl:attribute-set child must be "attribute" (see XSLT 1.0 sec. 7.1.4)'),
    #Error.ATTRIBUTESET_REQUIRES_NAME: _('xsl:attribute-set requires "name" attribute (see XSLT 1.0 sec. 7.1.4)'),
    Error.CIRCULAR_ATTRIBUTE_SET: _("Circular attribute-set error for '%s'. (see XSLT 1.0 sec. 7.1.4)"),

    # xsl:param and xsl:variable
    #Error.ILLEGAL_PARAM: _('xsl:param elements must be the first children of xsl:template (see XSLT 1.0 sec. 11).'),
    #Error.ILLEGAL_PARAM_PARENT: _('Uri: %s line %s col: %s\n   xsl:param can only appear at top level or as the child of an xsl:template (see XSLT 1.0 sec. 11).'),
    Error.ILLEGAL_SHADOWING: _('Illegal shadowing of %s.  An xsl:param or xsl:variable may not shadow another variable not at top level (see XSLT 1.0 sec. 11).'),
    Error.VAR_WITH_CONTENT_AND_SELECT: _('Illegal binding of of %s.  An xsl:param or xsl:variable may not have both a select attribute and non-empty content. (see XSLT 1.0 sec. 11.2).'),

    # xsl:message
    #Error.ILLEGAL_MESSAGE_PARENT: _('xsl:message cannot be a top-level element. (see XSLT 1.0 sec. 2.2)'),
    Error.STYLESHEET_REQUESTED_TERMINATION: _('A message instruction in the Stylesheet requested termination of processing:\n%s'),

    # xsl:processing-instruction
    Error.ILLEGAL_XML_PI: _('A processing instruction cannot be used to output an XML or text declaration. (see XSLT 1.0 sec. 7.3)'),
    Error.NONTEXT_IN_PI: _('Nodes other than text nodes created during xsl:processing-instruction instantiation. (see XSLT 1.0 sec. 7.4)'),

    # xsl:output
    Error.UNKNOWN_OUTPUT_METHOD: _('Unknown output method (%s)'),

    # xsl:decimal-format
    Error.DUPLICATE_DECIMAL_FORMAT: _('Duplicate declaration of decimal-format %s. (XSLT Spec: 12.3)'),
    Error.UNDEFINED_DECIMAL_FORMAT: _('Undefined decimal-format (%s)'),

    # xsl:sort
    #Error.ILLEGAL_SORT_CASE_ORDER_VALUE: _('The case-order attribute of sort must be either "upper-first" or "lower-first" (see XSLT 1.0 sec. 10)'),
    #Error.ILLEGAL_SORT_DATA_TYPE_VALUE: _('The data-type attribute of sort must be either "text" or "number" (see XSLT 1.0 sec. 10).'),
    #Error.ILLEGAL_SORT_ORDER_VALUE: _('The order attribute of sort must be either "ascending" or "descending". (see XSLT 1.0 sec. 10)'),

    # xsl:number
    #Error.ILLEGAL_NUMBER_GROUPING_SIZE_VALUE: _('The "grouping-size" attribute of number must be an integer. (see XSLT 1.0 sec. 7.7.1)'),
    #Error.ILLEGAL_NUMBER_LEVEL_VALUE: _('The "level" attribute of number must be "single", "multiple" or "any". (see XSLT 1.0 sec. 7.7)'),
    #Error.ILLEGAL_NUMBER_LETTER_VALUE: _('The "letter-value" attribute of number must be "alphabetic" or "traditional". (see XSLT 1.0 sec. 7.7.1)'),
    Error.ILLEGAL_NUMBER_FORMAT_VALUE: _('Value "%s" for "format" attribute of xsl:number is invalid. (see XSLT 1.0 sec. 7.7)'),
    Error.UNSUPPORTED_NUMBER_LANG_VALUE: _('Language "%s" for alphabetic numbering in xsl:number is unsupported.'),
    Error.UNSUPPORTED_NUMBER_LETTER_FOR_LANG: _('Value "%s" for "letter-value" attribute of xsl:number is not supported with the language "%s".'),

    # xsl:namespace-alias
    #Error.INVALID_NAMESPACE_ALIAS: _('Invalid arguments to the namespace-alias instruction. (see XSLT 1.0 sec. 7.1.1)'),

    # xsl:comment
    Error.NONTEXT_IN_COMMENT: _('Nodes other than text nodes created during xsl:comment instantiation. (see XSLT 1.0 sec. 7.4)'),

    # xsl:fallback and forwards-compatible processing
    Error.FWD_COMPAT_WITHOUT_FALLBACK: _('No xsl:fallback instruction found for element %r processed in forward-compatible mode.'),
    Error.UNKNOWN_EXTENSION_ELEMENT:
    _('No implementation for extension element %r, %r'),

    # built-in functions and XSLT-specific extension functions
    Error.DOC_FUNC_EMPTY_NODESET: _('Second argument to document(), if given, must be a non-empty node-set. (see XSLT 1.0 sec. 12.1 erratum E14)'),
    Error.UNKNOWN_NODE_BASE_URI: _('Could not determine base URI of node: %s'),
    #Error.KEY_WITH_RTF_CONTEXT: _('key() must not be invoked when the context node comes from the result tree (probably due to an earlier invokation of node-set()).'),
    #Error.WRONG_NUMBER_OF_ARGUMENTS: _('A built-in or extension function was called with the wrong number of arguments.'),
    Error.WRONG_ARGUMENT_TYPE: _('A built-in or extension function was called with the wrong type of argument(s).'),
    Error.INVALID_QNAME_ARGUMENT: _('A built-in or extension function requiring a QName argument was called with this non-QName value: "%s".'),

    # EXSLT messages use 3000-3999; see Exslt/MessageSource.py

    # built-in output methods
    Error.RESTRICTED_OUTPUT_VIOLATION: _('The requested output of element "%s" is forbidden according to output restrictions'),

    #Error.FEATURE_NOT_SUPPORTED: _('4XSLT does not yet support this feature.'),

}
