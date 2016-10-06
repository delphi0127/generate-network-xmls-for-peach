# $Header: /var/local/cvsroot/4Suite/Ft/Xml/ThirdParty/Xvif/FragmentFilter.py,v 1.3 2004/10/12 22:59:14 uogbuji Exp $

from xml.dom import XMLNS_NAMESPACE
from xml.sax import ContentHandler
from string import *
import re
import copy
from xml.sax.saxutils import XMLFilterBase
from xml.sax.xmlreader import AttributesNSImpl

"""
The contents of this file are subject to the Mozilla Public License  Version 1.1 (the "License"); you may not use this file except in  compliance with the License. 
You may obtain a copy of the License at http://www.mozilla.org/MPL/ 
Software distributed under the License is distributed on an "AS IS"  basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the  License for the specific language governing rights and limitations under  the License. 

The Original Code is available at http://downloads.xmlschemata.org/python/xvif/

The Initial Developer of the Original Code is Eric van der Vlist. Portions  created by Eric van der Vlist are Copyright (C) 2002. All Rights Reserved. 

The name, specification and XML syntax of Regular Fragmentation is from Simon St.Laurent and his original Java implementation available at http://simonstl.com/projects/fragment/original .

Contributor(s): 
"""


InvalidRuleException = "InvalidRulesException"
InvalidFragmentException = "InvalidFragmentException"

class _Callback:

    def __init__(self):
        self.children=[]
        self.parent = None
    
    def append(self, child):
        self.children.append(child)
    
    def startElementNS(self, rulesLoader, name, qname, attrs):
        self.parent = rulesLoader.appendMe()

    def endElementNS(self, rulesLoader, name, qname):
        return

    def characters(self, content):
        return

class PseudoMatch:

    def __init__(self, values):
        self.values = values
        self.lastindex = len(values)
    
    def group(self, id):
        return self.values[id-1]


class FragmentRules(_Callback):

    """
    <!ELEMENT fragmentRules (fragmentRule+)>
    <!ATTLIST fragmentRules
    xmlns   CDATA  "http://simonstl.com/ns/fragments/">
    """

    def __init__(self):
        _Callback.__init__(self)

    def match(self, uri, name, ruleClass):
        for rule in self.children:
            if rule.match(uri, name, ruleClass):
                return rule
        return None
    
class FragmentRule(_Callback):

    """
    <!ELEMENT fragmentRule (applyTo, produce)>
    <!ATTLIST fragmentRule
  	  pattern CDATA #REQUIRED
    	repeat (true | false) "false"
        skipFirst (true | false) "true" ???
        break (true | false) "true" ???
  	  split (true | false) "false">
    """

    def __init__(self):
        _Callback.__init__(self)
        self.applyTo = None
        self.produce = None
        self.re = None
        self.repeat =0
        self.skipFirst = 0
        self.split = 0
        self.brk = 0

    def set_pattern(self, rules, value):
        self.pattern = value
    
    def set_repeat(self, rules, value):
        self.repeat = value == "true"

    def set_break(self, rules, value):
        self.brk = value == "true"

    def set_skipFirst(self, rules, value):
        self.skipFirst = value == "true"

    def set_split(self, rules, value):
        self.split = value == "true"

    def append(self, child):
        if child.__class__ == ApplyTo:
            self.applyTo = child
        elif child.__class__ == Produce:
            self.produce = child
        else:
            raise InvalidFragmentException, "%s not expected in %s" % (child.__class__.__name__, self.__class__.__name__)
    
    def match(self, uri, name, ruleClass):
        if self.applyTo.match(uri, name, ruleClass):
            return self
        else:
            return None
    
    def getMatch(self, content):
        if self.re == None:
            self.re = re.compile(self.pattern)
        if self.split:
            return PseudoMatch(self.re.split(content))
        else:
            match = self.re.match(content)
            if match == None:
                return PseudoMatch([])
            else:
                return match

    def fragment(self, filter, match):
        self.produce.fragment(filter, match, self.skipFirst, self.repeat, self.brk)
    
    def getFragmentedAttributes(self, filter, match, attrs):
        return self.produce.getFragmentedAttributes(filter, match, attrs, self.skipFirst, self.repeat, self.brk)
    
class ApplyTo(_Callback):

    """
    <!ELEMENT applyTo (element | attribute +)>
    """

    def __init__(self):
        _Callback.__init__(self)
        self.elements = {}
        self.attributes = {}
    
    def endElementNS(self, rules, (uri, name), qname):
        for child in self.children:
            if child.__class__ == Element:
                self.elements[(child.nsURI, child.localName)] = child
            elif child.__class__ == Attribute:
                self.attributes[(child.nsURI, child.localName)] = child
            else: 
                raise InvalidFragmentException, "%s not expected in %s" % (child.__class__.__name__, self.__class__.__name__)

    def match(self, uri, name, ruleClass):
        return (ruleClass == Element and self.elements.has_key((uri, name))) or \
             (ruleClass == Attribute and self.attributes.has_key((uri, name))) 

class Element(_Callback):

    """
    <!ELEMENT element (attribute*)>
    <!ATTLIST element
  	  nsURI  CDATA ""
    	localName CDATA #REQUIRED
 	   prefix CDATA #IMPLIED
  	  before CDATA #IMPLIED
    	after CDATA #IMPLIED
 	   beforeInside CDATA #IMPLIED
  	  afterInside CDATA #IMPLIED
    >
    """

    def __init__(self):
        _Callback.__init__(self)
        self.localName = None
        self.nsURI = None
        self.prefix = None
    
    def set_localName(self, rules, value):
        self.localName = value

    def set_nsURI(self, rules, value):
        if value != "":
            self.nsURI = value

    def set_prefix(self, rules, value):
        if value != "":
            self.prefix = value
    
    def endElementNS(self, rules, (nsURI, localName), qName):
        if self.prefix == None:
            self.qName = self.localName
        else:
            self.qName = "%s:%s" % (self.prefix, self.localName)

    def produce(self, filter, content, brk):
        filter.pushContext()
        if brk:
            ch = filter.getContentHandler()
        else:
            ch = filter
        existingPrefix = filter.prefixes.has_key(self.prefix)
        differentPrefix = 1
        if existingPrefix:
            previousUri = filter.prefixes[self.prefix]
            differentPrefix = previousUri != self.nsURI
        if differentPrefix:
        #	if existingPrefix:
        #		ch.endPrefixMapping(self.prefix)
            ch.startPrefixMapping(self.prefix, self.nsURI)
        ch.startElementNS((self.nsURI, self.localName), self.qName, AttributesNSImpl({}, []))
        ch.characters(content)
        ch.endElementNS((self.nsURI, self.localName), self.qName)
        if differentPrefix:
            ch.endPrefixMapping(self.prefix)
        #	if existingPrefix:
        #		ch.startPrefixMapping(self.prefix, previousUri)
        filter.popContext()

    def getProduceAttribute(self, filter, content, attrs, brk):
        return attrs
        
class Attribute(_Callback):

    """
    <!ELEMENT attribute EMPTY>
    <!ATTLIST attribute
  	  nsURI  CDATA ""
    	localName CDATA #REQUIRED
    	prefix CDATA #IMPLIED
    	content CDATA #IMPLIED
    >
    """
    
    def __init__(self):
        _Callback.__init__(self)
        self.localName = None
        self.nsURI = None
        self.prefix = None
    
    def set_localName(self, rules, value):
        if value != "":
            self.localName = value

    def set_nsURI(self, rules, value):
        if value != "":
            self.nsURI = value

    def set_prefix(self, rules, value):
        if value != "":
            self.prefix = value

    def endElementNS(self, rules, (nsURI, localName), qName):
        if (self.prefix == None and self.nsURI != None) or \
            (self.nsURI ==None and self.prefix != None):
            raise InvalidRuleException, "Attribute prefixes and namespace URI must both null or non null"

    def produce(self, filter, content, brk):
        return

    def getProduceAttribute(self, filter, content, attrs, brk):
        return filter.startAttribute(self.nsURI, self.localName, self.prefix, content, attrs, brk)

class Produce(_Callback):

    """
    <!ELEMENT produce (element | attribute | skip | chars)+>
    """
    
    def __init__(self):
        _Callback.__init__(self)
    
    def fragment(self, filter, match, skipFirst, repeat, brk):
        if skipFirst:
            i=2
        else:
            i=1
        first = 1
        while repeat or first:
            first = 0
            for child in self.children:
                if i > match.lastindex:
                    return
                child.produce(filter, match.group(i), brk)
                i += 1

    def getFragmentedAttributes(self, filter, match, attrs, skipFirst, repeat, brk):
        if skipFirst:
            i=2
        else:
            i=1
        first = 1
        while repeat or first:
            first = 0
            for child in self.children:
                if i > match.lastindex:
                    return attrs
                attrs = child.getProduceAttribute(filter, match.group(i), attrs, brk)
                i += 1
        return attrs

class Skip(_Callback):

    """
    <!ELEMENT skip EMPTY>
    <!ATTLIST skip
  	  before CDATA #IMPLIED
    	after CDATA #IMPLIED
    >
    """

    def __init__(self):
        _Callback.__init__(self)

    def produce(self, filter, content, brk):
        return

    def getProduceAttribute(self, filter, content, attrs, brk):
        return attrs
        
class Chars(_Callback):

    """
    <!ELEMENT chars EMPTY>
    <!ATTLIST chars
  	  before CDATA #IMPLIED
    	after CDATA #IMPLIED
    >
    """

    def __init__(self):
        _Callback.__init__(self)
        self.before=""
        self.after=""
    
    def set_before(self, rules, value):
        self.before = value

    def set_after(self, rules, value):
        self.after = value

    def produce(self, filter, content, brk):
        filter.pushContext()
        filter.characters(self.before+content+self.after)
        filter.popContext()

    def getProduceAttribute(self, filter, content, attrs, brk):
        return attrs
        

class FilterContext:

    def __init__(self):
        self.rule = None 
        self.content =""
        self.attrs = None
        self.match = None
        self.temporaryPrefixes = []
    
    def appendContent(self, content):
        self.content += content
    
    def setRule(self, rule):
        self.rule = rule
    
    def setMatch(self):
        self.match = self.rule.getMatch(self.content)
    
    def setAttrs(self, attrs):
        self.attrs = attrs
    
    def appendTemporaryPrefix(self, prefix):
        self.temporaryPrefixes.append(prefix)

class FragmentFilter(XMLFilterBase):

    def __init__(self, rules):
        XMLFilterBase.__init__(self)
        self.rules = rules
        self.prefixes = {None:None}
        self.prefixesStack = {}
        self.contexts = [FilterContext()]

    def context(self):
        return self.contexts[len(self.contexts) -1]
    
    def pushContext(self, ctx = None):
        if ctx == None:
            ctx = FilterContext()
        self.contexts.append(ctx)
    
    def popContext(self):
        del(self.contexts[len(self.contexts) -1])
    
    def findPrefix(self, uri):
        for prefix in self.prefixes.keys():
            if self.prefixes[prefix] == uri:
                return prefix
        return None

    def startAttribute(self, uri, name, prefix, content, attrs, brk=0):
        self.pushContext()
        if not brk:
            rule = self.rules.match(uri, name, Attribute)
            if rule != None:
                self.context().setRule(rule)
                self.context().appendContent(content)
                self.context().setMatch()
                return self.context().rule.getFragmentedAttributes(self, self.context().match, attrs)
        p = prefix
        if prefix != None:
            if not self.prefixes.has_key(prefix):
                self.startPrefixMapping(prefix, uri)
                self.context().appendTemporaryPrefix(prefix)
            if self.prefixes[prefix] != uri:
                p = self.findPrefix(uri)
                if p == None:
                    i = 1
                    p = "%s%d" % (prefix, i)
                    while self.prefixes.has_key(p):
                        i+=1
                        p= "%s%d" % (prefix, i)
                    self.startPrefixMapping(p, uri)
                    self.context().appendTemporaryPrefix(p)
        att = attrs._attrs
        if att.has_key((uri, name)):
            raise InvalidFragmentException, "Duplicate attribute {%s}%s" % (uri, name)
        att[(uri, name)] = content
        qnames = attrs._qnames
        if p == None:
            qname = name
        else:
            qname = p+":"+name
        qnames[(uri, name)] = qname
        newattrs = AttributesNSImpl(att, qnames)
        return newattrs
        
    
    def endAttribute(self):
        if self.context().rule != None:
            self.context().rule.fragment(self, self.context().match)
        for prefix in self.context().temporaryPrefixes:
            self.endPrefixMapping(prefix)
        self.popContext()
    

    def startElementNS(self, (uri, name), qname, attrs):
        if self.context().rule!=None:
            raise InvalidFragmentException, "Element {%s}%s found while fragmenting." % (uri, name)
        else:
            self.context().rule = self.rules.match(uri, name, Element)
            ictx = len(self.contexts)
            if self.context().rule!=None:
                self.context().setAttrs(attrs)
            else:
                newattrs = AttributesNSImpl({}, {})
                for ((auri,aname), avalue) in attrs.items():
                    if attrs._qnames.has_key((auri,aname)):
                        prefix = attrs.getQNameByName((auri,aname)).split(":")[0]
                    else:
                        prefix = None
                    newattrs = self.startAttribute(auri, aname, prefix, avalue, newattrs)
                XMLFilterBase.startElementNS(self, (uri, name), qname, newattrs)
                while len(self.contexts) > ictx:
                    self.endAttribute()

    def characters(self, content):
        if self.context().rule==None:
            XMLFilterBase.characters(self, content)
        else:
            self.context().content += content
        
    def endElementNS(self, (uri, name), qname):
        if self.context().rule==None:
            XMLFilterBase.endElementNS(self, (uri, name), qname)
        else:
            ictx = len(self.contexts)
            self.context().setMatch()
            attrs = self.context().rule.getFragmentedAttributes(self, self.context().match, self.context().attrs)
            XMLFilterBase.startElementNS(self, (uri, name), qname, attrs)
            while len(self.contexts) > ictx:
                self.endAttribute()
            self.context().rule.fragment(self, self.context().match)
            XMLFilterBase.endElementNS(self, (uri, name), qname)
            for prefix in self.context().temporaryPrefixes:
                self.endPrefixMapping(prefix)
            self.context().__init__()
    
    def startPrefixMapping(self, prefix, uri):
        if self.prefixes.has_key(prefix):
            if self.prefixesStack.has_key(prefix):
                self.prefixesStack[prefix].append(self.prefixes[prefix])
            else:
                self.prefixesStack[prefix] = [self.prefixes[prefix]]
        self.prefixes[prefix] = uri
        XMLFilterBase.startPrefixMapping(self, prefix, uri)
    
    def endPrefixMapping(self, prefix):
        if self.prefixesStack.has_key(prefix):
            self.prefixes[prefix] = self.prefixesStack[prefix][-1]
            del(self.prefixesStack[prefix][-1])
            if self.prefixesStack[prefix] == []:
                del (self.prefixesStack[prefix])
        else:
            del(self.prefixes[prefix])
        XMLFilterBase.endPrefixMapping(self, prefix)

class RulesLoader(ContentHandler, _Callback):

    callbacks= \
    { "http://simonstl.com/ns/fragments/" :
        { "fragmentRules" : FragmentRules,
            "fragmentRule"  : FragmentRule,
            "applyTo"       : ApplyTo,
            "produce"       : Produce,
            "element"       : Element,
            "attribute"     : Attribute,
            "skip"          : Skip,
            "chars"         : Chars
        }
    }

    def __init__(self, xmlReader = None):
        _Callback.__init__(self)
        ContentHandler.__init__(self)
        self.xmlReader = xmlReader
        self.stack=[self]
        self.rules = None
    
    def startElementNS(self, (uri, name), qname, attrs):
        if RulesLoader.callbacks.has_key(uri):
            nsc = RulesLoader.callbacks[uri]
            if nsc.has_key(name):
                thing = nsc[name]()
                self.stack.append(thing)
                for ((auri, aname), val) in attrs.items():
                    if auri is None:
                        methodName = u"set_"+aname
                        if methodName in dir(thing):
                            method = getattr(thing, methodName)
                            method(self, val)
                        #else:
                            #raise InvalidRuleException, "Attribute %s inexpected in %s" % (aname, name)
                    #else:
                        #raise InvalidRuleException, "Attribute %s inexpected in %s" % (aname, name)
                thing.startElementNS(self, (uri, name), qname, attrs)
            else:
                self.unKnownElement(uri, name)
        else:
            self.unKnownElement(uri, name)

    def unKnownElement(self, uri, name):
        raise InvalidRuleException, "Element {%s}%s forbidden" % (uri, name)
    
    def endElementNS(self, (uri, name), qname):
        nsc = RulesLoader.callbacks[uri]
        if nsc.has_key(name):
            thing = self.stack[len(self.stack)-1]
            thing.endElementNS(self, (uri, name), qname)
            del self.stack[len(self.stack)-1]
    
    def characters(self, content):
        self.stack[len(self.stack)-1].characters(content)
        
    def endDocument(self):
        dummy=0
    
    def previousElement(self):
        return self.stack[len(self.stack)-2]

    def appendStack(self, element):
        elt = self.previousElement()
        elt.append(element)
        return elt

    def appendMe(self):
        return self.appendStack(self.stack[len(self.stack)-1])

    def __str__(self):
        return "RulesLoader"
    
    def append(self, child):
        if child.__class__ != FragmentRules:
            raise InvalidFragmentException, "Document element should be fragmentRules, not %s" % child.__class__.__name__
        else:
            self.rules = child
    
    def match(self, uri, name, matchClass):
        return self.rules.match(uri, name, matchClass)

