"""
The contents of this file are subject to the Mozilla Public License  
Version 1.1 (the "License"); you may not use this file except in  
compliance with the License. 
You may obtain a copy of the License at http://www.mozilla.org/MPL/ 
Software distributed under the License is distributed on an "AS IS"  
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the  
License for the specific language governing rights and limitations under  
the License. 

The Original Code is available at 
http://downloads.xmlschemata.org/python/xvif/

The Initial Developer of the Original Code is Eric van der Vlist. Portions  
created by Eric van der Vlist are Copyright (C) 2002. All Rights Reserved. 

Contributor(s): 
"""

                                                            
def transform(self, node):
    from Ft.Xml.Xslt import Processor, StylesheetReader, DomWriter
    from Ft.Xml import InputSource
    processor = Processor.Processor()
    xreader = StylesheetReader.StylesheetReader()
    style=xreader.fromDocument(self.applyElt.dom, baseUri="dummy")
    processor.appendStylesheetInstance(style)
    factory = InputSource.DefaultFactory
    isrc=factory.fromString("dummy", "dummy")
    resWriter = DomWriter.DomWriter()
    processor.execute(node, isrc, ignorePis=1, writer=resWriter)
    dom = resWriter.getResult()
    #print dom.firstChild.nodeValue
    return dom.firstChild
        
