########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/AttributeInfo.py,v 1.30 2006/08/11 15:13:36 jkloth Exp $
"""
Classes that support validation and evaluation of attribute values in
XSLT instruction elements

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft import TranslateMessage as _

import cStringIO, traceback

from Ft.Xml.XPath import Conversions
from Ft.Xml.XPath import RuntimeException as XPathRuntimeException
from Ft.Xml.XPath import parser
_xpath_parser = parser.new()

from Ft.Xml.Xslt import XsltException, XsltRuntimeException, Error
from Ft.Xml.Xslt import parser
_xpattern_parser = parser.new()
del parser

from Ft.Xml import XML_NAMESPACE, XMLNS_NAMESPACE, EMPTY_NAMESPACE
from Ft.Xml.Lib.XmlString import IsQName, SplitQName

from AttributeValueTemplate import AttributeValueTemplate


class AttributeInfo:

    display = 'unknown'

    def __init__(self, required=0, default=None, description=''):
        self.required = required
        self.default = default
        self.description = description
        return

    def __str__(self):
        return self.display

    def prepare(self, element, value):
        if value is None:
            return self.default
        return value
    reprocess = prepare

    def validate(self, validation):
        return 1


class _ConstantValue:
    def __init__(self, value):
        self.value = value

    def isConstant(self):
        return 1

    def evaluate(self, context):
        return self.value

    def __repr__(self):
        return repr(self.value)

    def __nonzero__(self):
        return self.value is not None


class Choice(AttributeInfo):

    def __init__(self, values, required=0, default=None, description=''):
        AttributeInfo.__init__(self, required, default, description)
        self.values = values
        return

    def prepare(self, element, value):
        if value is None:
            return self.default
        if value not in self.values:
            # check for a AttributeInfo instance
            allowed = filter(lambda v, t=type(self): type(v) is t, self.values)
            for info in allowed:
                try:
                    allowed.prepare(element, value)
                    return value
                except:
                    pass
            # if we get here it is an error
            raise XsltException(Error.INVALID_ATTR_CHOICE, value, str(self))
        return value
    reprocess = prepare

    def __str__(self):
        return ' | '.join(map(lambda v: '"' + v + '"', self.values))


class Avt:

    def __str__(self):
        return '{ %s }' % self.display

    def prepare(self, element, value):
        if value is None:
            return _ConstantValue(self.reprocess(element, self.default))
        elif '{' not in value and '}' not in value:
            return _ConstantValue(self.reprocess(element, value))
        try:
            return AttributeValueTemplate(value, self, element)
        except SyntaxError, error:
            # an error from the XPath parser
            raise XsltException(Error.INVALID_AVT, value,
                                element.baseUri, element.lineNumber,
                                element.columnNumber, str(error))
        except XsltException, error:
            raise XsltException(Error.INVALID_AVT, value,
                                element.baseUri, element.lineNumber,
                                element.columnNumber, error.args[0])


class ChoiceAvt(Avt, Choice):

    def __str__(self):
        return '{ %s }' % Choice.__str__(self)


class AnyAvt(Avt, AttributeInfo):
    display = _('any avt')


class String(AttributeInfo):
    display = _('string')


class StringAvt(Avt, String):
    pass


class Char(AttributeInfo):
    """
    A string value with a length of one
    """
    display = _('char')

    def prepare(self, element, value):
        if value is None:
            return self.default
        if len(value) > 1:
            raise XsltException(Error.INVALID_CHAR_ATTR, value)
        return value
    reprocess = prepare


class CharAvt(Avt, Char):
    pass


class Number(AttributeInfo):
    display = _('number')

    def prepare(self, element, value):
        if value is None:
            return self.default
        try:
            return float(value or self.default)
        except:
            raise XsltException(Error.INVALID_NUMBER_ATTR, value)
    reprocess = prepare


class NumberAvt(Avt, Number):
    reprocess = Number.prepare


class UriReference(AttributeInfo):
    display = _('uri-reference')

    def __init__(self, required=0, default=None, description='', isNsName=0):
        AttributeInfo.__init__(self, required, default, description)
        self._isNsName = isNsName

    def prepare(self, element, value):
        if value is None:
            return self.default
        if self._isNsName and \
            value == XML_NAMESPACE or value == XMLNS_NAMESPACE:
            raise XsltException(Error.INVALID_NS_URIREF_ATTR, value)
        return value
    reprocess = prepare


class UriReferenceAvt(Avt, UriReference):
    pass


class Id(AttributeInfo):
    display = _('id')

    def prepare(self, element, value):
        if value is None:
            return self.default
        if not value:
            raise XsltException(Error.INVALID_ID_ATTR, value)
        return value
    reprocess = prepare


class IdAvt(Avt, Id):
    pass


class QName(AttributeInfo):
    display = _('qname')

    def prepare(self, element, value):
        if value is None:
            if self.default is None:
                return None
            value = self.default
        elif not IsQName(value):
            raise XsltException(Error.INVALID_QNAME_ATTR, value)

        prefix, local = SplitQName(value)
        if prefix:
            try:
                namespace = element.namespaces[prefix]
            except KeyError:
                raise XsltRuntimeException(Error.UNDEFINED_PREFIX,
                                           element, prefix)
        else:
            namespace = EMPTY_NAMESPACE
        return (namespace, local)
    reprocess = prepare


class QNameAvt(Avt, QName):
    pass


class RawQName(QName):

    def prepare(self, element, value):
        if value is None:
            if self.default is None:
                return None
            value = self.default
        elif not IsQName(value):
            raise XsltException(Error.INVALID_QNAME_ATTR, value)
        return SplitQName(value)
    reprocess = prepare


class RawQNameAvt(Avt, RawQName):
    pass


class NCName(AttributeInfo):
    display = _('ncname')

    def prepare(self, element, value):
        if value is None:
            return self.default
        if not value:
            raise XsltException(Error.INVALID_NCNAME_ATTR, value)
        if ':' in value:
            raise XsltException(Error.INVALID_NCNAME_ATTR, value)
        return value
    reprocess = prepare


class NCNameAvt(Avt, NCName):
    pass


class Prefix(AttributeInfo):
    display = _('prefix')

    def prepare(self, element, value):
        if value is None:
            return self.default
        if not value:
            raise XsltException(Error.INVALID_PREFIX_ATTR, value)
        if ':' in value:
            raise XsltException(Error.INVALID_PREFIX_ATTR, value)
        if value == '#default':
            value = None
        return value
    reprocess = prepare


class PrefixAvt(Avt, Prefix):
    pass


class NMToken(AttributeInfo):
    display = _('nmtoken')

    def prepare(self, element, value):
        if value is None:
            return self.default
        if not value:
            raise XsltException(Error.INVALID_NMTOKEN_ATTR, value)
        return value
    reprocess = prepare


class NMTokenAvt(Avt, NMToken):
    pass


class QNameButNotNCName(AttributeInfo):
    display = _('qname-but-not-ncname')

    def prepare(self, element, value):
        if value is None:
            if self.default is None:
                return None
            value = self.default
        elif not value:
            raise XsltException(Error.QNAME_BUT_NOT_NCNAME, value)

        try:
            index = value.index(':')
        except ValueError:
            raise XsltException(Error.QNAME_BUT_NOT_NCNAME, value)
        prefix, local = value[:index], value[index+1:]
        try:
            namespace = element.namespaces[prefix]
        except KeyError:
            raise XsltRuntimeException(Error.UNDEFINED_PREFIX,
                                       element, prefix)
        return (namespace, local)
    reprocess = prepare


class Token(AttributeInfo):
    """
    An attribute whose value is used as an XPath NameTest
    """
    display = _('token')

    def prepare(self, element, value):
        # a 'token' is really an XPath NameTest; '*' | NCName ':' '*' | QName
        # From XPath 1.0 section 2.3:
        #  if the QName does not have a prefix, then the namespace URI is null
        index = value.rfind(':')
        if index == -1:
            namespace = None
            local = value
        else:
            prefix = value[:index]
            local = value[index+1:]
            try:
                namespace = element.namespaces[prefix]
            except KeyError:
                raise XsltRuntimeException(Error.UNDEFINED_PREFIX,
                                           element, prefix)
        return (namespace, local)
    reprocess = prepare


class TokenAvt(Avt, Token):
    pass


class ExpressionWrapper:

    def __init__(self, expression, element, original):
        self.expression = expression
        self.element = element
        self.original = original
        return

    def __nonzero__(self):
        # True if self.expression is not None, which is always the case
        # otherwise this instance would not exist!
        return True

    def __getattr__(self, attr):
        """Make this behave as if it was the expression object itself."""
        return getattr(self.expression, attr)

    # Provide the copy/pickle helpers so as to not get them from the
    # wrapped expression.
    def __getstate__(self):
        return (self.expression, self.element, self.original)

    def __setstate__(self, state):
        self.expression, self.element, self.original = state
        return

    def evaluate(self,context):
        try:
            return self.expression.evaluate(context)
        except XPathRuntimeException, e:
            import MessageSource
            e.message = MessageSource.EXPRESSION_POSITION_INFO % (
                self.element.baseUri, self.element.lineNumber,
                self.element.columnNumber, self.original, str(e))
            # By modifying the exception value directly, we do not need
            # to raise with that value, thus leaving the frame stack
            # intact (original traceback is displayed).
            raise
        except XsltRuntimeException, e:
            import MessageSource
            e.message = MessageSource.XSLT_EXPRESSION_POSITION_INFO % (
                str(e), self.original)
            # By modifying the exception value directly, we do not need
            # to raise with that value, thus leaving the frame stack
            # intact (original traceback is displayed).
            raise
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception, e:
            import MessageSource
            tb = cStringIO.StringIO()
            tb.write("Lower-level traceback:\n")
            traceback.print_exc(1000, tb)
            raise RuntimeError(MessageSource.EXPRESSION_POSITION_INFO % (
                self.element.baseUri, self.element.lineNumber,
                self.element.columnNumber, self.original, tb.getvalue()))

class Expression(AttributeInfo):
    """
    An attribute whose value is used as an XPath expression
    """
    display = _('expression')

    def prepare(self, element, value):
        if value is None:
            if self.default is None:
                return None
            value = self.default
        try:
            expression = _xpath_parser.parse(value)
        except SyntaxError, error:
            raise XsltException(Error.INVALID_EXPRESSION, value,
                                element.baseUri, element.lineNumber,
                                element.columnNumber, str(error))
        return ExpressionWrapper(expression, element, value)

class NodeSetExpression(Expression):
    display = _('node-set-expression')

class StringExpression(Expression):
    display = _('string-expression')

class NumberExpression(Expression):
    display = _('number-expression')

class BooleanExpression(Expression):
    display = _('boolean-expression')


class Pattern(AttributeInfo):
    """
    An attribute whose value is used as an XPattern expression
    """
    display = _('pattern')

    def prepare(self, element, value):
        if value is None:
            if self.default:
                value = self.default
            else:
                return None
        try:
            return _xpattern_parser.parse(value)
        except SyntaxError, error:
            raise XsltException(Error.INVALID_PATTERN, value,
                                element.baseUri, element.lineNumber,
                                element.columnNumber, str(error))

class Tokens(Token):
    """
    A whitespace separated list of tokens (see Token for description of a token)
    """
    display = _('tokens')

    def prepare(self, element, value):
        if value is None:
            return []
        tokens = []
        for token in value.split():
            prepared = Token.prepare(self, element, token)
            tokens.append(prepared)
        return tokens
    reprocess = prepare

class TokensAvt(Avt, Tokens):
    pass


class QNames(QName):
    """
    A whitespace separated list of qnames (see QName for description of a qname)
    """
    display = _('qnames')

    def prepare(self, element, value):
        if value is None:
            return []
        qnames = []
        for qname in value.split():
            prepared = QName.prepare(self, element, qname)
            qnames.append(prepared)
        return qnames
    reprocess = prepare

class QNamesAvt(Avt, QNames):
    pass


class Prefixes(Prefix):
    """
    A whitespace separated list of prefixes (see Prefix for more information)
    """
    display = _('prefixes')

    def prepare(self, element, value):
        if value is None:
            return []
        prefixes = []
        for prefix in value.split():
            prepared = Prefix.prepare(self, element, prefix)
            prefixes.append(prepared)
        return prefixes
    reprocess = prepare

class PrefixesAvt(Avt, Prefixes):
    pass


class YesNo(AttributeInfo):

    display = '"yes" | "no"'

    def prepare(self, element, value):
        if value is None:
            return self.default and self.default == 'yes'
        elif value not in ['yes', 'no']:
            raise XsltException(Error.INVALID_ATTR_CHOICE, value, str(self))
        return value == 'yes'
    reprocess = prepare

class YesNoAvt(Avt, YesNo):
    pass

