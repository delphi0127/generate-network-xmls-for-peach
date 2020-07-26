#!/usr/bin/python

'''
Crack a group of files and determin if parts of the Peach pit have
not been filled in.  Mainly looking at Choice blocks to verify every
Choice has been hit.

TODO: Locate when relations!
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

import os, sys, glob, cPickle
sys.path.append("c:/peach")
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
	'''
	Implement a 4Suite URL resolver to find pits!
	'''
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

class Missing:
	'''
	Locate Choice's that have not been excersised between
	all of our sample files.
	'''
	
	def __init__(self):
		self.crackedModels = {}
		self.peach = None
		self.mainModel = None
		self.sampleFiles = []
		self.pitFilename = None
	
	def getSampleFiles(self, folder):
		'''
		Populate sampleFiles array.
		'''
		
		self.sampleFiles = glob.glob(folder)
	
	def parsePitFile(self, pitFilename, modelName):
		'''
		Parse PIT file and load model into self.mainModel
		'''
		
		print "[*] Parsing pit file:", pitFilename
		
		self.pitFilename = pitFilename
		p = parser.ParseTemplate()
		p.dontCrack = True
		self.peach = p.parse("file:"+pitFilename)
		
		for n in self.peach:
			if n.elementType == 'template' and n.name == modelName:
				self.mainModel = n
				break
		
		if self.mainModel == None:
			raise Exception("Could not locate model named [%s]" % modelName)
	
	def pickleModel(self, model):
		newModel = model.copy(None)
		newModel.parent = None
		
		self.pickleRemoveInstanceMethods(newModel)
		
		return cPickle.dumps(newModel)
	
	def unpickleModel(self, dump):
		model = cPickle.loads(dump)
		self.pickleAddInstanceMethods(model)
		
		return model
		
	def pickleAddInstanceMethods(self, model):
		'''
		Add back in the non-pickleable instancemethods.
		'''
		
		
		if model.elementType == 'block':
			model.toXml = new.instancemethod(BlockToXml, model, model.__class__)
		
		elif model.elementType == 'namespace':
			model.toXml = new.instancemethod(NamespaceToXml, model, model.__class__)
		
		for c in dir(model):
			if c == 'parent':
				continue
			
			obj = getattr(model, c)
			if isinstance(obj, Element):
				self.pickleAddInstanceMethods(obj)
		
		if isinstance(model, ElementWithChildren):
			for c in model:
				if isinstance(c, Element):
					self.pickleAddInstanceMethods(c)
	
	def pickleRemoveInstanceMethods(self, model):
		'''
		Remove any instance methods.
		'''
		
		
		if hasattr(model, "toXml") and (model.elementType == 'block' or model.elementType == 'namespace'):
			delattr(model, "toXml")
		
		for c in dir(model):
			if c == 'parent':
				continue
			
			obj = getattr(model, c)
			if isinstance(obj, Element):
				self.pickleRemoveInstanceMethods(obj)
		
		if isinstance(model, ElementWithChildren):
			for c in model:
				if isinstance(c, Element):
					self.pickleRemoveInstanceMethods(c)
	
	def crackAllSampleFiles(self):
		'''
		Crack sample files into self.crackedModels[file]
		'''
		
		for file in self.sampleFiles:
			
			statPeach = None
			try:
				statPeach = os.stat(file+".peach")
				statFile = os.stat(file)
				statPit = os.stat(self.pitFilename)
			except:
				pass
			
			if statPeach != None and statPeach.st_mtime > statFile.st_mtime and statPeach.st_mtime > statPit.st_mtime:
				# Load pre-parsed peach file
				print "[*] Loading model for: %s" % file
				
				fd = open(file+".peach", "rb+")
				data = fd.read()
				fd.close()
				
				model = self.unpickleModel(data)
				
			else:
				# Reparse file
				print "[*] Cracking file: %s" % file
				
				fd = open(file, "rb+")
				data = fd.read()
				fd.close()
				
				buff = PublisherBuffer(None, data)
				cracker = incoming.DataCracker(self.peach)
				cracker.optmizeModelForCracking(self.mainModel)
				cracker.haveAllData = True
				model = self.mainModel.copy(None)
				(rating, pos) = cracker.crackData(model, buff, "setDefaultValue")
				
				if rating > 2:
					raise Exception("Unable to crack file [%s], rating was [%d]" % (file, rating))
				
				# Pickle model
				fd = open(file + ".peach", "wb+")
				fd.write(self.pickleModel(model))
				fd.close()
			
			# Save model
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
	
	def locateChoices(self):
		self.choices = []
		for node in self.mainModel.getAllChildDataElements():
			if isinstance(node, Choice):
				self.choices.append(node)
	
	def getEveryOccurenceOf(self, fullName, model):
		'''
		Return every occurence of the element.
		'''
		
		names = fullName.split('.')
		if len(names) == 1:
			if model.name == names[0]:
				return [model]
			
			return [model[names[0]]]
		
		topName = names[-1]
		rootName = ".".join(names[0:-1])
		
		roots = self.getEveryOccurenceOf(rootName, model)
		occurs = []
		
		for root in roots:
			if root.has_key(topName):
				occurs.append(root[topName])
			
			elif root.has_key(topName+"-0"):
				obj = root[topName+"-0"]
				for i in range(obj.getArrayCount()):
					occurs.append(obj.getArrayElementAt(i))
		
		return occurs
	
	def checkChoices(self):
		
		# check each choice
		for choice in self.choices:
			fullName = choice.getFullDataName()
			foundChoices = []
			
			# find every choice selection
			for model in self.crackedModels.values():
				choices = self.getEveryOccurenceOf(fullName, model)
				if len(choices) == 0:
					print "[-] Warning can't locate [%s] in [%s]" % (fullName, model.name)
					continue
				
				for choice2 in choices:
					#print "Found: ", choice2.getFullDataName()
					foundChoices.append(choice2.currentElement.name)
			
			# now check the main
			for child in choice:
				if isinstance(child, DataElement):
					if child.name not in foundChoices:
						print "[!] Missing: %s" % child.getFullDataName()
						
		# done
	

print ""
print "] Peach Choice Coverage Check"
print "] Copyright (c) Michael Eddington"
print ""

if len(sys.argv) < 4:
	print '''
Syntax: missing.py MyPit.xml DataModelName samples\\*.png

This tool will crack every file provided into the specified
data model and then determin if any of the choice blocks
are not covered by the provided files.

'''
	sys.exit(0)

pit = sys.argv[1]
dataModel = sys.argv[2]
path = sys.argv[3]
	
c = Missing()
c.getSampleFiles(path)
c.parsePitFile(pit, dataModel)
c.crackAllSampleFiles()
c.locateChoices()
c.checkChoices()

print "[*] Done\n"

# end
