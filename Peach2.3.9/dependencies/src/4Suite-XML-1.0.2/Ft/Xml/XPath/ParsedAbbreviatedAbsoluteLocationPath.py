########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XPath/ParsedAbbreviatedAbsoluteLocationPath.py,v 1.7 2005/03/07 02:25:58 mbrown Exp $
"""
A parsed token that represents an abbreviated absolute location path.

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from xml.dom import Node
from Ft.Lib.Set import Unique

class ParsedAbbreviatedAbsoluteLocationPath:
    def __init__(self, rel):
        self._rel = rel
        return

    def _descendants(self, context, nodeset):
        for child in context.node.childNodes:
            context.node = child
            results = self._rel.select(context)
            # Ensure no duplicates
            if results:
                nodeset.extend(results)
                nodeset = Unique(nodeset)
            if child.nodeType == Node.ELEMENT_NODE:
                nodeset = self._descendants(context, nodeset)
        return nodeset

    def evaluate(self, context):
        state = context.copy()

        # Start at the document node
        context.node = context.node.rootNode

        nodeset = self._descendants(context, self._rel.select(context))

        context.set(state)
        return nodeset
    select = evaluate

    def pprint(self, indent=''):
        print indent + str(self)
        self._rel.pprint(indent + '  ')

    def __str__(self):
        return '<AbbreviatedAbsoluteLocationPath at %x: %s>' % (
            id(self),
            repr(self)
            )

    def __repr__(self):
        return '//%r' % self._rel

