import xml.dom
import rng

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
        if node.nodeType == xml.dom.Node.TEXT_NODE:
            library, type = self.apply.split("#")
            rng._Callback.set_datatypeLibrary(self, None, library)
            module = __import__(rng.RngParser.typeLibraries[self.library])
            cl = module.__dict__[ type + "Type" ]
            try:
                value = cl(node.nodeValue);
            except ValueError:
                return None
            return node.ownerDocument.createTextNode(value.__str__())
        else:
            return None
                
def validate(self, node):
    res = self.transform(node)
    if res == None:
        return None
    else:
        return node
