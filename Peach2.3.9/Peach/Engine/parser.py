
'''
Peach XML Parser.  Sucks in the crazy XML and returns a top level context
object that contians things like templates, namespaces, etc.

@author: Michael Eddington
@version: $Id: parser.py 2697 2012-01-31 21:55:00Z meddingt $
'''

#
# Copyright (c) Michael Eddington
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in	
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# Authors:
#   Michael Eddington (mike@phed.org)

# $Id: parser.py 2697 2012-01-31 21:55:00Z meddingt $

import sys, re, types, os, glob
import traceback
from uuid import uuid1

try:
	import Ft.Xml.Domlette
	from Ft.Xml.Catalog import GetDefaultCatalog
	from Ft.Xml.InputSource import InputSourceFactory
	from Ft.Lib.Resolvers import SchemeRegistryResolver
	from Ft.Lib import Uri
	from Ft.Xml import Parse
	from Ft.Xml.Sax import DomBuilder
	from Ft.Xml import Sax, CreateInputSource
except:
	raise PeachException("Error loading 4Suite XML library.  This library\ncan be installed from the dependencies folder or\ndownloaded from http://4suite.org/.\n\n")

from Peach.Engine.dom import *
from Peach.Engine import dom
import Peach.Engine
from Peach.Mutators import *
from Peach.Engine.common import *
from Peach.Engine.incoming import DataCracker
from Peach.mutatestrategies import *

def PeachStr(s):
	'''
	Our implementation of str() which does not
	convert None to 'None'.
	'''
	
	if s == None:
		return None
	
	return str(s)

class PeachResolver(SchemeRegistryResolver):
	def __init__(self):
		SchemeRegistryResolver.__init__(self)
	
	def resolve(self, uri, base=None):
		scheme = Uri.GetScheme(uri)
		if scheme == None:
			if base != None:
				scheme = Uri.GetScheme(base)
			if scheme == None:
				#Another option is to fall back to Base class behavior
				raise Uri.UriException(Uri.UriException.SCHEME_REQUIRED,
									   base=base, ref=uri)
		
		# Add the files path to our sys.path
		
		if scheme == 'file':
			filename = uri[5:]
			try:
				index = filename.rindex('\\')
				sys.path.append(filename[: 0 - (index+1)])
				#print "Adding [%s]" % filename[: 0 - (index+1)]
				
			except:
				try:
					index = filename.rindex('/')
					sys.path.append(filename[: 0 - (index+1)])
					#print "Adding [%s]" % filename[: 0 - (index+1)]
					
				except:
					#print "Adding [.][%s]" % uri
					sys.path.append('.')
		
		try:
			func = self.handlers.get(scheme)
			if func == None:
				func = self.handlers.get(None)
				if func == None:
					return Uri.UriResolverBase.resolve(self, uri, base)
			
			return func(uri, base)
		
		except:
			
			if scheme != 'file':
				raise PeachException("Peach was unable to locate [%s]" % uri)
			
			# Lets try looking in our sys.path
			
			paths = []
			for path in sys.path:
				paths.append(path)
				paths.append("%s/Peach/Engine" % path)
			
			for path in paths:
				newuri = uri[:5] + path + '/' + uri[5:]
				#print "Trying: [%s]" % newuri
				
				try:
					func = self.handlers.get(scheme)
					if func == None:
						func = self.handlers.get(None)
						if func == None:
							return Uri.UriResolverBase.resolve(self, newuri, base)
					
					return func(uri, base)
				except:
					pass
			
			raise PeachException("Peach was unable to locate [%s]" % uri)


class ParseTemplate:
	'''
	The Peach 2 XML -> Peach DOM parser.  Uses 4Suite XML
	library.
	'''
	
	dontCrack = False
	
	def parse(self, uri):
		'''
		Parse a Peach XML file pointed to by uri.
		'''
		
		factory = InputSourceFactory(resolver=PeachResolver(), catalog=GetDefaultCatalog())
		isrc = factory.fromUri(uri)
		doc = Ft.Xml.Domlette.NonvalidatingReader.parse(isrc)
		
		obj = self.HandleDocument(doc, uri)
		
		return obj
	
	def parseString(self, xml):
		'''
		Parse a string as Peach XML.
		'''
		
		doc = Ft.Xml.Domlette.NonvalidatingReader.parseString(xml, "http://phed.org")
		return self.HandleDocument(doc)
	
	def GetClassesInModule(self, module):
		'''
		Return array of class names in module
		'''
		
		classes = []
		for item in dir(module):
			i = getattr(module, item)
			if type(i) == types.ClassType and item[0] != '_':
				classes.append(item)
			elif type(i) == types.MethodType and item[0] != '_':
				classes.append(item)
			elif type(i) == types.FunctionType and item[0] != '_':
				classes.append(item)
			elif repr(i).startswith("<class"):
				classes.append(item)
		
		return classes
	
	def HandleDocument(self, doc, uri = ""):
		
		self.StripComments(doc)
		self.StripText(doc)
		
		ePeach = doc.firstChild
		
		peach = dom.Peach()
		peach.peachPitUri = uri
		#peach.node = doc
		self.context = peach
		peach.mutators = None
		
		#: List of nodes that need some parse love list of [xmlNode, parent]
		self.unfinishedReferences = []
		
		setattr(peach, 'templates',		ElementWithChildren())
		setattr(peach, 'data',			ElementWithChildren())
		setattr(peach, 'agents',		ElementWithChildren())
		setattr(peach, 'namespaces',	ElementWithChildren())
		setattr(peach, 'tests',			ElementWithChildren())
		setattr(peach, 'runs',			ElementWithChildren())
		
		if ePeach.nodeName != 'Peach':
			raise PeachException("First element in document must be Peach")
		
		# Peach attributes
		
		setattr(peach, 'version',		self._getAttribute(ePeach, 'version'))
		setattr(peach, 'author',		self._getAttribute(ePeach, 'author'))
		setattr(peach, 'description',	self._getAttribute(ePeach, 'description'))
		
		# The good stuff -- We are going todo multiple passes here to increase the likely hood
		# that things will turn out okay.
		
		# Pass 1 -- Include, PythonPath, Defaults
		for child in ePeach.childNodes:
			
			if child.nodeName == 'Include':
				# Include this file
				
				nsName = self._getAttribute(child, 'ns')
				nsSrc = self._getAttribute(child, 'src')
				
				parser = ParseTemplate()
				ns = parser.parse(nsSrc)
				
				ns.name = nsName + ':' + nsSrc
				ns.nsName = nsName
				ns.nsSrc = nsSrc
				ns.elementType = 'namespace'
				ns.toXml = new.instancemethod(PeachModule.Engine.dom.NamespaceToXml, ns, ns.__class__)
				
				nss = Namespace()
				nss.ns = ns
				nss.nsName = nsName
				nss.nsSrc = nsSrc
				nss.name = nsName + ":" + nsSrc
				nss.parent = peach
				ns.parent = nss
				
				peach.append(nss)
				peach.namespaces.append(ns)
				setattr(peach.namespaces, nsName, ns)
			
			elif child.nodeName == 'PythonPath':
				# Add a search path
				
				p = self.HandlePythonPath(child, peach)
				peach.append(p)
				sys.path.append(p.name)
				
			elif child.nodeName == 'Defaults':
				self.HandleDefaults(child, peach)

		# Pass 2 -- Import
		for child in ePeach.childNodes:
			
			if child.nodeName == 'Import':
				# Import module
				
				if not child.hasAttributeNS(None, 'import'):
					raise PeachException("Import element did not have import attribute!")
				
				importStr = self._getAttribute(child, 'import')
				
				if child.hasAttributeNS(None, 'from'):
					fromStr = self._getAttribute(child, 'from')
					
					if importStr == "*":
						module = __import__(PeachStr(fromStr), globals(), locals(), [ PeachStr(importStr) ], -1)
						
						try:
							# If we are a module with other modules in us then we have an __all__
							for item in module.__all__:
								globals()["PeachXml_"+item] = getattr(module, item)
							
						except:
							# Else we just have some classes in us with no __all__
							for item in self.GetClassesInModule(module):
								globals()["PeachXml_"+item] = getattr(module, item)
						
					else:
						module = __import__(PeachStr(fromStr), globals(), locals(), [ PeachStr(importStr) ], -1)
						for item in importStr.split(','):
							item = item.strip()
							globals()["PeachXml_"+item] = getattr(module, item)
				
				else:
					globals()["PeachXml_"+importStr] = __import__(PeachStr(importStr), globals(), locals(), [], -1)
					
				Holder.globals = globals()
				Holder.locals = locals()
					
				i = Element()
				i.elementType = 'import'
				i.importStr = self._getAttribute(child, 'import')
				i.fromStr = self._getAttribute(child, 'from')
				
				peach.append(i)
		
		# Pass 3 -- Template
		for child in ePeach.childNodes:
			
			if child.nodeName == "Python":
				code = self._getAttribute(child, "code")
				if code != None:
					exec(code)
					
			elif child.nodeName == 'Analyzer':
				self.HandleAnalyzerTopLevel(child, peach)
			
			elif child.nodeName == 'DataModel' or child.nodeName == 'Template':
				# do something
				template = self.HandleTemplate(child, peach)
				#template.node = child
				peach.append(template)
				peach.templates.append(template)
				setattr(peach.templates, template.name, template)
		
		# Pass 4 -- Data, Agent
		for child in ePeach.childNodes:
			
			if child.nodeName == 'Data':
				# do data
				data = self.HandleData(child, peach)
				#data.node = child
				peach.append(data)
				peach.data.append(data)
				setattr(peach.data, data.name, data)
			
			elif child.nodeName == 'Agent':
				agent = self.HandleAgent(child, None)
				#agent.node = child
				peach.append(agent)
				peach.agents.append(agent)
				setattr(peach.agents, agent.name, agent)
			
			elif child.nodeName == 'StateModel' or child.nodeName == 'StateMachine':
				stateMachine = self.HandleStateMachine(child, peach)
				#stateMachine.node = child
				peach.append(stateMachine)
			
			elif child.nodeName == 'Mutators':
				mutators = self.HandleMutators(child, peach)
				peach.mutators = mutators
		
		# Pass 5 -- Tests
		for child in ePeach.childNodes:
			
			if child.nodeName == 'Test':
				
				tests = self.HandleTest(child, None)
				#tests.node = child
				peach.append(tests)
				peach.tests.append(tests)
				setattr(peach.tests, tests.name, tests)
			
			elif child.nodeName == 'Run':
				
				run = self.HandleRun(child, None)
				#run.node = child
				peach.append(run)
				peach.runs.append(run)
				setattr(peach.runs, run.name, run)
		
		# Pass 6 -- Analyzers
		
		# Simce analyzers can modify the DOM we need to make our list
		# of objects we will look at first!
		
		objs = []
		
		for child in peach.getElementsByType(Blob):
			if child.analyzer != None and child.defaultValue != None and child not in objs:
				objs.append(child)
		for child in peach.getElementsByType(String):
			if child.analyzer != None and child.defaultValue != None and child not in objs:
				objs.append(child)
		
		for child in objs:
			try:
				analyzer = eval("%s()" % child.analyzer)
			except:
				analyzer = eval("PeachXml_"+"%s()" % child.analyzer)
			
			analyzer.asDataElement(child, {}, child.defaultValue)
		
		# We suck, so fix this up
		peach._FixParents()
		peach.verifyDomMap()
		#peach.printDomMap()
		
		return peach
	
	def StripComments(self, node):
		
		for child in node.childNodes:
			
			if child.nodeName == '#comment':
				node.removeChild(child)
			else:
				self.StripComments(child)
	
	def StripText(self, node):
		
		for child in node.childNodes:
			
			if child.nodeName == '#text':
				node.removeChild(child)
			else:
				self.StripText(child)
	
	def GetRef(self, str, parent = None, childAttr = 'templates'):
		'''
		Get the object indicated by ref.  Currently the object must have
		been defined prior to this point in the XML
		'''
		
		#print "GetRef(%s) -- Starting" % str
		
		origStr = str
		baseObj = self.context
		hasNamespace = False
		isTopName = True
		found = False
		
		# Parse out a namespace
		
		if str.find(":") > -1:
			ns, tmp = str.split(':')
			str = tmp
			
			#print "GetRef(%s): Found namepsace: %s" % (str, ns)
			
			# Check for namespace
			if hasattr(self.context.namespaces, ns):
				baseObj = getattr(self.context.namespaces, ns)
			else:
				#print self
				raise PeachException("Unable to locate namespace: " + origStr)
			
			hasNamespace = True
		
		for name in str.split('.'):
			
			#print "GetRef(%s): Looking for part %s" % (str, name)
			
			found = False
			
			if not hasNamespace and isTopName and parent != None:
				# check parent, walk up from current parent to top
				# level parent checking at each level.
				
				while parent != None and not found:
					
					#print "GetRef(%s): Parent.name: %s" % (name, parent.name)
					
					if hasattr(parent, 'name') and parent.name == name:
						baseObj = parent
						found = True
						
					elif hasattr(parent, name):
						baseObj = getattr(parent, name)
						found = True
					
					elif hasattr(parent.children, name):
						baseObj = getattr(parent.children, name)
						found = True
					
					elif hasattr(parent, childAttr) and hasattr( getattr(parent, childAttr), name):
						baseObj = getattr( getattr(parent, childAttr), name)
						found = True
						
					else:
						parent = parent.parent
			
			# check base obj
			elif hasattr(baseObj, name):
				baseObj = getattr(baseObj, name)
				found = True
				
			# check childAttr
			elif hasattr(baseObj, childAttr):
				obj = getattr(baseObj, childAttr)
				if hasattr(obj, name):
					baseObj = getattr(obj, name)
					found = True
			
			else:
				raise PeachException("Could not resolve ref %s" % origStr)
			
			# check childAttr
			if found == False and hasattr(baseObj, childAttr):
				obj = getattr(baseObj, childAttr)
				if hasattr(obj, name):
					baseObj = getattr(obj, name)
					found = True
			
			# check across namespaces if we can't find it in ours
			if isTopName and found == False:
				for child in baseObj:
					if child.elementType != 'namespace':
						continue
					
					#print "GetRef(%s): CHecking namepsace: %s" % (str, child.name)
					ret = self._SearchNamespaces(child, name, childAttr)
					if ret:
						#print "GetRef(%s) Found part %s in namespace" % (str, name)
						baseObj = ret
						found = True
			
			isTopName = False
		
		if found == False:
			raise PeachException("Unable to resolve reference: %s" % origStr)
		
		return baseObj
	
	def _SearchNamespaces(self, obj, name, attr):
		'''
		Used by GetRef to search across namespaces
		'''
		
		#print "_SearchNamespaces(%s, %s)" % (obj.name, name)
		#print "dir(obj): ", dir(obj)
		
		# Namespaces are stuffed under this variable
		# if we have it we should be it :)
		if hasattr(obj, 'ns'):
			obj = obj.ns

		if hasattr(obj, name):
			return getattr(obj, name)
		
		elif hasattr(obj, attr) and hasattr(getattr(obj, attr), name):
			return getattr(getattr(obj, attr), name)
		
		for child in obj:
			if child.elementType != 'namespace':
				continue
			
			ret = self._SearchNamespaces(child, name, attr)
			if ret != None:
				return ret
		
		return None
	
	def GetDataRef(self, str):
		'''
		Get the data object indicated by ref.  Currently the object must
		have been defined prior to this point in the XML.
		'''
		
		origStr = str
		baseObj = self.context
		
		# Parse out a namespace
		
		if str.find(":") > -1:
			ns, tmp = str.split(':')
			str = tmp
			
			#print "GetRef(): Found namepsace:",ns
			
			# Check for namespace
			if hasattr(self.context.namespaces, ns):
				baseObj = getattr(self.context.namespaces, ns)
			else:
				raise PeachException("Unable to locate namespace")
		
		for name in str.split('.'):
			
			# check base obj
			if hasattr(baseObj, name):
				baseObj = getattr(baseObj, name)
			
			# check templates
			elif hasattr(baseObj, 'data') and hasattr(baseObj.data, name):
				baseObj = getattr(baseObj.data, name)
			
			else:
				raise PeachException("Could not resolve ref '%s'" % origStr)
		
		return baseObj
	
	_regsHex = (
		re.compile(r"^([,\s]*\\x([a-zA-Z0-9]{2})[,\s]*)"),
		re.compile(r"^([,\s]*%([a-zA-Z0-9]{2})[,\s]*)"),
		re.compile(r"^([,\s]*0x([a-zA-Z0-9]{2})[,\s]*)"),
		re.compile(r"^([,\s]*x([a-zA-Z0-9]{2})[,\s]*)"),
		re.compile(r"^([,\s]*([a-zA-Z0-9]{2})[,\s]*)")
	)
	
	def GetValueFromNode(self, node):
		
		value = None
		type = 'string'
		
		if node.hasAttributeNS(None, 'valueType'):
			type = self._getAttribute(node, 'valueType')
			if not (type == 'literal' or type == 'hex'):
				type = 'string'
		
		if node.hasAttributeNS(None, 'value'):
			value = self._getAttribute(node, 'value')
			
			# Convert variouse forms of hex into a binary string
			if type == 'hex':
				
				if len(value) == 1:
					value = "0" + value

				ret = ''
				
				valueLen = len(value)+1
				while valueLen > len(value):
					valueLen = len(value)
					
					for i in range(len(self._regsHex)):
						match = self._regsHex[i].search(value)
						if match != None:
							while match != None:
								ret += chr(int(match.group(2),16))
								value = self._regsHex[i].sub('', value)
								match = self._regsHex[i].search(value)
							break
				
				return ret
			
			elif type == 'literal':
				return eval(value)
		
		if value != None and (type == 'string' or not node.hasAttributeNS(None, 'valueType')):
			value = re.sub(r"([^\\])\\n", r"\1\n", value)
			value = re.sub(r"([^\\])\\r", r"\1\r", value)
			value = re.sub(r"([^\\])\\t", r"\1\t", value)
			value = re.sub(r"([^\\])\\n", r"\1\n", value)
			value = re.sub(r"([^\\])\\r", r"\1\r", value)
			value = re.sub(r"([^\\])\\t", r"\1\t", value)
			value = re.sub(r"^\\n", r"\n", value)
			value = re.sub(r"^\\r", r"\r", value)
			value = re.sub(r"^\\t", r"\t", value)
			value = re.sub(r"\\\\", r"\\", value)

		return value
		
	def GetValueFromNodeString(self, node):
		'''
		This one is specific to <String> elements.  We
		want to preserve unicode characters.
		'''
		
		value = None
		type = 'string'
		
		if node.hasAttributeNS(None, 'valueType'):
			type = self._getAttribute(node, 'valueType')
			if not type in ['literal', 'hex', 'string']:
				raise PeachException("Error: [%s] has invalid valueType attribute." % node.getFullname())
		
		if node.hasAttributeNS(None, 'value'):
			value = node.getAttributeNS(None, 'value')
			
			# Convert variouse forms of hex into a binary string
			if type == 'hex':
				
				value = str(value)
				
				if len(value) == 1:
					value = "0" + value
				
				ret = ''
				
				valueLen = len(value)+1
				while valueLen > len(value):
					valueLen = len(value)
					
					for i in range(len(self._regsHex)):
						match = self._regsHex[i].search(value)
						if match != None:
							while match != None:
								ret += chr(int(match.group(2),16))
								value = self._regsHex[i].sub('', value)
								match = self._regsHex[i].search(value)
							break
				
				return ret
			
			elif type == 'literal':
				value = eval(value)
		
		if value != None and type == 'string':
			value = re.sub(r"([^\\])\\n", r"\1\n", value)
			value = re.sub(r"([^\\])\\r", r"\1\r", value)
			value = re.sub(r"([^\\])\\t", r"\1\t", value)
			value = re.sub(r"([^\\])\\n", r"\1\n", value)
			value = re.sub(r"([^\\])\\r", r"\1\r", value)
			value = re.sub(r"([^\\])\\t", r"\1\t", value)
			value = re.sub(r"^\\n", r"\n", value)
			value = re.sub(r"^\\r", r"\r", value)
			value = re.sub(r"^\\t", r"\t", value)
			value = re.sub(r"\\\\", r"\\", value)
		
		return value
		
	def GetValueFromNodeNumber(self, node):
		
		value = None
		type = 'string'
		
		if node.hasAttributeNS(None, 'valueType'):
			type = self._getAttribute(node, 'valueType')
			if not type in ['literal', 'hex', 'string']:
				raise PeachException("Error: [%s] has invalid valueType attribute." % node.getFullname())
		
		if node.hasAttributeNS(None, 'value'):
			value = self._getAttribute(node, 'value')
			
			# Convert variouse forms of hex into a binary string
			if type == 'hex':
				if len(value) == 1:
					value = "0" + value
				
				ret = ''
				
				valueLen = len(value)+1
				while valueLen > len(value):
					valueLen = len(value)
					
					for i in range(len(self._regsHex)):
						match = self._regsHex[i].search(value)
						if match != None:
							while match != None:
								ret += match.group(2)
								value = self._regsHex[i].sub('', value)
								match = self._regsHex[i].search(value)
							break
				
				return long(ret, 16)
			
			elif type == 'literal':
				value = eval(value)
			
		return value
		
	# Handlers for Template ###################################################
	
	def HandleTemplate(self, node, parent):
		'''
		Parse an element named Template.  Can handle actual
		Template elements and also reference Template elements.
		
		e.g.:
		
		<Template name="Xyz"> ... </Template>
		
		or
		
		<Template ref="Xyz" />
		'''
		
		template = None
		
		# ref
		
		if node.hasAttributeNS(None, 'ref'):
			
			# We have a base template
			obj = self.GetRef( self._getAttribute(node, 'ref') )
			
			template = obj.copy(parent)
			template.ref = self._getAttribute(node, 'ref')
			template.parent = parent
		
		else:
			template = Template(self._getAttribute(node, 'name'))
			template.ref = None
			template.parent = parent
		
		# name
		
		if node.hasAttributeNS(None, 'name'):
			template.name = self._getAttribute(node, 'name')
		
		template.elementType = 'template'
		
		# mutable
		
		mutable = self._getAttribute(node, 'mutable')
		if mutable == None or len(mutable) == 0:
			template.isMutable = True
		
		elif mutable.lower() == 'true':
			template.isMutable = True
			
		elif mutable.lower() == 'false':
			template.isMutable = False
		
		else:
			raise PeachException("Attribute 'mutable' has unexpected value [%s], only 'true' and 'false' are supported." % mutable)
		
		# pointer
		
		pointer = self._getAttribute(node, 'pointer')
		if pointer == None:
			pass
		
		elif pointer.lower() == 'true':
			template.isPointer = True
			
		elif pointer.lower() == 'false':
			template.isPointer = False
		
		else:
			raise PeachException("Attribute 'pointer' has unexpected value [%s], only 'true' and 'false' are supported." % pointer)
		
		# pointerDepth
		
		if node.hasAttributeNS(None, "pointerDepth"):
			template.pointerDepth = self._getAttribute(node, 'pointerDepth')
		
		# children
		
		self.HandleDataContainerChildren(node, template)
		
		# Switch any references to old name
		if node.hasAttributeNS(None, 'ref'):
			oldName = self._getAttribute(node, 'ref')
			for relation in template._genRelationsInDataModelFromHere():
				if relation.of == oldName:
					relation.of = template.name
				
				elif relation.From == oldName:
					relation.From = template.name


		#template.printDomMap()
		return template
	
	def HandleCommonTemplate(self, node, elem):
		'''
		Handle the common children of data elements like String and Number.
		'''
		
		elem.onArrayNext = self._getAttribute(node, "onArrayNext")
		
		for child in node:
			
			if child.nodeName == 'Relation':
				relation = self.HandleRelation(child, elem)
				elem.relations.append(relation)
			
			elif child.nodeName == 'Transformer':
				if elem.transformer != None:
					raise PeachException("Error, data element [%s] already has a transformer." % elem.name)
				
				elem.transformer = self.HandleTransformer(child, elem)
				
			elif child.nodeName == 'Fixup':
				self.HandleFixup(child, elem)
			
			elif child.nodeName == 'Placement':
				self.HandlePlacement(child, elem)
			
			elif child.nodeName == 'Hint':
				self.HandleHint(child, elem)
			
			else:
				raise PeachException("Found unexpected child node '%s' in element '%s'." % (child.nodeName, elem.name))
	
	def HandleTransformer(self, node, parent):
		'''
		Handle Transformer element
		'''
		
		transformer = Transformer(parent)
		
		childTransformer = None
		params = []
		
		# class
		
		if not node.hasAttributeNS(None, "class"):
			raise PeachException("Transformer element missing class attribute")
		
		generatorClass = self._getAttribute(node, "class")
		transformer.classStr = generatorClass
		
		# children
		
		for child in node.childNodes:
			
			if child.nodeName == 'Transformer':
				if childTransformer != None:
					raise PeachException("A transformer can only have one child transformer")
				
				childTransformer = self.HandleTransformer(child, transformer)
				continue
			
			if child.nodeName == 'Param':
				param = self.HandleParam(child, transformer)
				transformer.append(param)
				params.append([param.name, param.defaultValue])
		
		code = "PeachXml_"+generatorClass + '('
		
		isFirst = True
		for param in params:
			if not isFirst:
				code += ', '
			else:
				isFirst = False
			
			code += PeachStr(param[1])
		
		code += ')'
		
		trans = eval(code, globals(), locals())
		
		if childTransformer != None:
			trans.setAnotherTransformer(childTransformer.transformer)
		
		transformer.transformer = trans
		
		if parent != None:
			parent.transformer = transformer
			transformer.parent = parent
			#parent.append(transformer)
		
		return transformer
		
	def HandleDefaults(self, node, parent):
		'''
		Handle data element defaults
		'''

		# children

		for child in node.childNodes:
			if child.nodeName == 'Blob':
				if child.hasAttributeNS(None, 'valueType'):
					Blob.defaultValueType = self._getAttribute(child, 'valueType')
					
					if Blob.defaultValueType not in ['string', 'literal','hex']:
						raise PeachException("Error, default value for Blob.valueType incorrect.")
					
				if child.hasAttributeNS(None, 'lengthType'):
					Blob.defaultLengthType = self._getAttribute(child, 'lengthType')
					
					if Blob.defaultLengthType not in ['string', 'literal','calc']:
						raise PeachException("Error, default value for Blob.lengthType incorrect.")
					
			elif child.nodeName == 'Flags':
				if child.hasAttributeNS(None, 'endian'):
					Flags.defaultEndian = self._getAttribute(child, 'endian')
					
					if Flags.defaultEndian not in ['little', 'big','network']:
						raise PeachException("Error, default value for Flags.endian incorrect.")
			
			elif child.nodeName == 'Number':
				if child.hasAttributeNS(None, 'endian'):
					Number.defaultEndian = self._getAttribute(child, 'endian')
					
					if Number.defaultEndian not in ['little', 'big','network']:
						raise PeachException("Error, default value for Number.endian incorrect.")
			
				if child.hasAttributeNS(None, 'size'):
					Number.defaultSize = int(self._getAttribute(child, 'size'))
					
					if Number.defaultSize not in Number._allowedSizes:
						raise PeachException("Error, default value for Number.size incorrect.")
			
				if child.hasAttributeNS(None, 'signed'):
					Number.defaultSigned = self._getAttribute(child, 'signed')
					
					if Number.defaultSigned not in ['true', 'false']:
						raise PeachException("Error, default value for Number.signed incorrect.")
					
					if Number.defaultSigned == 'true':
						Number.defaultSigned = True
					else:
						Number.defaultSigned = False
			
				if child.hasAttributeNS(None, 'valueType'):
					Number.defaultValueType = self._getAttribute(child, 'valueType')
					
					if Number.defaultValueType not in ['string', 'literal', 'hex']:
						raise PeachException("Error, default value for Number.valueType incorrect.")
			
			elif child.nodeName == 'String':
				if child.hasAttributeNS(None, 'valueType'):
					String.defaultValueType = self._getAttribute(child, 'valueType')
					
					if String.defaultValueType not in ['string', 'literal', 'hex']:
						raise PeachException("Error, default value for String.valueType incorrect.")

				if child.hasAttributeNS(None, 'lengthType'):
					String.defaultLengthType = self._getAttribute(child, 'lengthType')
					
					if String.defaultLengthType not in ['string', 'literal', 'calc']:
						raise PeachException("Error, default value for String.lengthType incorrect.")

				if child.hasAttributeNS(None, 'padCharacter'):
					String.defaultPadCharacter = child.getAttributeNS(None, 'padCharacter')
					
				if child.hasAttributeNS(None, 'type'):
					String.defaultType = self._getAttribute(child, 'type')
					
					if String.defaultType not in ['wchar', 'char', 'utf8']:
						raise PeachException("Error, default value for String.type incorrect.")
				
				if child.hasAttributeNS(None, 'nullTerminated'):
					String.defaultNullTerminated = self._getAttribute(child, 'nullTerminated')
					
					if String.defaultNullTerminated not in ['true', 'false']:
						raise PeachException("Error, default value for String.nullTerminated incorrect.")
					
					if String.defaultNullTerminated == 'true':
						String.defaultNullTerminated = True
					else:
						String.defaultNullTerminated = False


	def HandleFixup(self, node, parent):
		'''
		Handle Fixup element
		'''
		
		fixup = Fixup(parent)
		
		params = []
		
		# class
		
		if not node.hasAttributeNS(None, "class"):
			raise PeachException("Fixup element missing class attribute")
		
		fixup.classStr = self._getAttribute(node, "class")
		
		# children
		
		for child in node.childNodes:
			
			if child.nodeName == 'Param':
				param = self.HandleParam(child, fixup)
				fixup.append(param)
				params.append([param.name, param.defaultValue])
		
		code = "PeachXml_"+fixup.classStr + '('
		
		isFirst = True
		for param in params:
			if not isFirst:
				code += ', '
			else:
				isFirst = False
			
			code += PeachStr(param[1])
		
		code += ')'
		
		fixup.fixup = eval(code, globals(), locals())
		
		if parent != None:
			if parent.fixup != None:
				raise PeachException("Error, data element [%s] already has a fixup." % parent.name)
			
			parent.fixup = fixup
		
		return fixup
		
	def HandlePlacement(self, node, parent):
		'''
		Handle Placement element
		'''
		
		placement = Placement(parent)
		
		placement.after = self._getAttribute(node, "after")
		placement.before = self._getAttribute(node, "before")
		
		if placement.after == None and placement.before == None:
			raise PeachException("Error: Placement element must have an 'after' or 'before' attribute.")
		
		if placement.after != None and placement.before != None:
			raise PeachException("Error: Placement can only have one of 'after' or 'before' but not both.")
		
		if parent != None:
			if parent.placement != None:
				raise PeachException("Error, data element [%s] already has a placement." % parent.name)
			
			#print "Setting placement on",parent.name
			parent.placement = placement
			#parent.append(placement)
		
		return placement
		
	def HandleRelation(self, node, elem):
		
		if not node.hasAttributeNS(None, "type"):
			raise PeachException("Relation element does not have type attribute")
		
		type = self._getAttribute(node, "type")
		of = self._getAttribute(node, "of")
		From = self._getAttribute(node, "from")
		name = self._getAttribute(node, "name")
		when = self._getAttribute(node, "when")
		expressionGet = self._getAttribute(node, "expressionGet")
		expressionSet = self._getAttribute(node, "expressionSet")
		relative = self._getAttribute(node, "relative")
		
		if of == None and From == None and when == None:
			raise PeachException("Relation element does not have of, from, or when attribute.")
		
		if type not in ['size', 'count', 'index', 'when', 'offset']:
			raise PeachException("Unknown type value in Relation element")
		
		relation = Relation(name, elem)
		relation.of = of
		relation.From = From
		relation.type = type
		relation.when = when
		relation.expressionGet = expressionGet
		relation.expressionSet = expressionSet
		
		if self._getAttribute(node, "isOutputOnly") != None and self._getAttribute(node, "isOutputOnly") in ["True","true"]:
			relation.isOutputOnly = True
		
		if relative != None:
			if relative.lower() in ["true", "1"]:
				relation.relative = True
				relation.relativeTo = self._getAttribute(node, "relativeTo")
			elif relative.lower() in ["false", "0"]:
				relation.relative = False
				relation.relativeTo = None
			else:
				raise PeachException("Error: Value of Relation relative attribute is not true or false.")
		
		return relation
	
	def HandleAnalyzerTopLevel(self, node, elem):
		
		if not node.hasAttributeNS(None, "class"):
			raise PeachException("Analyzer element must have a 'class' attribute")
		
		# Locate any arguments
		args = {}
		
		for child in node:
			if child.nodeName == 'Param' and child.hasAttributeNS(None, 'name'):
				args[self._getAttribute(child, 'name')] = self._getAttribute(child, 'value')
		
		cls = self._getAttribute(node, "class")
		
		try:
			obj = eval("%s()" % cls)
		except:
			raise PeachException("Error creating analyzer '%s': %s" % (obj, repr(sys.exc_info())))
		
		if not obj.supportTopLevel:
			raise PeachException("Analyzer '%s' does not support use as top-level element"%cls)
		
		obj.asTopLevel(self.context, args)
	
	def HandleCommonDataElementAttributes(self, node, element):
		'''
		Handle attributes common to all DataElements such as:
		
		 - minOccurs, maxOccurs
		 - mutable
		 - isStatic
		 - constraint
		 - pointer
		 - pointerDepth
		 - token
		
		'''
		
		# min/maxOccurs
		
		self._HandleOccurs(node, element)
		
		# isStatic/token
		
		isStatic = self._getAttribute(node, 'isStatic')
		if isStatic == None:
			isStatic = self._getAttribute(node, 'token')
		if isStatic == None or len(isStatic) == 0:
			element.isStatic = False
		
		elif isStatic.lower() == 'true':
			element.isStatic = True
		
		elif isStatic.lower() == 'false':
			element.isStatic = False
		
		else:
			if node.hasAttributeNS(None, "isStatic"):
				raise PeachException("Attribute 'isStatic' has unexpected value [%s], only 'true' and 'false' are supported." % isStatic)
			else:
				raise PeachException("Attribute 'token' has unexpected value [%s], only 'true' and 'false' are supported." % isStatic)
		
		# mutable
		
		mutable = self._getAttribute(node, 'mutable')
		if mutable == None or len(mutable) == 0:
			element.isMutable = True
		
		elif mutable.lower() == 'true':
			element.isMutable = True
			
		elif mutable.lower() == 'false':
			element.isMutable = False
		
		else:
			raise PeachException("Attribute 'mutable' has unexpected value [%s], only 'true' and 'false' are supported." % mutable)
		
		# pointer
		
		pointer = self._getAttribute(node, 'pointer')
		if pointer == None:
			pass
		
		elif pointer.lower() == 'true':
			element.isPointer = True
			
		elif pointer.lower() == 'false':
			element.isPointer = False
		
		else:
			raise PeachException("Attribute 'pointer' has unexpected value [%s], only 'true' and 'false' are supported." % pointer)
		
		# pointerDepth
		
		if node.hasAttributeNS(None, "pointerDepth"):
			element.pointerDepth = self._getAttribute(node, 'pointerDepth')
		
		# constraint
		
		element.constraint = self._getAttribute(node, "constraint")

	
	def _HandleOccurs(self, node, element):
		'''
		Grab min, max, and generated Occurs attributes
		'''
		
		if node.hasAttributeNS(None, 'generatedOccurs'):
			element.generatedOccurs = self._getAttribute(node, 'generatedOccurs')
		else:
			element.generatedOccurs = 10
		
		occurs = self._getAttribute(node, 'occurs')
		minOccurs = self._getAttribute(node, 'minOccurs')
		maxOccurs = self._getAttribute(node, 'maxOccurs')
		
		if minOccurs == None:
			minOccurs = 1
		else:
			minOccurs = eval(minOccurs)
		
		if maxOccurs == None:
			maxOccurs = 1
		else:
			maxOccurs = eval(maxOccurs)
		
		if minOccurs != None and maxOccurs != None:
			element.minOccurs = int(minOccurs)
			element.maxOccurs = int(maxOccurs)
		
		elif minOccurs != None and maxOccurs == None:
			element.minOccurs = int(minOccurs)
			element.maxOccurs = 1024
		
		elif maxOccurs != None and minOccurs == None:
			element.minOccurs = 0
			element.maxOccurs = int(maxOccurs)
			
		else:
			element.minOccurs = 1
			element.maxOccurs = 1
	
		if occurs != None:
			element.occurs = element.minOccurs = element.maxOccurs = int(occurs)
	
	def HandleBlock(self, node, parent):
		
		# name
		
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		else:
			name = None
		
		# ref
		
		if node.hasAttributeNS(None, 'ref'):
			
			oldName = self._getAttribute(node, "ref")

			if name == None or len(name) == 0:
				name = Element.getUniqueName()
			
			# We have a base template
			obj = self.GetRef( self._getAttribute(node, 'ref'), parent )
			
			block = obj.copy(parent)
			block.name = name
			block.parent = parent
			block.ref = self._getAttribute(node, 'ref')
			
			# Block may not be a block!
			block.toXml = new.instancemethod(PeachModule.Engine.dom.BlockToXml, block, block.__class__)
			block.elementType = 'block'
			
		else:
			block = dom.Block(name, parent)
			block.ref = None
			
		#block.node = node
		
		# length (in bytes)

		if node.hasAttributeNS(None, 'lengthType') and self._getAttribute(node, 'lengthType') == 'calc':
			block.lengthType = self._getAttribute(node, 'lengthType')
			block.lengthCalc = self._getAttribute(node, 'length')
			block.length = -1

		elif node.hasAttributeNS(None, 'length'):
			length = self._getAttribute(node, 'length')
			if length != None and len(length) != 0:
				block.length = int(length)
			else:
				block.length = None

		# alignment
		
		try:
			alignment = self._getAttribute(node, 'alignment')
			if len(alignment) == 0:
				alignment = None
		except:
			alignment = None
		
		if alignment != None:
			block.isAligned = True
			block.alignment = int(alignment)**2
		
		# common attributes
		
		self.HandleCommonDataElementAttributes(node, block)
		
		# children
		
		self.HandleDataContainerChildren(node, block)

		# Switch any references to old name
		
		if node.hasAttributeNS(None, 'ref'):
			for relation in block._genRelationsInDataModelFromHere():
				if relation.of == oldName:
					relation.of = name
				
				elif relation.From == oldName:
					relation.From = name

		# Add to parent
		parent.append(block)
		return block
	

	def HandleDataContainerChildren(self, node, parent, errorOnUnknown = True):
		'''
		Handle parsing conatiner children.  This method
		will handle children of DataElement types for
		containers like Block, Choice, and Template.
		
		Can be used by Custom types to create Custom container
		types.
		
		@type	node: XML Element
		@param	node: Current XML Node being handled
		@type	parent: ElementWithChildren
		@param	parent: Parent of this DataElement
		@type	errorOnUnknown: Boolean
		@param	errorOnUnknonw: Should we throw an error on unexpected child node (default True)
		'''
		# children

		for child in node.childNodes:
			
			name = self._getAttribute(child, 'name')
			if name != None and '.' in name:
				# Replace a deep node, can only happen if we
				# have a ref on us.
				
				if not node.hasAttributeNS(None, 'ref'):
					raise PeachException("Error, periods (.) are not allowed in element names unless overrideing deep elements when a parent reference (ref). Name: [%s]" % name)
				
				# Okay, lets locate the real parent.
				obj = parent
				for part in name.split('.')[:-1]:
					if not obj.has_key(part):
						raise PeachException("Error, unable to resolve [%s] in deep parent of [%s] override." % (part, name))
						
					obj = obj[part]
				
				if obj == None:
					raise PeachException("Error, unable to resolve deep parent of [%s] override." % name)
				
				# Remove periods from name
				child.setAttributeNS(None, 'name', name.split('.')[-1])
				
				# Handle child with new parent.
				self._HandleDataContainerChildren(node, child, obj, errorOnUnknown)
			
			else:
				self._HandleDataContainerChildren(node, child, parent, errorOnUnknown)
				
	
	def _HandleDataContainerChildren(self, node, child, parent, errorOnUnknown = True):
		if child.nodeName == 'Block':
			self.HandleBlock(child, parent)
		elif child.nodeName == 'String':
			self.HandleString(child, parent)
		elif child.nodeName == 'Number':
			self.HandleNumber(child, parent)
		elif child.nodeName == 'Flags':
			self.HandleFlags(child, parent)
		elif child.nodeName == 'Flag':
			self.HandleFlag(child, parent)
		elif child.nodeName == 'Blob':
			self.HandleBlob(child, parent)
		elif child.nodeName == 'Choice':
			self.HandleChoice(child, parent)
		elif child.nodeName == 'Transformer':
			parent.transformer = self.HandleTransformer(child, parent)
		elif child.nodeName == 'Relation':
			relation = self.HandleRelation(child, parent)
			parent.relations.append(relation)
		elif child.nodeName == 'Fixup':
			self.HandleFixup(child, parent)
		elif child.nodeName == 'Placement':
			self.HandlePlacement(child, parent)
		elif child.nodeName == 'Hint':
			self.HandleHint(child, parent)
		elif child.nodeName == 'Seek':
			self.HandleSeek(child, parent)
		elif child.nodeName == 'Custom':
			self.HandleCustom(child, parent)
		elif child.nodeName == 'Asn1':
			self.HandleAsn1(child, parent)
		elif child.nodeName == 'XmlElement':
			# special XmlElement reference
		
			if child.hasAttributeNS(None, 'ref'):
				# This is our special case, if we ref we suck the children
				# of the ref into our selves.  This is tricky!
				
				# get and copy our ref
				obj = self.GetRef( self._getAttribute(child, 'ref'), parent.parent )
				
				newobj = obj.copy(parent)
				newobj.parent = None
				
				# first verify all children are XmlElement or XmlAttribute
				for subchild in newobj:
					if not isinstance(subchild, XmlElement) and not isinstance(subchild, XmlAttribute):
						raise PeachException("Error, special XmlElement ref case, reference must only have Xml elements!! (%s,%s,%s)" % (subchild.parent.name, subchild.name, subchild))
				
				# now move over children
				for subchild in newobj:
					parent.append(subchild)
					
				# remove replaced element
				if parent.has_key(self._getAttribute(child, 'name')):
					del parent[self._getAttribute(child, 'name')]
			
			else:
				self.HandleXmlElement(child, parent)
		
		elif child.nodeName == 'XmlAttribute':
			self.HandleXmlAttribute(child, parent)
			
		elif errorOnUnknown:
			raise PeachException(PeachStr("found unexpected node [%s] in Element: %s" % (child.nodeName, node.nodeName)))
	
	def HandleMutators(self, node, parent):
		# name
		
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		else:
			name = None
		
		mutators = dom.Mutators(name, parent)
		
		# children
		
		for child in node.childNodes:
			
			if child.nodeName != 'Mutator':
				raise PeachException(PeachStr("Found unexpected node in Mutators element: %s" % child.NodeName))
				
			if not child.hasAttributeNS(None, 'class'):
				raise PeachException("Mutator element does not have required class attribute")
			
			mutator = Mutator(self._getAttribute(child, 'class'), mutators)
			mutators.append(mutator)
			
		parent.append(mutators)
		return mutators

	
	def HandleChoice(self, node, parent):
		
		# name
		
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		else:
			name = None
		
		# ref
		
		if node.hasAttributeNS(None, 'ref'):
			
			if name == None or len(name) == 0:
				name = Element.getUniqueName()
			
			# We have a base template
			obj = self.GetRef( self._getAttribute(node, 'ref'), parent )
			
			#print "About to deep copy: ", obj, " for ref: ", self._getAttribute(node, 'ref')
			
			block = obj.copy(parent)
			block.name = name
			block.parent = parent
			block.ref = self._getAttribute(node, 'ref')
			
		else:
			block = Choice(name, parent)
			block.ref = None
			
		block.elementType = 'choice'
		
		# length (in bytes)
		
		if node.hasAttributeNS(None, 'lengthType') and self._getAttribute(node, 'lengthType') == 'calc':
			block.lengthType = self._getAttribute(node, 'lengthType')
			block.lengthCalc = self._getAttribute(node, 'length')
			block.length = -1
		
		elif node.hasAttributeNS(None, 'length'):
			length = self._getAttribute(node, 'length')
			if length != None and len(length) != 0:
				block.length = int(length)
			else:
				block.length = None
		
		# common attributes
		
		self.HandleCommonDataElementAttributes(node, block)
		
		# children
		self.HandleDataContainerChildren(node, block)
		
		parent.append(block)
		return block
	
	def HandleAsn1(self, node, parent):
		
		# name
		
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		else:
			name = None
		
		# ref
		
		if node.hasAttributeNS(None, 'ref'):
			
			raise PeachException("Asn1 element does not yet support ref!")
			#
			#if name == None or len(name) == 0:
			#	name = Element.getUniqueName()
			#
			## We have a base template
			#obj = self.GetRef( self._getAttribute(node, 'ref'), parent )
			#
			##print "About to deep copy: ", obj, " for ref: ", self._getAttribute(node, 'ref')
			#
			#block = obj.copy(parent)
			#block.name = name
			#block.parent = parent
			#block.ref = self._getAttribute(node, 'ref')
			
		else:
			block = Asn1Type(name, parent)
			block.ref = None
			
		# encode type
		
		if node.hasAttributeNS(None, "encode"):
			block.encodeType = node.getAttributeNS(None, "encode")
		
		# asn1Type
		
		if not node.hasAttributeNS(None, "type"):
			raise PeachException("Error, all Asn1 elements must have 'type' attribute.")
		
		block.asn1Type = node.getAttributeNS(None, "type")
		
		# Tag Stuff
		
		if node.hasAttributeNS(None, "tagNumber"):
			try:
				block.tagClass = Asn1Type.ASN1_TAG_CLASS_MAP[self._getAttribute(node, "tagClass").lower()]
				block.tagFormat = Asn1Type.ASN1_TAG_TYPE_MAP[self._getAttribute(node, "tagFormat").lower()]
				block.tagCategory = self._getAttribute(node, "tagCategory").lower()
				block.tagNumber = int(self._getAttribute(node, "tagNumber"))
			except:
				raise PeachException("Error, When using tags you must specify 'tagClass', 'tagFormat', 'tagCategory', and 'tagNumber'.")
		
		# common attributes
		
		self.HandleCommonDataElementAttributes(node, block)
		
		# children
		self.HandleDataContainerChildren(node, block)
		
		parent.append(block)
		return block

	def HandleXmlElement(self, node, parent):

		# name
		
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		else:
			name = None
		
		block = XmlElement(name, parent)
		
		# elementName
		
		block.elementName = self._getAttribute(node, "elementName")
		if block.elementName == None:
			raise PeachException("Error: XmlElement without elementName attribute.")
		
		# ns
		
		block.xmlNamespace = self._getAttribute(node, "ns")
		
		# length (in bytes)
		
		if node.hasAttributeNS(None, 'lengthType') and self._getAttribute(node, 'lengthType') == 'calc':
			block.lengthType = self._getAttribute(node, 'lengthType')
			block.lengthCalc = self._getAttribute(node, 'length')
			block.length = -1
		
		elif node.hasAttributeNS(None, 'length'):
			length = self._getAttribute(node, 'length')
			if length != None and len(length) != 0:
				block.length = int(length)
			else:
				block.length = None
		
		# common attributes
		
		self.HandleCommonDataElementAttributes(node, block)
		
		# children
		self.HandleDataContainerChildren(node, block)
		
		parent.append(block)
		return block

	def HandleXmlAttribute(self, node, parent):
		
		# name
		
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		else:
			name = None
		
		block = XmlAttribute(name, parent)
		
		# elementName
		
		block.attributeName = self._getAttribute(node, "attributeName")
		
		# ns
		
		block.xmlNamespace = self._getAttribute(node, "ns")
		
		# length (in bytes)
		
		if node.hasAttributeNS(None, 'lengthType') and self._getAttribute(node, 'lengthType') == 'calc':
			block.lengthType = self._getAttribute(node, 'lengthType')
			block.lengthCalc = self._getAttribute(node, 'length')
			block.length = -1
		
		elif node.hasAttributeNS(None, 'length'):
			length = self._getAttribute(node, 'length')
			if length != None and len(length) != 0:
				block.length = int(length)
			else:
				block.length = None
		
		# common attributes
		
		self.HandleCommonDataElementAttributes(node, block)

		# children
		self.HandleDataContainerChildren(node, block)
		
		parent.append(block)
		return block

	def _getAttribute(self, node, name):
		
		if not node.hasAttributeNS(None, name):
			return None
		
		return PeachStr(node.getAttributeNS(None, name))
	
	def _getValueType(self, node):
		
		valueType = self._getAttribute(node, 'valueType')
		if valueType == None:
			return 'string'
		
		return valueType
		
	def HandleString(self, node, parent):
		
		# name
		
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		else:
			name = None

		string = String(name, parent)
		
		# value
		
		string.defaultValue = self.GetValueFromNodeString(node)
		string.valueType = self._getValueType(node)
		string.defaultValue = self._HandleValueTypeString(string.defaultValue, string.valueType)

		# tokens
		
		if node.hasAttributeNS(None, 'tokens'):
			string.tokens = self._getAttribute(node, 'tokens')
		else:
			string.tokens = None

		# padCharacter
		
		if node.hasAttributeNS(None, 'padCharacter'):
			val = node.getAttributeNS(None, 'padCharacter')
			val = val.replace("'", "\\'")
			string.padCharacter = eval("u'''" + val + "'''")
		
		# type
		
		if node.hasAttributeNS(None, 'type'):
			type = self._getAttribute(node, 'type')
			if type == None or len(type) == 0:
				string.type = 'char'
		
			elif not (type in ['char', 'wchar', 'utf8', 'utf-8', 'utf-16le', 'utf-16be']):
				raise PeachException("Unknown type of String: %s" % type)
		
			else:
				string.type = type
		
		# nullTerminated (optional)
		
		if node.hasAttributeNS(None, 'nullTerminated'):
			nullTerminated = self._getAttribute(node, 'nullTerminated')
			if nullTerminated == None or len(nullTerminated) == 0:
				nullTerminated = 'false'
		
			if nullTerminated.lower() == 'true':
				string.nullTerminated = True
			elif nullTerminated.lower() == 'false':
				string.nullTerminated = False
			else:
				raise PeachException("nullTerminated should be true or false")
		
		# length (bytes)
		
		if node.hasAttributeNS(None, 'lengthType') and self._getAttribute(node, 'lengthType') == 'calc':
			string.lengthType = self._getAttribute(node, 'lengthType')
			string.lengthCalc = self._getAttribute(node, 'length')
			string.length = -1
		
		elif node.hasAttributeNS(None, 'length'):
			length = self._getAttribute(node, 'length')
			if length == None or len(length) == 0:
				length = None
			
			try:
				if length != None:
					string.length = int(length)
				else:
					string.length = None
			except:
				raise PeachException("length must be a number or missing %s" % length)
		
		# Analyzer
		
		if node.hasAttributeNS(None, 'analyzer'):
			string.analyzer = self._getAttribute(node, 'analyzer')
		else:
			string.analyzer = None
		
		# common attributes
		
		self.HandleCommonDataElementAttributes(node, string)

		
		# Handle any common children
		
		self.HandleCommonTemplate(node, string)
		
		parent.append(string)
		return string	
		
	def HandleNumber(self, node, parent):
	
		# name
		
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		else:
			name = None

		number = Number(name, parent)
		
		# value
		
		number.defaultValue = PeachStr(self.GetValueFromNodeNumber(node))
		number.valueType = self._getValueType(node)
		
		if number.defaultValue != None:
			try:
				number.defaultValue = long(number.defaultValue)
			except:
				raise PeachException("Error: The default value for <Number> elements must be an integer.")
		
		# size (bits)
		
		if node.hasAttributeNS(None, 'size'):
			size = self._getAttribute(node, 'size')
			if size == None:
				raise PeachException("Number element %s is missing the 'size' attribute which is required." % number.name)
		
			number.size = int(size)
		
			if not number.size in number._allowedSizes:
				raise PeachException("invalid size")
		
		# endian (optional)
		
		if node.hasAttributeNS(None, 'endian'):
			number.endian = self._getAttribute(node, 'endian')
			if number.endian == 'network':
				number.endian = 'big'
			
			if number.endian != 'little' and number.endian != 'big':
				raise PeachException("invalid endian %s" % number.endian)
	
		# signed (optional)
		
		if node.hasAttributeNS(None, 'signed'):
			signed = self._getAttribute(node, 'signed')
			if signed == None or len(signed) == 0:
				signed = Number.defaultSigned
			
			if signed.lower() == 'true':
				number.signed = True
			elif signed.lower() == 'false':
				number.signed = False
			else:
				raise PeachException("signed must be true or false")
		
		# common attributes
		
		self.HandleCommonDataElementAttributes(node, number)
		
		# Handle any common children
		
		self.HandleCommonTemplate(node, number)
		
		parent.append(number)
		return number
		
		
	def HandleFlags(self, node, parent):
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		else:
			name = None
		
		flags = dom.Flags(name, parent)
		#flags.node = node
		
		# length (in bits)
		
		length = self._getAttribute(node, 'size')
		flags.length = int(length)
		if flags.length % 2 != 0:
			raise PeachException("length must be multiple of 2")
		
		if flags.length not in [8, 16, 24, 32, 64]:
			raise PeachException("Flags size must be one of 8, 16, 24, 32, or 64.")
		
		# endian
		
		if node.hasAttributeNS(None, 'endian'):
			flags.endian = self._getAttribute(node, 'endian')
			
			if not ( flags.endian == 'little' or flags.endian == 'big' ):
				raise PeachException("Invalid endian type on Flags element")
		
		# rightToLeft
		
		if node.hasAttributeNS(None, 'rightToLeft'):
			if self._getAttribute(node, 'rightToLeft').lower() == "true":
				flags.rightToLeft = True
			
			elif self._getAttribute(node, 'rightToLeft').lower() == "false":
				flags.rightToLeft = False
			
			else:
				raise PeachException("Flags attribute rightToLeft must be 'true' or 'false'.")
		
		# padding
		
		if node.hasAttributeNS(None, 'padding'):
			if self._getAttribute(node, 'padding').lower() == "true":
				flags.padding = True
			
			elif self._getAttribute(node, 'padding').lower() == "false":
				flags.padding = False
			
			else:
				raise PeachException("Flags attribute padding must be 'true' or 'false'.")
		
		# constraint
		flags.constraint = self._getAttribute(node, "constraint")

		# children
		
		for child in node.childNodes:
			
			if child.nodeName == 'Flag':
				
				childName = self._getAttribute(child, 'name')
				if childName != None:
					if flags.has_key(childName):
						raise PeachException("Error, found duplicate Flag name in Flags set [%s]" % flags.name)
				
				self.HandleFlag(child, flags)
			
			elif child.nodeName == 'Relation':
				self.HandleRelation(child, flags)
				
			else:
				raise PeachException(PeachStr("found unexpected node in Flags: %s" % child.nodeName))
		
		parent.append(flags)
		return flags
	

	def HandleFlag(self, node, parent):
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		else:
			name = None

		flag = Flag(name, parent)
		#flag.node = node
		
		# value
		
		flag.defaultValue = PeachStr(self.GetValueFromNode(node))
		flag.valueType = self._getValueType(node)
		
		# position (in bits)
		
		position = self._getAttribute(node, 'position')
		flag.position = int(position)
		
		# length (in bits)
		
		length = self._getAttribute(node, 'size')
		flag.length = int(length)
		
		if flag.position > parent.length:
			raise PeachException("Invalid position, parent not big enough")
		
		if flag.position + flag.length > parent.length:
			raise PeachException("Invalid length, parent not big enough")
		
		
		# Handle any common children
		
		self.HandleCommonTemplate(node, flag)
		
		# Handle common data elements attributes
		
		self.HandleCommonDataElementAttributes(node, flag)
		
		# rest
		
		parent.append(flag)
		return flag
	

	def HandleBlob(self, node, parent):
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		else:
			name = None

		blob = Blob(name, parent)
		
		# value
		
		blob.defaultValue = PeachStr(self.GetValueFromNode(node))
		blob.valueType = self._getValueType(node)
		
		# length (in bytes)
		
		if node.hasAttributeNS(None, 'lengthType') and self._getAttribute(node, 'lengthType') == 'calc':
			blob.lengthType = self._getAttribute(node, 'lengthType')
			blob.lengthCalc = self._getAttribute(node, 'length')
			blob.length = -1
		
		elif node.hasAttributeNS(None, 'length'):
			length = self._getAttribute(node, 'length')
			if length != None and len(length) != 0:
				blob.length = int(length)
			else:
				blob.length = None
		
		# padValue
		
		if node.hasAttributeNS(None, 'padValue'):
			blob.padValue = self._getAttribute(node, 'padValue')
		else:
			blob.padValue = "\0"
		
		# Analyzer
		
		if node.hasAttributeNS(None, 'analyzer'):
			blob.analyzer = self._getAttribute(node, 'analyzer')
		else:
			blob.analyzer = None
		
		# common attributes
		
		self.HandleCommonDataElementAttributes(node, blob)
		
		# Handle any common children
		
		self.HandleCommonTemplate(node, blob)
		
		parent.append(blob)
		return blob


	def HandleCustom(self, node, parent):
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		else:
			name = None

		if node.hasAttributeNS(None, 'class'):
			cls = self._getAttribute(node, 'class')
		else:
			cls = None

		code = "PeachXml_%s(name, parent)" % cls
		custom = eval(code, globals(), locals())
		#custom.node = node

		# value

		custom.defaultValue = PeachStr(self.GetValueFromNode(node))
		custom.valueType = self._getValueType(node)

		# Hex handled elsewere.
		if custom.valueType == 'literal':
			custom.defaultValue = PeachStr(eval(custom.defaultValue))

		# common attributes
		
		self.HandleCommonDataElementAttributes(node, custom)

		# Handle any common children

		self.HandleCommonTemplate(node, custom)

		# constraint
		custom.constraint = self._getAttribute(node, "constraint")

		# Custom parsing
		custom.handleParsing(node)

		# Done
		parent.append(custom)
		return custom


	def HandleSeek(self, node, parent):
		'''
		Parse a <Seek> element, part of a data model.
		'''
		
		seek = Seek(None, parent)
		#seek.node = node
		
		seek.expression = self._getAttribute(node, 'expression')
		seek.position = self._getAttribute(node, 'position')
		seek.relative = self._getAttribute(node, 'relative')
		
		if seek.relative != None:
			seek.relative = int(seek.relative)
		
		if seek.position != None:
			seek.position = int(seek.position)
		
		if seek.expression == None and seek.position == None and seek.relative == None:
			raise PeachException("Error: <Seek> element must have an expression, position, or relative attribute.")
		
		parent.append(seek)
		return seek


	# Handlers for Data ###################################################

	def HandleData(self, node, parent):
		
		data = None
		
		# name
		
		name = self._getAttribute(node, 'name')
		
		# ref
		
		if node.hasAttributeNS(None, 'ref'):
			
			if name == None or len(name) == 0:
				name = Element.getUniqueName()
			
			# We have a base template
			obj = self.GetDataRef( self._getAttribute(node, 'ref') )
			
			data = obj.copy(parent)
			data.name = name
			
		else:
			data = Data(name)
		
			if (not isinstance(parent, Action)) and (name == None or len(name) == 0):
				raise PeachException(PeachStr("Error: Data element must have name attribute!"))
		
		data.elementType = 'data'
		
		# fileName
		
		if node.hasAttributeNS(None, 'fileName'):
			data.fileName = self._getAttribute(node, 'fileName')
			
			if data.fileName.find('*') != -1:
				data.fileGlob = data.fileName
				
				for f in glob.glob(data.fileGlob):
					if not os.path.isdir(f):
						data.fileName = f
				
				data.multipleFiles = True
			
			elif os.path.isdir(data.fileName):
				data.folderName = data.fileName
				
				for f in os.listdir(data.folderName):
					f = os.path.join(data.folderName, f)
					if not os.path.isdir(f):
						data.fileName = f
						
				data.multipleFiles = True
		
		# switchCount

		if node.hasAttributeNS(None, 'switchCount'):
			data.switchCount = int(self._getAttribute(node, 'switchCount'))
		else:
			data.switchCount = None
		
		# expression
		
		if node.hasAttributeNS(None, 'expression'):
			
			if data.fileName != None:
				raise PeachException("Data element cannot have both a fileName and expression attribute.")
			
			data.expression = self._getAttribute(node, 'expression')
		
		# children
		
		for child in node.childNodes:
			
			if child.nodeName == 'Field':
				if data.fileName != None or data.expression != None:
					raise PeachException("Data element cannot have a fileName or expression attribute along with Field child elements.")
				
				self.HandleField(child, data)
			
			else:
				raise PeachException(PeachStr("found unexpected node in Data: %s" % child.nodeName))
		
		return data
	

	def HandleField(self, node, parent):
		
		# name
		
		if not node.hasAttributeNS(None, 'name'):
			raise PeachException("No attribute name found on field element")
		
		name = self._getAttribute(node, 'name')
		
		# value
		
		if not node.hasAttributeNS(None, 'value'):
			raise PeachException("No attribute value found on Field element")
		
		value = self._getAttribute(node, 'value')
		
		field = Field(name, value, parent)
		field.value = PeachStr(self.GetValueFromNode(node))
		field.valueType = self._getValueType(node)
		
		if parent.has_key(field.name):
			parent[field.name] = field
		else:
			parent.append(field)
		
		return field

	# Handlers for Agent ###################################################
	
	def HandleAgent(self, node, parent):
		
		# name
		
		name = None
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
			
		# ref
		
		if node.hasAttributeNS(None, 'ref'):
			if name == None or len(name) == 0:
				name = Element.getUniqueName()
			
			obj = self.GetRef( self._getAttribute(node, 'ref') )
			
			agent = obj.copy(parent)
			agent.name = name
			agent.ref = self._getAttribute(node, 'ref')

		else:
			agent = Agent(name, parent)
		
		#agent.node = node
		agent.description = self._getAttribute(node, 'description')
		agent.location = self._getAttribute(node, 'location')
		if agent.location == None or len(agent.location) == 0:
			agent.location = "LocalAgent"
			#raise PeachException("Error: Agent definition must include location attribute.")
		
		agent.password = self._getAttribute(node, 'password')
		if agent.password != None and len(agent.password) == 0:
			agent.password = None
		
		for child in node.childNodes:
			
			if child.nodeName == 'Monitor':
				agent.append(self.HandleMonitor(child, agent))
			
			elif child.nodeName == 'PythonPath':
				p = self.HandlePythonPath(child, agent)
				agent.append(p)
				
			elif child.nodeName == 'Import':
				p = self.HandleImport(child, agent)
				agent.append(p)
				
			else:
				raise PeachException("Found unexpected child of Agent element")
		
		## A remote publisher might be in play
		#if len(agent) < 1:
		#	raise Exception("Agent must have at least one Monitor child.")
		
		return agent
	
	def HandleMonitor(self, node, parent):
		'''
		Handle Monitor element
		'''
		
		name = None
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		
		monitor = Monitor(name, parent)
		
		# class
		
		if not node.hasAttributeNS(None, "class"):
			raise PeachException("Monitor element missing class attribute")
		
		monitor.classStr = self._getAttribute(node, "class")
		
		# children
		
		for child in node.childNodes:
			
			if not child.nodeName == 'Param':
				raise PeachException(PeachStr("Unexpected Monitor child node: %s" % child.nodeName))
			
			param = self.HandleParam(child, parent)
			monitor.params[param.name] = param.defaultValue
		
		return monitor
	
	
	# Handlers for Test ###################################################
	
	def HandleTest(self, node, parent):
		
		# name
		
		name = None
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		
		# ref
		
		if node.hasAttributeNS(None, 'ref'):
			if name == None or len(name) == 0:
				name = Element.getUniqueName()
			
			obj = self.GetRef( self._getAttribute(node, 'ref') , None, 'tests')
			
			test = obj.copy(parent)
			test.name = name
			test.ref = self._getAttribute(node, 'ref')
			
		else:
			test = Test(name, parent)
		
		#test.node = node
		if node.hasAttributeNS(None, 'description'):
			test.description = self._getAttribute(node, 'description')
		
		test.mutators = None
		
		for child in node.childNodes:
						
			if child.nodeName == 'Publisher':
				if not test.publishers:
					test.publishers = []
			
				pub = self.HandlePublisher(child, test)
				test.publishers.append(pub)
				test.append(pub.domPublisher)
			
			elif child.nodeName == 'Agent':
				if child.hasAttributeNS(None, 'ref'):
					agent = self.GetRef( self._getAttribute(child, 'ref') , None, 'agents')
					
				if agent == None:
					raise PeachException(PeachStr("Unable to locate agent %s specified in Test element %s" % (self._getAttribute(child, 'ref'), name)))
				
				test.append(agent.copy(test))
			
			elif child.nodeName == 'StateMachine' or child.nodeName == 'StateModel':
				if not child.hasAttributeNS(None, 'ref'):
					raise PeachException("StateMachine element in Test declaration must have a ref attribute.")
				
				stateMachine = self.GetRef( self._getAttribute(child, 'ref'), None, 'children')
				if stateMachine == None:
					raise PeachException("Unable to locate StateMachine [%s] specified in Test [%s]" % (str(self._getAttribute(child, 'ref')), name))
				
				#print "*** StateMachine: ", stateMachine
				test.stateMachine = stateMachine.copy(test)
				test.append(test.stateMachine)
				
				path = None
				for child2 in child.childNodes:
					if child2.nodeName == 'Path':
						path = self.HandlePath(child2, test.stateMachine)
						test.stateMachine.append(path)
						
					elif child2.nodeName == 'Stop':
						if path == None:
							raise PeachException("Stop element must be used after a Path element.")
						
						path.stop = True
						# Do not accept anything after Stop element ;)
						break
					
					elif child2.nodeName == 'Strategy':
						strategy = self.HandleStrategy(child2, test.stateMachine)
						test.stateMachine.append(strategy)
					
					else:
						raise PeachException("Unexpected node %s" % child2.nodeName)
						
			elif child.nodeName == 'Mutator':
				
				if not child.hasAttributeNS(None, 'class'):
					raise PeachException("Mutator element does not have required class attribute")
				
				mutator = Mutator(self._getAttribute(child, 'class'), test)
				
				if not test.mutators:
					test.mutators = Mutators(None, test)
				
				mutator.parent = test.mutators
				test.mutators.append(mutator)
				
			elif child.nodeName == 'Include' or child.nodeName == 'Exclude':				
				self._HandleIncludeExclude(child, test)
			
			elif child.nodeName == 'Strategy':
				test.mutator = self.HandleFuzzingStrategy(child, test)
				
			else:
				raise PeachException("Found unexpected child of Test element")
		
		if test.mutator == None:
			test.mutator = MutationStrategy.DefaultStrategy(None, test)
			
		if test.mutators == None:
			# Add the default mutators instead of erroring out
			test.mutators = self._locateDefaultMutators()
		
		if test.template == None and test.stateMachine == None:
			raise PeachException(PeachStr("Test %s does not have a Template or StateMachine defined" % name))
		
		if len(test.publishers) == 0:
			raise PeachException(PeachStr("Test %s does not have a publisher defined!" % name))
		
		if test.template != None and test.stateMachine != None:
			raise PeachException(PeachStr("Test %s has both a Template and StateMachine defined.  Only one of them can be defined at a time." % name))
		
		# Now mark Mutatable(being fuzzed) elements
		# instructing on inclusions/exlusions
		test.markMutatableElements(node)
		
		return test
	
	def HandleFuzzingStrategy(self, node, parent):
		'''
		Handle parsing <Strategy> element that is a child of
		<Test>
		'''
		
		# name
		
		name = None
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
		
		# class
		
		cls = None
		if node.hasAttributeNS(None, 'class'):
			cls = self._getAttribute(node, 'class')
		
		strategy = None
		try:
			exec("strategy = PeachXml_%s(node, parent)" % cls)
			
		except:
			raise
			#raise PeachException("Error, unable to load strategy '%s'." % cls)
		
		return strategy

	def HandlePath(self, node, parent):
		if not node.hasAttributeNS(None, 'ref'):
			raise PeachException("Parser: Test::StateModel::Path missing ref attribute")

		stateMachine = parent
		ref = self._getAttribute(node, 'ref')
		state = self.GetRef(ref, stateMachine, None)
		
		path = Path(ref, parent)
		
		for child in node.childNodes:
			if child.nodeName == 'Include' or child.nodeName == 'Exclude':				
				self._HandleIncludeExclude(child, state)
			
			elif child.nodeName == 'Data':
			# Handle Data elements at Test-level
				data = self.HandleData(child, path)
				#data.node = child
				
				actions = [child for child in state if child.elementType=='action']
				for action in actions:
					cracker = DataCracker(action.getRoot())
					cracker.optmizeModelForCracking(action.template)
					action.template.setDefaults(data, self.dontCrack)
				
			elif child.nodeName not in ['Mutator']:
				raise PeachException("Found unexpected child of Path element")
					
		
		return path
	
	def _HandleIncludeExclude(self, node, parent):
		ref = None
		
		isExclude = node.nodeName != 'Exclude'
		
		if node.hasAttributeNS(None, 'ref') and node.hasAttributeNS(None, 'xpath'):
			raise PeachException("Include/Exclude node can only have one of either ref or xpath attributes.")
		
		xpath = None
		if node.hasAttributeNS(None, 'xpath'):
			xpath = self._getAttribute(node, 'xpath')
		else:
			ref = None;
			if node.hasAttributeNS(None, 'ref'):
				ref = self._getAttribute(node, 'ref').replace('.','/')
				
			xpath = self._retrieveXPath(ref, node.parentNode)
		
		test = self._getTest(parent)
		test.mutatables.append([isExclude, xpath])
			
	def _getTest(self, element):
		if element == None:
			return None
		
		if element.elementType == 'test':
			return element
		
		return self._getTest(element.parent)
		
	def _retrieveXPath(self, xpath, node):
		if node.nodeName == 'Test':
			if xpath == None:
				return "//*"
			else:
				return "//%s" % xpath
		
		if not node.hasAttributeNS(None, 'ref'):
			raise PeachException("All upper elements must have a ref attribute. Cannot retrieve relative XPath.")
					
		ref = self._getAttribute(node, 'ref')
		
		if xpath != None:
			xpath = ref + "/" + xpath
		else:
			xpath = ref
			
		return self._retrieveXPath(xpath, node.parentNode)
	
	def HandleStrategy(self, node, parent):
		# class
		if not node.hasAttributeNS(None, "class"):
			raise PeachException("Strategy element missing class attribute")
		
		classStr = self._getAttribute(node, "class")
		strategy = Strategy(classStr, parent)
		
		# children
		for child in node.childNodes:
			if not child.nodeName == 'Param':
				raise PeachException(PeachStr("Unexpected Strategy child node: %s" % child.nodeName))
			
			param = self.HandleParam(child, parent)
			strategy.params[param.name] = eval(param.defaultValue)
		
		return strategy

	def _locateDefaultMutators(self, obj = None):
		'''
		Look for a default set of mutators.  We will follow this
		search pattern:
		
		1. Look at our self (context) level
		2. Look at our imported namespaces
		3. Recerse into namespaces (sub namespaces, etc)
		
		This means a <Mutators> element in the top level XML file will
		get precidence over the defaults.xml file which is included into
		a namepsace.
		'''
		
		if obj == None:
			obj = self.context
		
		# First look at us
		if obj.mutators != None:
			return obj.mutators
		
		# Now look at namespaces
		for n in obj:
			if n.elementType == 'namespace':
				if n.ns.mutators != None:
					return n.ns.mutators
		
		# Now look inside namespace
		for n in obj:
			if n.elementType == 'namespace':
				m = self._locateDefaultMutators(n.ns)
				if m != None:
					return m
		
		# YUCK
		raise PeachException("Could not locate default set of Mutators to use.  Please fix this!")
	
	
	def HandleRun(self, node, parent):
				
		haveLogger = False

		# name
		
		name = None
		if node.hasAttributeNS(None, 'name'):
			name = self._getAttribute(node, 'name')
			
		run = Run(name, parent)
		#run.node = node
		run.description = self._getAttribute(node, 'description')
		
		if node.hasAttributeNS(None, 'waitTime'):
			run.waitTime = float(self._getAttribute(node, 'waitTime'))
		
		for child in node.childNodes:
			
			if child.nodeName == 'Test':
				
				test = None
				if child.hasAttributeNS(None, 'ref'):
					test = self.GetRef( self._getAttribute(child, 'ref') , None, 'tests')
				
				if test == None:
					raise PeachException(PeachStr("Unable to locate tests %s specified in Run element %s" % (testsName, name)))
				
				test = test.copy(run)
				run.tests.append(test)
				run.append(test)
				
			elif child.nodeName == 'Logger':
				logger = self.HandleLogger(child, run)
				run.append(logger)
				haveLogger = True
				
			else:
				raise PeachException("Found unexpected child of Run element")
		
		if len(run.tests) == 0:
			raise PeachException(PeachStr("Run %s does not have any tests defined!" % name))
		
		if not haveLogger:
			print "Warning: Run '%s' does not have logging configured!" % name
		
		return run
	
	
	def HandlePublisher(self, node, parent):
		
		params = []
		
		publisher = Publisher()
		
		# class
		
		if not node.hasAttributeNS(None, "class"):
			raise PeachException("Publisher element missing class attribute")
			
		if len(node.getAttributeNS(None, "class")) == 0:
			raise PeachException("Publisher class attribute is empty")
		
		publisher.classStr = publisherClass = self._getAttribute(node, "class")
		
		if node.hasAttributeNS(None, "name"):
			publisher.name = self._getAttribute(node, "name")
		
		# children
		
		for child in node.childNodes:
			
			if not child.hasAttributeNS(None, "name"):
				raise PeachException("Publisher element missing name attribute")
			
			if not child.hasAttributeNS(None, "value"):
				raise PeachException("Publisher element missing value attribute")
			
			if not child.hasAttributeNS(None, "valueType"):
				valueType = "string"
			else:
				valueType = self._getAttribute(child, "valueType")
			
			name = self._getAttribute(child, "name")
			value = self._getAttribute(child, "value")
			
			param = Param(publisher)
			param.name = name
			param.defaultValue = PeachStr(value)
			param.valueType = valueType
			
			if valueType == 'string':
				# create a literal out of a string value
				value = "'''" + value + "'''"
			elif valueType == 'hex':
				
				ret = ''
				
				valueLen = len(value)+1
				while valueLen > len(value):
					valueLen = len(value)
					
					for i in range(len(self._regsHex)):
						match = self._regsHex[i].search(value)
						if match != None:
							while match != None:
								ret += '\\x' + match.group(2)
								value = self._regsHex[i].sub('', value)
								match = self._regsHex[i].search(value)
							break
				
				value = "'" + ret + "'"
			
			publisher.append(param)
			params.append([name, value])
		
		code = "PeachXml_"+publisherClass + '('
		
		isFirst = True
		for param in params:
			if not isFirst:
				code += ', '
			else:
				isFirst = False
			
			code += PeachStr(param[1])
		
		code += ')'
		
		try:
			pub = eval(code, globals(), locals())
		
		except TypeError, e:
			error = str(e)
			
			if error.find(r"__init__() takes ") > -1:
				m = re.match(r"^__init__\(\) (.*) (\d+) arguments \((\d+) given\)$", error)
				msg = m.group(1)
				arg = int(m.group(2)) - 1
				given = int(m.group(3)) - 1
				
				raise PeachException("Error: Publisher '%s' %s %d arguments (%d given)" %(publisher.classStr, msg, arg, given) )
			
			raise e
			
		pub.domPublisher = publisher
		pub.parent = parent
		return pub
	

	def HandleLogger(self, node, parent):
		
		params = {}
		logger = Logger(parent)
		#logger.node = node
		
		# class
		
		if not node.hasAttributeNS(None, "class"):
			raise PeachException("Logger element missing class attribute")
		
		logger.classStr = self._getAttribute(node, "class")
		
		# children
		
		for child in node.childNodes:
			
			if not child.hasAttributeNS(None, "name"):
				raise PeachException("Logger element missing name attribute")
			
			if not child.hasAttributeNS(None, "value"):
				raise PeachException("Logger element missing value attribute")
			
			if not child.hasAttributeNS(None, "valueType"):
				valueType = "string"
			else:
				valueType = self._getAttribute(child, "valueType")
			
			name = self._getAttribute(child, "name")
			value = self._getAttribute(child, "value")
			
			param = Param(logger)
			param.name = name
			param.defaultValue = PeachStr(value)
			param.valueType = valueType
			
			if valueType == 'string':
				# create a literal out of a string value
				value = "'''" + value + "'''"
			elif valueType == 'hex':
				
				ret = ''
				
				valueLen = len(value)+1
				while valueLen > len(value):
					valueLen = len(value)
					
					for i in range(len(self._regsHex)):
						match = self._regsHex[i].search(value)
						if match != None:
							while match != None:
								ret += '\\x' + match.group(2)
								value = self._regsHex[i].sub('', value)
								match = self._regsHex[i].search(value)
							break
				
				value = "'" + ret + "'"
			
			#print "LoggeR: Adding %s:%s" % (PeachStr(name),PeachStr(value))
			logger.append(param)
			params[PeachStr(name)] = PeachStr(value)
		
		code = "PeachXml_"+ logger.classStr + '(params)'
		pub = eval(code)
		pub.domLogger = logger
		return pub
	
	
	def HandleStateMachine(self, node, parent):
		
		if not node.hasAttributeNS(None, "name"):
			raise PeachException("Parser: StateMachine missing name attribute")
		
		if not node.hasAttributeNS(None, 'initialState'):
			raise PeachException("Parser: StateMachine missing initialState attribute")
		
		stateMachine = StateMachine(self._getAttribute(node, "name"), parent)
		stateMachine.initialState = self._getAttribute(node, 'initialState')
		stateMachine.onLoad = self._getAttribute(node, 'onLoad')
		
		for child in node.childNodes:
			
			if child.nodeName == 'State':
				state = self.HandleState(child, stateMachine)
				stateMachine.append(state)
			
			else:
				raise PeachException("Parser: StateMachine has unknown child [%s]" % PeachStr(child.nodeName))
		
		return stateMachine
	
	def HandleState(self, node, parent):
		
		if not node.hasAttributeNS(None, "name"):
			raise PeachException("Parser: State missing name attribute")
		
		state = State(self._getAttribute(node, 'name'), parent)
		state.onEnter = self._getAttribute(node, 'onEnter')
		state.onExit = self._getAttribute(node, 'onExit')
		
		foundAction = False
		
		for child in node.childNodes:
			
			if child.nodeName == 'Action':
				action = self.HandleAction(child, state)
				if state.has_key(action.name):
					raise PeachException("Found duplicate Action name [%s]!" % action.name)
				
				state.append(action)
				foundAction = True

			elif child.nodeName == 'Choice': 
				choice = self.HandleStateChoice(child, state)
				state.append(choice)
			
			else:
				raise PeachException("Parser: State has unknown child [%s]" % PeachStr(child.nodeName))
			
		if foundAction == False:
			raise PeachException("State [%s] has no actions" % state.name)
		
		return state
	
	def HandleStateChoice(self, node, parent):
		choice = StateChoice(parent)
	
		for child in node.childNodes:
			choice.append(self.HandleStateChoiceAction(child, node))
		
		return choice
	
	def HandleStateChoiceAction(self, node, parent):
		
		if not node.hasAttributeNS(None, "ref"):
			raise PeachException("Parser: State::Choice::Action missing ref attribute")
		
		if not node.hasAttributeNS(None, "type"):
			raise PeachException("Parser: State::Choice::Action missing type attribute")
		
		ref = self._getAttribute(node, "ref")
		type = self._getAttribute(node, "type")
		
		return StateChoiceAction(ref, type, parent)
		  	
	def HandleAction(self, node, parent):
		
		if not node.hasAttributeNS(None, "type"):
			raise PeachException("Parser: Action missing 'type' attribute")
		
		action = Action(self._getAttribute(node, 'name'), parent)
		action.type = self._getAttribute(node, 'type')
		
		if not action.type in [ 'input', 'output', 'call', 'setprop', 'getprop', 'changeState',
								'slurp', 'connect', 'close', 'accept', 'start', 'stop', 'wait', 'open' ]:
			raise PeachException("Parser: Action type attribute is not valid [%s]." % action.type)
		
		action.onStart = self._getAttribute(node, 'onStart')
		action.onComplete = self._getAttribute(node, 'onComplete')
		action.when = self._getAttribute(node, 'when')
		action.ref = self._getAttribute(node, 'ref')
		action.setXpath = self._getAttribute(node, 'setXpath')
		action.valueXpath = self._getAttribute(node, 'valueXpath')
		action.valueLiteral = self._getAttribute(node, 'value')
		action.method = self._getAttribute(node, 'method')
		action.property = self._getAttribute(node, 'property')
		action.publisher = self._getAttribute(node, 'publisher')
		
		# Quick hack to get open support.  open and connect are same.
		if action.type == 'open':
			action.type = 'connect'
		
		if (action.setXpath or action.valueXpath or action.valueLiteral) and (action.type != 'slurp' and action.type != 'wait'):
			raise PeachException("Parser: Invalid attribute for Action were type != 'slurp'")
		
		if action.method != None and action.type != 'call':
			raise PeachException("Parser: Method attribute on an Action only available when type is 'call'.")
		
		if action.property != None and not action.type in ['setprop', 'getprop']:
			raise PeachException("Parser: Property attribute on an Action only available when type is 'setprop' or 'getprop'.")
		
		for child in node.childNodes:
			
			if child.nodeName == 'Param':
				if not action.type in ['call', 'setprop', 'getprop' ]:
					raise PeachException("Parser: Param is an invalid child of Action for this Action type")
				
				param = self.HandleActionParam(child, action)
				
				if action.has_key(param.name):
					raise PeachException("Error, duplicate Param name [%s] found in Action [%s]." % (param.name, action.name))
				
				action.append(param)
			
			elif child.nodeName == 'Template' or child.nodeName == 'DataModel':
				
				if action.type not in ['input', 'output', 'getprop']:
					raise PeachException("Parser: DataModel is an invalid child of Action for this Action type")
				
				#if not child.hasAttributeNS(None, 'ref'):
				#	raise PeachException("Parser: When DataModel is a child of Action it must have the ref attribute.")
				
				if action.template != None:
					raise PeachException("Error, action [%s] already has a DataModel specified." % action.name)

				obj = self.HandleTemplate(child, action)
				action.template = obj
				action.append(obj)
			
			elif child.nodeName == 'Data':
				
				if not (action.type == 'input' or action.type == 'output'):
					raise PeachException("Parser: Data is an invalid child of Action for this Action type")
				
				if action.data != None:
					raise PeachException("Error, action [%s] already has a Data element specified." % action.name)

				data = self.HandleData(child, action)
				action.data = data
			
			elif child.nodeName == 'Result':
				if not action.type in ['call']:
					raise PeachException("Parser: Result is an invalid child of Action of type 'call'.")
				
				result = self.HandleActionResult(child, action)
				
				if action.has_key(result.name):
					raise PeachException("Error, duplicate Result name [%s] found in Action [%s]." % (param.name, action.name))
				
				action.append(result)
					
			else:
				raise PeachException("Parser: State has unknown child [%s]" % PeachStr(child.nodeName))
		
		if action.template != None and action.data != None:
			cracker = DataCracker(action.getRoot())
			cracker.optmizeModelForCracking(action.template)
			
			# Somehow data not getting parent.  Force setting
			action.data.parent = action
			
			action.template.setDefaults(action.data, self.dontCrack, True)
		
		# Verify action has a DataModel if needed
		if action.type in ['input', 'output']:
			if action.template == None:
				raise PeachException("Parser: Action [%s] of type [%s] must have a DataModel child element." % (action.name, action.type))
		
		# Verify that setprop has a parameter
		if action.type == 'setprop':
			foundActionParam = False
			for c in action:
				if isinstance(c, ActionParam):
					foundActionParam = True
			
			if not foundActionParam:
				raise PeachException("Parser: Action [%s] of type [%s] must have a Param child element." % (action.name, action.type))
		
		return action
	
	def HandleActionParam(self, node, parent):
		
		if not node.hasAttributeNS(None, "type"):
			raise PeachException("Parser: ActionParam missing required type attribute")
		
		param = ActionParam(self._getAttribute(node, 'name'), parent)
		param.type = self._getAttribute(node, 'type')
		
		if not param.type in [ 'in', 'out', 'inout', 'return' ]:
			raise PeachException("Parser: ActionParam type attribute is not valid [%s].  Must be one of: in, out, or inout" % param.type)
		
		for child in node.childNodes:
			
			if child.nodeName == 'Template' or child.nodeName == 'DataModel':
				
				#if not child.hasAttributeNS(None, 'ref'):
				#	raise PeachException("Parser: When Template is a child of ActionParam it must have the ref attribute.")
				
				obj = self.HandleTemplate(child, param)
				param.template = obj
				param.append(obj)
			
			elif child.nodeName == 'Data':
				
				if not (param.type == 'in' or param.type == 'inout'):
					raise PeachException("Parser: Data is an invalid child of ActionParam for this type [%s]" % param.type)
				
				data = self.HandleData(child, param)
				data.parent = param
				param.data = data
				
			else:
				raise PeachException("Parser: ActionParam has unknown child [%s]" % PeachStr(child.nodeName))
		
		if param.template != None and param.data != None:
			cracker = DataCracker(param.template.getRoot())
			cracker.optmizeModelForCracking(param.template)
			param.template.setDefaults(param.data, self.dontCrack, True)
		
		# Verify param has data model
		if param.template == None:
			raise PeachException("Parser: Action Param must have DataModel as child element.")
		
		return param
	
	def HandleActionResult(self, node, parent):
		
		result = ActionResult(self._getAttribute(node, 'name'), parent)
		
		for child in node.childNodes:
			
			if child.nodeName == 'Template' or child.nodeName == 'DataModel':
				
				if not child.hasAttributeNS(None, 'ref'):
					raise PeachException("Parser: When Template is a child of ActionParam it must have the ref attribute.")
				
				obj = self.HandleTemplate(child, result)
				result.template = obj
				result.append(obj)
			
			else:
				raise PeachException("Parser: Action Result has unknown child [%s]" % PeachStr(child.nodeName))
		
		# Verify param has data model
		if result.template == None:
			raise PeachException("Parser: Action Result must have DataModel as child element.")
		
		return result
	
	def _HandleValueType(self, value, valueType):
		'''
		Handle types: string, literal, and hex
		'''
		
		if not value or not valueType:
			return None
		
		if valueType == 'literal':
			return PeachStr(eval(value))
		
		return PeachStr(value)
		
	def _HandleValueTypeString(self, value, valueType):
		'''
		Handle types: string, literal, and hex
		'''
		
		if not value or not valueType:
			return None
		
		if valueType == 'literal':
			return eval(value)
		
		return value
		
	
	def HandleParam(self, node, parent):
		param = Param(parent)
		
		if not node.hasAttributeNS(None, "name"):
			raise PeachException("Parser: Param element missing name attribute.  Parent is [%s]" % node.parentNode.nodeName)
		
		if not node.hasAttributeNS(None, "value"):
			raise PeachException("Parser: Param element missing value attribute")
		
		if not node.hasAttributeNS(None, "valueType"):
			valueType = "string"
		else:
			valueType = self._getAttribute(node, "valueType")
		
		name = self._getAttribute(node, "name")
		value = self._getAttribute(node, "value")
		
		if valueType == 'string':
			# create a literal out of a string value
			value = "'''" + value + "'''"
		
		elif valueType == 'hex':
			
			ret = ''
			
			valueLen = len(value)+1
			while valueLen > len(value):
				valueLen = len(value)
				
				for i in range(len(self._regsHex)):
					match = self._regsHex[i].search(value)
					if match != None:
						while match != None:
							ret += '\\x' + match.group(2)
							value = self._regsHex[i].sub('', value)
							match = self._regsHex[i].search(value)
						break
			
			value = "'" + ret + "'"
		
		param.name = name
		param.defaultValue = PeachStr(value)
		param.valueType = valueType
		
		return param
	
	def HandlePythonPath(self, node, parent):
		if not node.hasAttributeNS(None, 'path'):
			raise PeachException("PythonPath element did not have a path attribute!")
		
		p = PythonPath()
		p.name = self._getAttribute(node, 'path')
		
		return p
	
	def HandleImport(self, node, parent):
		# Import module
		
		if not node.hasAttributeNS(None, 'import'):
			raise PeachException("HandleImport: Import element did not have import attribute!")
		
		i = Element()
		i.elementType = 'import'
		i.importStr = self._getAttribute(node, 'import')
		if node.hasAttributeNS(None, 'from'):
			i.fromStr = self._getAttribute(node, 'from')
		else:
			i.fromStr = None
		
		return i
	
	def HandleHint(self, node, parent):
		
		if not node.hasAttributeNS(None, 'name') or not node.hasAttributeNS(None, 'value'):
			raise PeachException("Error: Found Hint element that didn't have both name and value attributes.")
		
		hint = Hint(self._getAttribute(node, 'name'), parent)
		hint.value = self._getAttribute(node, 'value')
		parent.hints.append(hint)
		
		return hint

# ###########################################################################

from Peach.Analyzers import *

#if sys.version.find("AMD64") == -1:
#	import psyco
#	psyco.bind(ParseTemplate)

# end
