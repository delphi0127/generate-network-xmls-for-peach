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

def validate(self, node):
    #print "validate(%s, %s)" % (self, node.nodeType)
    if node == None:
        return node
    if isinstance(node, list):
        res = self.applyElt
        for token in node:
            res = res.deriv(token)
            if res == rng.NotAllowed():
                return None
    else:
        res = self.applyElt.deriv(node)
    if res == rng.NotAllowed() or not res.nullable():
        return None
    else:
        return node
