from xml.dom import XMLNS_NAMESPACE
from xml.sax import ContentHandler
import xml.dom
from string import *
import re
import copy
import rng
from rng import *
from Ft.Xml import XPath, cDomlette
import Ft.Xml
from types import *
from sax2dom_chunker import sax2dom_chunker
from Ft.Xml import Domlette

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

methods= {
    #"http://www.w3.org/TR/1999/REC-xpath-19991116" : "iFrameXPath",
    #"http://namespaces.xmlschemata.org/xvif/regexp" : "iFrameRegExp",
    "http://relaxng.org/ns/structure/1.0" : "iFrameRNG",
    "http://www.w3.org/1999/XSL/Transform": "iFrameXSLT",
    "http://namespaces.xmlschemata.org/xvif/datatypes": "iFrameTypes",
    "http://simonstl.com/ns/fragments/": "iFrameRegFrag"
    } 

class Transform(rng._Pattern, rng._Callback):

    def __init__(self):
        rng._Pattern.__init__(self)
        self.type = ""
        self.module = None
        self.apply = ""
#		self.ret = "outer"
        self.applyElt = None

    def startElementNS(self, schema, name, qname, attrs):
        self.parent = schema.previousElement()
        self.context = copy.deepcopy(schema.context)
        rng._Callback.startElementNS(self, schema, name, qname, attrs)
        
    def append(self, child):
        if child.__class__ == Apply:
            self.applyElt = child
        else:
            raise RngSchemaInvalidException, "Unsupported iframe construct"

    def set_type(self, context, value):
        if methods.has_key(value):
            module = __import__(methods[value])
            if "transform" not in dir(module):
                raise RngSchemaInvalidException, "Unsupported transformation type: %s" % value
            else:
                self.type = value
        else:
            raise RngSchemaInvalidException, "Unsupported transformation type: %s" % value
    
#	def set_return(self, context, value):
#		if not value in ("inner", "outer"):
#			raise RngSchemaInvalidException, "Unsupported return type: %s" % value
#		else:
#			self.ret = value
    
    def set_apply(self, context, value):
        self.apply = value
                                                                
    def transform(self, node):
        module = __import__(methods[self.type])
        return module.transform(self, node)


class Apply(rng._Container, rng._Callback):

    def __init__(self):
        rng._Container.__init__(self)
        self.dom = None
        self.type=""

    def startElementNS(self, schema, name, qname, attrs):
        rng._Callback.startElementNS(self, schema, name, qname, attrs)
        self.type = schema.previousElement().type
        if self.type != "http://relaxng.org/ns/structure/1.0":
            rng._Callback.startElementNS(self, schema, name, qname, attrs)
            self.handler = sax2dom_chunker(domimpl=Domlette.implementation)
            #for prefix in schema.context.prefixes.keys():
            #    if prefix != "xml":
            #        self.handler.startPrefixMapping(prefix, schema.context.prefixes[prefix])
            schema.divertEventsTo(self.handler)
        
    def endElementNS(self, schema, name, qname):
        if self.type == "http://relaxng.org/ns/structure/1.0":
            rng._Container.endElementNS(self, schema, name, qname)
        else:
            rng._Callback.endElementNS(self, schema, name, qname)
            self.dom = self.handler.get_root_node()


class Validate(Transform):

    def set_type(self, context, value):
        if methods.has_key(value):
            module = __import__(methods[value])
            if "validate" not in dir(module):
                raise RngSchemaInvalidException, "Unsupported transformation type: %s" % value
            else:
                self.type = value
        else:
            raise RngSchemaInvalidException, "Unsupported transformation type: %s" % value
    
    def transform(self, node):
        module = __import__(methods[self.type])
        res= module.validate(self, node)
        if res==None:
            return res
        else:
            return node

class Pipe(rng._Pattern, rng._Callback):

    def __init__(self):
        rng._Pattern.__init__(self)
        self.children = []

    def startElementNS(self, schema, name, qname, attrs):
        rng._Callback.startElementNS(self, schema, name, qname, attrs)
        
    def append(self, child):
        self.children.append(child)

    def deriv(self, node):
        for t in self.children:
            node = t.transform(node)
            if node == None:
                return rng.NotAllowed()
        return rng.Empty()
    
