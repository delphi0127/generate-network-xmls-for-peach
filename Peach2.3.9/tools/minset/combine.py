#!/usr/bin/python

'''
Crack a group of files and combine the data models.  Ultimately 
we want to use this information to allow for better mutations
such as understanding each portion of a choice even though only
one is used at once.

Ultimatly this code will have to be integrated into the main Peach
tree to be of use.  Probably in the 2.3 branch of Peach.

-- OR -- 

Use 4Suite to read in, modify and write out XML file with defaults
added!

--------

Several changes will be needed to support these changes such as:

 1. Hanging on to the other choices in a <Choice> block
 2. Having an array of known values for elements (??)
 3. ...

Another option for use is to create a pickled file of defaults.  In-
fact, for known slow initial crackings we could save the cracked
information for loading.  Perhaps mypit.xml.peach could be the pre-
cracked file?
'''

#
# Copyright (c) 2008 Michael Eddington
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

import os, sys, glob
sys.path.append("../..")
sys.path.append(os.getcwd() + "\\..\\..\\")

try:
	import Ft
	import Ft.Xml.Domlette
	from Ft.Xml.Catalog import GetDefaultCatalog
	from Ft.Xml.InputSource import InputSourceFactory
	from Ft.Lib.Resolvers import SchemeRegistryResolver
	from Ft.Lib import Uri
	from Ft.Xml import Parse
	from Ft.Xml.Sax import DomBuilder
	from Ft.Xml import Sax, CreateInputSource
except:
	print "\nError loading 4Suite XML library.  This library"
	print "can be installed from the dependencies folder or"
	print "downloaded from http://4suite.org/.\n\n"
	sys.exit(0)

from Peach.Engine import parser, engine, incoming, dom
from Peach.Engine.dom import *
import Peach


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

class Combine:
	
	def __init__(self):
		self.crackedModels = {}
		self.peach = None
		self.mainModel = None
		self.sampleFiles = []
	
	def getSampleFiles(self, folder):
		'''
		Populate sampleFiles array.
		'''
		
		self.sampleFiles = glob.glob(folder)
		#for f in os.listdir(folder):
			#f = os.path.join(folder, f)
			##print "[*] Found sample file:",f
			#self.sampleFiles.append(f)
	
	def parsePitFile(self, pitFilename, modelName):
		
		print "[*] Parsing pit file:", pitFilename
		
		p = parser.ParseTemplate()
		p.dontCrack = True
		self.peach = p.parse("file:"+pitFilename)
		
		for n in self.peach:
			if n.elementType == 'template' and n.name == modelName:
				self.mainModel = n
				break
		
		if self.mainModel == None:
			raise Exception("Could not locate model named [%s]" % modelName)
	
	def crackAllSampleFiles(self):
		
		for file in self.sampleFiles:
			
			print "[*] Cracking file: %s" % file
			
			fd = open(file, "rb+")
			data = fd.read()
			fd.close()
			
			cracker = incoming.DataCracker(self.peach)
			cracker.haveAllData = True
			model = self.mainModel.copy(None)
			(rating, pos) = cracker.crackData(model, data, "setDefaultValue")
			
			if rating > 2:
				raise Exception("Unable to crack file [%s], rating was [%d]" % (file, rating))
			
			self.crackedModels[file] = model

	def setDefaultsOnPit(self, pitFilename):
		'''
		Create a new PIT file that has defaults set based on all sample
		files parsed.
		'''
		
		# Load pit file
		
		uri = "file:"+pitFilename
		factory = InputSourceFactory(resolver=PeachResolver(), catalog=GetDefaultCatalog())
		isrc = factory.fromUri(uri)
		doc = Ft.Xml.Domlette.NonvalidatingReader.parse(isrc)
		
		# Combine data into pit file
		
		print "[*] Setting defaults on XML document..."
		for k in self.crackedModels:
			self.setXmlFromPeach(doc, self.crackedModels[k])
		
		# Output XML file
		
		print "[*] Writing combined PIT file to [%s]" % pitFilename + ".defaults"
		fd = open(pitFilename + ".defaults", "wb+")
		Ft.Xml.Domlette.PrettyPrint(doc, stream=fd)
		fd.close()
	
	def setXmlFromPeach(self, doc, dataModel):
		'''
		Set all default values from a data model to XML document.
		'''
		
		for dataElement in dataModel.getAllChildDataElements():
			self.setXmlField(doc, dataElement)
	
	def toHexString(self, data):
		'''
		Convert binary data into a hex string.
		'''
		
		tmp = ''
		ret = ''

		for c in data:
			h = hex(ord(c))[2:]
			
			if len(h) == 2:
				tmp += h 
			else:
				tmp += "0%s" % h
			
		return tmp

	def setXmlField(self, doc, dataElement):
		'''
		Set a single field in an xml document from data model.
		'''
		
		# 1. Get full name of data element
		name = dataElement.getFullDataName()
		
		# 2. Convert to xpath
		
		xpathName = "/"
		#xpathName=""
		for n in name.split("."):
			xpathName += "/*[@name='%s']" % n
		print "Xpath: ", xpathName
		
		# 3. Find XML node
		
		nodes = doc.xpath(xpathName)
		if nodes == None or len(nodes) == 0:
			raise Exception("Failed to find element for xpath [%s] on name [%s]" % (xpathName, dataElement.getFullDataName()))
		if len(nodes) > 1:
			raise Exception("Found to many results for xpath [%s] on name [%s]" % (xpathName, dataElement.getFullDataName()))
		
		# 4. Set default value
		
		if dataElement.elementType == 'blob':
			nodes[0].setAttributeNS(None, "valueType", "hex")
			nodes[0].setAttributeNS(None, "value", self.toHexString(dataElement.getInternalValue()))
		else:
			nodes[0].setAttributeNS(None, "value", dataElement.getInternalValue())
		

print ""
print "] Peach Sample File Combiner"
print "] Copyright (c) Michael Eddington"
print ""

c = Combine()
c.getSampleFiles("samples\\*2.png")
c.parsePitFile("png.xml", "Png")
c.crackAllSampleFiles()
c.setDefaultsOnPit("png.xml")

print "[*] Done\n"

# end
