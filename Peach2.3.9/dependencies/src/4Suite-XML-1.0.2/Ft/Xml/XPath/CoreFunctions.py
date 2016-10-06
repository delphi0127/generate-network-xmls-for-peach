########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XPath/CoreFunctions.py,v 1.31.4.1 2006/09/18 13:49:49 uogbuji Exp $
"""
The implementation of the core functions from XPath 1.0.

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import warnings

from xml.dom import Node

from Ft import TranslateMessage as _
from Ft.Lib import number, boolean, Set
from Ft.Xml import EMPTY_NAMESPACE, XML_NAMESPACE
from Ft.Xml.XPath import NAMESPACE_NODE
from Ft.Xml.XPath import Conversions, RuntimeException
from Ft.Xml.XPath.XPathTypes import NodesetType, NumberType
from Ft.Xml.XPath.XPathTypes import StringType as XPathStringType

### Node Set Functions ###

def Last(context):
    """Function: <number> last()"""
    return float(context.size)


def Position(context):
    """Function: <number> position()"""
    return float(context.position)


def Count(context, nodeSet):
    """Function: <number> count(<node-set>)"""
    if not isinstance(nodeSet, NodesetType):
        raise RuntimeException(RuntimeException.WRONG_ARGUMENTS, 'count',
                               _("expected node-set argument"))
    return float(len(nodeSet))


def Id(context, object_):
    """Function: <node-set> id(<object>)"""
    if not isinstance(object_, NodesetType):
        st = Conversions.StringValue(object_)
        id_list = st.split()
    else:
        id_list = [ Conversions.StringValue(n) for n in object_ ]

    id_list = Set.Unique(id_list)
    doc = context.node.rootNode
    nodeset = []
    for id in id_list:
        element = doc.getElementById(id)
        if element:
            nodeset.append(element)
    return nodeset


def LocalName(context, nodeSet=None):
    """Function: <string> local-name(<node-set>?)"""
    if nodeSet is None:
        node = context.node
    elif not isinstance(nodeSet, NodesetType):
        raise RuntimeException(RuntimeException.WRONG_ARGUMENTS, 'local-name',
                               _("expected node-set"))
    elif not nodeSet:
        return u''
    else:
        nodeSet.sort()
        node = nodeSet[0]

    node_type = getattr(node, 'nodeType', None)
    if node_type in (Node.ELEMENT_NODE, Node.ATTRIBUTE_NODE):
        # localName could be null
        return node.localName or u''
    elif node_type == NAMESPACE_NODE:
        # localName could be null
        return node.localName or u''
    elif node_type == Node.PROCESSING_INSTRUCTION_NODE:
        # target cannot be null
        return node.target
    return u''


def NamespaceUri(context, nodeSet=None):
    """Function: <string> namespace-uri(<node-set>?)"""
    if nodeSet is None:
        node = context.node
    elif not isinstance(nodeSet, NodesetType):
        raise RuntimeException(RuntimeException.WRONG_ARGUMENTS,
                               'namespace-uri', _("expected node-set"))
    elif not nodeSet:
        return u''
    else:
        nodeSet.sort()
        node = nodeSet[0]

    # only elements and attributes have a namespace-uri
    node_type = getattr(node, 'nodeType', None)
    if node_type in (Node.ELEMENT_NODE, Node.ATTRIBUTE_NODE):
        return node.namespaceURI or u''
    return u''


def Name(context, nodeSet=None):
    """Function: <string> name(<node-set>?)"""
    if nodeSet is None:
        node = context.node
    elif not isinstance(nodeSet, NodesetType):
        raise RuntimeException(RuntimeException.WRONG_ARGUMENTS, 'name',
                               _("expected node-set"))
    elif not nodeSet:
        return u''
    else:
        nodeSet.sort()
        node = nodeSet[0]

    node_type = getattr(node, 'nodeType', None)
    if node_type in (Node.ELEMENT_NODE, Node.ATTRIBUTE_NODE):
        return node.nodeName
    elif node_type == NAMESPACE_NODE:
        # localName could be null
        return node.localName or u''
    elif node_type == Node.PROCESSING_INSTRUCTION_NODE:
        # target cannot be null
        return node.target
    return u''


### String Functions ###

def String(context, object_=None):
    """Function: <string> string(<object>?)"""
    if isinstance(object_, XPathStringType):
        return object_
    if object_ is None:
        object_ = context.node
    return Conversions.StringValue(object_)


def Concat(context, *args):
    """Function: <string> concat(<string>, <string>, ...)"""
    if len(args) < 1:
        raise RuntimeException(RuntimeException.WRONG_ARGUMENTS, 'concat', _("at least 2 arguments expected"))
    return reduce(lambda a, b: a + Conversions.StringValue(b), args, u'')


def StartsWith(context, outer, inner):
    """Function: <string> starts-with(<string>, <string>)"""
    if not isinstance(outer, XPathStringType):
        outer = Conversions.StringValue(outer)
    if not isinstance(inner, XPathStringType):
        inner = Conversions.StringValue(inner)
    if not inner:
        return boolean.true
    return outer[:len(inner)] == inner and boolean.true or boolean.false


def Contains(context, outer, inner):
    """Function: <string> contains(<string>, <string>)"""
    if not isinstance(outer, XPathStringType):
        outer = Conversions.StringValue(outer)
    if not isinstance(inner, XPathStringType):
        inner = Conversions.StringValue(inner)
    if not inner:
        return boolean.true
    return outer.find(inner) >= 0 and boolean.true or boolean.false


def SubstringBefore(context, outer, inner):
    """Function: <string> substring-before(<string>, <string>)"""
    if not isinstance(outer, XPathStringType):
        outer = Conversions.StringValue(outer)
    if not isinstance(inner, XPathStringType):
        inner = Conversions.StringValue(inner)
    if not inner:
        return u''
    index = outer.find(inner)
    if index == -1:
        return u''
    return outer[:index]


def SubstringAfter(context, outer, inner):
    """Function: <string> substring-after(<string>, <string>)"""
    if not isinstance(outer, XPathStringType):
        outer = Conversions.StringValue(outer)
    if not isinstance(inner, XPathStringType):
        inner = Conversions.StringValue(inner)
    if not inner:
        return u''
    index = outer.find(inner)
    if index == -1:
        return u''
    return outer[index+len(inner):]


def Substring(context, st, start, length=None):
    """Function: <string> substring(<string>, <number>, <number>?)"""
    if not isinstance(st, XPathStringType):
        st = Conversions.StringValue(st)
    if not isinstance(start, NumberType):
        start = Conversions.NumberValue(start)

    # start == NaN: spec doesn't say; assume no substring to return
    # start == +Inf or -Inf: no substring to return
    if number.isnan(start) or number.isinf(start):
        return u''

    # start is finite, safe for int() and round().
    start = int(round(start))
    # convert to 0-based index for python string slice
    if start < 1:
        startidx = 0
    else:
        startidx = start - 1

    # length undefined: return chars startidx to end
    if length is None:
        return st[startidx:]
    elif not isinstance(length, NumberType):
        length = Conversions.NumberValue(length)

    # length == NaN: spec doesn't say; assume no substring to return
    if number.isnan(length):
        return u''
    # length == +Inf: return chars startidx to end
    # length == -Inf: no substring to return
    elif number.isinf(length):
        if length > 0:
            return st[startidx:]
        else:
            return u''

    # length is finite, safe for int() and round().
    length = int(round(length))

    # return value must end before position (start+length)
    # which is (start+length-1) in 0-based index
    endidx = start + length - 1
    if endidx > startidx:
        return st[startidx:endidx]
    else:
        return u''


def StringLength(context, st=None):
    """Function: <number> string-length(<string>?)"""
    if st is None:
        st = context.node
    if not isinstance(st, XPathStringType):
        st = Conversions.StringValue(st)
    return float(len(st))


def Normalize(context, st=None):
    """Function: <string> normalize-space(<string>?)"""
    if st is None:
        st = context.node
    if not isinstance(st, XPathStringType):
        st = Conversions.StringValue(st)
    return u' '.join(st.split())


def Translate(context, source, fromChars, toChars):
    """Function: <string> translate(<string>, <string>, <string>)"""
    if not isinstance(source, XPathStringType):
        source = Conversions.StringValue(source)
    if not isinstance(fromChars, XPathStringType):
        fromChars = Conversions.StringValue(fromChars)
    if not isinstance(toChars, XPathStringType):
        toChars = Conversions.StringValue(toChars)

    # remove duplicate chars from From string
    fromChars = reduce(lambda st, c: st + c * (st.find(c) == -1), fromChars, '')
    toChars = toChars[:len(fromChars)]

    # string.maketrans/translate do not handle unicode
    translate = {}
    for from_char, to_char in map(None, fromChars, toChars):
        translate[ord(from_char)] = to_char

    result = reduce(lambda a, b, t=translate:
                    a + (t.get(ord(b), b) or ''),
                    source, '')
    return result

### Boolean Functions ###

def Boolean(context, object_):
    """Function: <boolean> boolean(<object>)"""
    return Conversions.BooleanValue(object_)


def Not(context, object_):
    """Function: <boolean> not(<boolean>)"""
    return ((not Conversions.BooleanValue(object_) and boolean.true)
            or boolean.false)


def True(context):
    """Function: <boolean> true()"""
    return boolean.true


def False(context):
    """Function: <boolean> false()"""
    return boolean.false


def Lang(context, lang):
    """Function: <boolean> lang(<string>)"""
    lang = Conversions.StringValue(lang).lower()
    node = context.node
    while node.parentNode:
        for attr in node.attributes.values():
            # Search for xml:lang attribute
            if (attr.localName == 'lang' and
                attr.namespaceURI == XML_NAMESPACE):
                value = attr.nodeValue.lower()
                # Exact match (PrimaryPart and possible SubPart)
                if value == lang:
                    return boolean.true

                # Just PrimaryPart (ignore '-' SubPart)
                index = value.find('-')
                if index != -1 and value[:index] == lang:
                    return boolean.true

                # Language doesn't match
                return boolean.false

        # Continue to next ancestor
        node = node.parentNode

    # No xml:lang declarations found
    return boolean.false

### Number Functions ###

def Number(context, object_=None):
    """Function: <number> number(<object>?)"""
    if object_ is None:
        object_ = [context.node]
    return Conversions.NumberValue(object_)


def Sum(context, nodeSet):
    """Function: <number> sum(<node-set>)"""
    if not isinstance(nodeSet, NodesetType):
        raise RuntimeException(RuntimeException.WRONG_ARGUMENTS, 'sum',
                               _("expected node-set argument"))
    nns = map(Conversions.NumberValue, nodeSet)
    return reduce(lambda x, y: x + y, nns, 0)


def Floor(context, object_):
    """Function: <number> floor(<number>)"""
    num = Conversions.NumberValue(object_)
    if number.isnan(num) or number.isinf(num):
        return num
    elif int(num) == num:
        return num
    elif num < 0:
        return float(int(num) - 1)
    else:
        return float(int(num))


def Ceiling(context, object_):
    """Function: <number> ceiling(<number>)"""
    num = Conversions.NumberValue(object_)
    if number.isnan(num) or number.isinf(num):
        return num
    elif int(num) == num:
        return num
    elif num > 0:
        return float(int(num) + 1)
    else:
        return float(int(num))


def Round(context, object_):
    """Function: <number> round(<number>)"""
    num = Conversions.NumberValue(object_)
    if number.isnan(num) or number.isinf(num):
        return num
    elif num < 0 and num % 1.0 == 0.5:
        return round(num, 0) + 1
    else:
        return round(num, 0)


### Function Mappings ###

CoreFunctions = {
    (EMPTY_NAMESPACE, 'last'): Last,
    (EMPTY_NAMESPACE, 'position'): Position,
    (EMPTY_NAMESPACE, 'count'): Count,
    (EMPTY_NAMESPACE, 'id'): Id,
    (EMPTY_NAMESPACE, 'local-name'): LocalName,
    (EMPTY_NAMESPACE, 'namespace-uri'): NamespaceUri,
    (EMPTY_NAMESPACE, 'name'): Name,
    (EMPTY_NAMESPACE, 'string'): String,
    (EMPTY_NAMESPACE, 'concat'): Concat,
    (EMPTY_NAMESPACE, 'starts-with'): StartsWith,
    (EMPTY_NAMESPACE, 'contains'): Contains,
    (EMPTY_NAMESPACE, 'substring-before'): SubstringBefore,
    (EMPTY_NAMESPACE, 'substring-after'): SubstringAfter,
    (EMPTY_NAMESPACE, 'substring'): Substring,
    (EMPTY_NAMESPACE, 'string-length'): StringLength,
    (EMPTY_NAMESPACE, 'normalize-space'): Normalize,
    (EMPTY_NAMESPACE, 'translate'): Translate,
    (EMPTY_NAMESPACE, 'boolean'): Boolean,
    (EMPTY_NAMESPACE, 'not'): Not,
    (EMPTY_NAMESPACE, 'true'): True,
    (EMPTY_NAMESPACE, 'false'): False,
    (EMPTY_NAMESPACE, 'lang'): Lang,
    (EMPTY_NAMESPACE, 'number'): Number,
    (EMPTY_NAMESPACE, 'sum'): Sum,
    (EMPTY_NAMESPACE, 'floor'): Floor,
    (EMPTY_NAMESPACE, 'ceiling'): Ceiling,
    (EMPTY_NAMESPACE, 'round'): Round,
    }

