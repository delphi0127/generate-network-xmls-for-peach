########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XPath/XPathTypes.py,v 1.1 2005/08/02 22:43:00 mbrown Exp $
"""
Mappings between Python types and standard XPath object types

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

__all__ = ['NodesetType', 'StringType', 'NumberType', 'BooleanType',
           'g_xpathPrimitiveTypes', 'g_xpathRecognizedNodes']

from xml.dom import Node

from Ft.Lib import boolean
from Ft.Xml.XPath import NAMESPACE_NODE

# -- canonical implementation of standard XPath object types -----------
# (compare these to an object's type; do not use as callable converters)
ObjectType = object
NodesetType = list
StringType = unicode
NumberType = float
BooleanType = boolean.BooleanType

# -- all Python types usable as standard XPath object types ------------
# (mapped to strings to help with error message generation)
g_xpathPrimitiveTypes = {
    str: 'string',
    unicode: 'string',
    int: 'number',
    long: 'number',
    float: 'number',
    list: 'node-set',
    bool: 'boolean',
    boolean.BooleanType: 'boolean',
    object: 'object',
    }

NumberTypes = {
    int: True,
    long: True,
    float: True
    }


# -- DOM node types usable as XPath node types -------------------------

g_xpathRecognizedNodes = {
    Node.ELEMENT_NODE: True,
    Node.ATTRIBUTE_NODE: True,
    Node.TEXT_NODE: True,
    Node.DOCUMENT_NODE: True,
    Node.PROCESSING_INSTRUCTION_NODE: True,
    Node.COMMENT_NODE: True,
    NAMESPACE_NODE: True,
    }
