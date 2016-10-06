########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XPath/Context.py,v 1.13.4.1 2006/12/17 01:17:31 uogbuji Exp $
"""
The context of an XPath expression

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from types import ModuleType
import CoreFunctions, BuiltInExtFunctions
from Ft.Xml import XML_NAMESPACE

__all__ = ['Context']

class Context:
    functions = CoreFunctions.CoreFunctions.copy()
    functions.update(BuiltInExtFunctions.ExtFunctions)
    currentInstruction = None

    def __init__(self,
                 node,
                 position=1,
                 size=1,
                 varBindings=None,
                 processorNss=None,
                 extModuleList=None,
                 extFunctionMap=None):
        self.node = node
        self.position = position
        self.size = size
        self.varBindings = varBindings or {}
        self.processorNss = processorNss or {}
        self.processorNss.update({'xml': XML_NAMESPACE})

        # This may get mutated during processing
        functions = self.functions.copy()

        # Search the extension modules for defined functions
        if extModuleList:
            for module in extModuleList:
                if module:
                    if not isinstance(module, ModuleType):
                        module = __import__(module, {}, {}, ['ExtFunctions'])

                    if hasattr(module, 'ExtFunctions'):
                        functions.update(module.ExtFunctions)

        # Add functions given directly
        if extFunctionMap:
            functions.update(extFunctionMap)
        self.functions = functions
        return

    def __repr__(self):
        return "<Context at 0x%x: Node=%s, Postion=%d, Size=%d>" % (
            id(self), self.node, self.position, self.size)

    def addFunction(self, expandedName, function):
        if not callable(function):
            raise TypeError("function must be a callable object")
        self.functions[expandedName] = function
        return

    def copy(self):
        return (self.node, self.position, self.size)

    def set(self, state):
        self.node, self.position, self.size = state
        return

    def clone(self):
        newobj = self.__class__(self, self.node, self.position, self.size)
        newobj.varBindings = self.varBindings.copy()
        newobj.processorNss = self.processorNss.copy()
        newobj.functions = self.functions
        return newobj

