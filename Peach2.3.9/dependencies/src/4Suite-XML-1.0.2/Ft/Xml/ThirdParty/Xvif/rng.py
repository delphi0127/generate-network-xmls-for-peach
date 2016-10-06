from xml.dom import XMLNS_NAMESPACE
from xml.sax import ContentHandler
import xml.dom
from string import *
import re
import copy
from characters import re_NCName
import urlparse
#import rngCoreTypeLib

"""
The contents of this file are subject to the Mozilla Public License
Version 1.1 (the "License"); you may not use this file except in
compliance with the License.
You may obtain a copy of the License at http://www.mozilla.org/MPL/
Software distributed under the License is distributed on an "AS IS"
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
License for the specific language governing rights and limitations under
the License.

The Original Code is available at http://downloads.xmlschemata.org/python/xvif/

The Initial Developer of the Original Code is Eric van der Vlist. Portions
created by Eric van der Vlist are Copyright (C) 2002. All Rights Reserved.

Relax NG is a specification edited by the OASIS RELAX NG Technical Committee:
http://www.oasis-open.org/committees/relax-ng/

This implementation uses the implementation notes written by James Clark:
http://www.thaiopensource.com/relaxng/implement.html

Contributor(s):
"""

IMPORT_PREFIX = "Ft.Xml.ThirdParty.Xvif."

def ImportModule(modname):
    """
    Helper import funation based on example in std Python docs:
    http://docs.python.org/lib/built-in-funcs.html
    """
    modname = IMPORT_PREFIX + modname
    mod = __import__(modname)
    components = modname.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


RngAbstractException = "RngAbstractException"
RngSchemaInvalidException = "RngSchemaInvalidException"
RngSchemaInvalidRecursionException = "RngSchemaInvalidRecursionException"

undefined = "::undefined::"

#
# Simplifications:
#
# 4.1  : parsing
# 4.2  : parsing
# 4.3  : Not yet implemented
# 4.4  : Not yet implemented
# 4.5  : Not yet implemented
# 4.6  : Not yet implemented
# 4.7  : Not yet implemented
# 4.8  : parsing
# 4.9  : parsing
# 4.10 : parsing
# 4.11 : parsing
# 4.12 : parsing
# 4.13 : parsing
# 4.14 : parsing
# 4.15 : parsing
# 4.16 : Not yet implemented
# 4.17 : parsing
# 4.18 : parsing
# 4.19 : checkRecursion & expand
# 4.20 : simplify
# 4.21 : simplify
# 7.1  : selfValidate
# 7.2  : simplify ???
# 7.3  : simplify ???
# 7.4  : simplify ???



class PseudoTextNode(unicode):

    def __init__(self, value):
        self.nodeType = self.__class__
        self.nodeValue = self

PSEUDO_TEXT_NODE=PseudoTextNode

class NameClass:

    def contains(self, QName):
        raise RngAbstractException, "NameClass"

class Context:

    def __init__(self):
        self.uri = [None]
        self.prefixes = {"xml" : xml.dom.XML_NAMESPACE}

    def pushUri(self, uri):
        self.uri.append(uri)

    def popUri(self):
        uri = self.getUri()
        del self.uri[len(self.uri)-1]
        return uri

    def getUri(self):
        return self.uri[len(self.uri)-1]

    def getUriByPrefix(self, prefix):
        if self.prefixes.has_key(prefix):
            return self.prefixes[prefix]
        else:
            return None

    def removePrefix(self, prefix):
        if self.prefixes.has_key(prefix):
            del self.prefixes[prefix]

    def addPrefix(self, prefix, uri):
        self.prefixes[prefix] = uri

class QName(NameClass):

    def __init__(self, name, uri=None, context=None):
        if name != None:
            name = strip(name)
        colon = name.find(u":")
        if colon > -1:
            uri = context.getUriByPrefix(name[:colon])
            if uri==None:
                raise RngSchemaInvalidException, "Undeclared prefix %s in '%s'" % (name[:colon], name)
            name = name[colon+1:]
        if uri != None:
            uri = strip(uri)
        if uri == u"":
            self.uri=None
        else:
            self.uri=uri
        if re_NCName().match(name) == None:
            raise RngSchemaInvalidException, "Invalid NCName: %s" % name
        self.localName=name

    def __cmp__(self, other):
        if self.uri == other.uri and self.localName==other.localName:
            return 0
        else:
            return -1

    def __str__(self):
        return u"{%s}%s" % (self.uri, self.localName)

    def contains(self, qname):
        return self == qname


class _Named:

    def set_name(self, context, value, test=1):
        value = value.strip()
        if (test == 0) or (re_NCName().match(value) != None):
            self.name = value
        else:
            raise RngSchemaInvalidException, "Invalid NCName: %s" % value

    def checkName(self):
        if not "name" in dir(self) or self.name==undefined:
            raise RngSchemaInvalidException, "Unnamed %s" % self.__class__.__name__


class _Callback:
    def __init__(self):
        self.library = None

    def setGrammar(self, grammar):
        self.grammar = grammar

    def set_datatypeLibrary(self, context, library):
        library = strip(library)
        if library == "":
            self.library = library
        else:
            scheme, loc, path, query, fragment = urlparse.urlsplit(strip(library))
            # still need to escape characters to be conform to http://www.ietf.org/rfc/rfc2396.txt
            if fragment != "" or "_" in scheme or scheme=="" or loc+path=="" or library.endswith("#") :
                raise RngSchemaInvalidException, "Invalid library %s" % library
            self.library = urlparse.urlunsplit((scheme, loc, path, query, fragment))

    def startElementNS(self, schema, name, qname, attrs):
        self.parent = schema.appendMe()
        if self.library == None:
            self.library = self.parent.library
        if self.library == None:
            self.library = ""

    def endElementNS(self, schema, name, qname):
        return

    def characters(self, content):
        return

    def defaultNs(self, context):
        return context.getUri()

    def isOpen(self):
        return 1

class _Pattern:

    def __init__(self):
        self.isnullable = 0
        self.msg = u""
        self.parent = None

    def deriv(self, node):
        if (node.nodeType == xml.dom.Node.TEXT_NODE or node.nodeType == xml.dom.Node.CDATA_SECTION_NODE)\
            and not strip(node.nodeValue):
            return self
        else:
            self.msg = "_Pattern %s, no content expected, node %s" % (self.__class__.__name__, node)
            return NotAllowed(self.msg)

    def nullable(self):
        return self.isnullable

    def __str__(self):
        if self.msg:
            return u"%s '%s'" % (self.__class__.__name__, self.msg)
        else:
            return lower(self.__class__.__name__)

    def __cmp__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            return 0
        else:
            return -1

    def checkRecursion(self, depth):
        return

    def expand(self):
        return self

    def qualifyRefs(self, id, grammar):
        self.grammar = grammar
        return

    def setParent(self, parent):
        self.parent = parent

    def append(self, p):
        raise RngSchemaInvalidException, "Invalid pattern %s in %s (%s)" % (p.__class__.__name__, self.__class__.__name__, self.path())

    def set_ns(self, context, value):
        return

    def checkAttributeContent(self):
        return 1

    def selfValidate(self, prohibitions):
        newp = []
        c = self.__class__.__name__
        cl = len(c)
        for p in prohibitions:
            if p[0] == "/":
                i =1
            else:
                i = 0
                newp.append(p)
            if p[i:i+cl] == c:
                if len(p) == i + cl:
                    raise RngSchemaInvalidException, "Prohibited path %s at %s" % (self.path(), self)
                else:
                    if p[i+cl+1] =="/":
                        newp.append(p[i+cl+2:])
                    else:
                        newp.append(p[i+cl:])
        sub = self.subPatterns()
        if sub.__class__==list or sub.__class__==tuple :
            for p in (sub):
                p.selfValidate(newp)
        else:
            sub.selfValidate(newp)

    def isSimple(self):
        return 0

    def subPatterns(self):
        return ()

    def simplify(self, parent):
        return self

    def path(self):
        if self.parent == None:
            return "/"+self.__class__.__name__
        else:
         return self.parent.path()+"/"+self.__class__.__name__



class Empty(_Pattern, _Callback):

    def __init__(self):
        _Pattern.__init__(self)
        _Callback.__init__(self)
        self.isnullable = 1

class Undefined(_Pattern):

    def __init__(self):
        _Pattern.__init__(self)
        self.isnullable = 1

class NotAllowed(_Pattern, _Callback):
    def __init__(self, msg=u""):
        _Pattern.__init__(self)
        _Callback.__init__(self)
        self.msg = msg


class _Container(_Pattern):

    def __init__(self, p=Undefined()):
        _Pattern.__init__(self)
        self.p = Undefined()
        self.expanded = 0
        if p.__class__ != Undefined:
            self.append(p)
        p.setParent(self)

    def append(self, p):
        if not p.__class__ in _patterns:
            raise RngSchemaInvalidException, "%s forbidden in %s" % (p.__class__.__name__, self.__class__.__name__)
        if (self.p.__class__ == Undefined):
            self.p=p
        elif (self.p.__class__ == Group):
            self.p.append(p)
        else:
            self.p=Group(self.p, p)
        self.p.setParent(self)

    def deriv(self, node):
        return self.p.deriv(node)

    def checkRecursion(self, depth):
        self.p.checkRecursion(depth)

    def expand(self):
        if not self.expanded:
            self.expanded = 1
            self.p = self.p.expand()
        self.p.setParent(self)
        return self

    def qualifyRefs(self, id, grammar):
        self.grammar = grammar
        self.p.qualifyRefs(id, grammar)

    def nullable(self):
        return self.p.nullable()

    def endElementNS(self, schema, name, qname):
        if self.p == undef:
            raise RngSchemaInvalidException, "Empty %s" % self.__class__.__name__

    def checkAttributeContent(self):
        return self.p.checkAttributeContent()

    def subPatterns(self):
        return (self.p)

    def simplify(self, parent):
        self.p = self.p.simplify(self)
        if self.p == notAllowed:
            return self.p
        else:
            return self

class _TypedPattern(_Pattern, _Callback):

    def __init__(self):
        _Pattern.__init__(self)
        _Callback.__init__(self)
        self.type=None

    def set_type(self, context, type):
        self.type = type.strip()

    def startElementNS(self, schema, name, qname, attrs):
        _Callback.startElementNS(self, schema, name, qname, attrs)
        if self.type == None:
            self.library = ""
            self.type = "token"
        if not RngParser.typeLibraries.has_key(self.library):
            raise RngSchemaInvalidException, "Invalid library %s" % self.library
        module = ImportModule(RngParser.typeLibraries[self.library])
        className = self.type + "Type"
        if className not in dir(module):
            raise RngSchemaInvalidException, "Invalid type %s for library %s" % (self.type, self.library)


import iframe

class _Compositor(_Pattern):

    def __init__(self, p1=Undefined(), p2=Empty()):
        _Pattern.__init__(self)
        self.p1 = Undefined()
        self.p2 = Empty()
        if p1.__class__ != Undefined:
            self.append(p1)
        if p2.__class__ != Empty:
            self.append(p2)

    def append(self, p, cl=None):
        if cl == None:
            cl = self.__class__
        if not p.__class__ in _patterns:
            raise RngSchemaInvalidException, "%s forbidden in %s" % (p.__class__.__name__, self.__class__.__name__)
        if self.p1.__class__ in (Empty, Undefined):
            self.p1=p
        elif self.p2.__class__ in (Empty, Undefined):
            self.p2=p
        else:
            self.p1 = cl(self.p1, self.p2)
            self.p2 = p
        self.p1.setParent(self)
        self.p2.setParent(self)

    def _OrderedDeriv(self, node):
        p1d = self.p1.deriv(node)
        if p1d == notAllowed:
            if self.p1.nullable():
                return self.p2.deriv(node)
            else:
                return p1d
        else:
            if p1d == empty:
                return self.p2
            else:
                return self.__class__(p1d, self.p2)

    def _UnorderedDeriv(self, node):
        p1d = self.p1.deriv(node)
        if p1d == notAllowed:
            p2d = self.p2.deriv(node)
            if p2d == notAllowed:
                return p2d
            elif p2d == empty:
                return self.p1
            else:
                return self.__class__(self.p1, p2d)
        elif p1d == empty:
            return self.p2
        else:
            return self.__class__(p1d, self.p2)

    def checkRecursion(self, depth):
        self.p1.checkRecursion(depth)
        self.p2.checkRecursion(depth)

    def expand(self):
        self.p1 = self.p1.expand()
        self.p2 = self.p2.expand()
        if self.p2.__class__ == Empty or self.p2.__class__ == Undefined:
            return self.p1
        if self.p1.__class__ == Empty or self.p1.__class__ == Undefined:
            return self.p2
        else:
            return self

    def qualifyRefs(self, id, grammar):
        self.grammar = grammar
        self.p2.qualifyRefs(id, grammar)
        self.p1.qualifyRefs(id, grammar)

    def endElementNS(self, schema, name, qname):
        if self.p1 == undef:
            raise RngSchemaInvalidException, "Empty %s" % self.__class__.__name__


    def checkAttributeContent(self):
        return self.p1.checkAttributeContent() and self.p2.checkAttributeContent()

    def subPatterns(self):
        return (self.p1, self.p2)

    def simplify(self, parent):
        self.p1 = self.p1.simplify(self)
        self.p2 = self.p2.simplify(self)
        if self.p1 == notAllowed or self.p2 == notAllowed:
            return notAllowed
        elif self.p1 == empty:
            return self.p2
        elif self.p2 == empty:
            return self.p1
        else:
            return self


class Text(Empty, _Callback):
    def __init__(self):
        Empty.__init__(self)
        _Callback.__init__(self)

    def deriv(self, node):
        if node.nodeType in (xml.dom.Node.TEXT_NODE or node.nodeType, xml.dom.Node.CDATA_SECTION_NODE, PSEUDO_TEXT_NODE):
            return self
        else:
            #return NotAllowed(u"Expected a text node instead of %s" % node.nodeName)
            return NotAllowed(u"Expected a text node instead of '%s'" % node.nodeName)


class Data (_Container, _TypedPattern):

    def __init__(self, p=Undefined()):
        _Container.__init__(self, p)
        _TypedPattern.__init__(self)
        self.type=""
        self.params = []

    def deriv(self, node):
        if node.nodeType in (xml.dom.Node.TEXT_NODE or node.nodeType, xml.dom.Node.CDATA_SECTION_NODE, PSEUDO_TEXT_NODE):
            try:
                module = ImportModule(RngParser.typeLibraries[self.library])
                cl = module.__dict__[ self.type + "Type" ]
                if hasattr(cl, 'stateful'):
                    self.value = cl(node.nodeValue, self.grammar.state)
                else:
                    self.value = cl(node.nodeValue)
                # good, the value is valid...
                for p in self.params:
                    d = p.deriv(node)
                    if d == notAllowed:
                        return d
                if self.p == undef:
                    return empty
                else:
                    return self.p.deriv(node)
            except ValueError:
                return NotAllowed(u"Unexpected value %s for type %s#%s" % (node.nodeValue, self.library, self.type))
        else:
            return NotAllowed(u"Expected a text node instead of %s" % node)

    def nullable(self):
        if self.p == undef:
            return 0
        else:
            return self.p.nullable()

    def endElementNS(self, schema, name, qname):
        """ Data can be empty """

    def append(self, p):
        if p.__class__ == Except:
            if self.p != undef:
                raise RngSchemaInvalidException, "At most one except element."
            self.p = p
        elif p.__class__ == Param:
            self.params.append(p)
        else:
            raise RngSchemaInvalidException, "%s forbidden in %s" % (p.__class__.__name__, self.__class__.__name__)


class Except(_Container, _Callback):
    def __init__(self, p=Undefined()):
        _Container.__init__(self, p)
        _Callback.__init__(self)

    def append(self, p):
        if not p.__class__ in _patterns:
            raise RngSchemaInvalidException, "%s forbidden in %s" % (p.__class__.__name__, self.__class__.__name__)
        if (self.p.__class__ == Undefined):
            self.p=p
        elif (self.p.__class__ == Choice):
            self.p.append(p)
        else:
            self.p=Choice(self.p, p)

    def deriv(self, node):
        res = self.p.deriv(node)
        if res==notAllowed:
            return empty
        else:
            return NotAllowed("Value matches an except pattern (%s)" % node)

    def nullable(self):
        return not self.p.nullable()

    def simplify(self, parent):
        self.p = self.p.simplify(self)
        if self.p == notAllowed:
            return empty
        else:
            return self


class Param(_Pattern, _Callback):
    def __init__(self):
        _Pattern.__init__(self)
        _Callback.__init__(self)
        self.tmpValue = ""
        self.value = None
        self.name = None

    def characters(self, content):
        self.tmpValue += content

    def endElementNS(self, schema, name, qname):
        self.value = self.tmpValue

    def set_name(self, context, name):
        self.name = name.strip()

    def startElementNS(self, schema, name, qname, attrs):
        _Callback.startElementNS(self, schema, name, qname, attrs)
        if self.name == None:
            raise RngSchemaInvalidException, "param elements must have a name"
        module = ImportModule(RngParser.typeLibraries[self.parent.library])
        cl = module.__dict__[ self.parent.type + "Type" ]
        methodName = self.name + "Facet"
        if methodName not in dir(cl):
            raise RngSchemaInvalidException, "Invalid param '%s' for type '%s#%s'" % (self.name, self.parent.type, self.parent.library)

    def deriv(self, node):
        cl = self.parent.value.__class__
        # method = self.parent.value.__dict__[self.name + "Facet"]
        # for whatever reason, __dict__ doesn't take base classes :-(
        #print "self.parent.value.%sFacet(u'%s')" % (self.name, self.value)
        #FIXME: This eval is a security hole: possible "Python injection" attack
        res = eval ("self.parent.value.%sFacet(u'%s')" % (self.name, self.value))
        if res:
            return empty
        else:
            return NotAllowed(u"Value %s not valid per facet %s='%'" % (self.parent.value, self.name, self.value))


import iframe

class Value(_TypedPattern):

    def __init__(self):
        _TypedPattern.__init__(self)
        self.tmpValue = ""
        self.value = None

    def isOpen(self):
        return 0

    def setValue(self, value):
        module = ImportModule(RngParser.typeLibraries[self.library])
        cl = module.__dict__[ self.type + "Type" ]
        try:
            if hasattr(cl, 'stateful'):
                self.value = cl(value, self.grammar.state)
            else:
                self.value = cl(value)
        except ValueError:
            raise RngSchemaInvalidException, "Value not allowed % for type %s#%s" % (value, self.typeLibrary, self.type)
        try:
            self.isnullable = (self.value == cl(""))
        except ValueError:
            self.isnullable = 0


    def characters(self, content):
        self.tmpValue += content

    def endElementNS(self, schema, name, qname):
        self.setValue(self.tmpValue)

    def deriv(self, node):
        if node.nodeType in (xml.dom.Node.TEXT_NODE or node.nodeType, xml.dom.Node.CDATA_SECTION_NODE, PSEUDO_TEXT_NODE):
            if self.value == self.value.__class__(node.nodeValue):
                return empty
            else:
                return NotAllowed(u"Actual value '%s' doesn't match expected value '%s' as %s#%s" % (node.nodeValue, self.value, self.library, self.type))
        else:
            return NotAllowed(u"Expected a text node instead of %s" % node)


class OneOrMore(_Container, _Callback):

    def __init__(self, p=Undefined()):
        _Container.__init__(self, p)
        _Callback.__init__(self)
        self.savp = p

    def append(self, p):
        _Container.append(self, p)
        self.savp = self.p

    def deriv(self, node):
        pderiv = self.p.deriv(node)
        if pderiv == notAllowed:
            if self.p.nullable():
                pderiv = self.savp.deriv(node)
                if pderiv == notAllowed:
                    return pderiv
                else:
                    self.p = pderiv
                    return self
            else:
                return pderiv
        else:
            self.p = pderiv
            return self

    def checkRecursion(self, depth):
        self.savp.checkRecursion(depth)

    def __str__(self):
        return u"(%s)+" % (self.p)

    def nullable(self):
        return self.p.nullable()

    def qualifyRefs(self, id, grammar):
        self.grammar = grammar
        self.p.qualifyRefs(id, grammar)


    def endElementNS(self, schema, name, qname):
        if self.p == undef:
            raise RngSchemaInvalidException, "Empty oneOrMore"


    def checkAttributeContent(self):
        return self.p.checkAttributeContent()

    def subPatterns(self):
        return (self.savp)

    def expand(self):
        self.savp = self.savp.expand()
        self.p = self.savp
        return self


class Group(_Compositor, _Callback):

    def __init__(self, p1=Undefined(), p2=Empty()):
        _Compositor.__init__(self, p1, p2)
        _Callback.__init__(self)

    def deriv(self, node):
        if node.nodeType == xml.dom.Node.ATTRIBUTE_NODE:
         return _Compositor._UnorderedDeriv(self, node)
        else:
         return _Compositor._OrderedDeriv(self, node)

    def __str__(self):
        return u"(%s, %s)" % (self.p1, self.p2)

    def nullable(self):
        return self.p1.nullable() and self.p2.nullable()

    def checkAttributeContent(self):
        return self.p1.checkAttributeContent() and self.p2.checkAttributeContent()


class List(_Container, _Callback):

    def __init__(self, p=Undefined()):
        _Container.__init__(self, p)
        _Callback.__init__(self)

    def deriv(self, node):
        if node.nodeType in (xml.dom.Node.TEXT_NODE, xml.dom.Node.CDATA_SECTION_NODE):
            for token in node.nodeValue.split():
                self.p = self.p.deriv(PseudoTextNode(token))
                if self.p == notAllowed:
                    return self.p
            return self
        else:
            return NotAllowed("Node forbidden in a list :%s" % node)


class Choice(_Compositor, _Callback):

    def __init__(self, p1=Undefined(), p2=NotAllowed()):
        #Pattern is the grandparent (base of _Compositor)
        #The way _Compositor.__init__ is written, we don't want to
        #Call it directly
        #But this feels like a place where some class hierarchy redesign might be in order
        _Pattern.__init__(self)
        _Callback.__init__(self)
        self.p1 = Undefined()
        self.p2 = NotAllowed()
        if p1.__class__ != Undefined:
            Choice.append(self, p1)
        if p2.__class__ != NotAllowed:
            Choice.append(self, p2)

    def append(self, p):
        if not p.__class__ in _patterns:
            raise RngSchemaInvalidException, "%s forbidden in %s" % (p.__class__.__name__, self.__class__.__name__)
        if self.p1 == notAllowed or self.p1 == undef:
            self.p1=p
        elif self.p2 == notAllowed:
            self.p2=p
        else:
            self.p1 = self.__class__(self.p1, self.p2)
            self.p2 = p
        self.p1.setParent(self)
        self.p2.setParent(self)

    def deriv(self, node):
        p1d = self.p1.deriv(node)
        p2d = self.p2.deriv(node)
        if p1d==NotAllowed(u""):
            return p2d
        if p2d==NotAllowed(u""):
            return p1d
        return Choice(p1d, p2d)

    def __str__(self):
        return u"(%s|%s)" % (self.p1, self.p2)

    def nullable(self):
        return self.p1.nullable() or self.p2.nullable()

    def expand(self):
        if self.p2 == notAllowed:
            return self.p1.expand()
        elif self.p1 == notAllowed:
            return self.p2.expand()
        else:
            self.p1 = self.p1.expand()
            self.p2 = self.p2.expand()
            return self

    def endElementNS(self, schema, name, qname):
        if self.p1 == undef:
            raise RngSchemaInvalidException, "Empty choice"

    def checkAttributeContent(self):
        return self.p1.checkAttributeContent() and self.p2.checkAttributeContent()

    def simplify(self, parent):
        self.p1 = self.p1.simplify(self)
        self.p2 = self.p2.simplify(self)
        if self.p1 == notAllowed:
            return self.p2
        elif self.p2 == notAllowed:
            return self.p1
        else:
            return self


class Interleave(_Compositor, _Callback):

    def __init__(self, p1=Undefined(), p2=Empty()):
        _Compositor.__init__(self, p1, p2)
        _Callback.__init__(self)

    def deriv(self, node):
        return _Compositor._UnorderedDeriv(self, node)

    def __str__(self):
        return u"(%s&%s)" % (self.p1, self.p2)

    def nullable(self):
        return self.p1.nullable() and self.p2.nullable()


class ZeroOrMore(Choice, _Callback):

    def __init__(self, p=Undefined()):
        Choice.__init__(self, OneOrMore(p), Empty())
        _Callback.__init__(self)

    def append(self, p):
        if not p.__class__ in _patterns:
            raise RngSchemaInvalidException, "%s forbidden in %s" % (p.__class__.__name__, self.__class__.__name__)
        self.p1.append(p)

    def endElementNS(self, schema, name, qname):
        if self.p1.p == undef:
            raise RngSchemaInvalidException, "Empty zeroOrMore"


class Optional(Choice, _Callback):

    def __init__(self, p=Undefined()):
        Choice.__init__(self, Group(p), Empty())
        _Callback.__init__(self)

    def append(self, p):
        if not p.__class__ in _patterns:
            raise RngSchemaInvalidException, "%s forbidden in %s" % (p.__class__.__name__, self.__class__.__name__)
        self.p1.append(p)


    def endElementNS(self, schema, name, qname):
        if self.p1.p1 == undef:
            raise RngSchemaInvalidException, "Empty optional"


class Mixed(Interleave, _Callback):

    def __init__(self, p1=Undefined(), p2=Empty()):
        Interleave.__init__(self,  Interleave(p1, p2), Text())
        _Callback.__init__(self)

    def endElementNS(self, schema, name, qname):
        if self.p1.p1 == undef:
            raise RngSchemaInvalidException, "Empty mixed"


class Attribute(_Container, _Callback):

    def __init__(self, nc=None, p=Text()):
        _Container.__init__(self)
        _Callback.__init__(self)
        self.nc = nc
        self.p = p
        self.p.setParent(self)
        self.cnt = 0

    def append(self, p):
        if not p.__class__ in _patterns:
            raise RngSchemaInvalidException, "%s forbidden in %s" % (p.__class__.__name__, self.__class__.__name__)
        self.cnt += 1
        if self.cnt > 1:
            raise RngSchemaInvalidException, "More than 1 content in attribute %s" % self.nc
        self.p = p
        self.p.setParent(self)

    def deriv(self, node):
        if node.nodeType != xml.dom.Node.ATTRIBUTE_NODE:
            return NotAllowed (u"Attribute expected.")
        else:
            if self.nc.contains(QName(node.localName, node.namespaceURI)):
                val = node.nodeValue
                if val == "":
                    if self.p.nullable():
                        return empty
                    else:
                        return NotAllowed (u"Empty attribute forbidden.")
                else:
                    deriv = self.p.deriv(node.ownerDocument.createTextNode(val))
                    if deriv.nullable():
                        return empty
                    else:
                        return deriv
            else:
                return NotAllowed (u"Attribute name mismatch.")

    def set_name(self, context, localName):
        self.nc = QName(localName, context.getUri(), context)
        if self.nc.localName == "xmlns":
            raise RngSchemaInvalidException, "'xml' is reserved: %s" % self.nc.localName
        if self.nc.uri == "http://www.w3.org/2000/xmlns":
            raise RngSchemaInvalidException, "'the xmlns' namespace is reserved: %s" % self.nc.uri

    def defaultNs(self, context):
        return None

    def __str__(self):
        if self.nc.uri == None:
            return u"attribute %s (%s)" % (self.nc.localName, self.p)
        else:
            return u"attribute %s:%s (%s)" % (self.grammar.getPrefix(self.nc.uri), self.nc.localName, self.p)

    def qualifyRefs(self, id, grammar):
        self.grammar = grammar
        self.p.qualifyRefs(id, grammar)

    def startElementNS(self, schema, name, qname, attrs):
        if self.nc is None:
            raise RngSchemaInvalidException, "Unnamed %s" % self.__class__.__name__
        _Callback.startElementNS(self, schema, name, qname, attrs)

    #def endElementNS(self, schema, name, qname):
        #if not self.p.checkAttributeContent():
        #   raise RngSchemaInvalidException, "Illegal attribute content %s" % self

    def checkAttributeContent(self):
        return 0

    def subPatterns(self):
        return (self.p)

    def nullable(self):
        return 0


class Element(_Container, _Callback, _Named):

    def __init__(self, nc=None, p=Undefined(), g=None):
        _Container.__init__(self, p)
        _Callback.__init__(self)
        self.nc = nc
        self.expanded = 0
        self.grammar = g

    def deriv(self, node):
        if node.nodeType in (xml.dom.Node.TEXT_NODE, xml.dom.Node.CDATA_SECTION_NODE)\
            and strip(node.nodeValue) == "":
            return self
        elif node.nodeType != xml.dom.Node.ELEMENT_NODE:
            return NotAllowed(u"Expected an element")
        else:
            p1 = self.startTagOpenDeriv(QName(node.localName, node.namespaceURI))
            if p1 == notAllowed:
                return p1
            p2 = p1.attributesDeriv(node.attributes)
            if p2 == notAllowed:
                return p2
            p3 = p2.startTagCloseDeriv()
            if p3 == notAllowed:
                return p3
            p4 = p3.childrenDeriv(node.childNodes)
            if p4 == notAllowed:
                return p4
            return p4.endTagDeriv(node)

    def startTagOpenDeriv(self, qname):
        if self.nc.contains(qname):
            return self
        else:
            return NotAllowed(u"Qname %s not expected" % qname)

    def childrenDeriv(self, children):
        ptail = self.p
        accumulatedText = ""
        for node in children:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if accumulatedText != "":
                    textNode = node.ownerDocument.createTextNode(accumulatedText)
                    accumulatedText = ""
                    ptail = ptail.deriv(textNode)
                    if ptail==notAllowed:
                        break
                ptail = ptail.deriv(node)
                if ptail==notAllowed:
                    break
            elif node.nodeType == xml.dom.Node.TEXT_NODE \
                    or node.nodeType == xml.dom.Node.CDATA_SECTION_NODE:
                accumulatedText += node.nodeValue
        if ptail != notAllowed and accumulatedText != "":
            textNode = children[0].ownerDocument.createTextNode(accumulatedText)
            ptail = ptail.deriv(textNode)
        return Element(self.nc, ptail, self.grammar)

    def attributesDeriv(self, children):
        ptail = self.p
        for node in children.values():
            if node.namespaceURI != XMLNS_NAMESPACE:
                ptail = ptail.deriv(node)
                if ptail==notAllowed:
                    break
        return Element(self.nc, ptail, self.grammar)

    def startTagCloseDeriv(self):
        # jjc says we can replace the attributes by "notAllowed"
        # here, but I don't see the benefit of doing so!
        return self


    def endTagDeriv(self, node):
        if self.p.nullable():
            return Empty()
        else:
            textNode = node.ownerDocument.createTextNode("")
            self.p = self.p.deriv(textNode)
            return self.p

    def __str__(self):
        if self.nc.uri == None:
            return u"element %s (%s)" % (self.nc.localName, self.p)
        else:
            return u"element %s:%s (%s)" % (self.grammar.getPrefix(self.nc.uri), self.nc.localName, self.p)

    def set_name(self, context, localName):
        self.nc = QName(localName, context.getUri(), context)

    def startElementNS(self, schema, name, qname, attrs):
        if self.nc is None:
            raise RngSchemaInvalidException, "Unnamed %s" % self.__class__.__name__
        _Callback.startElementNS(self, schema, name, qname, attrs)

    def expand(self):
        if not self.expanded:
            if self.parent.isSimple():
                self.p = self.p.expand()
                self.expanded = 1
                return self
            else:
                i = 0
                while self.grammar.getDef(u"%d:elt" % i) != notAllowed:
                    i = i+1
                refname = u"%d:elt" % i
                self.grammar.addDef(refname, None)
                ref = Ref()
                ref.set_name(None, refname, 0)
                ref.setGrammar(self.grammar)
                define = Define()
                define.set_name(None, refname, 0)
                define.setGrammar(self.grammar)
                define.append(self)
                self.grammar.addDef(refname, define.expand())
                return ref
        else:
            return self

    def endElementNS(self, schema, name, qname):
        if self.p == undef:
            raise RngSchemaInvalidException, "Empty element"

    def checkRecursion(self, depth):
        self.p.checkRecursion(depth+1)

    def qualifyRefs(self, id, grammar):
        self.grammar= grammar
        self.p.qualifyRefs(id, grammar)

    def checkAttributeContent(self):
        return 0

    def subPatterns(self):
        return (self.p)

    def nullable(self):
        return 0


notAllowed = NotAllowed(u"")
empty = Empty()
undef = Undefined()

class Div(_Callback, _Pattern):

    def __init__(self):
        _Callback.__init__(self)
        _Pattern.__init__(self)

    def startElementNS(self, schema, name, qname, attrs):
        self.parent = schema.previousElement()
        if self.parent.__class__ == Div:
            self.parent == self.parent.parent

    def append(self, p):
        self.parent.append(p)


class Grammar(_Callback, _Pattern):

    def __init__(self, parent=None):
        _Callback.__init__(self)
        _Pattern.__init__(self)
        self.schema=None
        self.parent=parent
        self.refPatterns={":start" : NotAllowed()}
        self.stack=[]
        self.patterns = None
        self.nsUris = {"http://www.w3.org/XML/1998/namespace" : "xml"}
        self.id = -1
        self.state = {}
        #self.complete = 0

    def startElementNS(self, schema, name, qname, attrs):
        #_Callback.startElementNS(self, schema, name, qname, attrs)
        self.parent = schema.grammar
        self.nsUris = self.parent.nsUris
        schema.setGrammar(self)
        self.id = schema.elementid
        if self.library == None:
            self.library = schema.previousElement().library
        if self.library == None:
            self.library = ""

    def endElementNS(self, schema, name, qname):
        start = self.start()
        del(self.refPatterns[":start"])
        if start == notAllowed:
            raise RngSchemaInvalidException, u"Grammar found without start"
        if start.p.__class__ == Ref:
            name = start.p.name
            start = self.refPatterns[start.p.name]
            del(self.refPatterns[name])
        if start == notAllowed:
            raise RngSchemaInvalidException, u"Grammar found with notAllowed start"
        start.qualifyRefs(self.id, self.parent)
        for ref in self.refPatterns:
            if self.refPatterns[ref] == notAllowed:
                raise RngSchemaInvalidException, u"Named pattern %s undefined" % ref
            self.refPatterns[ref].qualifyRefs(self.id, self.parent)
            self.refPatterns[ref].qualifyDef(self.id)
            self.parent.refPatterns[self.refPatterns[ref].name] = self.refPatterns[ref]
        for uri in self.nsUris:
            self.parent.nsUris[uri] = self.nsUris[uri]
        schema.setGrammar(self.parent)
        schema.append(start.p)

    def start(self):
        return self.refPatterns[":start"]

    def setStart(self, p):
        self.refPatterns[":start"] = p

    def deriv(self, node):
        return self.start().deriv(node)

    def addDef(self, name, pattern=notAllowed):
        self.refPatterns[name]=pattern

    def getDef(self, name):
        if self.refPatterns.has_key(name):
            return self.refPatterns[name]
        else:
            return notAllowed

    def normalizeNsUris(self):
        i = 1
        for uri in self.nsUris:
            self.nsUris[uri] = u"ns%d" % i
            i += 1

    def getPrefix(self, uri):
        if self.nsUris.has_key(uri):
            return self.nsUris[uri]
        else:
            return u"<undefined>"

    def __str__(self):
        str  = u"grammar {\n"
        for ref in self.refPatterns:
         str += u"\n%s" % self.refPatterns[ref]
        str += u"\n}"
        return str

    def checkRecursion(self, depth):
        self.start().checkRecursion(depth)
        #for v in self.refPatterns.values():
            #if v.isSimple():
            #v.checkRecursion(depth)

    def expand(self):
        #refPatterns = {}
        #for ref in self.refPatterns.keys():
        #   if self.refPatterns[ref].isSimple() or self.refPatterns[ref].__class__ == Start:
        #       self.refPatterns[ref] = self.refPatterns[ref].expand()
        #       refPatterns[ref] = self.refPatterns[ref]
        #self.refPatterns = refPatterns
        self.start().expand()
        return self

    def simplify (self, parent):
        for ref in self.refPatterns.keys():
            self.refPatterns[ref] = self.refPatterns[ref].simplify(self)
        return self

    def subPatterns(self):
        ret = []
        for v in self.refPatterns.values():
            ret.append(v)
        return (ret)

class Define(_Container, _Callback, _Named):

    def __init__(self, p=Undefined()):
        _Container.__init__(self, p)
        _Callback.__init__(self)
        self.combine = "undefined"
        self.undefine = 1

    def set_combine(self, context, value):
        self.combine = value
        self.undefine = 0

    def startElementNS(self, schema, name, qname, attrs):
        _Named.checkName(self)
        if not schema.previousElement().__class__ in _definers:
            raise RngSchemaInvalidException, "%s forbidden in %s" % (schema.previousElement().__class__.__name__, self.__class__.__name__)
        if self.library == None:
            self.library = schema.previousElement().library
        if self.library == None:
            self.library = ""
        #   schema.grammar.addDef(self.name, self)


    def endElementNS(self, schema, name, qname):
        _Container.endElementNS(self, schema, name, qname)
        prev = schema.grammar.getDef(self.name)
        if not prev == notAllowed:
            self.undefine += prev.undefine
            if self.undefine > 1:
                raise RngSchemaInvalidException, "Illegal redefinition of %s" % self.name
            if (self.combine=="choice" and prev.combine!="interleave") \
                or (self.combine!="interleave" and prev.combine=="choice"):
                self.combine = "choice"
                self.p = Choice(self.p, prev.p)
            elif (self.combine=="interleave" and prev.combine!="choice") \
                or (self.combine!="choice" and prev.combine=="interleave"):
                self.combine = "interleave"
                self.p = Interleave(self.p, prev.p)
            else:
                raise RngSchemaInvalidException, "Redefinition of %s" % self.name
        self.p.setParent(self)
        schema.grammar.addDef(self.name, self)

    def simplify(self, parent):
        self.p = self.p.simplify(self)
        return self

    def isSimple(self):
        return self.p.__class__ in (Element, Undefined)

    def __str__(self):
        return u"%s = %s" % (self.name, self.p)

    def expandAsGroup(self):
        return self.p.expand()

    def qualifyDef(self, id):
        self.name = "%d:%s" % (id, self.name)


class Ref(_Pattern, _Callback, _Named):

    def __init__(self):
        _Pattern.__init__(self)
        _Callback.__init__(self)
        self.recursionDepth = -1
        self.name = undefined

    def startElementNS(self, schema, name, qname, attrs):
        _Named.checkName(self)
        if schema.grammar.getDef(self.name) == notAllowed:
            schema.grammar.addDef(self.name)
        self.parent = schema.appendMe()
        self.grammar = schema.grammar

    def deriv(self, node):
        return self.grammar.getDef(self.name).deriv(node)

    def nullable(self):
        #return self.grammar.getDef(self.name).nullable()
        return 0

    def __str__(self):
        return self.name

#   def checkRecursion(self, depth):
#       if self.recursionDepth == -1:
#           self.recursionDepth = depth
#           self.grammar.getDef(self.name).checkRecursion(depth)
#       elif depth == self.recursionDepth:
#           raise RngSchemaInvalidRecursionException, "Invalid recursion (%s, %s)" % (self.path(), self)

    def expand(self):
        if self.grammar.getDef(self.name) == notAllowed:
            raise RngSchemaInvalidException, u"Named pattern %s undefined" % self.name
        if self.grammar.getDef(self.name).isSimple():
            self.grammar.getDef(self.name).expand()
            return self
        else:
            return self.grammar.getDef(self.name).expandAsGroup()

    def qualifyRefs(self, id, grammar):
        self.grammar = grammar
        self.name = "%d:%s" % (id, self.name)

    def checkAttributeContent(self):
        return self.grammar.getDef(self.name).checkAttributeContent()


class PatternRef(Ref, _Callback, _Named):

    def __init__(self):
        Ref.__init__(self)
        _Callback.__init__(self)

    def checkRecursion(self, depth):
        if self.recursionDepth == -1:
            self.recursionDepth = depth
            self.grammar.getDef(self.name).checkRecursion(depth)
            self.recursionDepth = -2
        elif depth == -2:
            return
        elif depth == self.recursionDepth:
            raise RngSchemaInvalidRecursionException, "Invalid recursion (%s, %s)" % (self.path(), self)


class Start(Define):

    def __init__(self):
        Define.__init__(self)
        self.name=":start"
        self.cnt = 0

    def __str__(self):
        return u"start = %s" % self.p

    def set_name(self, context, value):
        raise RngSchemaInvalidException, "Start should not have a name"

    def append(self, p):
        Define.append(self, p)
        self.cnt +=1
        if self.cnt > 1:
            raise RngSchemaInvalidException, "More than 1 pattern in a start (%s)" % p

    def isSimple(self):
        return 0


class rngTypeLib:
    """
    Abstract class which should be derived.
    """

    def __init__(self, value):
        self.value = value

    def toString(self):
        return self.value

    def isValid(self):
        return 1

    def isEqual(self, value):
        return self.value == value


class RngParser(ContentHandler, _Callback, _Pattern):

    callbacks= \
    { "http://relaxng.org/ns/structure/1.0" :
        { "grammar"   : Grammar,
            "start"     : Start,
            "attribute" : Attribute,
            "element"   : Element,
            "zeroOrMore": ZeroOrMore,
            "choice"    : Choice,
            "interleave": Interleave,
            "mixed"     : Mixed,
            "empty"     : Empty,
            "notAllowed": NotAllowed,
            "group"     : Group,
            "optional"  : Optional,
            "text"      : Text,
            "define"    : Define,
            "ref"       : PatternRef,
            "div"       : Div,
            "value"     : Value,
            "list"      : List,
            "data"      : Data,
            "except"    : Except,
            "oneOrMore" : OneOrMore,
            "param" : Param
        },
     "http://namespaces.xmlschemata.org/xvif/iframe" :
        { "transform"   : iframe.Transform ,
          "apply"       : iframe.Apply ,
          "validate"    : iframe.Validate ,
          "pipe"        : iframe.Pipe }
    }

    typeLibraries = {
        "" : "rngCoreTypeLib",
        "http://www.w3.org/2001/XMLSchema-datatypes" : "wxsTypeLib"
    }

    def __init__(self):
        _Callback.__init__(self)
        _Pattern.__init__(self)
        self.grammar = Grammar()
        start = Start()
        self.grammar.setStart(start)
        self.stack = [self.grammar, start]
        self.ns = None
        self.context = Context()
        self.ignoreDepth = 0
        self.elementid = 0
        self.diversionDepth = 0

    def startPrefixMapping(self, prefix, uri):
        if self.diversionDepth > 0:
            self.diversionHandler.startPrefixMapping(prefix, uri)
        else:
            self.context.addPrefix(prefix, uri)
            self.grammar.nsUris[uri] = prefix

    def endPrefixMapping(self, prefix):
        if self.diversionDepth > 0:
            self.diversionHandler.endPrefixMapping(prefix)
        else:
            self.context.removePrefix(prefix)

    def startElementNS(self, (uri, name), qname, attrs):
        if self.diversionDepth > 0:
            self.diversionHandler.startElementNS((uri, name), qname, attrs)
            self.diversionDepth += 1
        else:
            if self.ignoreDepth == 0:
                if attrs.has_key(("http://namespaces.xmlschemata.org/xvif/iframe", "ignore")) \
                    and attrs[("http://namespaces.xmlschemata.org/xvif/iframe", "ignore")] != "0":
                    self.ignoreDepth += 1
                else:
                    if RngParser.callbacks.has_key(uri):
                        nsc = RngParser.callbacks[uri]
                        if nsc.has_key(name):
                            thing = nsc[name]()
                            thing.setGrammar(self.grammar)
                            self.stack.append(thing)
                            if attrs.has_key((None, 'ns')):
                                nsuri = attrs[(None, 'ns')].strip()
                                if nsuri == u"":
                                    nsuri = None
                                else:
                                    self.grammar.nsUris[nsuri] = 'ns'
                                self.context.pushUri(nsuri)
                            else:
                                self.context.pushUri(thing.defaultNs(self.context))
                            for ((auri, aname), val) in attrs.items():
                                if auri is None:
                                    methodName = u"set_"+aname
                                    if methodName in dir(thing):
                                        method = getattr(thing, methodName)
                                        method(self.context, val)
                                    else:
                                        raise RngSchemaInvalidException, "Attribute %s unexpected in %s" % (aname, name)
                                elif auri == "http://relaxng.org/ns/structure/1.0":
                                    raise RngSchemaInvalidException, "Attribute {%s}%s unexpected in %s" % (auri, aname, name)
                            thing.startElementNS(self, (uri, name), qname, attrs)
                        else:
                            self.unKnownElement(uri, name)
                    else:
                        self.unKnownElement(uri, name)
            else:
                    self.ignoreDepth += 1
            #   self.unKnownElement(uri, name)
        self.elementid +=1

    def unKnownElement(self, uri, name):
        if self.stack[len(self.stack)-1].isOpen():
            self.ignoreDepth += 1
        else:
            raise RngSchemaInvalidException, "Element {%s}%s forbidden" % (uri, name)

    def endElementNS(self, (uri, name), qname):
        if self.diversionDepth > 0:
            self.diversionDepth -= 1
            if self.diversionDepth > 0:
                self.diversionHandler.endElementNS((uri, name), qname)
                return
        if self.ignoreDepth > 0:
            self.ignoreDepth -= 1
        elif RngParser.callbacks.has_key(uri):
            nsc = RngParser.callbacks[uri]
            if nsc.has_key(name):
                thing = self.stack[len(self.stack)-1]
                thing.endElementNS(self, (uri, name), qname)
                del self.stack[len(self.stack)-1]
                self.context.popUri()

    def characters(self, content):
        if self.diversionDepth > 0:
            self.diversionHandler.characters(content)
        elif self.ignoreDepth == 0:
            self.stack[len(self.stack)-1].characters(content)

    def endDocument(self):
        self.grammar.checkRecursion(0)
        self.grammar.expand()
        self.grammar.simplify(self)
        if self.grammar.start() == empty or self.grammar.start().p == undef:
            raise RngSchemaInvalidException, "Empty start"
        self.grammar.selfValidate(_prohibitions)
        #self.grammar.complete = 1

    def previousElement(self):
        return self.stack[len(self.stack)-2]

    def append(self, element):
        elt = self.previousElement()
        elt.append(element)
        return elt

    def appendMe(self):
        return self.append(self.stack[len(self.stack)-1])

    def deriv(self, node):
        return self.grammar.deriv(node)

    def divertEventsTo(self, handler):
        self.diversionHandler=handler
        self.diversionDepth = 1

    def __str__(self):
        self.grammar.normalizeNsUris()
        str = u"-----"
        for uri in self.grammar.nsUris:
            str += u"\nnamespace %s = %s" % (self.grammar.nsUris[uri], uri)
        str += u"\n%s\n-----" %self.grammar
        return str

_patterns = (Element,
    Attribute,
    Group,
    Interleave,
    Choice,
    Optional,
    ZeroOrMore,
    OneOrMore,
    Mixed,
    Ref,
    PatternRef,
    Empty,
    Text,
    NotAllowed,
    List,
    Value,
    Data,
    iframe.Transform,
    iframe.Validate,
    iframe.Pipe,
    Grammar)

_definers = (Grammar,
    Div)

_prohibitions = ( "Attribute//Ref",
    "Attribute//Attribute",
    "OneOrMore//Group//Attribute",
    "OneOrMore//Interleave//Attribute",
    "Start//Attribute",
    "Start//Text",
    "Start//Group",
    "Start//Interleave",
    "Start//OneOrMore",
    "List//List",
    "List//Ref",
    "List//Attribute",
    "List//Text",
    "List//Interleave",
    "Data/Except//Attribute",
    "Data/Except//Ref",
    "Data/Except//Text",
    "Data/Except//List",
    "Data/Except//Group",
    "Data/Except//Interleave",
    "Data/Except//OneOrMore",
    "Data/Except//Empty",
    "Start//Data",
    "Start//Value",
    "Start//List",
    "Start//Empty")


#class RngProcessor:


