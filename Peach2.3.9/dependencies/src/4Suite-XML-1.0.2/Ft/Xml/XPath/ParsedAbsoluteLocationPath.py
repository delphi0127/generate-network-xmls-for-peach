########################################################################
#
# File Name:   ParsedAbsoluteLocationPath.py
#
# Docs:        http://docs.4suite.org/XPATH/ParsedAbsoluteLocationPath.py.html
#
"""
A Parsed Token that represents a absolute location path in the parsed tree.
WWW: http://4suite.org/XPATH        e-mail: support@4suite.org

Copyright (c) 2000-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

class ParsedAbsoluteLocationPath:
    def __init__(self, child):
        self._child = child

    def evaluate(self, context):
        root = context.node.rootNode

        if self._child is None:
            return [root]

        state = context.copy()

        context.node, context.position, context.size = root, 1, 1
        nodeset = self._child.select(context)

        context.set(state)
        return nodeset
    select = evaluate
    
    def pprint(self, indent=''):
        print indent + str(self)
        self._child and self._child.pprint(indent + '  ')


    def __str__(self):
        return '<AbsoluteLocationPath at %x: %s>' % (
            id(self),
            repr(self),
            )

    def __repr__(self):
        return '/' + (self._child and repr(self._child) or '')
