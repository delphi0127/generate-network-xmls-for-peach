########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XPath/ParsedNodeTest.py,v 1.11 2005/08/02 22:43:00 mbrown Exp $
"""
A parsed token that represents a node test.

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from xml.dom import Node

from Ft.Xml.XPath import RuntimeException
from Ft.Xml.XPath.XPathTypes import g_xpathRecognizedNodes


def ParsedNameTest(name):
    if name == '*':
        return PrincipalTypeTest()
    index = name.find(':')
    if index == -1:
        return LocalNameTest(name)
    elif name[index:] == ':*':
        return NamespaceTest(name[:index])
    return QualifiedNameTest(name[:index], name[index+1:])


def ParsedNodeTest(test, literal=None):
    if literal:
        if test != 'processing-instruction':
            raise SyntaxError('Literal only allowed in processing-instruction')
        return ProcessingInstructionNodeTest(literal)
    return g_classMap[test]()


class NodeTestBase:

    priority = -0.5
    nodeType = None

    def getQuickKey(self, namespaces):
        """
        Returns a tuple that indicates the expected node type and, if
        applicable, the expected name.
        """
        return (self.nodeType, None)

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        """
        The principalType is discussed in section [2.3 Node Tests]
        of the XPath 1.0 spec.  Only attribute and namespace axes
        differ from the default of elements.
        """
        return node.nodeType == self.nodeType

    def pprint(self, indent):
        print indent + str(self)

    def __str__(self):
        return '<%s at %x: %s>' % (
            self.__class__.__name__,
            id(self),
            repr(self),
            )


class NodeTest(NodeTestBase):

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        return node.nodeType in g_xpathRecognizedNodes

    def __repr__(self):
        return 'node()'


class CommentNodeTest(NodeTestBase):

    nodeType = Node.COMMENT_NODE

    def __repr__(self):
        return 'comment()'


class TextNodeTest(NodeTestBase):

    nodeType = Node.TEXT_NODE

    def __repr__(self):
        return 'text()'


class ProcessingInstructionNodeTest(NodeTestBase):

    nodeType = Node.PROCESSING_INSTRUCTION_NODE

    def __init__(self, target=None):
        if target:
            self.priority = 0
            if target[0] not in ['"', "'"]:
                raise SyntaxError("Invalid literal: %s" % target)
            self.target = target[1:-1]
        else:
            self.priority = -0.5
            self.target = ''

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        if node.nodeType != self.nodeType:
            return 0
        if self.target:
            return node.target == self.target
        return 1

    def __repr__(self):
        if self.target:
            target = repr(self.target)
        else:
            target = ''
        return 'processing-instruction(%s)' % target

# Name tests

class PrincipalTypeTest(NodeTestBase):

    nodeType = Node.ELEMENT_NODE

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        return node.nodeType == principalType

    def __repr__(self):
        return '*'

class LocalNameTest(NodeTestBase):

    nodeType = Node.ELEMENT_NODE

    def __init__(self, name):
        self.priority = 0
        self._name = name

    def getQuickKey(self, namespaces):
        return (self.nodeType, (None, self._name))

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        # NameTests do not use the default namespace, just as attributes
        if node.nodeType == principalType and not node.namespaceURI:
            return node.localName == self._name
        return 0

    def __repr__(self):
        return self._name

class NamespaceTest(NodeTestBase):

    nodeType = Node.ELEMENT_NODE

    def __init__(self, prefix):
        self.priority = -0.25
        self._prefix = prefix

    def getQuickKey(self, namespaces):
        # By specifing a name of None, this test will fall into the 'general'
        # category for the principal type
        return (self.nodeType, None)

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        if node.nodeType != principalType:
            return 0
        try:
            return node.namespaceURI == context.processorNss[self._prefix]
        except KeyError:
            raise RuntimeException(RuntimeException.UNDEFINED_PREFIX,
                                   self._prefix)

    def __repr__(self):
        return self._prefix + ':*'


class QualifiedNameTest(NodeTestBase):

    nodeType = Node.ELEMENT_NODE

    def __init__(self, prefix, localName):
        self.priority = 0
        self._prefix = prefix
        self._localName = localName

    def getQuickKey(self, namespaces):
        try:
            namespace = namespaces[self._prefix]
        except KeyError:
            raise RuntimeException(RuntimeException.UNDEFINED_PREFIX,
                                   self._prefix)
        return (self.nodeType, (namespace, self._localName))

    def match(self, context, node, principalType=Node.ELEMENT_NODE):
        if node.nodeType == principalType:
            if node.localName == self._localName:
                try:
                    return node.namespaceURI == context.processorNss[self._prefix]
                except KeyError:
                    raise RuntimeException(RuntimeException.UNDEFINED_PREFIX,
                                           self._prefix)
        return 0

    def __repr__(self):
        return self._prefix + ':' + self._localName

g_classMap = {
    'node' : NodeTest,
    'comment' : CommentNodeTest,
    'text' : TextNodeTest,
    'processing-instruction' : ProcessingInstructionNodeTest,
    }

