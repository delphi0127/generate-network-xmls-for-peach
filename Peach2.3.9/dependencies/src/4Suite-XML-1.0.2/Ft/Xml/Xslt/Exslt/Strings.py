########################################################################
# $Source: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/Exslt/Strings.py,v $ $Revision: 1.25.4.2 $ $Date: 2006/12/17 21:29:26 $
"""
EXSLT - Strings

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import re, codecs
from Ft.Xml.XPath import Conversions, XPathTypes, NAMESPACE_NODE
from Ft.Xml.Xslt import XsltRuntimeException, Error
from Ft.Xml.Xslt.CopyOfElement import CopyNode

EXSL_STRINGS_NS = "http://exslt.org/strings"

def Align(context, target, padding, alignment=''):
    """
    The str:align function aligns a string within another string.

    See http://exslt.org/str/functions/align/str.align.html for further
    explanation.
    """
    target = Conversions.StringValue(target)
    padding = Conversions.StringValue(padding)
    alignment = alignment and Conversions.StringValue(alignment)

    # If the target string is longer than the padding string, then it is
    # truncated to be the same length as the padding string and returned.
    if len(target) > len(padding):
        return target[:len(padding)]

    # If no third argument is given or if it is not one of 'left', 'right'
    # or 'center', then it defaults to left alignment.
    if alignment == 'right':
        result = padding[:-len(target)] + target
    elif alignment == 'center':
        # With center alignment, the range of characters replaced by the target
        # string is in the middle of the padding string, such that either the
        # number of unreplaced characters on either side of the range is the
        # same or there is one less on the left than there is on the right.
        left = (len(padding) - len(target)) / 2
        right = left + len(target)
        result = padding[:left] + target + padding[right:]
    else:
        result = target + padding[len(target):]
    return result

def Concat(context, nodeset):
    """
    The str:concat function takes a node set and returns the concatenation of
    the string values of the nodes in that node set. If the node set is empty,
    it returns an empty string.
    """
    if type(nodeset) != type([]):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)

    strings = map(Conversions.StringValue, nodeset)
    return u''.join(strings)

def DecodeUri(context, uri, encoding=u'UTF-8'):
    """
    The str:decode-uri function decodes a percent-encoded string, such as
    one would find in a URI.
    """
    uri = Conversions.StringValue(uri)
    encoding = Conversions.StringValue(encoding)
    try:
        decoder = codecs.lookup(encoding)[1]
    except LookupError:
        # Unsupported encoding
        return u''

    def repl(match, decoder=decoder):
        # Remove the leading '%'
        sequence = match.group()[1:]
        # There may be multiple encoded characters that are required
        # to produce a single Unicode character.
        ordinals = sequence.split('%')
        characters = [ chr(int(ordinal, 16)) for ordinal in ordinals ]

        # Ignore any invalid sequences in this encoding
        return decoder(''.join(characters), 'ignore')[0]

    return re.sub('(?:%[0-9a-fA-F]{2})+', repl, uri)


_unreserved = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789'
               "-_.!~*'()"
               '%') # not really unreserved, but handled specially before these

_reserved = ';/?:@&=+$,[]'

def EncodeUri(context, uri, escapeReserved, encoding=u'UTF-8'):
    """
    The str:encode-uri function percent-encodes a string for embedding in a URI.
    The second argument is a boolean indicating whether to escape reserved characters;
    if true, the given string can be a URI already, with just some of its characters
    needing to be escaped (not recommended, but users who don't understand the nuances
    of the URI syntax tend to prefer it over assembling a URI piece-by-piece).
    """
    uri = Conversions.StringValue(uri)
    escape_reserved = Conversions.BooleanValue(escapeReserved)
    encoding = Conversions.StringValue(encoding)

    try:
        encoder = codecs.lookup(encoding)[0]
    except LookupError:
        return u''

    # The "%" is escaped only if it is not followed by two hexadecimal digits.
    uri = re.sub('%(?![0-9A-Fa-f]{2})', u'%25', uri)

    safe = _unreserved
    if not escape_reserved:
        safe += _reserved

    res = list(uri)
    for i in xrange(len(res)):
        c = res[i]
        if c not in safe:
            try:
                if ord(c) > 127:
                    encoded = encoder(c, 'strict')[0]
                else:
                    encoded = chr(ord(c))
            except UnicodeError:
                # Not valid in this encoding
                encoded = '%3F'
            else:
                # The Unicode character could map to multiple bytes
                encoded = u''.join([ '%%%02X' % ord(c) for c in encoded ])
            res[i] = encoded
    return u''.join(res)


def Padding(context, length, chars=None):
    """
    The str:padding function creates a padding string of a certain length.

    The second argument gives a string to be used to create the padding.
    This string is repeated as many times as is necessary to create a string
    of the length specified by the first argument; if the string is more than
    a character long, it may have to be truncated to produce the required
    length. If no second argument is specified, it defaults to a space (' ').
    """
    length = int(Conversions.NumberValue(length))
    chars = chars and Conversions.StringValue(chars) or u' '
    return (chars*length)[:length]

def Replace(context, s, searchNodes, replNodes):
    """
    The str:replace function converts a string to a node-set, with
    each instance of a substring from a given list (obtained from the
    string-values of nodes in the second argument) replaced by the
    node at the corresponding position of the node-set given as the
    third argument. Unreplaced substrings become text nodes.

    The second and third arguments can be any type of object; if
    either is not a node-set, it is treated as if it were a node-set
    of just one text node, formed from the object's string-value.

    Attribute and namespace nodes in the replacement set are
    erroneous but are treated as empty text nodes.

    All occurrences of the longest substrings are replaced first,
    and once a replacement is made, that span of the original string
    is no longer eligible for future replacements.

    An empty search string matches between every character of the
    original string.

    See http://exslt.org/str/functions/replace/str.replace.html for details.
    """
    #FIXME: http://www.exslt.org/str/functions/replace/ doesn't say we have
    #to convert the first arg to a string, but should we, anyway?
    #If not, we should at least check and flag non-strings with a clear error?
    # prepare a list of strings to search for (based on searchNodeSet)
    s = Conversions.StringValue(s)
    if not isinstance(searchNodes, XPathTypes.NodesetType):
        search_set = [Conversions.StringValue(searchNodes)]
    else:
        search_set = map(Conversions.StringValue, searchNodes)

    # prepare a list of replacement nodes for each search string (based on replNodes)
    if type(replNodes) is not type([]):
        replace_set = [context.node.rootNode.createTextNode(Conversions.StringValue(replNodes))]
    else:
        # use replNodes but replace attr, ns nodes with empty text nodes
        replace_set = [(n.nodeType == n.ATTRIBUTE_NODE or
                        n.nodeType == NAMESPACE_NODE) and
                       context.node.createTextNode(u'') or n
                       for n in replNodes]

    # make a list of tuples that map each search string to a replacement node or None
    replacements = map(None, search_set, replace_set)
    replacements = [tup for tup in replacements if tup[0]]

    # Sort the tuples in ascending order by length of string.
    # So that the longest search strings will be replaced first,
    # we will process it in reverse order (it may be more efficient to
    # pop items off the end of a list; see
    # http://groups.google.com/groups?selm=3DE41EBE.B60BA9FE%40alcyone.com
    replacements.sort(lambda a, b: cmp(len(a[0]), len(b[0])))

    # generate a result tree fragment
    processor = context.processor
    processor.pushResultTree(context.currentInstruction.baseUri)
    try:
        _replace(s, replacements, processor)
    finally:
        rtf = processor.popResult()

    # return it as a node-set
    return rtf.childNodes


def _replace(s, replmap, processor):
    """
    Supports str:replace(). s is a string. replmap is a list of tuples,
    where each tuple is a search string and a replacement node or None.
    This recursive function will cause the original string to have
    occurrences of the search strings replaced with the corresponding
    node or deleted. When a replacement is made, that portion of the
    original string is no longer available for further replacements.
    All replacements are made for each search string before moving on
    to the next. Empty search strings match in between every character
    of the original string.
    """
    # rm is a locally-scoped copy of replmap
    rm = replmap[:]
    if rm:
        sr = rm.pop()
        if sr[0]:
            nms = s.split(sr[0])
        else:
            nms = [c for c in s] #FIXME nms = list(s) as soon as 2.3 is minimum
        last_i = len(nms) - 1
        for i in xrange(len(nms)):
            if nms[i]:
                _replace(nms[i], rm, processor)
            if i < last_i and sr[1]:
                CopyNode(processor, sr[1])
    else:
        processor.writer.text(s)
    return


def Split(context, string, pattern=u' '):
    """
    The str:split function splits up a string and returns a node set of
    token elements, each containing one token from the string.

    The first argument is the string to be split. The second argument is a
    pattern string (default=' '). The string given by the first argument is
    split at any occurrence of this pattern. An empty string pattern will
    result in a split on every character in the string.
    """
    string = Conversions.StringValue(string)
    pattern = Conversions.StringValue(pattern)
    processor = context.processor
    processor.pushResultTree(context.currentInstruction.baseUri)
    try:
        if pattern:
            for token in string.split(pattern):
                processor.writer.startElement(u'token')
                processor.writer.text(token)
                processor.writer.endElement(u'token')
        else:
            for ch in string:
                processor.writer.startElement(u'token')
                processor.writer.text(ch)
                processor.writer.endElement(u'token')
    finally:
        rtf = processor.popResult()
    return rtf.childNodes

def Tokenize(context, string, delimiters='\t\n\r '):
    """
    The str:tokenize function splits up a string and returns a node set of
    'token' elements, each containing one token from the string.

    The first argument is the string to be tokenized. The second argument
    is a string consisting of a number of characters. Each character in
    this string is taken as a delimiting character. The string given by the
    first argument is split at any occurrence of any of these characters.
    """
    string = Conversions.StringValue(string)
    if delimiters:
        delimiters = Conversions.StringValue(delimiters)
        tokens = re.split('[%s]' % delimiters, string)
    else:
        tokens = string

    processor = context.processor
    processor.pushResultTree(context.currentInstruction.baseUri)
    try:
        for token in tokens:
            processor.writer.startElement(u'token')
            processor.writer.text(token)
            processor.writer.endElement(u'token')
    finally:
        rtf = processor.popResult()
    return rtf.childNodes

ExtNamespaces = {
    EXSL_STRINGS_NS : 'str',
    }

ExtFunctions = {
    (EXSL_STRINGS_NS, 'align') : Align,
    (EXSL_STRINGS_NS, 'concat') : Concat,
    (EXSL_STRINGS_NS, 'decode-uri') : DecodeUri,
    (EXSL_STRINGS_NS, 'encode-uri') : EncodeUri,
    (EXSL_STRINGS_NS, 'padding') : Padding,
    (EXSL_STRINGS_NS, 'replace') : Replace,
    (EXSL_STRINGS_NS, 'split') : Split,
    (EXSL_STRINGS_NS, 'tokenize') : Tokenize,
}

ExtElements = {}

