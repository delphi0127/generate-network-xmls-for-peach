'''
XML Analyzers

@author: Michael Eddington
@version: $Id$
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

# $Id$

import sys, os

from Peach.analyzer import *
from Peach.Engine.dom import *
from Peach.Engine.common import *

try:
	import Ft.Xml.Domlette
	from Ft.Xml.Catalog import GetDefaultCatalog
	from Ft.Xml.InputSource import InputSourceFactory
	from Ft.Lib.Resolvers import SchemeRegistryResolver
	from Ft.Lib import Uri
	from Ft.Xml import Parse
	from Ft.Xml.Sax import DomBuilder
	from Ft.Xml import Sax, CreateInputSource
	from Ft.Xml import EMPTY_NAMESPACE
	from Ft.Xml.Domlette import Print, PrettyPrint

except:
	raise PeachException("Error loading 4Suite XML library.  This library\ncan be installed from the dependencies folder or\ndownloaded from http://4suite.org/.\n\n")


class XmlAnalyzer(Analyzer):
	'''
	Produces data models or peach pits from XML documents.
	'''
	
	#: Does analyzer support asDataElement()
	supportDataElement = True
	#: Does analyzer support asCommandLine()
	supportCommandLine = True
	#: Does analyzer support asTopLevel()
	supportTopLevel = True
	
	def __init__(self):
		pass

	def asDataElement(self, parent, args, dataBuffer):
		'''
		Called when Analyzer is used in a data model.
		
		Should return a DataElement such as Block, Number or String.
		'''
		
		if len(dataBuffer) == 0:
			return
		
		dom = _Xml2Dom().xml2Dom(dataBuffer)
		
		# Replace parent with new dom
		
		dom.name = parent.name
		parentOfParent = parent.parent
		
		indx = parentOfParent.index(parent)
		del parentOfParent[parent.name]
		parentOfParent.insert(indx, dom)
		
		# now just cross our fingers :)
		
	
	def asCommandLine(self, args):
		'''
		Called when Analyzer is used from command line.  Analyzer
		should produce Peach PIT XML as output.
		'''
		
		try:
			inFile = args["xmlfile"]
			outFile = args["out"]
		except:
			raise PeachException("XmlAnalyzer requires two parameters, xmlfile and out.")
		
		xml = _Xml2Peach().xml2Peach("file:"+inFile)
		
		fd = open(outFile, "wb+")
		fd.write(xml)
		fd.close()
	
	def asTopLevel(self, peach, args):
		'''
		Called when Analyzer is used from top level.
		
		From the top level producing zero or more data models and
		state models is possible.
		'''
		raise Exception("asTopLevel not supported")


class _PeachResolver(SchemeRegistryResolver):
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

class _Xml2Peach(object):
	
	XmlContainer = """<?xml version="1.0" encoding="utf-8"?>
<Peach xmlns="http://phed.org/2008/Peach" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://phed.org/2008/Peach /peach/peach.xsd">
	
	<!-- Import defaults for Peach instance -->
	<Include ns="default" src="file:defaults.xml" />
	
	<DataModel name="TheDataModel">
%s
	</DataModel>
	
	<!-- TODO: Create state model -->
	<StateModel name="TheState" initialState="Initial">
		
		<State name="Initial">
			<Action type="output">
				<DataModel ref="TheDataModel" />
			</Action>
		</State>
		
	</StateModel>
	
	<!-- TODO: Configure agent/monitors
	<Agent name="LocalAgent" location="http://127.0.0.1:9000">
		<Monitor class="test.TestStopOnFirst" />
	</Agent>
	-->
	
	<Test name="TheTest">
		<!-- <Agent ref="LocalAgent"/> -->
		<StateModel ref="TheState"/>
		
		<!-- TODO: Complete publisher -->
		<Publisher class="stdout.Stdout" />
	</Test>
	
	<!-- Configure a single run -->
	<Run name="DefaultRun">
		
		<Test ref="TheTest" />
		
	</Run>
	
</Peach>
<!-- end -->
"""
	
	def xml2Peach(self, url):
		factory = InputSourceFactory(resolver=_PeachResolver(), catalog=GetDefaultCatalog())
		isrc = factory.fromUri(url)
		doc = Ft.Xml.Domlette.NonvalidatingReader.parse(isrc)
		
		peachDoc = Ft.Xml.Domlette.implementation.createDocument(EMPTY_NAMESPACE, None, None)
		child = doc.firstChild
		while(child.nodeName == "#comment"):
			child = child.nextSibling
			
		self.handleElement(child, peachDoc)
		
		# Get the string representation
		import cStringIO
		buff = cStringIO.StringIO()
		PrettyPrint(peachDoc.firstChild, stream=buff, encoding="utf8")
		value = buff.getvalue()
		buff.close()
		
		return self.XmlContainer % value
		
	def handleElement(self, node, parent):
		'''
		Handle an XML element, children and attributes.
		Returns an XmlElement object.
		'''
		
		if parent == None:
			return None
		
		doc = parent.ownerDocument
		if doc == None:
			doc = parent

		## Element
		
		element = doc.createElementNS(None, "XmlElement")
		element.setAttributeNS(None, "elementName", node.nodeName)
		parent.appendChild(element)
		
		if node.namespaceURI != None:
			element.setAttributeNS(None, "ns", node.namespaceURI)
		
		## Element attributes
		
		if node.attributes != None:
			for attrib in node.attributes:
				attribElement = self.handleAttribute(attrib, node.attributes[attrib], element)
				element.appendChild(attribElement)
		
		## Element children
		
		for child in node.childNodes:
			if child.nodeName == "#text":
				if len(child.nodeValue.strip('\n\r\t\x10 ')) > 0:
					# This is node's value!
					string = doc.createElementNS(None, "String")
					string.setAttributeNS(None, "value", child.nodeValue)
					string.setAttributeNS(None, "type", "utf8")
					element.appendChild(string)
			
			elif child.nodeName == "#comment":
				# xml comment
				pass
			else:
				self.handleElement(child, element)
		
		return element
	
	def handleAttribute(self, attrib, attribObj, parent):
		'''
		Handle an XML attribute.   Returns an XmlAttribute object.
		'''
		
		doc = parent.ownerDocument
		if doc == None:
			doc = parent
		
		## Attribute
		
		element = doc.createElementNS(None, "XmlAttribute")
		element.setAttributeNS(None, "attributeName", attribObj.name)
		
		if attrib[0] != None:
			element.setAttributeNS(None, "ns", attrib[0])
		
		## Attribute value
		
		string = doc.createElementNS(None, "String")
		string.setAttributeNS(None, "value", attribObj.value)
		string.setAttributeNS(None, "type", "utf8")
		element.appendChild(string)
		
		return element
	
class _Xml2Dom(object):
	'''
	Convert an XML Documnet into Peach DOM
	'''
	
	def xml2Dom(self, data):
		doc = Ft.Xml.Parse(data)
		child = doc.firstChild
		while(child.nodeName == "#comment"):
			child = child.nextSibling
			
		root = self.handleElement(child, None)
		
		return root
		
	def handleElement(self, node, parent):
		'''
		Handle an XML element, children and attributes.
		Returns an XmlElement object.
		'''
		
		doc = node.rootNode
		
		## Element
		
		element = XmlElement(None, parent)
		element.elementName = node.nodeName
		
		if node.namespaceURI != None:
			element.xmlNamespace = node.namespaceURI
		
		## Element attributes
		
		if node.attributes != None:
			for attrib in node.attributes:
				attribElement = self.handleAttribute(attrib, node.attributes[attrib], element)
				element.append(attribElement)
		
		## Element children
		
		for child in node.childNodes:
			if child.nodeName == "#text":
				if len(child.nodeValue.strip('\n\r\t\x10 ')) > 0:
					# This is node's value!
					string = String(None, element)
					string.defaultValue = child.nodeValue
					element.append(string)
					
					# Look like a number? then add correct hint :)
					try:
						i = long(string.defaultValue)
						hint = Hint("NumericalString", string)
						hint.value = "true"
						string.hints.append(hint)
					except:
						pass
				
			elif child.nodeName == "#comment":
				# xml comment
				pass
			
			else:
				childElement = self.handleElement(child, element)
				element.append(childElement)
		
		return element
	
	def handleAttribute(self, attrib, attribObj, parent):
		'''
		Handle an XML attribute.   Returns an XmlAttribute object.
		'''
		
		## Attribute
		
		element = XmlAttribute(None, parent)
		element.attributeName = attribObj.name
		
		if attrib[0] != None:
			element.xmlNamespace = attrib[0]
		
		## Attribute value
		
		string = String(None, element)
		string.defaultValue = attribObj.value
		element.append(string)
		
		return element
	

# end
