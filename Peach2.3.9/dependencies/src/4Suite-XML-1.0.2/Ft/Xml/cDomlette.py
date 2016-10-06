########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/cDomlette.py,v 1.48.4.2 2006/08/27 17:55:13 jkloth Exp $
"""
cDomlette implementation: a very fast DOM-like library tailored for use in XPath/XSLT

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""
import re

from Ft.Xml import XML_NAMESPACE, XMLNS_NAMESPACE

# DOM stuff
from cDomlettec import implementation, \
     DOMImplementation, DocumentFragment, Document, Node, CharacterData, \
     Attr, Element, Text, Comment, ProcessingInstruction, XPathNamespace

from cDomlettec import NonvalParse, ValParse, Parse, ParseFragment

# cDomlette optimized NS functions
from cDomlettec import GetAllNs, SeekNss

# Functions used for testing
from cDomlettec import TestTree


# -- XInclude support --------------------------------------------------

from cDomlettec import XPTR_ELEMENT_ID as ELEMENT_ID
from cDomlettec import XPTR_ELEMENT_COUNT as ELEMENT_COUNT
from cDomlettec import XPTR_ELEMENT_MATCH as ELEMENT_MATCH
from cDomlettec import XPTR_ATTRIBUTE_MATCH as ATTRIBUTE_MATCH


__all__ = ['implementation',
           'DOMImplementation', 'DocumentFragment', 'Document', 'Node',
           'CharacterData', 'Attr', 'Element', 'Text', 'Comment',
           'ProcessingInstruction', 'XPathNamespace',
           'NonvalParse', 'Parse',
           'GetAllNs', 'SeekNss',
           'ValParse']


def ProcessFragment(frag):
    """
    Take an XPointer fragment and return a structure suitable for the
    cDomlette parser to update state tables
    Xptr e.g. xmlns(x=http://uche.ogbuji.net/eg) xpointer(/x:spam/x:eggs)
    """
    from Ft.Xml.XPointer import Compile, XPtrException
    from Ft.Xml.XPointer.XPointer import \
         Shorthand, SchemeBased, ElementScheme, XmlnsScheme, XPointerScheme
    from Ft.Xml.XPath.ParsedAbsoluteLocationPath import \
         ParsedAbsoluteLocationPath

    # Parse the XPointer expression
    xptr = Compile(frag)

    # Process XPointer Framework
    if isinstance(xptr, Shorthand):
        return [[(ELEMENT_ID, xptr.identifier)]]

    # Process Scheme-based Pointer
    assert isinstance(xptr, SchemeBased)
    namespaces = {u'xml': XML_NAMESPACE}
    for part in xptr.parts:
        if isinstance(part, XmlnsScheme):
            # Process xmlns() scheme
            if part.prefix != u'xml' and part.uri not in (XML_NAMESPACE,
                                                          XMLNS_NAMESPACE):
                namespaces[part.prefix] = part.uri
        elif isinstance(part, XPointerScheme):
            # Process xpointer() scheme
            expr = part.expr

            # The context is guaranteed to start at the root, so use the
            # RelativeLocationPath directly.
            if isinstance(expr, ParsedAbsoluteLocationPath):
                expr = expr._child
                # If there is no RelativeLocationPath, it is just '/', which
                # is the same as if there wasn't an XPointer at all.
                if expr is None:
                    return None
            return HandleStep(expr, [], namespaces)
        elif isinstance(part, ElementScheme):
            states = []
            if part.identifier:
                states.append([(ELEMENT_ID, part.identifier)])
            for index in part.sequence:
                states.append([(ELEMENT_MATCH, None, None),
                               (ELEMENT_COUNT, index)])
            return states
        else:
            # Unsupport scheme, ignore and continue processing
            pass

    raise XPtrException(XPtrExpression.SUB_RESOURCE_ERROR)


def HandleStep(expr, states, nss):
    from Ft.Xml.XPath.ParsedRelativeLocationPath import \
         ParsedRelativeLocationPath
    from Ft.Xml.XPath.ParsedStep import ParsedStep
    from Ft.Xml.XPath.ParsedAxisSpecifier import \
         ParsedChildAxisSpecifier, ParsedAttributeAxisSpecifier
    from Ft.Xml.XPath.ParsedNodeTest import \
         LocalNameTest, QualifiedNameTest, NamespaceTest, PrincipalTypeTest
    from Ft.Xml.XPath.ParsedExpr import ParsedNLiteralExpr, ParsedEqualityExpr

    if isinstance(expr, ParsedRelativeLocationPath):
        HandleStep(expr._left, states, nss)
        curr_step = expr._right
    elif isinstance(expr, ParsedStep):
        curr_step = expr
    else:
        raise NotImplementedError(expr)

    # Guarantee that only the child axis is used
    if not isinstance(curr_step._axis, ParsedChildAxisSpecifier):
        raise NotImplementedError(curr_step._axis)

    # Set criteria by expanded name
    node_test = curr_step._nodeTest
    if isinstance(node_test, LocalNameTest):
        namespace = None
        local = node_test._name
    elif isinstance(node_test, (QualifiedNameTest, NamespaceTest)):
        try:
            namespace = nss[node_test._prefix]
        except KeyError:
            from Ft.Xml.XPath import RuntimeException
            from Ft.Xml.XPointer import XPtrException
            error = RuntimeException(RuntimeException.UNDEFINED_PREFIX,
                                     node_test._prefix)
            raise XPtrException(XPtrException.SYNTAX_ERROR, error.message)
        local = getattr(node_test, '_localName', None)
    elif isinstance(node_test, PrincipalTypeTest):
        namespace = None
        local = None
    else:
        raise NotImplementedError(node_test)
    criteria = [(ELEMENT_MATCH, namespace, local)]

    # Set criteria from predicates
    if curr_step._predicates:
        pred = curr_step._predicates._predicates[0]
        if isinstance(pred, ParsedNLiteralExpr):
            #The third item is a counter used to count elements during the parsing
            criteria.extend([(ELEMENT_COUNT, int(pred._literal))])
        elif isinstance(pred, ParsedEqualityExpr) and pred._op == u'=':
            if isinstance(pred._left, ParsedStep) and \
                   isinstance(pred._left._axis, ParsedAttributeAxisSpecifier):
                # criteria code
                criterion = [ATTRIBUTE_MATCH]

                # Add the expanded name
                if hasattr(pred._left._nodeTest, '_localName'):
                    criterion.append(nss[pred._left._nodeTest._prefix])
                    criterion.append(pred._left._nodeTest._localName)
                else:
                    criterion.append(None)
                    criterion.append(pred._left._nodeTest._name)

                # Add the expected value
                criterion.append(pred._right._literal)

                # Add this information to the criteria
                criteria.append(tuple(criterion))

    # Add state transitions for the current step
    states.append(criteria)
    return states
