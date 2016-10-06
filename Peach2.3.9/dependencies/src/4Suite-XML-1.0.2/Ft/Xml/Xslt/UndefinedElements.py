########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/UndefinedElements.py,v 1.3 2005/04/06 23:05:47 jkloth Exp $
"""
Node classes for the stylesheet tree

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""
from Ft.Xml.Xslt import XSL_NAMESPACE, XsltElement
from Ft.Xml.Xslt import XsltRuntimeException, Error
from Ft.Xml.Xslt import CategoryTypes, ContentInfo

class _UndefinedElement(XsltElement):

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self

        fallback = False
        for child in self.children:
            if child.expandedName == (XSL_NAMESPACE, 'fallback'):
                fallback = True
                for fallback_child in child.children:
                    fallback_child.instantiate(context, processor)

        if not fallback:
            raise self._getError()

        return

    def _getError(self):
        raise NotImplemented

class UndefinedXsltElement(_UndefinedElement):

    legalAttrs = {}

    def _getError(self):
        return XsltRuntimeException(Error.FWD_COMPAT_WITHOUT_FALLBACK, self,
                                    self.expandedName[1])

class UndefinedExtensionElement(_UndefinedElement):

    legalAttrs = None

    def _getError(self):
        return XsltRuntimeException(Error.UNKNOWN_EXTENSION_ELEMENT, self,
                                    *self.expandedName)

    
