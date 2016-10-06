########################################################################
#
# File Name:   TemplateElement.py
#
# Docs:        http://docs.4suite.org/4XSLT/TemplateElement.py.html
#
"""
Implementation of the XSLT Spec template stylesheet element.
WWW: http://4suite.org/4XSLT        e-mail: support@4suite.org

Copyright (c) 1999-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from xml.dom import Node
from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.Xslt import XsltElement, XsltException, Error, XSL_NAMESPACE
from Ft.Xml.Xslt import CategoryTypes, ContentInfo, AttributeInfo

class TemplateElement(XsltElement):
    category = CategoryTypes.TOP_LEVEL_ELEMENT
    content = ContentInfo.Seq(
        ContentInfo.Rep(ContentInfo.QName(XSL_NAMESPACE, 'xsl:param')),
        ContentInfo.Template)
    legalAttrs = {
        'match' : AttributeInfo.Pattern(),
        'name' : AttributeInfo.QName(),
        'priority' : AttributeInfo.Number(),
        'mode' : AttributeInfo.QName(),
        }

    def getTemplateInfo(self, position):
        infos = []
        if self._match:
            # A 'match shortcut' is is tuple of tuples in the form:
            #  ((pattern, axis_type), (node_type, expanded_name))
            shortcuts = self._match.getShortcuts(self.namespaces)
            for ((pattern, axis_type), quick_key) in shortcuts:
                if self._priority is None:
                    priority = pattern.priority
                else:
                    priority = self._priority
                pattern_info = (pattern, axis_type, self)
                shortcut = (
                    (self.importIndex, priority, position), # sort key
                    (self._mode, pattern_info, quick_key))  # template info
                infos.append(shortcut)
        return (infos, self._name)

    def _printTemplateInfo(self):
        info, tname = self.getTemplateInfo()
        if tname:
            print "Template named %r:" % tname
        else:
            print "Template matching pattern %r :" % self._match
        print "  location: line %d, col %d of %s" % \
                (self.lineNumber, self.columnNumber, self.baseUri)
        for shortcut in info:
            print "  shortcut:"
            importidx, priority, tmode, patterninfo, quickkey = shortcut
            print "    ...import index:", importidx
            print "    .......priority:", priority
            print "    ...........mode:", tmode
            if not tname:
                print "    ......quick key: node type %s, expanded-name %r" % quickkey
                print "    ........pattern: %r  for axis type %s" % patterninfo[0:2]
        return

    def instantiate(self, context, processor, params=None):
        params = params or {}

        while 1:
            context.recursiveParams = None

            for child in self.children:
                if child.expandedName == (XSL_NAMESPACE, 'param'):
                    value = params.get(child._name)
                    if value is not None:
                        context.varBindings[child._name] = value
                    else:
                        child.instantiate(context, processor)
                else:
                    child.instantiate(context, processor)

            if context.recursiveParams is not None:
                # Update the params from the values given in recursiveParams.
                params.update(context.recursiveParams)
            else:
                break
        return
