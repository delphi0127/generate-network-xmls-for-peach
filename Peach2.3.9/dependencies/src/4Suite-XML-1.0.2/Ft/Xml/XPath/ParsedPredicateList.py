########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XPath/ParsedPredicateList.py,v 1.8 2005/08/02 22:43:00 mbrown Exp $
"""
A parsed token that represents a predicate list.

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Lib import number
from Ft.Xml.XPath import Conversions
from Ft.Xml.XPath.XPathTypes import NumberTypes, g_xpathPrimitiveTypes

__all__ = ['ParsedPredicateList']

class ParsedPredicateList:
    def __init__(self, preds):
        if isinstance(preds, tuple):
            preds = list(preds)
        elif not isinstance(preds, list):
            raise TypeError("Invalid Predicates: %s"%str(preds))

        self._predicates = preds
        self._length = len(preds)

    def append(self,pred):
        self._predicates.append(pred)
        self._length += 1

    def filter(self, nodeList, context, reverse):
        if self._length:
            state = context.copy()
            for pred in self._predicates:
                size = len(nodeList)
                ctr = 0
                current = nodeList
                nodeList = []
                for node in current:
                    position = (reverse and size - ctr) or (ctr + 1)
                    context.node, context.position, context.size = \
                                  node, position, size
                    res = pred.evaluate(context)
                    if type(res) in NumberTypes:
                        # This must be separate to prevent falling into
                        # the boolean check.
                        if not number.isnan(res) and res == position:
                            nodeList.append(node)
                    elif Conversions.BooleanValue(res):
                        nodeList.append(node)
                    ctr += 1
            context.set(state)
        return nodeList

    def __getitem__(self, index):
        return self._predicates[index]

    def __len__(self):
        return self._length

    def pprint(self, indent=''):
        print indent + str(self)
        for pred in self._predicates:
            pred.pprint(indent + '  ')

    def __str__(self):
        return '<PredicateList at %x: %s>' % (
            id(self),
            repr(self) or '(empty)',
            )

    def __repr__(self):
        return reduce(lambda result, pred:
                      result + '[%s]' % repr(pred),
                      self._predicates,
                      ''
                      )
