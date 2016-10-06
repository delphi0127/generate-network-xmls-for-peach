########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XPath/ParsedAxisSpecifier.py,v 1.15 2005/02/09 11:10:54 mbrown Exp $
"""
A parsed token that represents an axis specifier.

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from xml.dom import Node

from Ft.Xml.XPath import NAMESPACE_NODE

def ParsedAxisSpecifier(axis):
    try:
        return g_classMap[axis](axis)
    except KeyError:
        raise SyntaxError("Invalid axis: %s" % axis)


class AxisSpecifier:

    principalType = Node.ELEMENT_NODE

    def __init__(self, axis):
        self._axis = axis

    def select(self, context, nodeTest):
        """
        Always returns a node-set and 0 if forward, 1 if reverse.
        """
        return ([], 0)

    def descendants(self, context, nodeTest, node, nodeSet):
        """Select all of the descendants from the context node"""
        if context.node.nodeType != Node.ATTRIBUTE_NODE:
            for child in node.childNodes:
                if nodeTest(context, child, self.principalType):
                    nodeSet.append(child)
                if child.childNodes:
                    self.descendants(context, nodeTest, child, nodeSet)
        return (nodeSet, 0)

    def pprint(self, indent=''):
        print indent + str(self)

    def __str__(self):
        return '<AxisSpecifier at %x: %s>' % (id(self), repr(self))

    def __repr__(self):
        """Always displays verbose expression"""
        return self._axis


class ParsedAncestorAxisSpecifier(AxisSpecifier):
    def select(self, context, nodeTest):
        """Select all of the ancestors including the root"""
        nodeSet = []
        parent = ((context.node.nodeType == Node.ATTRIBUTE_NODE) and
                context.node.ownerElement or context.node.parentNode)
        while parent:
            if nodeTest(context, parent, self.principalType):
                nodeSet.append(parent)
            parent = parent.parentNode
        nodeSet.reverse()
        return (nodeSet, 1)


class ParsedAncestorOrSelfAxisSpecifier(AxisSpecifier):
    def select(self, context, nodeTest):
        """Select all of the ancestors including ourselves through the root"""
        node = context.node
        if nodeTest(context, node, self.principalType):
            nodeSet = [node]
        else:
            nodeSet = []
        parent = ((node.nodeType == Node.ATTRIBUTE_NODE) and
                node.ownerElement or node.parentNode)
        while parent:
            if nodeTest(context, parent, self.principalType):
                nodeSet.append(parent)
            parent = parent.parentNode
        nodeSet.reverse()
        return (nodeSet, 1)


class ParsedAttributeAxisSpecifier(AxisSpecifier):

    principalType = Node.ATTRIBUTE_NODE

    def select(self, context, nodeTest):
        """Select all of the attributes from the context node"""
        result = [ attr for attr in context.node.xpathAttributes
                   if nodeTest(context, attr, self.principalType) ]
        return (result, 0)


class ParsedChildAxisSpecifier(AxisSpecifier):
    def select(self, context, nodeTest):
        """Select all of the children of the context node"""
        result = [ node for node in context.node.childNodes
                   if nodeTest(context, node, self.principalType) ]
        return (result, 0)


class ParsedDescendantOrSelfAxisSpecifier(AxisSpecifier):
    def select(self, context, nodeTest):
        """Select the context node and all of its descendants"""
        if nodeTest(context, context.node, self.principalType):
            nodeSet = [context.node]
        else:
            nodeSet = []
        self.descendants(context, nodeTest, context.node, nodeSet)
        return (nodeSet, 0)


class ParsedDescendantAxisSpecifier(AxisSpecifier):
    def select(self, context, nodeTest):
        nodeSet = []
        self.descendants(context, nodeTest, context.node, nodeSet)
        return (nodeSet, 0)


class ParsedFollowingSiblingAxisSpecifier(AxisSpecifier):
    def select(self, context, nodeTest):
        """Select all of the siblings that follow the context node"""
        result = []
        sibling = context.node.nextSibling
        while sibling:
            if nodeTest(context, sibling, self.principalType):
                result.append(sibling)
            sibling = sibling.nextSibling
        return (result, 0)


class ParsedFollowingAxisSpecifier(AxisSpecifier):
    def select(self, context, nodeTest):
        """
        Select all of the nodes the follow the context node,
        not including descendants.
        """
        result = []
        curr = context.node
        while curr != (context.node.rootNode):
            sibling = curr.nextSibling
            while sibling:
                if nodeTest(context, sibling, self.principalType):
                    result.append(sibling)
                self.descendants(context, nodeTest, sibling, result)
                sibling = sibling.nextSibling
            curr = ((curr.nodeType == Node.ATTRIBUTE_NODE) and
                    curr.ownerElement or curr.parentNode)
        return (result, 0)



class ParsedNamespaceAxisSpecifier(AxisSpecifier):

    principalType = NAMESPACE_NODE

    def select(self, context, nodeTest):
        """Select all of the namespaces from the context node."""
        result = [ xns for xns in context.node.xpathNamespaces
                   if nodeTest(context, xns, self.principalType) ]
        return (result, 0)


class ParsedParentAxisSpecifier(AxisSpecifier):
    def select(self, context, nodeTest):
        """Select the parent of the context node"""
        parent = ((context.node.nodeType == Node.ATTRIBUTE_NODE) and
                  context.node.ownerElement or context.node.parentNode)
        if parent and nodeTest(context, parent, self.principalType):
            result = [parent]
        else:
            result = []
        return (result, 1)


class ParsedPrecedingSiblingAxisSpecifier(AxisSpecifier):
    def select(self, context, nodeTest):
        """Select all of the siblings that precede the context node"""
        result = []
        sibling = context.node.previousSibling
        while sibling:
            if nodeTest(context, sibling, self.principalType):
                result.append(sibling)
            sibling = sibling.previousSibling
        # Put the list in document order
        result.reverse()
        return (result, 1)


class ParsedPrecedingAxisSpecifier(AxisSpecifier):
    def select(self, context, nodeTest):
        """Select all of the nodes the precede the context node, not including ancestors"""
        # Create a list of lists of descendants of the nodes
        # that precede the context node. (reverse doc order)
        doc_list = []
        curr = context.node
        while curr:
            sib = curr.previousSibling
            while sib:
                result = []
                if nodeTest(context, sib, self.principalType):
                    result = [sib]
                self.descendants(context, nodeTest, sib, result)
                doc_list.append(result)
                sib = sib.previousSibling
            curr = curr.nodeType == Node.ATTRIBUTE_NODE and curr.ownerElement or curr.parentNode

        # Create a single list in document order
        result = []
        for i in xrange(1, len(doc_list)+1):
            result.extend(doc_list[-i])
        return (result, 1)


class ParsedSelfAxisSpecifier(AxisSpecifier):
    def select(self, context, nodeTest):
        """Select the context node"""
        if nodeTest(context, context.node, self.principalType):
            return ([context.node], 0)
        return ([], 0)


g_classMap = {
    'ancestor' : ParsedAncestorAxisSpecifier,
    'ancestor-or-self' : ParsedAncestorOrSelfAxisSpecifier,
    'child' : ParsedChildAxisSpecifier,
    'parent' : ParsedParentAxisSpecifier,
    'descendant' : ParsedDescendantAxisSpecifier,
    'descendant-or-self' : ParsedDescendantOrSelfAxisSpecifier,
    'attribute' : ParsedAttributeAxisSpecifier,
    'following' : ParsedFollowingAxisSpecifier,
    'following-sibling' : ParsedFollowingSiblingAxisSpecifier,
    'preceding' : ParsedPrecedingAxisSpecifier,
    'preceding-sibling' : ParsedPrecedingSiblingAxisSpecifier,
    'namespace' : ParsedNamespaceAxisSpecifier,
    'self' : ParsedSelfAxisSpecifier,
    }

