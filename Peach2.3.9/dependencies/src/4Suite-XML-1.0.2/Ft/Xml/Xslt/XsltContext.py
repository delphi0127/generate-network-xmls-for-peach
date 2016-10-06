########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/XsltContext.py,v 1.14.4.1 2006/12/17 01:17:34 uogbuji Exp $
"""
Context and state information for XSLT processing

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import Exslt, BuiltInExtFunctions
from Ft.Lib.Uri import UriDict
from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.XPath import Context, Util, RuntimeException
from Ft.Xml.Xslt import XsltFunctions


#NOTE: Some of the state information maintained here would probably be better
#managed by the processor, but until Python pre-GC support is phased out,
#the current arrangement will have to do

class XsltContext(Context.Context):

    functions = Context.Context.functions.copy()
    functions.update(XsltFunctions.CoreFunctions)
    functions.update(Exslt.ExtFunctions)
    functions.update(BuiltInExtFunctions.ExtFunctions)

    def __init__(self,
                 node,
                 position=1,
                 size=1,
                 currentNode=None,
                 varBindings=None,
                 processorNss=None,
                 stylesheet=None,
                 processor=None,
                 mode=None,
                 extModuleList = None,
                 extFunctionMap = None,
                 ):


        Context.Context.__init__(self,
                                 node,
                                 position,
                                 size,
                                 varBindings,
                                 processorNss,
                                 extModuleList,
                                 extFunctionMap
                                 )
        self.currentNode = currentNode
        self.stylesheet = stylesheet
        self.mode = mode
        self.processor = processor
        self.documents = UriDict()
        self.rtfs = []
        self.currentInstruction = None
        self.recursiveParams = None
        return

    def addDocument(self, document, documentUri=None):
        # RTF documents do not have a documentUri
        if documentUri:
            self.documents[documentUri] = document
        return

    def splitQName(self, qname):
        if not qname: return None
        index = qname.find(':')
        if index != -1:
            split = (qname[:index], qname[index+1:])
        else:
            split = (None, qname)
        return split

    def expandQName(self, qname):
        if not qname: return None
        prefix, local = self.splitQName(qname)
        if prefix:
            try:
                expanded = (self.processorNss[prefix], local)
            except KeyError:
                raise RuntimeException(RuntimeException.UNDEFINED_PREFIX, prefix)
        else:
            expanded = (EMPTY_NAMESPACE, local)
        return expanded

    def setProcessState(self, execNode):
        self.processorNss = execNode.namespaces
        self.currentInstruction = execNode
        return

    def clone(self):
        ctx = XsltContext(self.node, self.position, self.size,
                           self.currentNode, self.varBindings.copy(),
                           self.processorNss, self.stylesheet,
                           self.processor, self.mode)
        ctx.functions = self.functions
        return ctx

    def __repr__(self):
        return '<XsltContext at %x: node %s, position %d, size %d, mode %r>' % (
            id(self),
            repr(self.node),
            self.position,
            self.size,
            self.mode
            )

