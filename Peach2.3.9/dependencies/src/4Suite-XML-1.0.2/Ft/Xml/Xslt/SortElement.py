########################################################################  
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/SortElement.py,v 1.6 2005/02/09 11:21:20 mbrown Exp $
"""
xsl:sort implementation
    
Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Lib import number
from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.XPath import Conversions
from Ft.Xml.Xslt import XsltElement
#from Ft.Xml.Xslt import XsltException, Error
from Ft.Xml.Xslt import CategoryTypes, ContentInfo, AttributeInfo

class SortElement(XsltElement):
    category = None
    content = ContentInfo.Empty
    legalAttrs = {
        'select' : AttributeInfo.StringExpression(default='.'),
        'lang' : AttributeInfo.NMTokenAvt(),
        # We don't support any additional data-types, hence no
        # AttributeInfo.QNameButNotNCName()
        'data-type' : AttributeInfo.ChoiceAvt(['text', 'number'],
                                              default='text'),
        'order' : AttributeInfo.ChoiceAvt(['ascending', 'descending'],
                                          default='ascending'),
        'case-order' : AttributeInfo.ChoiceAvt(['upper-first', 'lower-first']),
        }

    doesSetup = 1

    def setup(self):
        # optimize for constant AVT attribute values (i.e., no {})
        if self._data_type.isConstant() and self._order.isConstant() and \
           self._case_order.isConstant():
            self._comparer = self.makeComparer(self._order.evaluate(None),
                                               self._data_type.evaluate(None),
                                               self._case_order.evaluate(None),
                                               )
        else:
            self._comparer = None
        return

    def makeComparer(self, order, data_type, case_order):
        #if order not in ['ascending', 'descending']:
        #    raise XsltException(Error.ILLEGAL_SORT_ORDER_VALUE)
        #if data_type not in ['text', 'number']:
        #    raise XsltException(Error.ILLEGAL_SORT_DATA_TYPE_VALUE)
        #if case_order and case_order not in ['upper-first', 'lower-first']:
        #    raise XsltException(Error.ILLEGAL_SORT_CASE_ORDER_VALUE)

        if data_type == 'number':
            comparer = FloatCompare
        else:
            if case_order == 'lower-first':
                comparer = LowerFirstCompare
            elif case_order == 'upper-first':
                comparer = UpperFirstCompare
            else:
                # use default for this locale
                comparer = cmp

        if order == 'descending':
            comparer = Descending(comparer)

        return comparer

    def getComparer(self, context):
        if self._comparer: return self._comparer

        data_type = self._data_type.evaluate(context)
        order = self._order.evaluate(context)
        case_order = self._case_order and self._case_order.evaluate(context)
        return self.makeComparer(order, data_type, case_order)

    def evaluate(self, context):
        return Conversions.StringValue(self._select.evaluate(context))


### Comparision Functions ###

class Descending:
    def __init__(self, comparer):
        self.comparer = comparer

    def __call__(self, a, b):
        return self.comparer(b, a)

def FloatCompare(a, b):
    a = float(a or 0)
    b = float(b or 0)
    
    # NaN seems to always equal everything else, so we'll do it ourselves
    # the IEEE definition of NaN makes it the largest possible number
    if number.isnan(a):
        if number.isnan(b):
            return 0
        else:
            return -1
    elif number.isnan(b):
        return 1

    return cmp(a, b)
        
def LowerFirstCompare(a, b):
    # case only matters if the strings are equal ignoring case
    if a.lower() == b.lower():
        for i in xrange(len(a)):
            if a[i] != b[i]:
                return a[i].islower() and -1 or 1
        # they are truly equal
        return 0
    else:
        return cmp(a, b)

def UpperFirstCompare(a, b):
    # case only matters if the strings are equal ignoring case
    if a.lower() == b.lower():
        for i in xrange(len(a)):
            if a[i] != b[i]:
                return a[i].isupper() and -1 or 1
        # they are truly equal
        return 0
    else:
        return cmp(a, b)
