########################################################################
#
# File Name:   ParsedNodeTest.py
#
# Docs:        http://docs.4suite.org/XPATH/ParsedNodeTest.py.html
#
"""
A Parsed Token that represents a node test.
WWW: http://4suite.org/XPATH        e-mail: support@4suite.org

Copyright (c) 2000-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

import Ft.Xml.XPath.ParsedNodeTest

def ParsedNameTest(name):
    return Ft.Xml.XPath.ParsedNodeTest.ParsedNameTest(name)

def ParsedNodeTest(test, literal=None):
    node_test = g_classMap.get(test)
    if node_test:
        return node_test()
    return Ft.Xml.XPath.ParsedNodeTest.ParsedNodeTest(test, literal)

class PointNodeTest(Ft.Xml.XPath.ParsedNodeTest.NodeTestBase):
    def match(self, context, node, principalType):
        return 0

class RangeNodeTest(Ft.Xml.XPath.ParsedNodeTest.NodeTestBase):
    def match(self, context, node, principalType):
        return 0

g_classMap = {
    'point' : PointNodeTest,
    'range' : RangeNodeTest,
    }
