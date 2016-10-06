"""
EXSLT 2.0 - Sets (http://www.exslt.org/set/index.html)
WWW: http://4suite.org/XSLT        e-mail: support@4suite.org

Copyright (c) 2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from Ft.Lib import boolean
from Ft.Xml.XPath import Conversions
from Ft.Xml.Xslt import XsltRuntimeException, Error

EXSL_SETS_NS = "http://exslt.org/sets"

def Difference(context, nodes1, nodes2):
    """
    The set:difference function returns the difference between two node
    sets - those nodes that are in the node set passed as the first argument
    that are not in the node set passed as the second argument.
    """
    if type(nodes1) != type([]) != type(nodes2):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    result = filter(lambda node, other=nodes2: node not in other, nodes1)
    return result
    

def Distinct(context, nodeset):
    """
    The set:distinct function returns a subset of the nodes contained in the
    node-set NS passed as the first argument. Specifically, it selects a node
    N if there is no node in NS that has the same string value as N, and that
    precedes N in document order.
    """
    if type(nodeset) != type([]):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    values = map(Conversions.StringValue, nodeset)
    found = {}
    result = []
    for node, value in map(None, nodeset, values):
        if not found.has_key(value):
            result.append(node)
            found[value] = 1
    return result


def HasSameNode(context, ns1, ns2):
    """
    The set:has-same-node function returns true if the node set passed as the
    first argument shares any nodes with the node set passed as the second
    argument. If there are no nodes that are in both node sets, then it
    returns false. 
    """
    if type(ns1) != type([]) != type(ns2):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    common = filter(lambda node, other=ns2: node in other, ns1)
    return common and boolean.true or boolean.false


def Intersection(context, ns1, ns2):
    """
    The set:intersection function returns a node set comprising the nodes that
    are within both the node sets passed as arguments to it. 
    """
    if type(ns1) != type([]) != type(ns2):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    return filter(lambda node, other=ns2: node in other, ns1)


def Leading(context, ns1, ns2):
    """
    The set:leading function returns the nodes in the node set passed as the
    first argument that precede, in document order, the first node in the node
    set passed as the second argument. If the first node in the second node
    set is not contained in the first node set, then an empty node set is
    returned. If the second node set is empty, then the first node set is
    returned.
    """
    if type(ns1) != type([]) != type(ns2):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    if not ns2:
        return ns1

    # L.index(item) raises an exception if 'item' is not in L
    if ns2[0] not in ns1:
        return []
    
    ns1.sort()
    return ns1[:ns1.index(ns2[0])]
    

def Trailing(context, ns1, ns2):
    """
    The set:trailing function returns the nodes in the node set passed as the
    first argument that follow, in document order, the first node in the node
    set passed as the second argument. If the first node in the second node
    set is not contained in the first node set, then an empty node set is
    returned. If the second node set is empty, then the first node set is
    returned. 
    """
    if type(ns1) != type([]) != type(ns2):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    if not ns2:
        return ns1

    # L.index(item) raises an exception if 'item' is not in L
    if ns2[0] not in ns1:
        return []
    
    ns1.sort()
    return ns1[ns1.index(ns2[0])+1:]


ExtNamespaces = {
    EXSL_SETS_NS : 'set',
    }

ExtFunctions = {
    (EXSL_SETS_NS, 'difference'): Difference,
    (EXSL_SETS_NS, 'distinct'): Distinct,
    (EXSL_SETS_NS, 'has-same-node'): HasSameNode,
    (EXSL_SETS_NS, 'intersection'): Intersection,
    (EXSL_SETS_NS, 'leading'): Leading,
    (EXSL_SETS_NS, 'trailing'): Trailing,
    }

ExtElements = {}
