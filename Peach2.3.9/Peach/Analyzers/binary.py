'''
Analyzers that produce data models from Binary blobs

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

import sys, os, re, struct, traceback

sys.path.append("c:/peach")

from Peach.Engine.dom import *
from Peach.Engine.common import *
from Peach.analyzer import Analyzer

class _Node(object):
	def __init__(self, type, startPos, endPos, value):
		self.type = type
		self.value = value
		self.startPos = startPos
		self.endPos = endPos


class Binary(Analyzer):
	'''
	Analyzes binary blobs to build data models
	
	 1. Locate strings, char & wchar
	   a. Analyze string for XML
	   b. UTF8/UTF16 and byte order marks
	 2. Find string lengths (relations!) --> Would also give us endian
	 3. Compressed segments (zip, gzip)
	 
	 ?. Look for ASN.1 style data?
	 ?. Look for CRCs
	'''
	
	#: Does analyzer support asParser()
	supportParser = False
	#: Does analyzer support asDataElement()
	supportDataElement = True
	#: Does analyzer support asCommandLine()
	supportCommandLine = False
	#: Does analyzer support asTopLevel()
	supportTopLevel = True
	
	def __init__(self):
		pass
	
	def locateStrings(self, data):
		maxLooseStrings = 200
		cnt = 0
		
		strs = []
		
		cnt = 0
		for match in re.finditer(r"[\n\r\ta-zA-Z0-9,./<>\?;':\"\[\]\\\{\}|=\-+_\)\(*&^%$#@!~`]{4,}\0?", data):
			strs.append(_Node('str', match.start(), match.end(), match.group(0)))
			cnt+=1
			if cnt > maxLooseStrings:
				break
		
		if cnt < maxLooseStrings:
			return strs
		
		strs = []
		
		cnt = 0
		for match in re.finditer(r"[a-zA-Z0-9,./\?;':\"\\\-_&%$@!]{5,}\0?", data):
			strs.append(_Node('str', match.start(), match.end(), match.group(0)))
			cnt+=1
			if cnt > maxLooseStrings:
				break
		
		if cnt < maxLooseStrings:
			return strs
		
		strs = []
		
		cnt = 0
		for match in re.finditer(r"[a-zA-Z0-9,.?:\"&@!]{5,}\0?", data):
			strs.append(_Node('str', match.start(), match.end(), match.group(0)))
			cnt+=1
			if cnt > maxLooseStrings:
				break
		
		if cnt < maxLooseStrings:
			return strs
		
		strs = []
		
		cnt = 0
		for match in re.finditer(r"[a-zA-Z0-9.\"]{6,}\0?", data):
			strs.append(_Node('str', match.start(), match.end(), match.group(0)))
			cnt+=1
			if cnt > maxLooseStrings:
				break
		
		if cnt < maxLooseStrings:
			return strs

		strs = []
		
		cnt = 0
		for match in re.finditer(r"[a-zA-Z0-9.\"]{10,}\0?", data):
			strs.append(_Node('str', match.start(), match.end(), match.group(0)))
			cnt+=1
			if cnt > maxLooseStrings:
				break
		
		if cnt < maxLooseStrings:
			return strs
		
		return []
	
	def locateStringLengths(self, strs, data):
		lengths = {}
		
		for s in strs:
			lengthL16 = 0
			lengthL32 = 0
			lengthB16 = 0
			lengthB32 = 0
			
			length = len(s.value)
			try:
				lengthL16 = struct.pack("H", length)
				lengthB16 = struct.pack("!H", length)
			except:
				pass
			
			lengthL32 = struct.pack("I", length)
			lengthB32 = struct.pack("!I", length)
			
			first2 = data[s.startPos - 2:s.startPos]
			first4 = data[s.startPos - 4:s.startPos]
			
			# Always check larger # first in case 0x00AA :)
			if first4 == lengthL32:
				obj = _Node('len', s.startPos - 4, s.startPos, length)
				obj.endian = 'little'
				obj.lengthOf = s
				obj.size = 32
				lengths[s] = obj
			elif first4 == lengthB32:
				obj = _Node('len', s.startPos - 4, s.startPos, length)
				obj.endian = 'big'
				obj.lengthOf = s
				obj.size = 32
				lengths[s] = obj
			elif first2 == lengthL16:
				obj = _Node('len', s.startPos - 2, s.startPos, length)
				obj.endian = 'little'
				obj.lengthOf = s
				obj.size = 16
				lengths[s] = obj
			elif first2 == lengthB16:
				obj = _Node('len', s.startPos - 2, s.startPos, length)
				obj.endian = 'big'
				obj.lengthOf = s
				obj.size = 16
				lengths[s] = obj
		
		return lengths
	
	def locateCompressedSegments(self, data):
		pass

	def analyzeBlob(self, data):
		'''
		Will analyze a binary blob and return a Block
		data element containing the split up blob.
		'''
		
		# 1. First we locate strings
		strs = self.locateStrings(data)
		
		# 2. Now we check for lengths
		lengths = self.locateStringLengths(strs, data)
		
		# 3. Now we need to build up our DataElement DOM
		root = Block(None, None)
		pos = 0
		
		for s in strs:
			
			## Check and see if we need a Blob starter
			
			startPos = s.startPos
			if s in lengths:
				startPos = lengths[s].startPos
			
			if startPos > pos:
				# Need a Blob filler
				b = Blob(None, None)
				b.defaultValue = data[pos:startPos]
				
				root.append(b)
			
			## Now handle what about length?
			
			stringNode = String(None, None)
			numberNode = None
			
			if s in lengths:
				l = lengths[s]
				
				numberNode = Number(None, None)
				numberNode.size = l.size
				numberNode.endian = l.endian
				numberNode.defaultValue = str(l.value)
				root.append(numberNode)
				
				relation = Relation(None, None)
				relation.type = "size"
				relation.of = stringNode.name
				
				numberNode.relations.append(relation)
				
				relation = Relation(None, None)
				relation.type = "size"
				relation.From = numberNode.name
				
				stringNode.relations.append(relation)
			
			if s.value[-1] == "\0":
				stringNode.defaultValue = s.value[:-1]
				stringNode.nullTerminated = True
			
			else:
				stringNode.defaultValue = s.value
			
			root.append(stringNode)
			
			pos = s.endPos
		
		# Finally, we should see if we need a trailing blob...
		if pos < (len(data)-1):
			
			b = Blob(None, None)
			b.defaultValue = data[pos:]
			root.append(b)
		
		return root

	def asDataElement(self, parent, args, dataBuffer):
		'''
		Called when Analyzer is used in a data model.
		
		Should return a DataElement such as Block, Number or String.
		'''
		dom = self.analyzeBlob(dataBuffer)
		
		# Replace parent with new dom
		
		parentOfParent = parent.parent
		dom.name = parent.name
		
		indx = parentOfParent.index(parent)
		del parentOfParent[parent.name]
		parentOfParent.insert(indx, dom)
		
		# now just cross our fingers :)
	
	def asCommandLine(self, args):
		'''
		Called when Analyzer is used from command line.  Analyzer
		should produce Peach PIT XML as output.
		'''
		raise Exception("asCommandLine not supported")
	
	def asTopLevel(self, peach, args):
		'''
		Called when Analyzer is used from top level.
		
		From the top level producing zero or more data models and
		state models is possible.
		'''
		raise Exception("asTopLevel not supported")

try:
	from OleFileIO_PL import *
except:
	pass

class OleStructuredStorage(Analyzer):
	'''
	Builds out a data model based on OLE Structured Storage.
	'''
	
	#: Does analyzer support asParser()
	supportParser = False
	#: Does analyzer support asDataElement()
	supportDataElement = True
	#: Does analyzer support asCommandLine()
	supportCommandLine = False
	#: Does analyzer support asTopLevel()
	supportTopLevel = True
	
	def __init__(self):
		pass
	
	def asDataElement(self, parent, args, dataBuffer):
		'''
		Called when Analyzer is used in a data model.
		
		Should return a DataElement such as Block, Number or String.
		'''
		dom = self.handleOleDocument(dataBuffer)
		
		# Replace parent with new dom
		
		parentOfParent = parent.parent
		dom.name = parent.name
		
		DomPrint(0,dom)
		
		indx = parentOfParent.index(parent)
		del parentOfParent[parent.name]
		parentOfParent.insert(indx, dom)
		
		# now just cross our fingers :)
	
	def asCommandLine(self, args):
		'''
		Called when Analyzer is used from command line.  Analyzer
		should produce Peach PIT XML as output.
		'''
		raise Exception("asCommandLine not supported")
	
	## NOTES: Use Hint's to store OLE information needed to build doc
	##  This will save us from needed custom types!
	##
	##  <Hint name="OleRootEntry" value="GUID" />
	##  <Hint name="OleStorage" value="NAME" />
	##  <Hint name="OleStorageClsid" value="NAME" />
	##  <Hint name="OleStream" value="NAME" />
	##  <Hint name="OleStreamProperties" value="NAME" />
	##  <Hint name="OleStreamProperty" value="NAME" />
	##  <Hint name="OleStreamPropertyType" value="30" />
	##  <Hint name="OleStreamPropertyPid" value="1" />

	def asTopLevel(self, peach, args):
		'''
		Called when Analyzer is used from top level.
		
		From the top level producing zero or more data models and
		state models is possible.
		'''
		raise Exception("asTopLevel not supported")

	def handleOleDocument(self, fileName):
		
		ole = OleFileIO(fileName, raise_defects=DEFECT_INCORRECT)
		
		hintOleRootEntry = Hint("OleRootEntry", None)
		hintOleRootEntry.value = ole.root.name
		hintOleStorageClsid = Hint("OleStorageClsid", None)
		hintOleStorageClsid.value = ole.root.clsid
		
		root = Block(None, None)
		root.name = ole.root.name
		root.hints.append(hintOleRootEntry)
		root.hints.append(hintOleStorageClsid)
		
		# First make all the storage containers
		for streamname in ole.listdir():
			storages = streamname[:-1]
			
			parent = None
			curname = []
			
			for s in storages:
				curname.append(s)
				
				reprS = repr(s)
				
				if parent != None and parent.has_key(reprS):
					parent = parent[reprS]
					continue
				
				elif parent == None and root.has_key(reprS):
					parent = root[reprS]
					continue
				
				print "Creating Storage:", reprS
				
				obj = ole.find(curname)
				
				hintOleStorage = Hint("OleStorage", None)
				hintOleStorage.value = s
				
				block = Block(None, None)
				block.name = reprS
				block.hints.append(hintOleStorage)
				
				if obj.clsid:
					hintOleStorageClsid = Hint("OleStorageClsid", None)
					hintOleStorageClsid.value = obj.clsid
					block.hints.append(hintOleStorageClsid)
				
				if parent != None:
					parent.append(block)
				else:
					root.append(block)
				
				parent = block
		
		for streamname in ole.listdir():
			
			parent = root
			for s in streamname[:-1]:
				print parent.name
				parent = parent[repr(s)]
			
			if streamname[-1][0] == '\005':
				# Found properties
				obj = self.handleOleProperties(ole, streamname)
			
			else:
				obj = self.handleOleStream(ole, streamname)
			
			parent.append(obj)
		
		return root
	
	def handleOleProperties(self, ole, streamname):
		
		hintOleStreamProperties = Hint("OleStreamProperties", None)
		hintOleStreamProperties.value = streamname[-1]
		
		block = Block(None, None)
		block.hints.append(hintOleStreamProperties)
		
		props = ole.getpropertieswithtype(streamname)
		for k,v in props.items():
			
			hintOleStreamProperty = Hint("OleStreamProperty", None)
			hintOleStreamProperty.value = k
			hintOleStreamPropertyType = Hint("OleStreamPropertyType", None)
			hintOleStreamPropertyType.value = v[1]
			
			blob = Blob(None, None)
			blob.defaultValue = str(v[0])
			blob.hints.append(hintOleStreamProperty)
			blob.hints.append(hintOleStreamPropertyType)
			
			block.append(blob)
		
		return block
	
	def handleOleStorage(self, ole, streamname):
		
		hintOleStorage = Hint("OleStorage", None)
		hintOleStorage.value = streamname[-1]
		
		block = Block(None, None)
		block.hints.append(hintOleStorage)
		
		return block
	
	def handleOleStream(self, ole, streamname):
		
		hintOleStream = Hint("OleStream", None)
		hintOleStream.value = streamname[-1]
		
		blob = Blob(None, None)
		blob.hints.append(hintOleStream)
		
		return blob

if __name__ == "__main__":

	import Ft.Xml.Domlette
	from Ft.Xml.Domlette import Print, PrettyPrint
	
	fd = open("sample.bin", "rb+")
	data = fd.read()
	fd.close()
	
	b = Binary()
	dom = b.analyzeBlob(data)
	data2 = dom.getValue()
	
	if data2 == data:
		print "THEY MATCH"
	else:
		print repr(data2)
		print repr(data)
	
	dict = {}
	doc  = Ft.Xml.Domlette.NonvalidatingReader.parseString("<Peach/>", "http://phed.org")
	xml = dom.toXmlDom(doc.rootNode.firstChild, dict)
	PrettyPrint(doc, asHtml=1)

# end
