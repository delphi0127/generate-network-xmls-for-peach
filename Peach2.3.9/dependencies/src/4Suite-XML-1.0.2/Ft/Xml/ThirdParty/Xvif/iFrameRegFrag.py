from xml.dom import XMLNS_NAMESPACE
from Ft.Xml.Domlette import implementation

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
    import FragmentFilter
    from Ft.Xml.Sax import CreateParser, DomBuilder
    rules = FragmentFilter.RulesLoader()
    parser = CreateParser()
    parser.setContentHandler(rules)
    parser.setFeature(xml.sax.handler.property_dom_node, self.applyElt.dom)
    parser.parse(None)
    fragFilter = FragmentFilter.FragmentFilter(rules)
    parser.setContentHandler(fragFilter)
    parser.setFeature(xml.sax.handler.property_dom_node, node)

    parser.setContentHandler(fragFilter)
    builder = DomBuilder()
    fragFilter.setContentHandler(builder)
    try:
        parser.parse(None)
    except:
        return None
    #print "reg frag result: %s" % domg.getRootNode().childNodes[1]
    return builder.getDocument().documentElement
