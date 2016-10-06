from Ft.Xml.XPath import Context
import XPtrFunctions

class XPtrContext(Context.Context):

    def __init__(self,
                 node,
                 position,
                 size,
                 originalContext,
                 processorNss=None,
                 extModuleList = None,
                 extFunctionMap = None):
        #Add the XPointer extensions
        extFunctionMap = extFunctionMap or {}
        extFunctionMap.update(XPtrFunctions.CoreFunctions)

        Context.Context.__init__(self,
                                 node,
                                 position,
                                 size,
                                 {},
                                 processorNss,
                                 extModuleList = extModuleList,
                                 extFunctionMap = extFunctionMap)
        self.originalContext = originalContext

    def __repr__(self):
        return '<XPtrContext at %x: Node=%s, Pos="%d", Size="%d", Origin=%s>' % (
            id(self),
            repr(self.node),
            self.position,
            self.size,
            repr(self.originalContext),
            )
