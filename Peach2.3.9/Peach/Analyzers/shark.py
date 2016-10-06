'''
Wireshark Analyzer(s)

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

from Peach.analyzer import *
from Peach.Engine.common import *

class WireSharkAnalyzer(Analyzer):
	'''
	Analyzers produce data and state models.  Examples of analyzers would be
	the parsing of Peach PIT XML files, tokenizing a string, building a data
	model based on XML file, etc.
	'''
	
	#: Does analyzer support asCommandLine()
	supportCommandLine = True
	
	def asParser(self, uri):
		'''
		Called when Analyzer is used as default PIT parser.
		
		Should produce a Peach DOM.
		'''
		raise Exception("asParser not supported")

	def asDataElement(self, parent, args, dataBuffer):
		'''
		Called when Analyzer is used in a data model.
		
		Should return a DataElement such as Block, Number or String.
		'''
		raise Exception("asDataElement not supported")
	
	def asCommandLine(self, args):
		'''
		Called when Analyzer is used from command line.  Analyzer
		should produce Peach PIT XML as output.
		'''
		
		inFile = args["in"]
		if args.has_key("proto"):
			proto = args["proto"]
		else:
			proto = None
		
		if args.has_key("out"):
			outFile = args["out"]
		else:
			outFile = None
		
		xml = DoTheShark(inFile, proto)
		
		if outFile != None:
			fd = open(outFile, "wb+")
			fd.write(xml)
			fd.close()
		else:
			print xml
	
	def asTopLevel(self, peach, args):
		'''
		Called when Analyzer is used from top level.
		
		From the top level producing zero or more data models and
		state models is possible.
		'''
		raise Exception("asTopLevel not supported")
	
import sys, struct, re
from Ft.Xml import Parse

def debug(str):
	sys.stderr.write("debug: %s\n" % str)

#pdml/packet/proto
# method

# 1. Check for children, if we have them make block and recurse
# 2. Look for value show attribute and see if it contains a sub portion of the
#    data (treat this different)
# 3. Look for items labled "len" or "length" and try and match them up
# 4. Optionally look at RFC's and try and match things up

class PeachShark:
	
	def __init__(self):
		self._currentPos = 0
		self._regexIp = re.compile("^\d+\.\d+\.\d+\.\d+$")
		self._regexFlagBit1 = re.compile("^(\.*)(\d+)(\.*)")
		self._relations = {}
		self._findStack = []
		self._templates = []
	
	def inStr(self, str, values):
		str = str.lower()
		for value in values:
			if str.find(value) > -1:
				#debug("found str")
				return True
		
		#debug("No: %s" % str)
		return False
	
	
	def findSizeRelation(self, sizeNode, node):
		# We know two things:
		#
		# 1. Sizes always come first
		# 2. It will be the size of something :P
		#
		
		# Prevent infinit looping
		if node in self._findStack:
			return None
		self._findStack.append(node)
		
		size = self.findSizeGetSize(sizeNode)
		
		# Search from us forward
		sibling = sizeNode.nextSibling
		while sibling != None:
			checkSize = self._getNodeSize(sibling)
			
			if checkSize == size:
				return sibling
			
			sibling = sibling.nextSibling
		
		# That didn't work look from parent
		for child in node.childNodes:
			if child != sizeNode:
				checkSize = self._getNodeSize(child)
				if checkSize == size:
					return child
				
				ret = self.findSizeRelation(sizeNode, child)
				if ret != None:
					return ret
		
		# Search from parent forward
		sibling = node.nextSibling
		while sibling != None:
			if not sibling.hasAttributeNS(None, 'size'):
				sibling = sibling.nextSibling
				continue
			
			checkSize = int(sibling.getAttributeNS(None, 'size'))
			
			if checkSize == size:
				return sibling
			
			ret = self.findSizeRelation(sizeNode, sibling)
			if ret != None:
				return ret
			
			sibling = sibling.nextSibling
		
		# !!!TODO!!! Sometimes length can indicate the rest of our siblings
		# but they may not be in a block of there own.
		#  -> Detect
		#  -> Force into a bock
		#
		#sibling = node.previousSibling
		#while sibling != None:
		#	sizeUptoMe += int(sibling.getAttributeNS(None, 'size'))
		#	sibling = sibling.previousSibling
		#
		## This is good, but not what we want!
		#if (parentSize - sizeUptoMe) == size:
		#	return True
		#else:
		#	debug("Nope: ParentSize: %d - SizeUptoMe: %d -- Size: %d" % (parentSize, sizeUptoMe, size))
		
		return None
	
	def findSizes(self, nodes):
		'''
		Find nodes that could be sizes or lengths.
		'''
		
		if nodes == None:
			return []
		
		findValues = ["length", "size"]
		sizeNodes = []
		
		for node in nodes:
			if node == None:
				continue
			
			name = node.getAttributeNS(None, 'name')
			show = node.getAttributeNS(None, 'show')
			showName = node.getAttributeNS(None, 'showname')
			
			if self.inStr(show, findValues) or self.inStr(showName, findValues) or self.inStr(name, findValues):
				#debug("findSizes(): Found size: %s:%s" % (node.nodeName, name))
				sizeNodes.append(node)
			
			for n in self.findSizes(node.childNodes):
				sizeNodes.append(n)
		
		return sizeNodes
	
	def findSizeGetSize(self, node):
		'''
		Take a size/length node and figure out it's value.
		'''
		
		ret = None
		if node.hasAttributeNS(None, 'show') and len(node.getAttributeNS(None, 'show')) > 0:
			try:
				return int(node.getAttributeNS(None, 'show'))
			except:
				pass
		
		if node.hasAttributeNS(None, 'value') and len(node.getAttributeNS(None, 'value')) > 0:
			try:
				return int(node.getAttributeNS(None, 'value'), 16)
			except:
				pass
			
		try:
			return int(re.compile(r"(\d+)").search(node.getAttributeNS(None, 'show')).group(1))
			
		except:
			pass
		
		debug(str("Failed on %s:%s" % (node.getAttributeNS(None, 'name'), node.nodeName)))
		debug(str("Show: " + node.getAttributeNS(None, 'show')))
		debug(str("Value: "+ node.getAttributeNS(None, 'value')))
		raise Exception("OMG!!")
	
	
	def findSizeRelationCheckSelf(self, node):
		'''
		Check if parent - me + prior siblings == size
		'''
		
		parentSize = self._getNodeSize(node.parentNode)
		sizeUptoMe = self._getNodeSize(node)
		size = self.findSizeGetSize(node)
		#debug("%d:%d" % (parentSize,size))
		
		# If our parent is the size we are indicating
		# then return True!
		if parentSize == size:
			return True
		
		return False
	
	def findSizeRelations(self, nodes):
		'''
		Find and resolve size relations.
		'''
		
		debug("Finding relations: " + nodes[0].nodeName)
		if nodes[0].nodeName == 'proto':
			parentNode = nodes[0]
		else:
			parentNode = nodes[0].parentNode
		
		for node in self.findSizes(nodes):
			#debug("findSizeRelations()... %s:%s" % (node.nodeName, node.getAttributeNS(None, 'name')))
			
			if self.findSizeRelationCheckSelf(node):
				debug("findSizeRelations: Found relation to parent: %s and %s" % (node.getAttributeNS(None, 'name'), node.parentNode.getAttributeNS(None, 'name')))
				self._relations[node] = node.parentNode
			
			else:
				ret = self.findSizeRelation(node, parentNode)
				if ret != None:
					debug("findSizeRelations: Found relation: %s and %s" % (node.getAttributeNS(None, 'name'), ret.getAttributeNS(None, 'name')))
					self._relations[node] = ret
		
	
	def removeTextNodes(self, node):
		
		for child in node.childNodes:
			if child.nodeName == '#text':
				node.removeChild(child)
			else:
				self.removeTextNodes(child)

	def htmlEncode(self, strInput, default=''):
		
		if strInput == None or len(strInput) == 0:
			strInput = default
			
			if strInput == None or len(strInput) == 0:
				return ''
		
		# Allow: a-z A-Z 0-9 SPACE , .
		# Allow (dec): 97-122 65-90 48-57 32 44 46
		
		out = ''
		for char in strInput:
			c = ord(char)
			if ((c >= 97 and c <= 122) or
				(c >= 65 and c <= 90 ) or
				(c >= 48 and c <= 57 ) or
				c == 32 or c == 44 or c == 46):
				out += char
			else:
				out += "&#%d;" % c
		
		return out
	
	def getNodeName(self, node):
		'''
		Check for name and show attributes.  Figureout a possible name
		for this node.
		'''
		
		if node.hasAttributeNS(None, 'name'):
			name = node.getAttributeNS(None, 'name')
			
			if len(name.strip()) < 1:
				return None
			
			# Sounds good on paper, but causes problems
			#try:
			#	name = name[name.rindex('.')+1:]
			#except:
			#	pass
			
			return name.replace(' ', '_').replace('.', '_')
		
		return None
	
	def _getNodeSize(self, node):
		if not node.hasAttributeNS(None, 'size'):
			size = 0
			
			for child in node.childNodes:
				if child.hasAttributeNS(None, "size"):
					size += int(child.getAttributeNS(None, 'size'))
		else:
			size = int(node.getAttributeNS(None, 'size'))
		
		return size
	
	def _getNodePosition(self, node):
		if not node.hasAttributeNS(None, "pos"):
			pos = 0
			
			for child in node.childNodes:
				if child.hasAttributeNS(None, "pos"):
					pos = int(child.getAttributeNS(None, 'pos'))
					break
			
		else:
			pos = int(node.getAttributeNS(None, 'pos'))
		
		return pos
		
	def peachNode(self, node, tabCount, size, parent):
		
		if node.nodeName == '#text':
			return '', 0, 0
		
		tabs = '\t' * tabCount
		name = node.getAttributeNS(None, 'name')
		show = node.getAttributeNS(None, 'show')
		showName = node.getAttributeNS(None, 'showname')
		size = self._getNodeSize(node)
		pos = self._getNodePosition(node)
		
		ret = ''
		nodeName = self.getNodeName(node)
		if nodeName != None:
			nodeName = 'name="%s"' % nodeName
		else:
			nodeName = ''
		
		debug("peachNode: " + name)
		
		# This should be prior sibling, not parent!!
		if parent != None:
			parentPos = self._getNodePosition(parent)
			parentSize = self._getNodeSize(parent)
		else:
			parentPos = -1
			parentSize = -1
		
		self._currentPos = pos
		
		if size == 0:
			#print "Size == 0: ", node.getAttributeNS(None, 'size')
			return '', 0, 0
		
		if tabCount == 1:
			# Do this just once
			self.findSizeRelations([node])
			
			if name.find('-'):
				newName = ''
				for n in name.split('-'):
					newName += n[:1].upper() + n[1:]
				name = newName
			
			self._groupName = name[:1].upper() + name[1:]
			self._genName = name[:1].upper() + name[1:]
			self._templates.append(self._genName)
			
			name = node.getAttributeNS(None, 'name')
		
		#if len(node.childNodes) > 0 and not (self._getNodeSize(node.childNodes[0]) == size and self._getNodePosition(node.childNodes[0]) == pos):
		if len(node.childNodes) > 0:
			
			curPos = pos
			sizeOfChildren = 0
			
			if tabCount == 1:
				if len(showName) > 1: ret += tabs + '<!-- %s -->\n' % showName
				ret += tabs + '<DataModel name="%s">\n' % self._genName
			else:
				ret += tabs + '<Block %s>\n' % nodeName
			
			for child in node.childNodes:
				
				if not child.hasAttributeNS(None, "value"):
					continue
				
				sibling = child.nextSibling
				if sibling != None:
					siblingSize = self._getNodeSize(sibling)
					siblingPos = self._getNodePosition(sibling)
					childSize = self._getNodeSize(child)
					childPos = self._getNodePosition(child)
					
					if siblingPos == childPos and siblingSize < childSize and sibling.hasAttributeNS(None, "value"):
						debug("Skipping " + child.getAttributeNS(None, 'name') + " same as " + sibling.getAttributeNS(None, "name"))
						ret += tabs + "\t<!-- Skipping %s, same as following fields -->\n" % child.getAttributeNS(None, 'name')
						continue
				
				childShow = child.getAttributeNS(None, 'show')
				
				#print "Child: %s" % childShow
				
				childRet, childSize, childPos = self.peachNode(child, tabCount + 1, size, node)
				
				childPos = int(childPos)
				childSize = int(childSize)
				
				#print "Child: %s, %d, %d" % (childShow, childPos, childSize)
				
				if childSize == 0:
					if len(childRet) > 0:
						ret += childRet
					continue
				
				if int(childPos) == pos + int(sizeOfChildren):
					ret += childRet
					
				else:
					valueHex = node.getAttributeNS(None, 'value')
					value = self.hex2bin(valueHex)
					
					# Locate "extra" bits not covered by children and
					# add them in.  Maybe we should fuzz this too?
					if curPos < childPos:
						if len(valueHex) >= (childPos-pos)*2:
							ret += tabs + "\t<!-- Found some extra bits... -->\n"
							ret += tabs + "\t<Blob %s valueType=\"hex\" value=\"%s\" />\n" % (nodeName, valueHex[(curPos-pos)*2:(childPos-pos)*2])
						else:
							ret += tabs + "\t<!-- Found some extra bits, guessing they are z3r0 -->\n"
							ret += tabs + "\t<Blob %s valueType=\"hex\" value=\"%s\" />\n\n"  % (nodeName, ('00'*((childPos-pos) - (curPos-pos))))
					
					ret += childRet
				
				sizeOfChildren += childSize
				curPos = childPos + childSize
			
			#if sizeOfChildren != size:
			#	raise Exception("Size not match %d != %d" % (size, sizeOfChildren))
			
			
			# Dunno if we need this anymore
			if tabCount == 1:
				name = self._genName[3:]
				ret += tabs + '</DataModel>\n'
			else:
				ret += tabs + '</Block>\n'
			
		else:
			
			type = self.figureType(node)
			valueHex = node.getAttributeNS(None, 'value')
			show = node.getAttributeNS(None, 'show')
			showName = node.getAttributeNS(None, 'showname')
			if len(showName) < 1:
				showName = show
			value = self.hex2bin(valueHex)
			
			if type != 'bit_flag':
				if node.previousSibling != None:
					previousSiblingPos = self._getNodePosition(node.previousSibling)
					previousSiblingSize = self._getNodeSize(node.previousSibling)
					
					if pos == previousSiblingPos and size == previousSiblingSize:
						debug("node same position and size of previousSibling")
						return tabs + "<!-- *** Skipping %s, same position and size of previousSibling *** -->\n\n" % node.getAttributeNS(None, 'name'), 0, 0
						#return '', 0, 0
			
			#ret += " [%s] " % type
			
			if len(showName) > 0:
				ret += tabs + '<!-- %s -->\n' % showName
			
			if type.find('str') > -1:
				# TODO: We should take into account that this string
				#       may be fixed in size as well as different lengths.
				
				if len(valueHex) == size*2:
					str = 'valueType="hex" value="%s"' % valueHex
				else:
					str = 'value="%s"' % value
				
				if type == 'str':
					# regular string
					ret += tabs + '<String %s %s' % (nodeName, str)
					if self._relations.has_key(node):
						of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
						ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</String>\n'
					else:
						ret += ' />\n'
				
				elif type == 'p_str':
					# Padded string
					ret += tabs + '<String %s %s length="%d"' % (nodeName, str, size)
					if self._relations.has_key(node):
						of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
						ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</String>\n'
					else:
						ret += ' />\n'
				
				elif type == 'w_str':
					# wchar string
					ret += tabs + '<String %s type="wchar" %s' % (nodeName, str)
					if self._relations.has_key(node):
						of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
						ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</String>\n'
					else:
						ret += ' />\n'
				
				elif type == 'p_w_str':
					# padded wchar string
					ret += tabs + '<String %s type="wchar" length="%d" %s' % (nodeName, size/2, str)
					if self._relations.has_key(node):
						of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
						ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</String>\n'
					else:
						ret += ' />\n'
			
			elif type == 'byte' or type == 'uint8':
				ret += tabs + '<Number %s size="8" valueType="hex" value="%s" signed="false"' % (nodeName, valueHex)
				if self._relations.has_key(node):
					of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
					ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</Number>\n'
				else:
					ret += ' />\n'
			
			elif type == 'int16':
				ret += tabs + ('<Number %s size="16" valueType="hex" value="%s" signed="true"' % (nodeName, valueHex))
				if self._relations.has_key(node):
					of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
					ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</Number>\n'
				else:
					ret += ' />\n'

			elif type == 'uint16':
				ret += tabs + ('<Number %s size="16" valueType="hex" value="%s" signed="false"' % (nodeName, valueHex))
				if self._relations.has_key(node):
					of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
					ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</Number>\n'
				else:
					ret += ' />\n'

			elif type == 'n_int16':
				ret += tabs + ('<Number %s size="16" valueType="hex" value="%s" signed="true" endian="big"' % (nodeName, valueHex))
				if self._relations.has_key(node):
					of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
					ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</Number>\n'
				else:
					ret += ' />\n'

			elif type == 'n_uint16':
				ret += tabs + ('<Number %s size="16" valueType="hex" value="%s" signed="false" endian="big"' % (nodeName, valueHex))
				if self._relations.has_key(node):
					of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
					ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</Number>\n'
				else:
					ret += ' />\n'
			

			elif type == 'int32':
				ret += tabs + ('<Number %s size="32" valueType="hex" value="%s" signed="true"' % (nodeName, valueHex))
				if self._relations.has_key(node):
					of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
					ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</Number>\n'
				else:
					ret += ' />\n'
			elif type == 'uint32':
				ret += tabs + ('<Number %s size="32" valueType="hex" value="%s" signed="false"' % (nodeName, valueHex))
				if self._relations.has_key(node):
					of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
					ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</Number>\n'
				else:
					ret += ' />\n'
			elif type == 'n_int32':
				ret += tabs + ('<Number %s size="32" valueType="hex" value="%s" signed="true" endian="big"' % (nodeName, valueHex))
				if self._relations.has_key(node):
					of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
					ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</Number>\n'
				else:
					ret += ' />\n'
			elif type == 'n_uint32':
				ret += tabs + ('<Number %s size="32" valueType="hex" value="%s" signed="false" endian="big"' % (nodeName, valueHex))
				if self._relations.has_key(node):
					of = self._relations[node].getAttributeNS(None, 'name').replace('.', '_')
					ret += '>\n' + tabs + '\t<Relation type="size" of="'+of+'" />\n'+tabs+'</Number>\n'
				else:
					ret += ' />\n'
			
			elif type == 'blob':
				ret += tabs + '<Blob %s valueType="hex" value="%s" />\n' % (nodeName, valueHex)
			
			elif type == 'ip':
				#ret += tabs + "WithDefault(%s.addNewGroup(), '%s', BadIpAddress()).setTransformer(Ipv4StringToOctet()),\n" % ( self._groupName, show )
				ret += tabs + "<!-- TODO: Handle IP Address Better! -->\n"
				ret += tabs + '<String %s value="%s">\n' % (nodeName, show)
				ret += tabs + '\t<Transformer class="encode.Ipv4StringToOctet" />\n'
				ret += tabs + '</String>\n'
				#raise Exception("TODO")
			
			elif type == 'n_ip':
				#ret += tabs + "WithDefault(%s.addNewGroup(), '%s', BadIpAddress()).setTransformer(Ipv4StringToNetworkOctet()),\n" % ( self._groupName, show )
				ret += tabs + "<!-- TODO: Handle IP Address Better! -->\n"
				ret += tabs + '<String %s value="%s">\n' % (nodeName, show)
				ret += tabs + '\t<Transformer class="encode.Ipv4StringToNetworkOctet" />\n'
				ret += tabs + '</String>\n'
				#raise Exception("TODO")
			
			elif type == 'bit_flag':
				# TODO: Handle flags!
				
				if node.previousSibling == None:
					# First flag, lets do it!
					
					nodeNames = []
					offsets = []
					bits = []
					shownames = []
					length = 0
					
					offset, bit = self.getFlagBits(node)
					length += bit
					
					offsets.append(offset)
					bits.append(bit)
					shownames.append(showName)
					
					nodeName = self.getNodeName(node)
					if nodeName != None:
						nodeNames.append('name="%s"' % nodeName)
					else:
						nodeNames.append('')
					
					sibling = node.nextSibling
					while sibling != None:
						offset, bit = self.getFlagBits(sibling)
						
						length += bit
						
						offsets.append(offset)
						bits.append(bit)
						shownames.append(sibling.getAttributeNS(None, 'showname'))
						
						nodeName = self.getNodeName(sibling)
						if nodeName != None:
							nodeNames.append('name="%s"' % nodeName)
						else:
							nodeNames.append('')
						
						sibling = sibling.nextSibling
					
					# Now output Flags generator
					
					# make sure length is multiple of 2
					while length % 2 != 0:
						length += 1
					
					parentName = self.getNodeName(node.parentNode)
					if parentName != None:
						ret += tabs + '<Flags name="%s" size="%d">\n' % (parentName, length)
					else:
						ret += tabs + '<Flags size="%d">\n' % length
					
					for i in range(len(offsets)):
						ret += tabs + '\t<Flag %s position="%d" size="%d" />\n' % (nodeNames[i], offsets[i], bits[i])
					
					ret += tabs + "</Flags>\n"
					
			else:
				raise Exception("Unknown type: %s" % type)
		
		return ret + '\n', size, pos
	
	def hex2bin(self, h):
		'''
		Convert hex string to binary string
		'''
		ret = ''
		for cnt in range(0, len(h), 2):
			ret += chr(int(h[cnt:cnt+2],16))
		
		return ret
	
	def isWideString(self, str):
		'''
		Is this a wchar string?
		'''
		
		# Wide chars should always have even string
		# length
		if len(str) < 4 or len(str) % 2 != 0:
			return False
		
		for i in range(0, len(str), 2):
			c = str[i]
			c2 = str[i+1]
			
			# Assume we don't actually have characters that
			# require two bytes to display.  So second byte
			# should always be NULL
			if c2 != '\0':
				return False
			
			o = ord(c)
			if o < 32 or o > 126:
				if c == '\n' or c == '\r' or c == '\t':
					continue
				
				return False
		
		return True
	
	def isPaddedWideString(self, str):
		'''
		Is this a wchar string with nulls at the end?
		'''
		
		# Wide chars should always have even string
		# length
		if len(str) < 4 or len(str) % 2 != 0:
			return False
		
		if str[-1] != '\0' or str[-2] != '\0':
			return False
		
		for i in range(0, len(str), 2):
			c = str[i]
			c2 = str[i+1]
			
			# Assume we don't actually have characters that
			# require two bytes to display.  So second byte
			# should always be NULL
			if c2 != '\0':
				return False
			
			o = ord(c)
			if o < 32 or o > 126:
				if c == '\n' or c == '\r' or c == '\t' or c == '\0':
					continue
				
				return False
		
		return True
	
	def isString(self, str):
		'''
		Is this a char string?
		'''
		
		if len(str) < 3:
			return False
		
		for c in str:
			o = ord(c)
			if o < 32 or o > 126:
				if c == '\n' or c == '\r' or c == '\t':
					continue
				
				return False
		
		#debug("isString('%s'): True" % str)
		
		return True

	def isPaddedString(self, str):
		'''
		Is this a char string with nulls at the end?
		'''
		
		if len(str) < 3:
			#debug("to small")
			return False
		
		if str[-1] != '\0':
			#debug("no null term")
			return False
		
		for c in str:
			o = ord(c)
			if o < 32 or o > 126:
				if c == '\n' or c == '\r' or c == '\t' or c == '\0':
					continue
				
				debug("odd char [%d]" % o)
				return False
		
		return True
	
	def getFlagBits(self, node):
		'''
		Checks out the showname field to see if we can determin
		the number of bits this flag is and it's offset in the packet.
		'''
		# .... ...1 .... .... = Recursion desired: Do query recursively
		
		show = node.getAttributeNS(None, 'showname')
		
		#debug("flag str (initial): [%s]" % show)
		
		# remove spaces
		show = show.replace(' ', '')
		
		# Get dots and numbers
		try:
			result = self._regexFlagBit1.match(show)
			firstDots = result.group(1)
			number = result.group(2)
			lastDots = result.group(3)
			
			offset = len(firstDots)
			bits = len(number)
			
			#debug("flag str: [%s]" % show)
			#debug("offset: %d - bits: %s - remander: %d" % (offset, bits, len(lastDots)))
			
			if (len(firstDots) + len(number) + len(lastDots)) % 2 != 0:
				debug("getFlagBits(): Something fishy about this!!! %d" % (len(firstDots) + len(number) + len(lastDots)))
		
			return offset, bits
		
		except:
			return -1, 1
	
	def figureType(self, node):
	
		# Try and figure out our type, number, string, etc.
	
		show = node.getAttributeNS(None, 'show')
		showName = node.getAttributeNS(None, 'showname')
		value = self.hex2bin(node.getAttributeNS(None, 'value'))
		valueHex = node.getAttributeNS(None, 'value')
		size = self._getNodeSize(node)
		pos = self._getNodePosition(node)
		parentPos = self._getNodePosition(node.parentNode)
		parentSize = self._getNodeSize(node.parentNode)
		
		#print "Show: [%s], valueHex: [%s], size: %d" % (show, valueHex, size)
	
		if showName != None and showName.find("Data:") == 0:
			return 'blob'
		
		# If just compar pos == parentPos we will get the first
		# child.  Should also check next child and size
		if pos == parentPos and parentSize == size:
			# A flag will have the same position as it's parent
			# parent will have size of 1
			#print "bit_flag: pos: %d parentPos: %d" % (pos, parentPos)
			#debug("show: %s - showName: %s" % (show, showName))
			
			(p,l) = self.getFlagBits(node)
			
			if p > -1:
				return 'bit_flag'
		
		if len(value) > 2 and value.isalnum() and not show.isdigit():
			return 'str'
		
		elif self._regexIp.match(show) != None and size == 4:
			# ip address
			ip1, ip2, ip3, ip4 = show.split('.')
			
			#debug("ip: %s - %s - %s - %s" % (show, ip1, valueHex[len(valueHex)-2:], valueHex))
			if int(ip1) == int(valueHex[6:], 16) and int(ip2) == int(valueHex[4:6], 16) and int(ip3) == int(valueHex[2:4], 16) and int(ip4) == int(valueHex[:2], 16):
				return 'n_ip'
			
			if int(ip1) == int(valueHex[:2], 16):
				return 'ip'
		
		elif show[:2] == "0x":
			
			# Figure if we are little or big endian
			
			showHex = show[2:]
			
			if showHex == valueHex or int(showHex, 16) == int(valueHex, 16):
				# little
				if size == 1:
					return 'uint8'
				
				if size == 2:
					return 'uint16'
					
				elif size == 4:
					return 'uint32'
				
				elif size == 8:
					return 'uint64'
			
			#debug("bigBalue: [%s][%s][%s]" % (valueHex, show, repr(value)))
			
			if len(value) == 2:
				format = '!H'
			elif len(value) == 4:
				format = '!I'
			else:
				debug("There's an issue with bigValue: [%s][%s][%s]" % (valueHex, show, repr(value)))
				if len(value) > 4:
					value = value[:4]
					format = '!I'
				else:
					value = value.ljust(4)
					format = '!I'
			
			bigValue = struct.unpack(format, value)[0]
			if int(bigValue) == int(showHex, 16):
				if size == 1:
					return 'n_uint8'
				
				if size == 2:
					return 'n_uint16'
					
				elif size == 4:
					return 'n_uint32'
				
				elif size == 8:
					return 'n_uint64'
	
		
		elif not show.isdigit() and self.isWideString(value):
			return 'w_str'
		
		elif not show.isdigit() and self.isPaddedWideString(value):
			return 'p_w_str'
		
		elif not show.isdigit() and self.isString(value):
			return 'str'
		
		elif not show.isdigit() and self.isPaddedString(value):
			return 'p_str'
		
		elif show.isdigit() or (len(showName) == 0 and size <= 4):
			
			cnt = len(valueHex)
			
			if size == 1:
				# Byte I bet
				return 'byte'
				
			elif size == 2:
				# Maybe 16 bit int?
				
				try:
					show = int(show)
				except:
					show = 0
				
				try:
					val = struct.unpack('H', value)[0]
					if int(val) == show:
						return 'uint16'
					
					val = struct.unpack('h', value)[0]
					if val == show:
						return 'int16'
					
					val = struct.unpack('!H', value)[0]
					if val == show:
						return 'n_int16'
					
					val = struct.unpack('!h', value)[0]
					if val == show:
						return 'n_uint16'
				
				except struct.error:
					pass
				
				return 'n_uint16'
			
			elif size == 4:
				# Maybe 32 bit int?
				if struct.unpack('I', value)[0] == show:
					return 'uint32'
				
				elif struct.unpack('i', value)[0] == show:
					return 'int32'
				
				elif struct.unpack('!I', value)[0] == show:
					return 'n_int32'
				
				return 'n_uint32'
	
		return 'blob'
	
	def figureOutPublisher(self, doc):
		'''
		Look for udp or tcp protocol and pull out
		address and port.
		'''
		
		defaultPublisher = "\t<Publisher class=\"Publisher\" />"
		
		nodes = doc.xpath('descendant::proto[@name="ip"]')
		if len(nodes) == 0:
			return defaultPublisher
		
		nodeIp = nodes[0]
		
		nodes = doc.xpath('descendant::proto[@name="tcp"]')
		if len(nodes) == 0:
			nodes = doc.xpath('descendant::proto[@name="udp"]')
		
		if len(nodes) == 0:
			return defaultPublisher
		
		nodeProt = nodes[0]
		
		m = re.search("Dst: ([^\s(]*)", str(nodeIp.getAttributeNS(None, 'showname')))
		ip = m.group(1)
		
		ret = ''
		for child in nodeProt.childNodes:
			if child.getAttributeNS(None, 'name') == 'udp.dstport':
				
				ret ="""
		<Publisher class="udp.Udp">
			<Param name="Host" value="%s" />
			<Param name="Port" value="%s" />
		</Publisher>
	""" % (ip, str(child.getAttributeNS(None, 'show')))
		
			if child.getAttributeNS(None, 'name') == 'tcp.dstport':
				
				ret ="""
		<Publisher class="tcp.Tcp">
			<Param name="Host" value="%s" />
			<Param name="Port" value="%s" />
		</Publisher>
	""" % (ip, str(child.getAttributeNS(None, 'show')))
		
		return ret
		
		

# ########################################################################

def DoTheShark(fileName,  proto):
	
	if proto == 2:
		# print out the protocols
		print "Select one of the following protocols:\n"
		
		doc = Parse(fileName)
		nodes = doc.xpath('descendant::proto')
		
		for n in nodes:
			print "\t", n.getAttributeNS(None, 'name')
		
		raise PeachException("")
	
	name = fileName
	doc = Parse(fileName)
	
	node = doc.xpath('descendant::proto[@name="%s"]' % proto)[0]
	
	shark = PeachShark()
	shark.removeTextNodes(node.parentNode)
	
	ret = """<?xml version="1.0" encoding="utf-8"?>
<Peach xmlns="http://phed.org/2008/Peach" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://phed.org/2008/Peach /peach/peach.xsd">

	<!-- ==// Auto Generated by PeachShark //== -->
	
	<!--
	
		Please do the following before using this fuzzer:
		
		- Take a look through the generated output, see if it makes sense
		- Integrate into a Peach Fuzzer
	
	-->
	
	<!-- Import defaults for Peach instance -->
	<Include ns="default" src="file:defaults.xml"/>
	
"""
	
	sibling = node
	while sibling != None:
	
		#shark.removeTextNodes(sibling.parentNode)
		debug("Handing node: " + sibling.getAttributeNS(None, 'name'))
		templateStr, s, p = shark.peachNode(sibling, 1, sibling.getAttributeNS(None, 'size'), None)
		ret += templateStr
		sibling = sibling.nextSibling
	
	ret += '\t<DataModel name="SharkTemplate">\n'
	
	for t in shark._templates:
		ret += '\t\t<Block ref="%s" />\n' % t
	
	ret += """
	</DataModel>
	
	<Test name="MyTest">
	   %s
	</Test>
	
	<Run name="DefaultRun">
		<Test ref="MyTest" />
	</Run>
	
</Peach>
""" % shark.figureOutPublisher(doc)
	
	return ret

# end
