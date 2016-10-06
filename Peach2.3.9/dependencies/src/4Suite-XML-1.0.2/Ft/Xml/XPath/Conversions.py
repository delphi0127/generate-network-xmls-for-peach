########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XPath/Conversions.py,v 1.16 2005/08/09 15:24:01 uogbuji Exp $
"""
The implementation of the XPath object type conversions.

Copyright 2000-2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import types
from xml.dom import Node

from Ft.Lib import number, boolean

StringValue = lambda obj: _strConversions.get(type(obj), _strUnknown)(obj)

NumberValue = lambda obj: _numConversions.get(type(obj), _numUnknown)(obj)

BooleanValue = lambda obj: _boolConversions.get(type(obj), _boolUnknown)(obj)

# -- String Conversions ----------------------------------------------

def _strUnknown(obj):
    # Allow for non-instance DOM node objects
    if hasattr(obj, 'nodeType'):
        # Add this type to the mapping for next time through
        _strConversions[type(obj)] = _strInstance
        return _strInstance(obj)
    return u''

def _strInstance(obj):
    if hasattr(obj, 'stringValue'):
        return obj.stringValue
    elif hasattr(obj, 'nodeType'):
        node_type = obj.nodeType
        if node_type in [Node.ELEMENT_NODE, Node.DOCUMENT_NODE]:
            # The concatenation of all text descendants
            text_elem_children = filter(lambda x:
                                        x.nodeType in [Node.TEXT_NODE, Node.ELEMENT_NODE],
                                        obj.childNodes)
            return reduce(lambda x, y: StringValue(x) + StringValue(y),
                          text_elem_children,
                          '')
        if node_type in [Node.ATTRIBUTE_NODE, NAMESPACE_NODE]:
            return obj.value
        if node_type in [Node.PROCESSING_INSTRUCTION_NODE, Node.COMMENT_NODE, Node.TEXT_NODE]:
            return obj.data
    return u''

def _strFloat(float):
    if number.finite(float):
        if float == round(float):
            return unicode(str(long(float)))
        else:
            # 12 digits is how many Python uses for str()
            return u'%0.12g' % float
    elif number.isnan(float):
        return u'NaN'
    elif float < 0:
        return u'-Infinity'
    else:
        return u'Infinity'

_strConversions = {
    str : unicode,
    unicode : unicode,
    int : lambda i: unicode(str(i)),
    long : lambda l: unicode(str(l)),
    float : _strFloat,
    boolean.BooleanType : lambda b: unicode(str(b)),
    types.InstanceType : _strInstance,
    list : lambda x: x and _strConversions.get(type(x[0]), _strUnknown)(x[0]) or u'',
}

# -- Number Conversions ----------------------------------------------

def _numString(string):
    try:
        # From XPath 1.0, sect 4.4 - number():
        #  Any string that does not match "S? '-'? Number" is converted to NaN
        #   S ::= [\x20\x09\x0A\x0D]*
        #   Digits ::= [0-9]+
        #   Number ::= Digits ('.' Digits?)? | '.' Digits
        return float(string)
    except:
        # Many platforms seem to have a problem with strtod('nan'),
        # reported on Windows and FreeBSD
        return number.nan

_numUnknown = lambda obj: _numString(StringValue(obj))

_numConversions = {
    int : float,
    long : float,
    float : float,
    boolean.BooleanType : float,
    str : _numString,
    unicode : _numString,
}

# -- Boolean Conversions ---------------------------------------------

_boolConversions = {
    boolean.BooleanType : boolean.bool,
    int : boolean.bool,
    long : boolean.bool,
    float : boolean.bool,
    str : boolean.bool,
    unicode : boolean.bool,
    list : boolean.bool,
    }

_boolUnknown = lambda obj: boolean.bool(StringValue(obj))

try:
    # Use C optimized functions, if available
    from _conversions import *
except:
    from Ft.Xml.XPath import NAMESPACE_NODE

