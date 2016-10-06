from Ft.Xml import EMPTY_NAMESPACE

class DebugWriter:
    def __init__(self):
        self.reset()

    def reset(self):
        self.calls = []

    def getMediaType(self):
        return ""

    def getResult(self):
        return ''

    def getCurrent(self):
        rt = self.calls
        self.reset()
        return rt

    def __makeCall(self,name,args):
        self.calls.append((name,args))
    def __startCall(self,name,args):
        self.calls.append(("Start: " + name,args))
    def __endCall(self,name):
        self.calls.append(("End: " + name,{}))

    def startDocument(self):
        self.__startCall("document",())
        return

    def endDocument(self):
        self.__endCall("document")
        return
    
    def text(self, text, escapeOutput=1):
        self.__makeCall("text",{'text':text})
        return
    
    def attribute(self, name, value, namespace=EMPTY_NAMESPACE):
        self.__makeCall("attribute",{'name':name,
                                      'value':value,
                                      'namespace':namespace})
        return

    def processingInstruction(self, target, data):
        self.__makeCall("processingInstruction",{'target':target,
                                                  'data':data})
        return

    def comment(self, body):
        self.__makeCall('comment',{'body':body})
        return

    def startElement(self, name, namespace=EMPTY_NAMESPACE, extraNss=None):
        self.__startCall("element",{'name':name,
                                    'namespace':namespace})
        return

    def endElement(self, name):
        self.__endCall("element")
        return
