########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/NumberElement.py,v 1.10 2005/04/06 23:05:47 jkloth Exp $
"""
Implementation of xsl:number

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Lib import number
from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.Xslt import XsltElement, XSL_NAMESPACE
from Ft.Xml.Xslt import CategoryTypes, AttributeInfo, ContentInfo
from Ft.Xml.Xslt import XsltException, XsltRuntimeException, Error
from Ft.Xml.XPath import Conversions

from NumberFormatter import DefaultFormatter

DEFAULT_LANG = 'en'
DEFAULT_FORMAT = '1'

SINGLE = 0
MULTIPLE = 1
ANY = 2
SIMPLE = 3  # no count or from

class NumberElement(XsltElement):

    category = CategoryTypes.INSTRUCTION
    content = ContentInfo.Empty
    legalAttrs = {
        'level' : AttributeInfo.Choice(['single', 'multiple', 'any'],
                                       default='single'),
        'count' : AttributeInfo.Pattern(),
        'from' : AttributeInfo.Pattern(),
        'value' : AttributeInfo.Expression(),
        'format' : AttributeInfo.StringAvt(default='1'),
        'lang' : AttributeInfo.NMToken(),
        'letter-value' : AttributeInfo.ChoiceAvt(['alphabetic', 'traditional']),
        'grouping-separator' : AttributeInfo.CharAvt(),
        'grouping-size' : AttributeInfo.NumberAvt(default=0),
        }

    doesSetup = 1

    def setup(self):
        if self._level == 'single':
            if not self._count and not self._from:
                self._level = SIMPLE
            else:
                self._level = SINGLE
        elif self._level == 'multiple':
            self._level = MULTIPLE
        elif self._level == 'any':
            self._level = ANY

        if self._format.isConstant():
            self._formatter = self.createFormatter(self._format.evaluate(None),
                                                   language=self._lang)
        else:
            self._formatter = None
        return

    def createFormatter(self, format, language=None, letterValue=None):
        """
        Creates a formatter appropriate for the given language and
        letterValue, or a default, English-based formatter. Raises an
        exception if the language or letterValue is unsupported.
        Currently, if the language value is given, it must indicate
        English.
        """
        # lang specifies the language whose alphabet is to be used
        #  for numbering when a format token is alphabetic.
        #
        # "if no lang value is specified, the language should be
        # determined from the system environment." -- unsupported;
        # we just default to English.
        if language and not language.lower().startswith('en'):
            raise XsltRuntimeException(Error.UNSUPPORTED_NUMBER_LANG_VALUE,
                                       self, language)

        # letter-value says how to resolve the ambiguity that arises when
        # you want alphabetic numbering to start with some letter, but
        # that letter, when used in a format token, normally indicates
        # some other numbering system. e.g., in English, the format token
        # "A" means to use the letter "A" for 1, "B" for 2, etc., and
        # "B" means to use the letter "B" for 1, "C" for 2, etc.,
        # but "I" indicates Roman numbering. letter-value="alphabetic" can
        # force the interpretation to be that "I" instead means to use the
        # letter "I" for 1, "J" for 2, etc.
        # Valid values are 'traditional' or 'alphabetic'.
        #
        # Our DefaultFormatter only supports English language and
        # traditional, not alphabetic, letter-value.
        if letterValue and letterValue != 'traditional':
            if not language or language.lower().startswith('en'):
                raise XsltRuntimeException(Error.UNSUPPORTED_NUMBER_LETTER_FOR_LANG,
                                           self, letterValue, language or 'en')

        return DefaultFormatter(format)

    def instantiate(self, context, processor):
        # get value(s) to format
        if self._value:
            value = Conversions.NumberValue(self._value.evaluate(context))
            if not number.finite(value) or value < 0.5:
                # This is an error.  However, recovery is to just write
                # the number as if the string() function was used.
                processor.writers[-1].text(Conversions.StringValue(value))
                return
            else:
                values = [int(round(value))]
        else:
            node = context.node
            if self._level == SINGLE:
                value = self._single_value(context, node, self._count, self._from)
                if value == 0:
                    values = []
                else:
                    values = [value]
            elif self._level == MULTIPLE:
                values = self._multiple_values(context, node)
            elif self._level == ANY:
                value = self._any_value(context, node)
                if value == 0:
                    values = []
                else:
                    values = [value]
            else:
                # 'single' without count or from attributes
                value = 1
                prev = node.previousSibling
                type = node.nodeType
                expanded = (node.namespaceURI, node.localName)
                while prev:
                    if prev.nodeType == type and \
                       (prev.namespaceURI, prev.localName) == expanded:
                        value += 1
                    prev = prev.previousSibling
                values = [value]

        # format the value(s)
        grouping_size = int(self._grouping_size.evaluate(context))
        if grouping_size:
            grouping_separator = self._grouping_separator.evaluate(context)
        else:
            grouping_separator = None

        formatter = self._formatter
        if not formatter:
            format = self._format and self._format.evaluate(context) or DEFAULT_FORMAT
            lang = self._lang and self._lang.evaluate(context) or DEFAULT_LANG
            letter_value =  self._letter_value.evaluate(context) or ''
            formatter = self.createFormatter(format, lang, letter_value)

        numstr = formatter.format(values, grouping_size, grouping_separator)
        processor.writers[-1].text(numstr)
        return

    def _single_value(self, context, node, countPattern, fromPattern):
        if not countPattern:
            if not node.localName:
                # text, comment and processing instruction
                countPattern = NodeTypeTest(node)
            else:
                countPattern = NameTest(node)

        if fromPattern:
            start = node.parentNode
            while start and not fromPattern.match(context, start):
                start = start.parentNode
        else:
            start = node.rootNode

        while not countPattern.match(context, node):
            node = node.parentNode
            if node is None or node == start:
                return 0

        value = 0
        while node:
            value += 1
            node = node.previousSibling
            while node and not countPattern.match(context, node):
                node = node.previousSibling
        return value

    def _multiple_values(self, context, node):
        if not self._count:
            if not node.localName:
                # text, comment and processing instruction
                count = NodeTypeTest(node)
            else:
                count = NameTest(node)
        else:
            count = self._count

        values = []
        while node:
            if count.match(context, node):
                value = self._single_value(context, node, count,  None)
                values.insert(0, value)
            node = node.parentNode
            if node and self._from and self._from.match(context, node):
                break
        return values

    def _any_value(self, context, node):
        if not self._count:
            if not node.localName:
                # text, comment and processing instruction
                count = NodeTypeTest(node)
            else:
                count = NameTest(node)
        else:
            count = self._count

        value = 0
        while node:
            if self._from and self._from.match(context, node):
                break
            if count.match(context, node):
                value += 1
            if not node.previousSibling:
                node = node.parentNode
            else:
                node = node.previousSibling
                while node.lastChild:
                    node = node.lastChild
        return value


class NodeTypeTest:
    def __init__(self, node):
        self.nodeType = node.nodeType
        return

    def match(self, context, node):
        return (node.nodeType == self.nodeType)

class NameTest:
    def __init__(self, node):
        self.nodeType = node.nodeType
        self.localName = node.localName
        self.namespaceURI = node.namespaceURI
        return

    def match(self, context, node):
        return (node.nodeType == self.nodeType and
                node.localName == self.localName and
                node.namespaceURI == self.namespaceURI)

##Note: emacs can uncomment the ff automatically.

##To: xsl-list@mulberrytech.com
##Subject: Re: number format test
##From: MURAKAMI Shinyu <murakami@nadita.com>
##Date: Thu, 3 Aug 2000 01:18:10 +0900 (Wed 10:18 MDT)

##Kay Michael <Michael.Kay@icl.com> wrote:
##>> 5. Saxon
##>>   - Fullwidth 1 (#xff11) are supported.
##>>   - Hiragana/Katakana/Kanji format generates incorrect result.
##>>     (Unicode codepoint order, such as #x3042, #x3043, #x3044,...)
##>>     useless and trouble with Non-European style processing.
##>>     fix it please!!
##>
##>If you could tell me what the correct sequence is, I'll be happy to include
##>it. Help me please!


##XSLT 1.0 spec says:

##    7.7.1 Number to String Conversion Attributes
##    ...

##    - Any other format token indicates a numbering sequence that starts
##      with that token.  If an implementation does not support a numbering
##      sequence that starts with that token, it must use a format token of 1.

##The last sentence is important.  ...it must use a format token of 1.

##If Saxon will support... the following are Japanese Hiragana/Katakana sequences
##-- modern(A...) and traditional(I...) -- and Kanji(CJK ideographs) numbers.

##format="&#x3042;" (Hiragana A)
##&#x3042;&#x3044;&#x3046;&#x3048;&#x304a;&#x304b;&#x304d;&#x304f;&#x3051;&#x3053;
##&#x3055;&#x3057;&#x3059;&#x305b;&#x305d;&#x305f;&#x3061;&#x3064;&#x3066;&#x3068;
##&#x306a;&#x306b;&#x306c;&#x306d;&#x306e;&#x306f;&#x3072;&#x3075;&#x3078;&#x307b;
##&#x307e;&#x307f;&#x3080;&#x3081;&#x3082;&#x3084;&#x3086;&#x3088;&#x3089;&#x308a;
##&#x308b;&#x308c;&#x308d;&#x308f;&#x3092;&#x3093;

##format="&#x30a2;" (Katakana A)
##&#x30a2;&#x30a4;&#x30a6;&#x30a8;&#x30aa;&#x30ab;&#x30ad;&#x30af;&#x30b1;&#x30b3;
##&#x30b5;&#x30b7;&#x30b9;&#x30bb;&#x30bd;&#x30bf;&#x30c1;&#x30c4;&#x30c6;&#x30c8;
##&#x30ca;&#x30cb;&#x30cc;&#x30cd;&#x30ce;&#x30cf;&#x30d2;&#x30d5;&#x30d8;&#x30db;
##&#x30de;&#x30df;&#x30e0;&#x30e1;&#x30e2;&#x30e4;&#x30e6;&#x30e8;&#x30e9;&#x30ea;
##&#x30eb;&#x30ec;&#x30ed;&#x30ef;&#x30f2;&#x30f3;

##format="&#x3044;" (Hiragana I)
##&#x3044;&#x308d;&#x306f;&#x306b;&#x307b;&#x3078;&#x3068;&#x3061;&#x308a;&#x306c;
##&#x308b;&#x3092;&#x308f;&#x304b;&#x3088;&#x305f;&#x308c;&#x305d;&#x3064;&#x306d;
##&#x306a;&#x3089;&#x3080;&#x3046;&#x3090;&#x306e;&#x304a;&#x304f;&#x3084;&#x307e;
##&#x3051;&#x3075;&#x3053;&#x3048;&#x3066;&#x3042;&#x3055;&#x304d;&#x3086;&#x3081;
##&#x307f;&#x3057;&#x3091;&#x3072;&#x3082;&#x305b;&#x3059;

##format="&#x30a4;" (Katakana I)
##&#x30a4;&#x30ed;&#x30cf;&#x30cb;&#x30db;&#x30d8;&#x30c8;&#x30c1;&#x30ea;&#x30cc;
##&#x30eb;&#x30f2;&#x30ef;&#x30ab;&#x30e8;&#x30bf;&#x30ec;&#x30bd;&#x30c4;&#x30cd;
##&#x30ca;&#x30e9;&#x30e0;&#x30a6;&#x30f0;&#x30ce;&#x30aa;&#x30af;&#x30e4;&#x30de;
##&#x30b1;&#x30d5;&#x30b3;&#x30a8;&#x30c6;&#x30a2;&#x30b5;&#x30ad;&#x30e6;&#x30e1;
##&#x30df;&#x30b7;&#x30f1;&#x30d2;&#x30e2;&#x30bb;&#x30b9;

##format="&#x4e00;" (Kanji 1) (decimal notation)
##&#x4e00;(=1) &#x4e8c;(=2) &#x4e09;(=3) &#x56db;(=4) &#x4e94;(=5)
##&#x516d;(=6) &#x4e03;(=7) &#x516b;(=8) &#x4e5d;(=9) &#x3007;(=0)
##e.g. &#x4e00;&#x3007;(=10)  &#x4e8c;&#x4e94;&#x516d;(=256)
##There are more ideographic(kanji)-number formats, but the above will be sufficient.


##Thanks,
##MURAKAMI Shinyu
##murakami@nadita.com


