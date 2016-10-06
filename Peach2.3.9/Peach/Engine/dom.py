
'''
Peach 2 DOM.  Peach XML files are parsed into an object model using
these classes.  The document object is Peach and all objects extend
from Element.

Elements used inside of <DataModel>'s are called data elements and
extend from DataElement.  This also allows easy checking for a data
element vs. a relation or other object by saying
isinstance(obj, DataElement).

For speed, a native deepcopy was implemented in cDeepCopy, also
some of the tree walking code for locating objects by name is
done in native code for performance reasons (see cPeach).

API documentation is generated using epydoc and the script
tools\gendocs.bat.  Output ends up in docs\apidocs\index.html.

@author: Michael Eddington
@version: $Id: dom.py 2742 2012-03-06 20:16:51Z meddingt $
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

# $Id: dom.py 2742 2012-03-06 20:16:51Z meddingt $

PROFILE = False

if PROFILE:
	print " --- INCOMING PROFILING ENABLED ---- "
	import profile

import sys, re, types, new, base64, time, ctypes, traceback, os, cPickle
import random, glob, struct
from Peach.Transformers.encode import WideChar
from Peach import Transformers
from Peach.Engine.common import *
from Peach.Engine.engine import Engine
from Peach.publisher import PublisherBuffer
import Peach
PeachModule = Peach
from cDeepCopy import deepcopy
# NOTE: Using internal python XML module here!!!!!
from xml.dom import *

class Empty(object):
	pass

class _DefaultStructure(ctypes.Structure):
	pass


class Element(object):
	'''
	Element in our template tree.
	'''
	
	__CurNameNum = 0	#: For generating unknown element names
	
	def __init__(self, name = None, parent = None):
		#: Name of Element, cannot include "."s
		self._name = name
		#: Parent of Element
		self.parent = parent
		#self._parent = parent
		
		#: Used instead of isinstance which is slow
		self.isDataElement = False
		#: Used instead of isinstance which is slow
		self.isElementWithChildren = False
		#: Used instead of isinstance which is slow
		self.isElement = True
		
		#: If element has children
		self.hasChildren = False
		
		#: Type of this element
		self.elementType = None
		
		#: Fullname cache
		self.fullName = None
		
		self.ref = None		#: The reference that made us, or None
		
		if self._name == None or len(self._name) == 0:
			self._name = self.getUniqueName()
		
	## The following are used for debugging purposes only
	#
	#def getParent(self):
	#	return self._parent
	#def setParent(self, parent):
	#	if self.name == "Lqcd" and parent == None and self.parent != None:
	#		print "Setting Lqcd("+repr(self)+").parent is not null, setting to null"
	#		#traceback.print_stack()
	#	if self.name == "Lqcd" and parent == None:
	#		print "Setting Lqcd("+repr(self)+").parent == None"
	#		#traceback.print_stack()
	#	elif self.name == "Lqcd" and parent != None:
	#		print "Setting Lqcd("+repr(self)+").parent:", parent
	#		#traceback.print_stack()
	#	
	#	self._parent = parent
	#parent = property(fget=getParent, fset=setParent)
	
	def get_Name(self):
		return self._name
	def set_Name(self, value):
		if(hasattr(self, "parent") and self.parent != None):
			if self.parent.has_key(self._name) and self.parent[self._name] == self:
				del self.parent._childrenHash[self._name]
				delattr(self.parent.children, self._name)
				
				self.parent._childrenHash[value] = self
				setattr(self.parent.children, value, self)
				
		self._name = value
	name = property(get_Name, set_Name, None)
	
	def __deepcopy__(self, memo):
		'''
		Copying objects in our DOM is a crazy business.  Here we
		try and help out as much as we can.
		
		NOTE: Deepcopy only works with cDeepCopy which is modified to
			look for __deepcopy__dont_use__ so we can configure our obj
			then re-call deepcopy.  On the next call deepcopy will
			ignore our __deepcopy__ method.
			
		'''
		
		# Copy procedures
		#
		#  - Only copy children array (_children)
		#  - Remove array and re-add children via append
		#  - Set our __deepcopy__ attributes
		#  - Fixup our toXml functions
		
		parent = self.parent
		self.parent = None
		
		# Only copy _children array
		if isinstance(self, ElementWithChildren):
			# Save other children collections
			_childrenHash = self._childrenHash
			children = self.children
			
			# Null out children except for array
			self._childrenHash = None
			self.children = None
		
		if self.elementType == 'block' or self.elementType == 'namespace':
			toXml = getattr(self, 'toXml')
			setattr(self, 'toXml', None)
		
		setattr(self, '__deepcopy__dont_use__', "true")
		
		## Perform actual copy
		
		e = deepcopy(self, memo)
		
		## Remove attributes
		
		delattr(e, '__deepcopy__dont_use__')
		delattr(self, '__deepcopy__dont_use__')
		
		if e.elementType == 'block':
			e.toXml = new.instancemethod(PeachModule.Engine.dom.BlockToXml, e, e.__class__)
			setattr(self, 'toXml', toXml)
		
		self.parent = parent

		if isinstance(self, ElementWithChildren):
			# Set back other children collections
			self._childrenHash = _childrenHash
			self.children = children
		
			# Fixup ElementWithChildren types
			# We need to try and keep things in order
			# and not have to many duplicated elements
			children = e._children
			
			e._children = []
			e._childrenHash = {}
			e.children = PeachModule.Engine.engine.Empty()
			
			for c in children:
				e.append(c)
		
			# Fixup DataElements
			if e.isDataElement:
				for r in e.relations:
					r.parent = e
				
				if e.placement != None:
					e.placement.parent = e
				
				for h in e.hints:
					h.parent = e
				
				if e.transformer != None:
					e.transformer.parent = e
		
		return e

	def updateRelationParents(self):
		'''
		Recurse through dom fixing
		relation's parents
		'''
		
		for r in self.relations:
			r.parent = self
		
		for c in self:
			c.updateRelationParents()

	def getElementsByType(self, type, ret = None):
		'''
		Will return an array all elements of a specific type
		in the tree starting with us.
		'''
		
		if ret == None:
			ret = []
		
		if isinstance(self, type):
			ret.append(self)
		
		return ret
	
	def getUniqueName():
		'''
		Provide a unique default name for elements.
		
		Note: Some graphs can get very large (500K nodes)
		  at which point this name can eat up alot of memeory.  So
		  lets keep it simple/small.
		'''
		
		name = "Named_%d" % Element.__CurNameNum
		Element.__CurNameNum += 1
		
		return name
	getUniqueName = staticmethod(getUniqueName)
	
	def getFullDataName(self):
		'''
		Return fully qualified name inside of data map
		'''
		
		return self.getFullnameInDataModel()
	
	def getRoot(self):
		'''
		Get the root of this DOM tree
		'''
		
		stack = []
		
		root = self
		stack.append(root)
		while root.parent != None and root.parent not in stack:
			root = root.parent
			stack.append(root)
		
		if root.parent != None and root.parent in stack:
			raise Exception("Error: getRoot found a recursive relationship! EEk!")
		
		return root
	
	def printDomMap(self, level = 0):
		'''
		Print out a map of the dom.
		'''
		print ("   "*level) + "- %s [%s](%s)" % (self.name, self.elementType, str(self)[-9:])
	
	def toXmlDom(self, parent, dict):
		'''
		Convert to an XML DOM object tree for use in xpath queries.
		'''
		
		owner = parent.ownerDocument
		if owner == None:
			owner = parent
		
		# Only use ref if name is not available!
		if hasattr(self, 'ref') and self.ref != None and self.name.startswith('Named_'):
			ref = self.ref.replace(":", "_")
			node = owner.createElementNS(None, ref)
		else:
			try:
				name = self.name.replace(":", "_")
				node = owner.createElementNS(None, name)
			except:
				print "name:", self.name
				raise
		
		node.setAttributeNS(None, "elementType", self.elementType)
		node.setAttributeNS(None, "name", self.name)
		
		if hasattr(self, 'ref') and self.ref != None:
			self._setXmlAttribute(node, "ref", self.ref)
		
		self._setXmlAttribute(node, "fullName", self.getFullname())
		
		dict[node] = self
		dict[self] = node
		
		parent.appendChild(node)
		
		return node
	
	def toXmlDomLight(self, parent, dict):
		'''
		Convert to an XML DOM object tree for use in xpath queries.
		Does not include values (Default or otherwise)
		'''
		
		owner = parent.ownerDocument
		if owner == None:
			owner = parent
		
		#if hasattr(self, 'ref') and self.ref != None:
		#	node = owner.createElementNS(None, self.ref)
		#else:
		node = owner.createElementNS(None, self.name)
		
		node.setAttributeNS(None, "elementType", self.elementType)
		node.setAttributeNS(None, "name", self.name)
		
		if hasattr(self, 'ref') and self.ref != None:
			self._setXmlAttribute(node, "ref", self.ref)
		
		self._setXmlAttribute(node, "fullName", self.getFullname())
		
		dict[node] = self
		dict[self] = node
		
		parent.appendChild(node)
		
		return node
	
	def _setXmlAttribute(self, node, key, value):
		'''
		Set an XML attribute with handling for UnicodeDecodeError.
		'''
		
		try:
			node.setAttributeNS(None, key, str(value))
			value = str(node.getAttributeNS(None, key))
		
		except UnicodeEncodeError:
			node.setAttributeNS(None, "%s-Encoded" % key, "base64")
			node.setAttributeNS(None, key, base64.b64encode(str(value)))
		
		except UnicodeDecodeError:
			node.setAttributeNS(None, "%s-Encoded" % key, "base64")
			node.setAttributeNS(None, key, base64.b64encode(str(value)))
	
	def _getXmlAttribute(self, node, key):
		'''
		Get an XML attribute with handling for UnicdeDecodeError.
		'''
		
		if not node.hasAttributeNS(None, key):
			return None
		
		if node.hasAttributeNS(None, "%s-Encoded" % key):
			value = node.getAttributeNS(None, key)
			value = base64.b64decode(value)
		
		else:
			value = str(node.getAttributeNS(None, key))
		
		return value
	
	def updateFromXmlDom(self, node, dict):
		'''
		Update our object based on an XML DOM object.
		All we are taking for now is defaultValue.
		'''
		
		if node.hasAttributeNS(None, 'defaultValue'):
			self.defaultValue = self._getXmlAttribute(node, "defaultValue")
			#print "updateFromXmlDom: Set defaultValue %s to %d bytes" % (self.name, len(self.defaultValue))
		
		if node.hasAttributeNS(None, 'currentValue'):
			self.currentValue = self._getXmlAttribute(node, "currentValue")
			#print "updateFromXmlDom: Set currentValue %s to %d bytes" % (self.name, len(self.currentValue))
		
		if node.hasAttributeNS(None, 'value'):
			self.value = self._getXmlAttribute(node, "value")
			#print "updateFromXmlDom: Set value %s to %d bytes" % (self.name, len(self.value))
	
	def compareTree(self, node1, node2):
		'''
		This method will compare two ElementWithChildren
		object tree's.
		'''
		
		if node1.name != node2.name:
			raise Exception("node1.name(%s) != node2.name(%s)" %(node1.name, node2.name))
		
		if node1.elementType != node2.elementType:
			raise Exception("Element types don't match [%s != %s]" % (node1.elementType, node2.elementType))

		if not isinstance(node1, DataElement):
			return True
		
		if len(node1) != len(node2):
			raise Exception("Lengths do not match %d != %d" % (len(node1), len(node2)))
		
		if len(node1._childrenHash) > len(node1._children):
			raise Exception("Node 1 length of hash > list")
		
		if len(node2._childrenHash) > len(node2._children):
			print "node1.name", node1.name
			print "node2.name", node2.name
			print "len(node1)", len(node1)
			print "len(node2)", len(node2)
			print "len(node1._childrenHash)", len(node1._childrenHash)
			print "len(node2._childrenHash)", len(node2._childrenHash)
			for c in node1._childrenHash.keys():
				print "node1 hash key:", c
			for c in node2._childrenHash.keys():
				print "node2 hash key:", c
			raise Exception("Node 2 length of hash > list")
		
		for (key,value) in node1._childrenHash.iteritems():
			if value not in node1._children:
				raise Exception("Error: %s not found in node1 list" % key)
		
		for key,value in node2._childrenHash.iteritems():
			if value not in node2._children:
				raise Exception("Error: %s not found in node2 list" % key)
		
		for i in range(len(node1)):
			if not self.compareTree(node1[i], node2[i]):
				return False
		
		return True
	
	def copy(self, parent):
		
		# We need to remove realParents before we can perform
		# the copy and then replace then.
		
		if self.isDataElement:
			
			if hasattr(self, 'realParent'):
				selfRealParent = self.realParent
				self.realParent = object()
			
			for child in self.getAllChildDataElements():
				if hasattr(child, 'realParent') and child.realParent != None:
					child.parent = child.realParent
					child.realParent = object()
		
		# Perform actual copy
		
		newSelf = deepcopy(self)
		newSelf.parent = parent
		self._FixParents(newSelf, parent)

		if self.isDataElement:
			
			if hasattr(self, 'realParent'):
				self.realParent = selfRealParent
			
			for child in self.getAllChildDataElements():
				if hasattr(child, 'realParent') and child.realParent != None:
					child.realParent = child.parent
			
			for child in newSelf.getAllChildDataElements():
				if hasattr(child, 'realParent') and child.realParent != None:
					child.realParent = child.parent
			
			# Not sure if we realy want todo this.
			if self.parent == None and parent == None and hasattr(self, 'realParent'):
				newSelf.realParent = self.realParent
		
		return newSelf
	
	def _FixParents(self, start = None, parent = None):
		'''
		Walk down from start and fix parent settings on children
		'''
		
		if start == None:
			start = self
		
		if parent != None:
			start.parent = parent
		
		if hasattr(start, 'fixup') and getattr(start, 'fixup') != None:
			start.fixup.parent = start
		
		if start.isElementWithChildren:
			for child in start._children:
				self._FixParents(child, start)
		
	def getFullname(self):
		
		if self.fullName != None:
			return self.fullName
		
		name = self.name
		node = self
		
		while node.parent != None:
			
			# We need to handle namespaces here!!!
			# TODO
			node = node.parent
			name = "%s.%s" % (node.name, name)
		
		return name
		
	def nextSibling(self):
		'''
		Get the next sibling or return None
		'''
		
		if self.parent == None:
			return None
		
		# First determin our position in parents children
		ourIndex = self.parent._children.index(self)
		
		# Check for next child
		if len(self.parent._children) <= (ourIndex+1):
			return None
		
		#sys.stderr.write("nextSibling: %d:%d\n" % (len(self.parent), (ourIndex+1)))
		return self.parent._children[ourIndex+1]
	
	def previousSibling(self):
		'''
		Get the prior sibling or return None
		'''
		
		if self.parent == None:
			return None
		
		# First determin our position in parents children
		ourIndex = self.parent._children.index(self)
		
		# Check for next child
		if ourIndex == 0:
			return None
		
		return self.parent._children[ourIndex-1]
	
	#def getDefaultValue(self):
	#	return self.transformer.realTransform(self.getDefaultRawValue())
	#
	#def getDefaultRawValue(self):
	#	return self.defaultValue

	def _setAttribute(self, node, name, value, default = None):
		'''
		Set an attribute on an XML Element.  We only set the
		attribute in the following cases:
		
			1. We have no attached xml node or self.ref == None
			2. We have a node, and the node has that attribute
			3. The value is not None
		
		'''
		
		# Simplify the XML by not adding defaults
		if value == default or value == None:
			return
		
		node.setAttributeNS(None, name, str(value))
	
	GuidRegex = re.compile('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
	def _xmlHadChild(self, child):
		'''
		Verify that we should serialize child node.  Checks
		to see if we have an attached xml node and that xml
		node has the child.  If we don't have an attached
		xml node then say we should add child.
		'''
		
		return True


class ElementWithChildren(Element):
	'''
	Contains functions that cause Element to act as a
	hash table and array for children.  Also children can
	be accessed by name via self.children.name.
	'''
	
	def __init__(self, name = None, parent = None):
		Element.__init__(self, name, parent)
		self._children = []			#: List of children (in order)
		self._childrenHash = {}		#: Dicitonary of children (by name)
		self.children = Empty()		#: Children object, has children as attributes by name
		self.hasChildren = True
		
		#: Used instead of isinstance which is slow
		self.isDataElement = False
		#: Used instead of isinstance which is slow
		self.isElementWithChildren = True
		#: Used instead of isinstance which is slow
		self.isElement = True

	def getByName(self, name):
		'''
		Internal helper method, not for use!
		'''
		
		names = name.split(".")
		node = self.getRoot()
		
		if node.name != names[0]:
			return None
		
		obj = node
		for i in range(1, len(names)):
			if not obj.has_key(names[i]):
				return None
			
			obj = obj[names[i]]
		
		return obj
	
	def getElementsByType(self, type, ret = None):
		'''
		Will return array of a specific type
		in the tree starting with us.
		'''
		
		#print "getElementsByType: %s: %s" % (self.name, self.elementType)
		
		if ret == None:
			ret = []
		
		if isinstance(self, type):
			ret.append(self)
		
		for child in self:
			if child.isElementWithChildren:
				child.getElementsByType(type, ret)
		
		return ret
	
	def printDomMap(self, level = 0):
		'''
		Print out a map of the dom.
		'''
		print ""
		print ("   "*level) + "+ %s [%s](%s)" % (self.name, self.elementType, str(self)[-9:])
		
		for child in self:
			if isinstance(child, Element):
				child.printDomMap(level+1)
				
				if child.parent != self:
					raise Exception("Error: printDomMap: %s.parent != self : %s:%s " % (child.name, child.name, repr(child.parent)))
	
	def verifyDomMap(self):
		'''
		Verify parent child relationship across DOM Tree
		'''
		for child in self:
			if isinstance(child, Element):
				if child.parent != self:
					raise Exception("Error: verifyDomMap: %s.parent != self : %s:%s " % (child.name, child.name, repr(child.parent)))
			
			if isinstance(child, ElementWithChildren):
				child.verifyDomMap()
	
	def toXmlDom(self, parent, dict):
		'''
		Convert to an XML DOM boject tree for use in xpath queries.
		'''
		
		node = Element.toXmlDom(self, parent, dict)
		
		for child in self._children:
			if hasattr(child, 'toXmlDom'):
				child.toXmlDom(node, dict)
		
		return node
	
	def toXmlDomLight(self, parent, dict):
		'''
		Convert to an XML DOM boject tree for use in xpath queries.
		
		Note: toXmlDomLight and toXmlDom are the same now
		'''
		
		node = Element.toXmlDomLight(self, parent, dict)
		
		for child in self._children:
			if hasattr(child, 'toXmlDomLight'):
				child.toXmlDomLight(node, dict)
		
		return node
	
	def updateFromXmlDom(self, node, dict):
		'''
		Update our object based on an XML DOM object.
		All we are taking for now is defaultValue.
		'''
		
		Element.updateFromXmlDom(self, node, dict)
		
		if node.hasChildNodes():
			for child in node.childNodes:
				dict[child].updateFromXmlDom(child, dict)
	
	def append(self, obj):

		## remove for speed
		#if obj in self._children:
		#	raise Exception("object already child of element")
		
		# If we have the key we need to replace it
		if self._childrenHash.has_key(obj.name):
			self[obj.name] = obj
			obj.parent = self
			return
		
		# Otherwise add it at the end
		self._children.append(obj)
		self._childrenHash[obj.name] = obj
		setattr(self.children, obj.name, obj)
		
		# Reset parent relationship
		obj.parent = self
	
	def index(self, obj):
		return self._children.index(obj)
	
	def insert(self, index, obj):
		if obj in self._children:
			raise Exception("object already child of element")
		
		# Update parent
		obj.parent = self
		
		self._children.insert(index, obj)
		if obj.name != None:
			#print "inserting ",obj.name
			self._childrenHash[obj.name] = obj
			setattr(self.children, obj.name, obj)
	
	def firstChild(self):
		if(len(self._children) >= 1):
			return self._children[0]
		
		return None
	
	def lastChild(self):
		if(len(self._children) >= 1):
			return self._children[-1]
		
		return None
	
	def has_key(self, name):
		return self._childrenHash.has_key(name)
	
	
	# Container emulation methods ############################
	
	# Note: We have both a dictionary and an ordered list
	#       that we must keep upto date.  This allows us
	#       to access children by index or by key
	#       So saying: elem[0] is valid as is elem['Name']
	
	def __len__(self):
		return self._children.__len__()
	
	def __getitem__(self, key):
		if type(key) == int:
			return self._children.__getitem__(key)
		
		return self._childrenHash.__getitem__(key)
	
	def __setitem__(self, key, value):
		if type(key) == int:
			oldObj = self._children[key]
			if oldObj.name != None:
				del self._childrenHash[oldObj.name]
				#delattr(self.children, oldObj.name)
			
			if value.name != None:
				self._childrenHash[value.name] = value
				setattr(self.children, value.name, value)
			
			return self._children.__setitem__(key, value)
		
		else:
			if key in self._childrenHash:
				# Existing item
				inx = self._children.index( self._childrenHash[key] )
					
				self._children[inx] = value
				self._childrenHash[key] = value
				setattr(self.children, value.name, value)
			else:
				self._children.append(value)
				self._childrenHash[key] = value
				setattr(self.children, value.name, value)
	
	def __delitem__(self, key):
		if type(key) == int:
			obj = self._children[key]
			if obj.name != None:
				del self._childrenHash[obj.name]
				delattr(self.children, obj.name)
			
			return self._children.__delitem__(key)
		
		obj = self._childrenHash[key]
		
		try:
			self._children.remove(obj)
		except:
			pass
		
		try:
			del self._childrenHash[key]
		except:
			pass
		
		if hasattr(self.children, key):
			delattr(self.children, key)
	
	def __iter__(self):
		return self._children.__iter__()
	
	def __contains__(self, item):
		return self._children.__contains__(item)

class Mutatable(ElementWithChildren):
	'''
	To mark a DOM object as mutatable(fuzzable) or not  
	'''
	def __init__(self, name = None, parent = None, isMutable = True):
		ElementWithChildren.__init__(self, name, parent)
		
		#: Can this object be changed by the mutators?
		self.isMutable = isMutable
	
	def setMutable(self, value):
		'''
		Update this element and all childrens isMutable.
		'''
		for child in self:
			if isinstance(child, Mutatable):
				child.setMutable(value)
				
		self.isMutable = value
		
class DataElement(Mutatable):
	'''
	Data elements compose the Data Modle.  This is the base
	class for String, Number, Block, Template, etc.
	
	When iterating over the Peach DOM if an element
	isinstance(obj, DataElement) it is part of a data model.
	'''
	
	def __init__(self, name = None, parent = None):
		ElementWithChildren.__init__(self, name, parent)
		
		if name != None and (name.find(".") > -1 or name.find(":") > -1):
			raise PeachException("Name '%s' contains characters not allowed in names such as period (.) or collen (:)" % name)
		
		
		#: Used instead of isinstance which is slow
		self.isDataElement = True
		#: Used instead of isinstance which is slow
		self.isElementWithChildren = True
		#: Used instead of isinstance which is slow
		self.isElement = True
		
		#: Is this a ctypes pointer to something? (Defaults to False)
		self.isPointer = False
		
		#: What is out pointer depth? (e.g. void** p is 2), (Defaults to 1)
		self.pointerDepth = 1
		
		#: Optional constraint used during data cracking, python expression
		self.constraint = None
		
		#: Should element be mutated?
		self.isMutable = True
		
		#: Does data model have an offset relation?
		self.modelHasOffsetRelation = None
		
		#: Cache of relation, list of full data names (String) of each relation from here down.  cache is build post incoming.
		self.relationCache = None
		
		#: Key is full data name of "of" element (string), value is list of relation full data names (String). cache is bulid post incoming.
		self.relationOfCache = None
		
		#: Event that occurs prior to parsing the next array element.
		self.onArrayNext = None
		
		#: Transformers to apply
		self.transformer = None
		
		#: Fixup if any
		self.fixup = None
		
		#: Placement if any
		self.placement = None
		
		#: Relations this element has
		self.relations = ArraySetParent(self)
		
		#: Mutator Hints
		self.hints = ArraySetParent(self)
		
		#: Fixed occurs
		self.occurs = None
		#: Minimum occurences
		self._minOccurs = 1
		#: Maximum occurences
		self._maxOccurs = 1
		
		self.generatedOccurs = 1
		
		#: Default value to use
		self._defaultValue = None
		#: Mutated value prior to packing and transformers
		self._currentValue = None
		#: Mutated value after everything but transformers
		self._finalValue = None
		#: Current value
		self._value = None
		
		#: Expression used by data cracker to determin
		#: if element should be included in cracking.
		self.when = None
		
		self._inInternalValue = False	#: Used to prevent recursion
		
		# Attributes for elements part of an array
		self.array = None			#: Name of array.  The origional name of the data element.
		self.arrayPosition = None	#: Our position in the array.
		self.arrayMinOccurs = None	#: The min occurences in the array
		self.arrayMaxOccurs = None	#: The max occurences in the array
		
		#: Position in data stream item was parsed at
		self._pos = None
		self._possiblePos = None
		#: Parse rating for element
		self.rating = None
	
		#: Is this element a static token?
		self.isStatic = False

		#: A StringBuffer used to determin offset relations
		self.relationStringBuffer = None
	
		#: Fullname in data model
		self.fullNameDataModel = None
	
	def get_DefaultValue(self):
		return self._defaultValue
	def set_DefaultValue(self, value):
		self._defaultValue = value
		#self._currentValue = None
		self._value = None
		self._finalValue = None
	defaultValue = property(get_DefaultValue, set_DefaultValue, None)
	def get_CurrentValue(self):
		return self._currentValue
	def set_CurrentValue(self, value):
		self._currentValue = value
		self._value = None
		self._finalValue = None
	currentValue = property(get_CurrentValue, set_CurrentValue, None)
	def get_Value(self):
		return self._value
	def set_Value(self, value):
		self._value = value
		self._finalValue = None
	value = property(get_Value, set_Value, None)
	def get_FinalValue(self):
		return self._finalValue
	def set_FinalValue(self, value):
		self._finalValue = value
	finalValue = property(get_FinalValue, set_FinalValue, None)
	
	def get_pos(self):
		'''
		Getter for pos property.  If we have a string buffer
		associated with the root node, use that for the correct
		position.
		'''
		
		obj = self
		while obj.parent != None and (not hasattr(obj, "relationStringBuffer") or obj.relationStringBuffer == None):
			obj = obj.parent
		
		if hasattr(obj, "relationStringBuffer") and obj.relationStringBuffer != None:
			value = obj.relationStringBuffer.getPosition(self.getFullDataName())
			if value != None:
				return value
			else:
				return 0
		
		return self._pos
	def set_pos(self, value):
		'''
		Setter for pos property
		'''
		self._pos = value
		return self._pos
	pos = property(get_pos, set_pos, None)
	
	def get_possiblePos(self):
		'''
		Getter for pos property.  If we have a string buffer
		associated with the root node, use that for the correct
		position.
		'''
		
		obj = self
		while obj.parent != None and (not hasattr(obj, "relationStringBuffer") or obj.relationStringBuffer == None):
			obj = obj.parent
		
		if hasattr(obj, "relationStringBuffer") and obj.relationStringBuffer != None:
			value = obj.relationStringBuffer.getPosition(self.getFullDataName())
			if value != None:
				return value
			##BUG: Leave this commented out else we introduce a bug in the data cracker
			## that was run into with opentype.xml used in eot.xml.
			##else:
			##	print "get_possiblePos: relationStringBuffer was of no use to us!"
			##	return 0
		
		return self._possiblePos
	def set_possiblePos(self, value):
		'''
		Setter for pos property
		'''
		self._possiblePos = value
		return self._possiblePos
	possiblePos = property(get_possiblePos, set_possiblePos, None)

	def getElementsByType(self, type, ret = None):
		'''
		Will return an array all elements of a specific type
		in the tree starting with us.
		'''

		#print "getElementsByType: %s: %s" % (self.name, self.elementType)
		
		if ret == None:
			ret = []
		
		if isinstance(self, type):
			ret.append(self)
		
		elif self.fixup != None:
			for child in self.fixup:
				if child.isElementWithChildren:
					child.getElementsByType(type, ret)
		
		for child in self:
			if child.isElementWithChildren:
				child.getElementsByType(type, ret)

		return ret
	
	def clone(self, obj):
		
		if obj == None:
			raise Exception("Generic clone needs object instance!")
		
		obj.name = self.name
		obj.parent = self.parent
		obj.isDataElement = self.isDataElement
		obj.isElementWithChildren = self.isElementWithChildren
		obj.isElement = self.isElement
		obj.hasChildren = self.hasChildren
		obj.elementType = self.elementType
		obj.fullName = self.fullName
		obj.ref = self.ref
		obj.generatedOccurs = self.generatedOccurs
		
		obj.isPointer = self.isPointer
		obj.pointerDepth = self.pointerDepth
		obj.constraint = self.constraint
		obj.isMutable = self.isMutable
		obj.modelHasOffsetRelation = self.modelHasOffsetRelation
		
		if self.relationCache != None:
			obj.relationCache = self.relationCache[:]
		if self.relationOfCache != None:
			obj.relationOfCache = self.relationOfCache.copy()
			
		obj.onArrayNext = self.onArrayNext
		
		if self.transformer != None:
			obj.transformer = self.transformer.clone()
		if self.fixup != None:
			obj.fixup = self.fixup.clone()
		if self.placement != None:
			obj.placement = self.placement.clone()
		
		for r in self.relations:
			obj.relations.append( r.clone() )
		
		for h in self.hints:
			obj.hints.append( h.clone() )
		
		obj.occurs = self.occurs
		obj._minOccurs = self._minOccurs
		obj._maxOccurs = self._maxOccurs
		
		obj._defaultValue = self._defaultValue
		obj._currentValue = self._currentValue
		obj._finalValue = self._finalValue
		obj._value = self._value
		
		obj.when = self.when
		obj._inInternalValue = self._inInternalValue
		obj.array = self.array
		obj.arrayPosition = self.arrayPosition
		obj.arrayMinOccurs = self.arrayMinOccurs
		obj.arrayMaxOccurs = self.arrayMaxOccurs
		obj._pos = self._pos
		obj._possiblePos = self._possiblePos
		obj.rating = self.rating
		obj.isStatic = self.isStatic
		obj.fullNameDataModel = self.fullNameDataModel
		
		return obj
		
	
	def asCType(self):
		'''
		Returns a ctypes module type for this DataElement.
		'''
		
		raise Exception("Error: asCType method not implemented yet!")
	
	def pickleModel(self, model):
		newModel = model.copy(None)
		newModel.parent = None
		
		self._pickleRemoveInstanceMethods(newModel)
		
		return cPickle.dumps(newModel)
	
	def unpickleModel(self, dump):
		model = cPickle.loads(dump)
		self._pickleAddInstanceMethods(model)
		
		return model
		
	def _pickleAddInstanceMethods(self, model):
		'''
		Add back in the non-pickleable instancemethods.
		'''
		
		#if not hasattr(model, "__deepcopy__"):
		#	model.__deepcopy__ = new.instancemethod(PeachDeepCopy, model, model.__class__)
		
		if model.elementType == 'block':
			model.toXml = new.instancemethod(PeachModule.Engine.dom.BlockToXml, model, model.__class__)
		
		#elif model.elementType == 'namespace':
		#	model.toXml = new.instancemethod(PeachModule.Engine.dom.NamespaceToXml, model, model.__class__)
		
		for c in dir(model):
			if c == 'parent':
				continue
			
			obj = getattr(model, c)
			if isinstance(obj, Element):
				self._pickleAddInstanceMethods(obj)
		
		if isinstance(model, ElementWithChildren):
			for c in model:
				if isinstance(c, Element):
					self._pickleAddInstanceMethods(c)
	
	def _pickleRemoveInstanceMethods(self, model):
		'''
		Remove any instance methods.
		'''
		
		#if hasattr(model, "__deepcopy__"):
		#	delattr(model, "__deepcopy__")
		
		if hasattr(model, "toXml") and (model.elementType == 'block' or model.elementType == 'namespace'):
			delattr(model, "toXml")
		
		for c in dir(model):
			if c == 'parent':
				continue
			
			obj = getattr(model, c)
			if isinstance(obj, Element):
				self._pickleRemoveInstanceMethods(obj)
		
		if isinstance(model, ElementWithChildren):
			for c in model:
				if isinstance(c, Element):
					self._pickleRemoveInstanceMethods(c)
	
	def setDefaults(self, data, dontCrack = False, mustPass = False):
		'''
		Set data elements defaultValue based on a Data object.
		'''
		
		if data.fileName != None:
			
			if dontCrack:
				return
			
			## Node: We are not ready to use the .peach files yet
			## still problems to work out!
			
			statPeach = None
			#try:
			#	if self.getRoot().peachPitUri[:5] == 'file:':
			#		statPit = os.stat(self.getRoot().peachPitUri[5:])
			#		statFile = os.stat(data.fileName)
			#		
			#		# Always do this one last
			#		statPeach = os.stat(data.fileName+".peach")
			#except:
			#	pass
			
			if statPeach != None and statPeach.st_mtime > statFile.st_mtime and statPeach.st_mtime > statPit.st_mtime:
				# Load pre-parsed peach file
				print "[*] Loading model for: %s" % data.fileName
				
				fd = open(data.fileName+".peach", "rb+")
				data = fd.read()
				fd.close()
				
				model = self.unpickleModel(data)
				model.parent = self.parent
				
				# Remove self and insert model
				index = self.parent.index(self)
				del self.parent[self.name]
				self.parent.insert(index, model)
			
			else:
				print "[*] Cracking data from %s into %s" % (data.fileName, self.name)
				
				fd = open(data.fileName, "rb")
				stuff = fd.read()
				fd.close()
				
				buff = PublisherBuffer(None, stuff)
				
				parent = self.parent
				while parent.parent != None: parent = parent.parent
				
				cracker = PeachModule.Engine.incoming.DataCracker(parent)
				#cracker.haveAllData = True
				
				startTime = time.time()
				if PROFILE:
					profile.runctx("cracker.crackData(self, buff, \"setDefaultValue\")",
								   globals(), {"cracker":cracker, "self":self, "stuff":stuff, "buff":buff})
				else:
					cracker.crackData(self, buff, "setDefaultValue")
					#if mustPass and not cracker.crackPassed:
					#	raise PeachException("Error, file did not properly parse.")
				
				print "[*] Total time to crack data: %.2f" % (time.time() - startTime)
				print "[*] Building relation cache"
				self.BuildRelationCache()
				
				## Pickle model
				##try:
				##	fd = open(data.fileName + ".peach", "wb+")
				##	fd.write(self.pickleModel(self))
				##	fd.close()
				##except:
				##	try:
				##		os.unlink(data.fileName+".peach")
				##	except:
				##		pass
			
			return cracker.crackPassed
		
		if data.expression != None:
			
			stuff = evalEvent(data.expression, {}, data)
			buff = PublisherBuffer(None, stuff)
			
			parent = self.parent
			while parent.parent != None: parent = parent.parent
			
			cracker = PeachModule.Engine.incoming.DataCracker(parent)
			cracker.haveAllData = True
			cracker.crackData(self, buff, "setDefaultValue")
			
			return
		
		for field in data:
			obj = self
			
			for name in field.name.split('.'):
				
				# See if we have an array index "name[n]"
				m = re.search(r"(.*)\[(-?\d+)\]$", name)
				if m != None:
					name = m.group(1)
					idx = int(m.group(2))
					
					if hasattr(obj.children, name):
						obj = getattr(obj.children, name)
					elif hasattr(obj.children, name + "-0"):
						obj = getattr(obj.children, name + "-0")
					else:
						raise PeachException("Error: Unable to locate field %s" % field.name)
					
					if idx == -1:
						# Negative index will cause
						# array to be removed
						relations = obj.getRelationsOfThisElement()
						del obj.parent[obj.name]
						
						# Remove any relations pointing to our
						# removed array.
						for r in relations:
							try:
								del r.parent[r.name]
							except:
								pass
							
							if r in r.parent.relations:
								r.parent.relations.remove(r)
						
						break
					
					if obj.maxOccurs > 1 and idx >= 0:
						# Convert first element to array
						
						orig = obj.copy(obj.parent)
						obj.origional = orig
						
						index = obj.parent.index(obj)
						del obj.parent[obj.name]
						
						obj.array = obj.name
						obj.name = obj.name + "-0"
						obj.arrayPosition = 0
						obj.arrayMinOccurs = obj.minOccurs
						obj.arrayMaxOccurs = obj.maxOccurs
						obj.minOccurs = 1
						obj.maxOccurs = 1
						
						obj.parent.insert(index, obj)
					
					if obj.array != None:
						
						# Check and see if we need to expand
						arrayCount = obj.getArrayCount()
						if arrayCount == idx:
							
							# Expand object
							newobj = obj.origional.copy(obj.parent)
							newobj.name = "%s-%d" % (obj.array, arrayCount)
							newobj.array = obj.array
							newobj.arrayPosition = arrayCount
							newobj.arrayMinOccurs = obj.arrayMinOccurs
							newobj.arrayMaxOccurs = obj.arrayMaxOccurs
							newobj.minOccurs = 1
							newobj.maxOccurs = 1
							
							lastobj = obj.getArrayElementAt(newobj.arrayPosition - 1)
							index = obj.parent.index(lastobj)
							obj.parent.insert(index+1, newobj)
							obj = newobj
						
						# Are we trying to expand by more then 1?
						elif arrayCount < idx:
							raise PeachException("Error: Attempting to expand array by more then one element. [%s]" % field.name)
						
						# Already expanded, just get correct index
						else:
							obj = obj.getArrayElementAt(idx)
					
					else:
						raise PeachException("Error: Attempting to use non-array element as array. [%s]" % field.name)
				
				else:
					if hasattr(obj.children, name):
						obj = getattr(obj.children, name)
				
					else:
						raise PeachException("Error: Unable to locate field %s" % field.name)
				
				# Was parent a choice?  If so select this element.
				if isinstance(obj.parent, Choice):
					obj.parent.currentElement = obj
					
					# Removing other children.  This is what incoming
					# cracker does, so lets match that behaviour.
					remove = []
					for child in obj.parent:
						if child.isDataElement and child != obj:
							remove.append(child)
					
					for child in remove:
						del obj.parent[child.name]
			
		
			# If obj is a number, and field type is hex we
			# need todo some mojo
			if field.valueType == 'hex' \
				and (isinstance(obj, Number) or isinstance(obj, Flags) \
				or isinstance(obj, Flag)):
				
				# Convert hex to number
				hexString = ""
				for b in field.value:
					h = hex(ord(b))[2:]
					if len(h) < 2:
						h = "0" + h
					
					hexString += h
					
				if len(hexString) == 0:
					obj.setDefaultValue(str(0))
				
				else:
					obj.setDefaultValue(str(long(hexString, 16)))
			
			else:
				obj.setDefaultValue(field.value)
	
	def BuildFullNameCache(self):
		'''
		Figure out our fullname and fullname in data model
		'''
		
		for node in self._getAllRelationsInDataModel():
			node.fullName = node.getFullname()
			node.fullNameDataModel = node.getFullnameInDataModel()
	
	def BuildRelationCache(self):
		'''
		Build the relation cache for this data element and it's children.
		'''

		root = self.getRootOfDataMap()
		if root != self:
			root.BuildRelationCache()
			return
		
		# 0. Build the fullname cache first
		if self.fullName == None or self.fullNameDataModel == None:
			self.BuildFullNameCache()

		# Update modelHasOffsetRelation when not using cache
		if self.modelHasOffsetRelation == None:
			relations = self._getAllRelationsInDataModel(self, False)
			for r in relations:
				if r.type == 'offset':
					self.modelHasOffsetRelation = True
					break
			
		# 1. Build list of all relations from here down
		relations = self._getAllRelationsInDataModel(self, False)
		
		# 2. Fill in both cache lists
		self.relationCache = []
		self.relationOfCache = {}
		
		for r in relations:
			
			# Skip from relations
			if r.From != None:
				continue
			
			rStr = r.getFullnameInDataModel()
			
			# Update modelHasOffsetRelation
			if r.type == 'count':
				self.modelHasOffsetRelation = True
			
			if r.type != 'when':
				ofStr = r.getOfElement().getFullnameInDataModel()
				if not self.relationOfCache.has_key(ofStr):
					self.relationOfCache[ofStr] = []
				
				if rStr not in self.relationOfCache[ofStr]:
					self.relationOfCache[ofStr].append(rStr)
			
			if rStr not in self.relationCache:
				self.relationCache.append(rStr)
		
	
	def get_minOccurs(self):
		minOccurs = self._minOccurs
		
		if minOccurs != None:
			minOccurs = eval(str(minOccurs))
		
		if minOccurs == None:
			minOccurs = 1
		
		elif minOccurs != None:
			minOccurs = int(minOccurs)
		
		return minOccurs
	
	def set_minOccurs(self, value):
		if value == None:
			self._maxOccurs = None
		
		else:
			self._minOccurs = str(value)
		
	#: Minimum occurences (property)
	minOccurs = property(get_minOccurs, set_minOccurs)
	
	def get_maxOccurs(self):
		if self._maxOccurs == None:
			return None
		
		return eval(str(self._maxOccurs))
	
	def set_maxOccurs(self, value):
		if value == None:
			self._maxOccurs = None
		else:	
			self._maxOccurs = str(value)
	
	#: Maximum occurences (property)
	maxOccurs = property(get_maxOccurs, set_maxOccurs)
	
	def getAllChildDataElements(self, ret = None):
		'''
		Get all children data elements.  Recursive
		'''
		
		if ret == None:
			ret = []
		
		for child in self:
			if child.isDataElement:
				ret.append(child)
				child.getAllChildDataElements(ret)
		
		return ret
	
	def hasRelation(self):
		'''
		Does this element have a size, count or offset relation?
		'''
		
		for relation in self.relations:
			if relation.type in ['size', 'count', 'offset']:
				return True
		
		return False
		
	def _HasSizeofRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'size' and relation.of != None and relation.From == None:
				return True
		
		return False
	
	def _HasOffsetRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'offset' and relation.of != None and relation.From == None:
				return True
		
		return False
	
	def _GetOffsetRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'offset' and relation.of != None and relation.From == None:
				return relation
		
		return False
	
	def _GetSizeofRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'size' and relation.of != None and relation.From == None:
				return relation
		
		return None
	
	def GetWhenRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'when':
				return relation
		
		return None
	
	def HasWhenRelation(self, node = None):
		
		if node == None:
			node = self
		
		for relation in node.relations:
			if relation.type == 'when':
				return True
		
		return False

	def _HasCountofRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'count' and relation.of != None and relation.From == None:
				return True
		
		return False

	def _GetCountofRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'count' and relation.of != None and relation.From == None:
				return relation
		
		return None

	def getFullnameInDataModel(self):
		'''
		This will get fully qualified name of this element starting with the
		root node of the data model.
		'''
		
		if self.fullNameDataModel != None:
			return self.fullNameDataModel
		
		name = self.name
		node = self
		
		while node.parent != None and node.parent.isDataElement:
			node = node.parent
			name = "%s.%s" % (node.name, name)
		
		return name
		
	def getRootOfDataMap(self):
		'''
		Return the root of this data map.  This should always return
		a Template object.
		'''
		
		# Slower then PSYCO
		#return cPeach.getRootOfDataMap(self)

		root = self
		while root.parent != None and root.parent.isDataElement:
			root = root.parent

		return root
	
	def findArrayByName(self, name):
		'''
		Will find first element in array named "name".
		
		This method should allow for more natural reuse of Blocks/Templates
		w/o the user needing to think about it.
		
		@type	name: string
		@param	name: Array to find.  Does not support dotted name.
		@rtype: DataElement
		@return: DataElement or None
		'''
		
		if name.find(".") > -1:
			# Handle foo.bar.wee
			parentName = name[:name.rfind(".")]
			arrayName = name[name.rfind(".")+1:]
			
			parent = self.find(parentName)
			if parent == None:
				print self
				print self.getFullname()
				
				for r in self.relations:
					print "r.of:", r.of
				
				raise Exception("Unable to locate [%s]" % parentName)
			
			obj = self._findArrayByName(parent, arrayName)
			if obj != None:
				return obj
		
		for block in self._findAllBlocksGoingUp():
			obj = self._findArrayByName(block, name)
			if obj != None:
				return obj
		
		return None
	
	def _findArrayByName(self, node, name):
		'''
		A generator that returns each instance of name in a data model.
		'''
		
		# look at us!
		if node.array == name:
			# Try and locate array elem 0
			obj = node.getArrayElementAt(0)
			if obj != None:
				return obj
			
			# Otherwise we found something :)
			return node
		
		# look at each child
		for child in node._children:
			if child.isDataElement and child.array == name and child.arrayPosition == 0:
				return child
		
		# search down each child path
		for child in node._children:
			if child.isDataElement:
				obj = self._findArrayByName(child, name)
				if obj != None:
					return obj
		
		# done!
		return None
	
	def findDataElementByName(self, name):
		'''
		Will find a data element in this data map by name.  The search
		pattern we use is to locate each block we are a member of
		starting with the nearest.  At each block we look down to see
		if we can resolve the name.  If not we move closer towards the
		root of the data model.
		
		This method should allow for more natural reuse of Blocks/Templates
		w/o the user needing to think about it.
		
		@type	name: string
		@param	name: Name of element to find.  Can be full or relative.
		@rtype: DataElement
		@return: DataElement or None
		'''
		
		try:
			self._fixRealParent(self)
			
			names = name.split('.')
			
			if self.name == names[0]:
				obj = self._checkDottedName(self, names)
				if obj != None:
					return obj
			
			# Assume if we have more then 2 parts we may be from the root
			if len(names) > 2:
				obj = self._checkDottedName(self.getRootOfDataMap(), names)
				if obj != None:
					return obj
			
			#if len(names) > 1:
			#	obj = cPeach.findDataElementByName(self, [names[0]])
			#	if obj != None:
			#		print obj
			#		obj = self._checkDottedName(obj, names)
			#		if obj != None:
			#			#print "[%s] R: %s" %(name, obj)
			#			return obj
			
			ret = cPeach.findDataElementByName(self, names)
			#print "[%s] R: %s" % (name, ret)
			
			return ret
			
			
			##print "----"
			##for block in self._findAllBlocksGoingUp():
			##	print "findDataElementByName: Looking for %s in %s" % (name, block.name)
			##	for node in self._findDataElementByName(block, names[0]):
			##		obj = self._checkDottedName(node, names)
			##		if obj != None:
			##			#print "Could not locate", name
			##			#print "But we did with old code", obj.getFullnameInDataModel()
			##			#print node
			##			#print obj.parent
			##			#raise Exception("Boggers")
			##			return obj
			##		else:
			##			print "checkdottednamefailed:", node.name, name
		
		finally:
			self._unFixRealParent(self)
		
		return None

	def find(self, name):
		'''
		Alias for findDataElementByName.
		
		Will find a data element in this data map by name.  The search
		pattern we use is to locate each block we are a member of
		starting with the nearest.  At each block we look down to see
		if we can resolve the name.  If not we move closer towards the
		root of the data model.
		
		This method should allow for more natural reuse of Blocks/Templates
		w/o the user needing to think about it.
		
		@type	name: string
		@param	name: Name of element to find.  Can be full or relative.
		@rtype: DataElement
		@return: DataElement or None
		'''
		return self.findDataElementByName(name)
	
	def _findAllBlocksGoingUp(self):
		'''
		Generator that locates all blocks by walking up
		our tree.
		'''
		
		ret = []
		
		obj = self
		if isinstance(obj, Block) or isinstance(obj, Template):
			ret.append(obj)
		
		while obj.parent != None and obj.parent.isDataElement:
			obj = obj.parent
			ret.append(obj)
			
		return ret
	
	def _findDataElementByName(self, node, name):
		'''
		A generator that returns each instance of name in a data model.
		'''
		
		# look at us!
		if node.name == name:
			yield node
		
		# look at each child
		if node._childrenHash.has_key(name):
			yield node[name]
		else:
			for c in node:
				print "%s: %s != %s" % (node.name, c.name, name)
		
		# search down each child path
		for child in node._children:
			if child.isDataElement:
				for n in self._findDataElementByName(child, name):
					yield n
		
		# done!
	
	def _checkDottedName(self, node, names):
		'''
		Internal helper method, not for use!
		'''
		
		if node.name != names[0]:
			print "_checkDottedName: %s != %s" % (node.name, names[0])
			return None
		
		obj = node
		for i in range(1, len(names)):
			if not obj.has_key(names[i]):
				#print "_checkDottedName: %s not found" % (names[i])
				#for child in obj:
				#	print "_checkDottedNames: Have:", child.name
				#	if child.parent != obj:
				#		print "_checkDottedNames: BAD PARRENT"
				#for key in obj._childrenHash.keys():
				#	print "_checkDottedName: Key:", key
				return None
			
			obj = obj[names[i]]
		
		return obj
	
	def getAllPlacementsInDataModel(self):
		'''
		As the name says, recurse looking for
		placements
		'''
		
		if self.placement != None:
			yield self.placement
		
		for child in self:
			if isinstance(child, DataElement):
				for p in child.getAllPlacementsInDataModel():
					yield p
	
	def getDataElementByName(self, name):
		'''
		Get an element relative to here with a qualified name
		'''
		
		names = name.split(".")
		
		if self.name != names[0]:
			#print "[%s] != [%s]" % (self.name, names[0])
			return None
		
		obj = self
		for i in range(1, len(names)):
			if not obj.has_key(names[i]):
				#print "no [%s]" % (names[i])
				return None
			
			obj = obj[names[i]]
		
		return obj
	
	
	def getRelationOfThisElement(self, type):
		'''
		Locate and return a relation of this element.
		'''
		
		self._fixRealParent(self)
		try:
			
			if PeachModule.Engine.engine.Engine.relationsNew:
				# Assume both of and from relations in model
				
				for r in self.relations:
					# Lets not return "when" :)
					if r.type == 'when' or r.From == None:
						continue
					
					if type == None or r.type == type:
						obj = self.findDataElementByName(r.From)
						
						if obj == None:
							raise Exception("Mismatched relations? Can't find r.From: '%s'" % r.From)
						
						if type != None:
							for rel in obj.relations:
								if rel.type == type and rel.of.endswith(r.parent.name):
									return rel
							
							print "r.parent.name:", r.parent.name
							print "rel.of:"
							print "of-object:", obj
							print "of-obj.fullname:", obj.getFullname()
							print "self.fullname:", self.getFullname()
							print "r.From:", r.From
							print "len(obj.relations)", len(obj.relations)
							for rel in obj.relations:
								print "rel:", rel.type, rel.of
							
							raise Exception("Mismatched relations???")
						
						for rel in obj.relations:
							if rel.type == 'when':
								continue
							
							return rel
						
						raise Exception("MIssmatched relations2???")
				
				return None
			
			if self.relationCache != None:
				root = self.getRootOfDataMap()
				name = self.getFullnameInDataModel()
				
				if root.relationOfCache.has_key(name):
					for r in root.relationOfCache[name]:
						r = self.find(r)
						if r != None and (type == None or r.type == type):
							return r

				return None
		
			# Back to native python due to bug fixes
			for r in self.getRelationsOfThisElement():
				if r.type == type:
					return r

			return None
		
		finally:
			self._unFixRealParent(self)
	
	def getRelationByName(self, name):
		relName = name[name.rfind(".")+1:]
		parentName = name[:name.rfind(".")]
		obj = self.getRootOfDataMap().getDataElementByName(parentName)
		
		if obj == None:
			print "Unable to locate:", parentName, name
		for r in obj:
			if r.name == relName:
				return r
		
		print "Returning None!"
		return None

	def getRelationsOfThisElement(self):
		'''
		Locate and return a relation of this element.
		'''
		
		relations = []
		
		if PeachModule.Engine.engine.Engine.relationsNew:
			# Assume both of and from relations in model
			
			for r in self.relations:
				# Lets not return "when" :)
				if r.type == 'when' or r.From == None:
					continue
				
				#print "Found of relation for", self.getFullDataName(), r.From
				self._fixRealParent(self)
				obj = self.find(r.From)
				self._unFixRealParent(self)
				
				if obj == None:
					raise Exception("Mismatched relations1??? [%s]" % r.From)
				
				for rel in obj.relations:
					if rel.type == 'when' or rel.of == None or not rel.of.endswith(self.name):
						continue
					
					#print rel.of
					relations.append(rel)
			
			#print "Not for", self.getFullDataName()
			return relations

		self._fixRealParent(self)
		if self.relationCache != None:
			#print "Using relation cache!"
			root = self.getRootOfDataMap()
			name = self.getFullnameInDataModel()
			
			if root.relationOfCache.has_key(name):
				for r in root.relationOfCache[name]:
					r = self.getRelationByName(r)
					if r != None:
						relations.append(r)
			
			self._unFixRealParent(self)
			return relations
		
		for r in self._genRelationsInDataModelFromHere(self, False):
			# Huh, do we break something here?
			if r.parent == None:
				raise Exception("Relation with no parent!")
			
			if r.type == 'when' or r.of == None:
				continue
			
			## The last part of both names must match
			## for it to ever be the same
			if r.of.split(".")[-1] != self.name:
				continue
			
			if r.getOfElement() == self:
				relations.append(r)
		
		self._unFixRealParent(self)
		return relations
	
	def getLastNamePart(self, name):
		'''Return the last part of a name:
		
		foo.bar.hello -- return hello
		'''
		
		names = name.split('.')
		return names[-1]

	def _genRelationsInDataModelFromHere(self, node = None, useCache = True):
		'''
		Instead of returning all relations starting with
		root we will walk up looking for relations.
		'''
		
		if node == None:
			node = self
		
		# Check if we are the top of the data model
		if node.parent == None or not node.parent.isDataElement:
			for r in self._getAllRelationsInDataModel(node, useCache):
				if r == None:
					continue
				
				yield r
			
		else:
			# If not start searching
			cur = node.parent
			while cur != None and cur.isDataElement:
				for r in self._getAllRelationsInDataModel(cur, useCache):
					if r == None:
						continue
					
					yield r
				
				cur = cur.parent
	
	def _getAllRelationsInDataModel(self, node = None, useCache = True):
		'''
		Generator that gets all relations in data model.
		'''
		
		if node == None:
			node = self.getRootOfDataMap()
		
		# Use cache if we have it
		if useCache and node.isDataElement and node.relationCache != None:
			root = self.getRootOfDataMap()
			for s in node.relationCache:
				relName = s[s.rfind(".")+1:]
				parentName = s[:s.rfind(".")]
				obj = root.getDataElementByName(parentName)
				
				if obj == None:
					continue
				
				for r in obj:
					if r.name == relName:
						yield r
			
			return
		
		for r in node.relations:
			if r.From == None:
				yield r
		
		for child in node._children:
			if child.isDataElement:
				for r in self._getAllRelationsInDataModel(child, useCache):
					yield r
	
	def isArray(self):
		'''
		Check if this data element is part of an array.
		'''
		
		if self.array != None:
			return True
	
	def getArrayCount(self):
		'''
		Return number of elements in array.
		'''
		
		if not self.isArray():
			return -1
		
		maxPos = int(self.arrayPosition)
		for c in self.parent:
			if c.isDataElement and c.array == self.array:
				if int(c.arrayPosition) > maxPos:
					maxPos = int(c.arrayPosition)
		
		return maxPos+1
	
	def getArrayElementAt(self, num):
		'''
		Return array element at position num.
		'''
		
		if not self.isArray():
			return None
		
		for c in self.parent:
			if c.isDataElement and c.array == self.array and int(c.arrayPosition) == num:
				return c
		
		return None

	def getCount(self):
		'''
		Return how many times this element occurs.  If it is part
		of an array the array size is returned, otherwise we will
		look at the min/max and any count relations.
		'''
		
		# If we are an array, we have a size already
		if self.isArray():
			return self.getArrayCount()
		
		# Sanity check
		if self.minOccurs == 1 and self.maxOccurs == 1:
			return 1
		
		# Otherwise see if we have a relation and min/max occurs
		rel = self.getRelationOfThisElement('count')
		if rel != None:
			try:
				#print "of:  ",self.getFullname()
				#print "from:",rel.parent.getFullname()
				#print rel.of
				#print rel.From
				cnt = int(rel.parent.getInternalValue())
				
				if cnt < self.minOccurs:
					cnt = self.minOccurs
				elif cnt > self.maxOccurs:
					cnt = self.maxOccurs
				
				return cnt
			
			except:
				# If relation wasn't set with number then ignore
				pass
		
		# If our minOccurs is larger than one and no relation
		# go with the min.
		if self.minOccurs > 1:
			return self.minOccurs
		
		return 1

	def getInternalValue(self):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int or long value.
		'''
		print self
		raise Exception("TODO: Implement me!")

	def getRelationValue(self, value):
		'''
		This is common logic that was being duplicated across several data
		elements.  The logic is used in getInternalValue() to check if a
		relation of size-of or count-of should modify the value.
		
		@rtype: string or number
		@return: the value passed in or an integer if the value needed to be changed.
		'''
		
		if self._HasSizeofRelation(self) and not self._inInternalValue:
			try:
				self._inInternalValue = True
				relation = self._GetSizeofRelation(self)
				#value = len(relation.getOfElement().getValue())
				value = relation.getOfElement().getSize()
				value = relation.setValue(value)
				#print "SIZE REALTION %s of %s: " % (relation.parent.name, relation.of), value
			
			finally:
				self._inInternalValue = False
		
		elif self._HasCountofRelation(self) and not self._inInternalValue:
			# This could cause recursion, use this variable to prevent
			self._inInternalValue = True
			try:
				
				relation = self._GetCountofRelation(self)
				ofElement = relation.getOfElement()
				
				# Ask for value before we get the count
				# Why do we do this?  When could this cause
				# the element to expand into an array?
				ofElement.getValue()
				
				#print "getRelationValue.count: ofElement:", ofElement.getFullname()
				value = ofElement.getCount()
				value = relation.setValue(value)
				#print "getRelationValue.count: getCount:", value
				#print "COUNT REALTION %s of %s: " % (relation.parent.name, relation.of), value
					
			finally:
				self._inInternalValue = False
		
		elif self._HasOffsetRelation() and not self._inInternalValue and self.getRootOfDataMap().relationStringBuffer != None:
			try:
				self._inInternalValue = True
				relation = self._GetOffsetRelation(self)
				ofElement = relation.getOfElement()
				#newValue = self.getRootOfDataMap().relationStringBuffer.getPosition(ofElement.getFullDataName())
				
				# Look for the nearest relationStringBuffer
				of = self.getRootOfDataMap().find(ofElement.getFullDataName())
				obj = of
				while obj.relationStringBuffer == None:
					obj = obj.parent
				
				newValue = obj.relationStringBuffer.getPosition(ofElement.getFullDataName())
				
				# Set value
				if newValue != None:
					value = relation.setValue(newValue)
			
			finally:
				self._inInternalValue = False
		
		return value
	
	def getRawValue(self, sout = None):
		'''
		Get the value of this data element pre-transformers.
		'''
		
		raise Exception("TODO: Implement me!")
	
	def isInvalidated(self):
		'''
		Check if we need to reproduce this value.
		
		If we have a relation always True.
		Otherwise False.
		'''
		
		if len(self.relations) > 0:
			return True
		
		return False

	def getSize(self):
		'''
		Determine length in bytes of this element.  Please
		override me and make faster :)
		'''
		
		# Default SLOW version
		return len(self.getValue())

	def getValue(self, sout = None):
		'''
		Get the value of this data element.
		'''
		
		## Check and see if we can just return our value
		
		#if self.value != None and not self.isInvalidated():
		#	if sout != None:
		#		sout.storePosition(self.getFullDataName())
		#		sout.write(self.value)
		#		
		#	return self.value
		
		## Otherwise lets generate and store our value
		
		# This method can be called while we are in it.
		# so lets not use self.value to hold anything.
		value = None
		
		if sout != None:
			sout.storePosition(self.getFullDataName())
		
		## If we have a cached value for ourselves, use it!
		if self.elementType not in ['template', 'block', 'choice', 'flags', \
									'xmlelement', 'xmlattribute', 'asn1type', 'custom']:
			if self.value != None and self.finalValue == None \
					and self.currentValue == None and self.fixup == None \
					and not self.hasRelation():
				
				if sout != None:
					sout.write(self.value)
				
				#print "getValue(%s): Using self.value" % self.name
				
				return self.value
		
		if self.transformer != None:
			#print "getValue(%s): Transformer will be applied" % self.name
			
			value = self.getRawValue()
			value = self.transformer.transformer.encode(value)
			
			if sout != None:
				sout.write(value)
		
		else:
			#print "getValue(%s): Using getrawvalue" % self.name
			value = self.getRawValue(sout)
			#print "getValue(%s): Using getrawvalue: %s" % (self.name, type(value))
			
		
		# See if we need to repeat ourselvs.
		if not self.isArray():
			count = self.getCount()
			if count > 1:
				#print "getValue(%s): Item is array, %d" % (self.name, count)
				origValue = value
				value = value * count
				
				if sout != None:
					sout.write(origValue * (count-1))
		
		if value == None:
			raise Exception("value is None for %s type %s" % (self.name, self.elementType))
		
		if self.elementType != 'flag' and type(value) == type(5):
			print "getValue(%s): WHOA, Returning integer!!!" % self.name
			print "self:",self
			print "self.name:",self.name
			print "self.getfullname", self.getFullDataName()
			print "self.maxOccurs", self.maxOccurs
			print "self.ref:",self.ref
			print "self.getInternalValue", self.getInternalValue()
			print "len(self._children)", len(self._children)
			for child in self:
				print "child:", child
				print "child.name", child.name
				print "child.getValue", child.getValue()
			raise Exception("WHOA, Returning integer!!")
		
		self.value = value
		return self.value
	
	def setDefaultValue(self, value):
		'''
		Set the default value for this data element.
		'''
		self.defaultValue = value
	
	def setValue(self, value):
		'''
		Set the current value for this data element
		'''
		self.currentValue = value
		self.getValue()
	
	def reset(self):
		'''
		Reset the value of this data element back to
		the default.
		'''
		self.currentValue = None
		self.value = None
		
	def resetDataModel(self, node = None):
		'''
		Reset the entire data model.
		'''
		
		if node == None:
			node = self.getRootOfDataMap()
		
		node.reset()
		
		for c in node._children:
			if c.isDataElement:
				self.resetDataModel(c)
	
	def _fixRealParent(self, node):
		'''
		Look for realParent attributes and
		enable that nodes correct parent.
		
		We could have multiple layers of realParents
		to deal with, so keep going until we find no more.
		'''
		
		#print "---> FIX REAL PARENT <-----", node
		#print traceback.format_stack()
		
		while True:
			# 1. Find root
			
			root = node
			while root.parent != None:
				root = root.parent
			
			# 2. Check if has a realParent
			
			if hasattr(root, 'realParent') and root.realParent != None:
				#print "FIXING:", root
				root.parent = root.realParent
			else:
				break
		
		# done!
	
	def _unFixRealParent(self, node):
		'''
		Locate any realParent attributes in our
		parent chain and enable them by setting
		that nodes parent to None.
		
		We could have several layers of realParents
		so check out each of our parents back to
		root.
		'''
		
		#print "---> UN-FIX REAL PARENT <-----", node
		#print traceback.format_stack()
		
		parents = [node]
		
		root = node
		#while root.parent != None and not root.parent.isDataElement:
		while root.parent != None and root.parent.isDataElement:
			root = root.parent
			parents.append(root)
		
		for parent in parents:
			# 1. Look for fake root
			if hasattr(parent, 'realParent') and parent.parent != None:
				# 2. Remove parent link
				#print "UNFIXING:", parent
				parent.parent = None

	def	calcLength(self):
		'''
		Calculate length
		'''
		
		environment = {
			'self' : self
			}
		
		try:
			self._fixRealParent(self)
			return evalEvent(self.lengthCalc, environment, self)
		finally:
			self._unFixRealParent(self)

class Transformer(ElementWithChildren):
	'''
	The Trasnfomer DOM object.  Should only be a child of
	a data element.
	'''
	def __init__(self, parent, transformer = None):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'transformer'
		
		# Instance of actual transformer
		self.transformer = transformer
		
		# Class string used to create transformer instance
		self.classStr = None
	
	def clone(self, obj = None):
		if obj == None:
			obj = Transformer(self.parent, self.transformer)
		
		obj.classStr = self.classStr
		
		return obj
	
	def changesSize(self):
		return self.transformer.changesSize()
	
class Fixup(ElementWithChildren):
	'''
	Fixup DOM element.  Child of data elements only.
	'''
	def __init__(self, parent, fixup = None):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'fixup'
		self.classStr = None
		self.fixup = fixup
		
	def clone(self, obj = None):
		
		if obj == None:
			obj = Fixup(self.parent, self.fixup)
		
		obj.elementType = self.elementType
		obj.classStr = self.classStr
		
		return obj
	
	
class Placement(ElementWithChildren):
	'''
	Indicates were a block goes after cracking.
	'''
	def __init__(self, parent):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'placement'
		self.after = None
		self.before = None
		
	def clone(self, obj = None):
		
		if obj == None:
			obj = Placement(self.parent)
		
		obj.elementType = self.elementType
		obj.after = self.after
		obj.before = self.before
		
		return obj

class Param(ElementWithChildren):
	def __init__(self, parent):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'param'
		self.valueType = 'string'


class Peach(ElementWithChildren):
	'''
	This is our root node container.
	'''
	def __init__(self):
		ElementWithChildren.__init__(self, 'peach', None)
		
		self.elementType = 'peach'
		self.version = None
		self.description = None
		self.author = None


class Test(ElementWithChildren):
	def __init__(self, name, parent = None):
		ElementWithChildren.__init__(self, name, parent)
		
		self.elementType = 'test'
		self.description = None
		self.template = None
		self.data = None
		self.publishers = None
		self.stateMachine = None
		self.ref = None
		self.mutators = None
		self.mutator = None

		# To mark Mutatable elements
		self.mutatables = []
		
	def getMutators(self):
		'''
		returns a lsit of mutators
		'''
		
		ret = []
		for m in self.mutators:
			if m.elementType == 'mutator':
				ret.append(m)
		
		return ret
	

	def markMutatableElements(self, node):
		if len(self.mutatables) == 0:
			return
		
		domDict = {}
		xmlDom = self.stateMachine.toXmlDomLight(node, domDict)
		
		for opt in self.mutatables:
			isMutable = opt[0]
			xpath = str(opt[1])
			
			try:
				xnodes = xmlDom.xpath(xpath)
				#print "XPATH: %s # of nodes: %s" % (xpath, str(len(xnodes)))
				if len(xnodes) == 0:
					print "Warning: XPath:[%s] must return at least an XNode. Please check your references or xpath declarations." % xpath
					continue
				
				for node in xnodes:
					try:
						elem = domDict[node]
		
						if isinstance(elem, Mutatable):
							elem.setMutable(isMutable)
							
					except KeyError:
						pass
							
			except SyntaxError:
				raise PeachException("Invalid xpath string: %s" % xpath)

class Run(ElementWithChildren):
	def __init__(self, name, parent = None):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'run'
		self.description = None
		self.tests = []
		self.parent = None
		self.waitTime = 0
	
	def getLogger(self):
		
		for child in self:
			if child.elementType == 'logger':
				return child
		
		return None


class Agent(ElementWithChildren):
	def __init__(self, name, parent = None):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'agent'
		self.description = None
		self.location = None
		self.password = None
	
	def getPythonPaths(self):
		p = []
		
		for child in self:
			if child.elementType == 'pythonpath':
				p.append({'name': child.name})
		
		if len(p) == 0:
			return None
		
		return p
	
	def getImports(self):
		p = []
		
		for child in self:
			if child.elementType == 'import':
				p.append({'import': child.importStr, 'from' : child.fromStr})
		
		if len(p) == 0:
			return None
		
		return p

class Monitor(ElementWithChildren):
	def __init__(self, name, parent = None):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'monitor'
		self.classStr = None
		self.params = {}

#############################################################################
## Data Generating Elements

class Template(DataElement):
	'''
	Essentially a Block, but is the top level element in a data model.
	
	TODO: Refactor this to DataModel
	'''
	
	ctypeClassName = 0
	
	def __init__(self, name):
		DataElement.__init__(self, name, None)
		self.elementType = 'template'
		self.ref = None
		self.length = None
		self.lengthType = None
	
	def clone(self, obj = None):
		
		if obj == None:
			obj = Template(self.name)
		
		DataElement.clone(self, obj)
		
		obj.ref = self.ref
		obj.length = self.length
		obj.lengthType = self.lengthType
		
		for c in self:
			obj.append( c.clone() )
		
		return obj
	
	def asCType(self):
		
		Template.ctypeClassName += 1
		ctypeClassName = Template.ctypeClassName
		
		exec("""class TemplateTempClass%d(ctypes.Structure):
	pass
""" % ctypeClassName)
		
		values = []
		fields = []
		for c in self:
			if c.isDataElement:
				cValue = c.asCType()
				fields.append((c.name, type(cValue)))
				values.append((c.name, cValue))
		
		exec("TemplateTempClass%d._fields_ = fields" % ctypeClassName)
		exec("ret = TemplateTempClass%d()" % ctypeClassName)
		
		for c in values:
			setattr(ret, c[0], c[1])
		
		# Are we a pointer?
		if self.isPointer:
			if self.pointerDepth != None:
				for i in range(int(self.pointerDepth)):
					ret = ctypes.pointer(ret)
			else:
				ret = ctypes.pointer(ret)
		
		return ret
	
	def asCTypeType(self):
		
		Template.ctypeClassName += 1
		ctypeClassName = Template.ctypeClassName
		
		exec("""class TemplateTempClass%d(ctypes.Structure):
	pass
""" % ctypeClassName)
		
		values = []
		fields = []
		for c in self:
			if c.isDataElement:
				cValue = c.asCType()
				fields.append((c.name, type(cValue)))
				values.append((c.name, cValue))
		
		exec("TemplateTempClass%d._fields_ = fields" % ctypeClassName)
		exec("ret = TemplateTempClass%d" % ctypeClassName)
		
		# Are we a pointer?
		if self.isPointer:
			if self.pointerDepth != None:
				for i in range(int(self.pointerDepth)):
					ret = ctypes.POINTER(ret)
			else:
				ret = ctypes.POINTER(ret)
		
		return ret
	
	def getSize(self):
		'''
		Return the length of this data element.  Try and
		be fast about it!
		'''
		
		if self.transformer != None and not self.transformer.changesSize():
			return len(self.getValue())
		
		if self.fixup != None:
			return len(self.getValue())
		
		if self.currentValue != None:
			return len(self.getValue())
		
		size = 0
		for c in self:
			if c.isDataElement:
				size += c.getSize()
		
		return size
	
	def hasLength(self):
		if self.length != None:
			return True
		
		return False
	
	def getLength(self):
		'''
		Get the length of this element.
		'''
		
		if self.lengthType == 'calc':
			self.length = self.calcLength()
		
			if self.length != None and self.length < 0:
				self.length = None
		
		elif self.isStatic:
			return len(self.getValue())
		
		return self.length
	
	def getValue(self, sout = None):
		'''
		Template needs a custom getValue method!
		'''
		try:
			# Sometimes a Template becomes a Block
			if self.elementType == 'template':
				self.relationStringBuffer = sout
			
			return DataElement.getValue(self, sout)
			
		finally:
			self.relationStringBuffer = None
	
	def isInvalidated(self):
		'''
		Check if we need to reproduce this value.
		
		If we have a relation always True.
		Otherwise False.
		'''
		
		if len(self.relations) > 0:
			return True
		
		# Check children
		for c in self:
			if c.isDataElement and c.isInvalidated():
				return True
		
		# Return false
		return False
	
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		
		@type	sout: StreamBuffer
		@param	sout: Output stream
		'''
		
		#print "getInternalValue(%s)" % self.name
		value = ""
		
		# 0. If using a stream store our location
		if sout != None:
			pos = sout.storePosition(self.getFullDataName())
		
		# 1. Override with currentValue
		
		if self.currentValue != None:
			#print "getInternalValue(%s): using currentValue" % self.name
			
			value = self.currentValue
			if sout != None:
				sout.write(value, self.getFullDataName())
		
			return value
		
		# 2. Get value from children
		
		for c in self:
			if c.isDataElement:
				try:
					if self.fixup != None or self.transformer != None:
						cv = c.getValue()
						
						#if type(cv) == type(5):
						#	print "getInternalValue(%s): int value for" % self.name, c
					
						value += cv
					else:
						cv = c.getValue(sout)
						
						#if type(cv) == type(5):
						#	print "getInternalValue(%s): int value for" % self.name, c
						#	print "c.name", c.name
						#	print "c.ref", c.ref
						
						value += cv
				
				except:
					print sys.exc_info()
					#print "value:", type(value)
					#print "value: [%s]" % repr(value)
					#print "c", c
					#print "c.name: %s" % c.name
					#print "c.type: %s" % c.elementType
					#if c.elementType == 'block':
					#	try:
					#		print "c[0]", c[0]
					#		print "c.ref", c.ref
					#		if c[0].elementType == 'choice':
					#			print "c[0].currentElement", c[0].currentElement
					#			print "c[0].currentElement.name", c[0].currentElement.name
					#			print "c[0].currentElement.ref", c[0].currentElement.ref
					#			#print "c[0].currentElement[0]", c[0].currentElement[0]
					#	except:
					#		pass
					
					raise
		
		# 3. Fixup
		
		if self.fixup != None:
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
				if sout != None:
					sout.write(value, self.getFullDataName())
		
		#if type(value) == type(5):
		#	print "WARNING: Returning integer from block!!!!"
		#	print self
		#	print self.name
		#	print self.ref
		#	raise Exception("ERROR, RETURNING INT!")
		
		return value

	def getRawValue(self, sout = None):
		'''
		Get value for this data element.
			
		Performs any needed transforms to produce
		value.
		'''
		
		#print "getRawValue(%s)" % self.name
		return self.getInternalValue(sout)
		
	def setValue(self, value):
		'''
		Override value created via children.
		'''
		
		self.currentValue = value
	
	def reset(self):
		'''
		Reset current state.
		'''
		self.currentValue = None
		self.value = None


class Choice(DataElement):
	'''
	Choice, chooses one or emore sub-elements
	'''
	def __init__(self, name, parent):
		'''
		Don't put too much logic here.  See HandleBlock in the parser.
		'''
		DataElement.__init__(self, name, parent)
		self.elementType = 'choice'
		self.currentElement = None
		self.length = None
		self.lengthType = None
		
		#: Used by cracker to optimize choice cracking
		self.choiceCache = (False, 0, None)

	def clone(self, obj = None):
		
		if obj == None:
			obj = Choice(self.name, self.parent)
		
		DataElement.clone(self, obj)
		
		obj.currentElement = self.currentElement
		obj.elementType = self.elementType
		obj.length = self.length
		obj.lengthType = self.lengthType
		
		for c in self:
			obj.append( c.clone() )
		
		return obj
	
	def asCType(self):
		
		self.getValue()
		return self.currentElement.asCType()
	
	def getSize(self):
		'''
		Return the length of this data element.  Try and
		be fast about it!
		'''
		
		if self.transformer != None or self.fixup != None:
			return len(self.getValue())
		
		if self.currentElement != None:
			return self.currentElement.getSize()
		
		if self.currentValue != None:
			return len(self.getValue())
		
		return len(self.getValue())
	
	def hasLength(self):
		if self.length != None:
			return True
		
		return False
	
	def getLength(self):
		'''
		Get the length of this element.
		'''
		
		if self.lengthType == 'calc':
			self.length = self.calcLength()
		
			if self.length != None and self.length < 0:
				self.length = None
		
		elif self.isStatic:
			return len(self.getValue())
		
		return self.length
	
	
	def SelectedElement(self, value = None):
		
		if value != None:
			self.currentElement = self[value]
		
		return self.currentElement
	
	def isInvalidated(self):
		'''
		Check if we need to reproduce this value.
		
		If we have a relation always True.
		Otherwise False.
		'''
		
		if len(self.relations) > 0:
			return True
		
		# Check children
		if self.currentElement == None:
			return True
		
		if self.currentElement.isInvalidated():
			return True
		
		# Return false
		return False
	
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		return self.getRawValue(sout)
		
	def getRawValue(self, sout = None):
		
		value = ""
		if self.currentValue != None:
			value = self.currentValue
			if sout != None:
				sout.write(value, self.getFullDataName())
		
		else:
			if self.currentElement == None:
				for n in self:
					if n.isDataElement:
						self.currentElement = n
						break
			
			value = self.currentElement.getValue(sout)
			
		if value == None or type(value) != type(""):
			print "Choice.getRawValue: value is null or string!", type(value)
			print "Choice.getRawValue: ", self.currentElement.getFullname()
			print "Choice.getRawValue: ", self.currentElement.elementType
			print "Choice.getRawValue: ", self.currentElement
			raise Exception("Value should not be null or string!")
		
		return value

def BlockToXml(self, parent):
	node = parent.rootNode.createElementNS(None, 'Block')
	parent.appendChild(node)
	
	self._setAttribute(node, 'name', self.name)
	self._setAttribute(node, 'ref', self.ref)
		
	for child in self:
		if self._xmlHadChild(child):
			child.toXml(node)
	
	return node

class Block(DataElement):
	'''
	Block or sequence of other data types.
	'''
	
	ctypeClassName = 0
	
	def __init__(self, name, parent):
		'''
		Don't put too much logic here.  See HandleBlock in the parser.
		'''
		DataElement.__init__(self, name, parent)
		self.elementType = 'block'
		self.toXml = new.instancemethod(PeachModule.Engine.dom.BlockToXml, self, self.__class__)
		self.length = None
		self.lengthType = None
		
	def clone(self, obj = None):
		
		if obj == None:
			obj = Block(self.name, self.parent)
		
		DataElement.clone(self, obj)
		
		obj.elementType = self.elementType
		obj.length = self.length
		obj.lengthType = self.lengthType
		
		for c in self:
			obj.append( c.clone() )
		
		if obj.getValue() != self.getValue():
			print "Value missmatch"
			sys.exit(0)
		for item in dir(self):
			if not hasattr(obj, item):
				print "Missing:", item
				sys.exit(0)
		return obj
	
	def asCType(self):
		
		Block.ctypeClassName += 1
		ctypeClassName = Block.ctypeClassName
		
		exec("""class BlockTempClass%d(ctypes.Structure):
	pass
""" % ctypeClassName)
		
		values = []
		fields = []
		for c in self:
			if c.isDataElement:
				cValue = c.asCType()
				fields.append( (c.name, type(cValue) ) )
				values.append((c.name, cValue))
		
		exec("BlockTempClass%d._fields_ = fields" % ctypeClassName)
		exec("ret = BlockTempClass%d()" % ctypeClassName)
		
		for c in values:
			setattr(ret, c[0], c[1])
		
		# Are we a pointer?
		if self.isPointer:
			if self.pointerDepth != None:
				for i in range(int(self.pointerDepth)):
					ret = ctypes.pointer(ret)
			else:
				ret = ctypes.pointer(ret)
		
		return ret
	
	def asCTypeType(self):
		
		Block.ctypeClassName += 1
		ctypeClassName = Block.ctypeClassName
		
		exec("""class BlockTempClass%d(ctypes.Structure):
	pass
""" % ctypeClassName)
		
		values = []
		fields = []
		for c in self:
			if c.isDataElement:
				cValue = c.asCType()
				fields.append( (c.name, type(cValue) ) )
				values.append((c.name, cValue))
		
		exec("BlockTempClass%d._fields_ = fields" % ctypeClassName)
		exec("ret = BlockTempClass%d" % ctypeClassName)
		
		# Are we a pointer?
		if self.isPointer:
			if self.pointerDepth != None:
				for i in range(int(self.pointerDepth)):
					ret = ctypes.POINTER(ret)
			else:
				ret = ctypes.POINTER(ret)
		
		return ret
	
	def hasLength(self):
		if self.length != None:
			return True
		
		return False
	
	def getLength(self):
		'''
		Get the length of this element.
		'''
		
		if self.lengthType == 'calc':
			self.length = self.calcLength()
		
			if self.length != None and self.length < 0:
				self.length = None
		
		elif self.isStatic:
			return len(self.getValue())
		
		return self.length
	
	def isInvalidated(self):
		'''
		Check if we need to reproduce this value.
		
		If we have a relation always True.
		Otherwise False.
		'''
		
		if len(self.relations) > 0:
			return True
		
		# Check children
		for c in self:
			if c.isDataElement:
				if c.isInvalidated():
					return True
		
		# Return false
		return False
	
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		
		@type	sout: StreamBuffer
		@param	sout: Output stream
		'''
		
		#print "Block.getInternalValue(%s)" % self.name
		value = ""
		
		# 0. If using a stream store our location
		if sout != None:
			pos = sout.storePosition(self.getFullDataName())
		
		# 1. Override with currentValue
		
		if self.currentValue != None:
			value = str(self.currentValue)
			if sout != None:
				sout.write(value, self.getFullDataName())
		
			return value
		
		# 2. Get value from children
		
		if self.transformer == None and self.fixup == None:
			for c in self:
				if c.isDataElement:
					try:
						value += c.getValue(sout)
					
					except:
						print c
						print repr(value)
						print repr(c.getValue(sout))
						print "c.getValue(sout) failed." + repr(sys.exc_info())
						print "c.name: %s" % c.name
						traceback.print_stack()
						print "---------------"
						raise
				else:
					print "FOUND NON DATAELEMENT:", c
		
		else:
			
			# To support offset relations in children we will
			# get the value twice using our own stringBuffer
			
			stringBuffer = StreamBuffer()
			self.relationStringBuffer = stringBuffer
			
			for c in self:
				if c.isDataElement:
					try:
						#print "Block.getInternalValue(%s): Getting child value" % self.name
						value += c.getValue(stringBuffer)
					
					except:
						#print "value: [%s]" % repr(value)
						print "c.name: %s" % c.name
						print "---------------"
						raise
			
			stringBuffer.setValue("")
			stringBuffer.seekFromStart(0)
			value = ""
			
			for c in self:
				if c.isDataElement:
					try:
						value += c.getValue(stringBuffer)
					
					except:
						#print "value: [%s]" % repr(value)
						print "c.name: %s" % c.name
						print "---------------"
						raise
		
		# 3. Fixup
		
		if self.fixup != None:
			#print "Block.getInternalValue(%s): Using fixup" % self.name
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
				if sout != None:
					sout.write(value, self.getFullDataName())
		
		if value == None:
			raise Exception("value should not be None here")
		
		return value
	
	def getRawValue(self, sout = None):
		'''
		Get value for this data element.
		
		Performs any needed transforms to produce
		value.
		'''
		
		return self.getInternalValue(sout)


class Number(DataElement):
	'''
	A numerical field
	'''
	
	_allowedSizes = [8, 16, 24, 32, 64]
	
	#: Default value used for size
	defaultSize = 8
	#: Default value used for endian
	defaultEndian = 'little'
	#: Default value used for signed
	defaultSigned = False
	#: Default value used for valueType
	defaultValueType = 'string'
	
	def __init__(self, name, parent):
		DataElement.__init__(self, name, parent)
		self.elementType = 'number'
		
		self.size = Number.defaultSize
		self.signed = Number.defaultSigned
		self.valueType = Number.defaultValueType
		
		# When None, the property method will
		# return the default.  This allows tricky users
		# to change Endian ness after we start cracking
		# a template file.
		self._endian = None
		
		self.ref = None
		self.currentValue = None
		self.generatedValue = None
		self.insideRelation = False
	
	def clone(self, obj = None):
		
		if obj == None:
			obj = Number(self.name, self.parent)
		
		DataElement.clone(self, obj)
		
		obj.size = self.size
		obj.signed = self.signed
		obj.valueType = self.valueType
		obj._endian = self._endian
		obj.ref = self.ref
		obj.insideRelation = self.insideRelation
		
		return obj
	
	def getEndian(self):
		if self._endian == None:
			return Number.defaultEndian
		
		return self._endian
	def setEndian(self, value):
		self._endian = value
	endian = property(getEndian, setEndian, None)
	
	def asCType(self):
		
		if self.size == 24:
			raise Exception("Number.asCType does not support 24bit numbers")
		
		value = int(self.getInternalValue())
		ret = None
		
		if self.signed:
			evalString = "ctypes.c_int%d(value)" % (self.size)
		else:
			evalString = "ctypes.c_uint%d(value)" % (self.size)
		
		ret = eval(evalString)
		
		return ret
	
	def getSize(self):
		'''
		Return the length of this data element.  Try and
		be fast about it!
		'''
		
		# Note in the case of numbers a fixup will not
		# make a difference
		if self.transformer != None:
			return len(self.getValue())
		
		return self.size/8
	
	def getMinValue(self):
		'''
		Get the minimum value this number can have.
		'''
		
		if not self.signed:
			return 0
		
		max = long('FF'*(self.size/8), 16)
		return 0 - max
	
	def getMaxValue(self):
		'''
		Get the maximum value for this number.
		'''
		max = long('FF'*(self.size/8), 16)
		if self.signed:
			return max/2
		
		return max
	
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		
		# 0. Override default?
		if self.currentValue != None:
			return self.currentValue
			
		# 1. Our value to return
		value = 0
		
		# 2. Have default value?
		
		if self.defaultValue != None:
			value = self.defaultValue
		
		# 3. Relation?
		
		value = self.getRelationValue(value)
		
		# 4. fixup?
		if self.fixup != None:
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
		
		if sout != None:
			sout.write(value, self.getFullDataName())
		
		return value
	
	def pack(self, num):
		'''
		Pack a number into proper format for this Number
		'''
		
		# 1. Get the transformer we need
		isSigned = 0
		if self.signed:
			isSigned = 1
		
		isLittleEndian = 0
		if self.endian == 'little':
			isLittleEndian = 1
		
		if self.size == 8:
			trans = Transformers.type.AsInt8(isSigned, isLittleEndian)
		elif self.size == 16:
			trans = Transformers.type.AsInt16(isSigned, isLittleEndian)
		elif self.size == 24:
			trans = Transformers.type.AsInt24(isSigned, isLittleEndian)
		elif self.size == 32:
			trans = Transformers.type.AsInt32(isSigned, isLittleEndian)
		elif self.size == 64:
			trans = Transformers.type.AsInt64(isSigned, isLittleEndian)

		# 2. Encode number
		
		try:
			# This could fail if our override was not
			# a number or empty ('')
			num = long(num)
		except:
			num = 0
			
		return trans.encode(long(num))
	
	def unpack(self, buff):
		'''
		Unpack a number from proper format fo this Number
		'''
		# 1. Get the transformer we need
		isSigned = 0
		if self.signed:
			isSigned = 1
		
		isLittleEndian = 0
		if self.endian == 'little':
			isLittleEndian = 1
		
		if self.size == 8:
			trans = Transformers.type.AsInt8(isSigned, isLittleEndian)
		elif self.size == 16:
			trans = Transformers.type.AsInt16(isSigned, isLittleEndian)
		elif self.size == 24:
			trans = Transformers.type.AsInt24(isSigned, isLittleEndian)
		elif self.size == 32:
			trans = Transformers.type.AsInt32(isSigned, isLittleEndian)
		elif self.size == 64:
			trans = Transformers.type.AsInt64(isSigned, isLittleEndian)

		# 2. Encode number
		
		try:
			# This could fail if our override was not
			# a number or empty ('')
			return trans.decode(buff)
		
		except:
			pass
		
		return 0
	
	def getRawValue(self, sout = None):
		
		value = self.getInternalValue()
		if value == '':
			return ''
		
		ret = self.pack(value)
		
		if sout != None:
			sout.write(ret, self.getFullDataName())
		
		return ret

try:
	from pyasn1.type import univ, char, useful
	import pyasn1.codec.ber.encoder
	import pyasn1.codec.cer.encoder
	import pyasn1.codec.der.encoder
	from pyasn1.type import tag
	
	class Asn1Type(DataElement):
		'''
		An XML Element
		'''
		
		ASN1_TYPES = ["BitString", "Boolean", "Choice", "Enumerated", "Integer", "Null",
					  "ObjectIdentifier", "OctetString", "Real", "Sequence",
					  "SequenceAndSetBase", "SequenceOf", "Set", "SetOf"]
		
		ASN1_ENCODE = ["ber", "cer", "der"]
		
		ASN1_MAP = {
			"BitString":univ.BitString,
			"Boolean":univ.Boolean,
			"Choice":univ.Choice,
			"Enumerated":univ.Enumerated,
			"Integer":univ.Integer,
			"Null":univ.Null,
			"ObjectIdentifier":univ.ObjectIdentifier,
			"OctetString":univ.OctetString,
			"Real":univ.Real,
			"Sequence":univ.Sequence,
			"SequenceAndSetBase":univ.SequenceAndSetBase,
			"SequenceOf":univ.SequenceOf,
			"Set":univ.Set,
			"SetOf":univ.SetOf,
			"UTF8String":char.UTF8String,
			"NumericString":char.NumericString,
			"PrintableString":char.PrintableString,
			"TeletexString":char.TeletexString,
			"VideotexString":char.VideotexString,
			"IA5String":char.IA5String,
			"GraphicString":char.GraphicString,
			"VisibleString":char.VisibleString,
			"GeneralString":char.GeneralString,
			"UniversalString":char.UniversalString,
			"BMPString":char.BMPString,
			"GeneralizedTime":useful.GeneralizedTime,
			"UTCTime":useful.UTCTime,
			}
		
		ASN1_TAG_CLASS_MAP = {
			"universal" : 0x00,
			"application" : 0x40,
			"context" : 0x80,
			"private" : 0xc0,
			}
		
		ASN1_TAG_TYPE_MAP = {
			"simple" : 0x00,
			"constructed" : 0x20,
			}
		
		ASN1_TAG_CAT_MAP = {
			"implicit":0x01,
			"explicit":0x02,
			"untagged":0x04,
			}
		
		def __init__(self, name, parent):
			DataElement.__init__(self, name, parent)
			self.elementType = 'asn1type'
			self.currentValue = None
			self.generatedValue = None
			self.insideRelation = False
			self.asn1Type = ""
			self.encodeType = "ber"
			self.tagClass = None
			self.tagFormat = None
			self.tagCategory = None
			self.tagNumber = None
		
		def clone(self, obj = None):
			
			if obj == None:
				obj = Asn1Type(self.name, self.parent)
			
			DataElement.clone(self, obj)
			
			obj.elementType = self.elementType
			obj.insideRelation = self.insideRelation
			obj.asn1Type = self.asn1Type
			obj.encodeType = self.encodeType
			
			return obj
		
		def asCType(self):
			# TODO: Should support Ctype, return a string or something...
			raise Exception("This DataElement (Asn1Type) does not support asCType()!")
		
		def int2bin(self, n, count=32):
			"""returns the binary of integer n, using count number of digits"""
			return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])
		
		def blob2bin(self, data):
			ret = ""
			for b in data:
				ret += self.int2bin(ord(b), 8)
			
			return ret

		def getInternalValue(self, sout = None, parent = None):
			'''
			Return the internal value of this date element.  This
			value comes before any modifications such as packing,
			padding, truncating, etc.
			
			For Numbers this is the python int value.
			'''
			try:
			
				if parent == None:
					haveParent = False
				elif isinstance(parent, Asn1Type):
					haveParent = True
				
				asn1Obj = None
				value = None
				childAsn1Objs = []
				for c in self:
					if isinstance(c, Asn1Type):
						childAsn1Objs.append(c.getInternalValue(None, self))
					
					elif self.asn1Type == 'BitString' and c.isDataElement:
						b = c.getValue()
						b = self.blob2bin(b)
						if b[:8] == '00000000':
							b = b[8:]
						
						value = "'%s'B" % b
						
					elif isinstance(c, Number):
						value = long(c.getInternalValue())
					
					elif c.isDataElement:
						value = c.getValue()
				
				if value != None:
					#if (self.objType == int or self.objType == long):
					#	if type(value) not in [int, long]:
					#		try:
					#			value = long(value)
					#		except:
					#			value = long(0)
					
					try:
						if self.tagNumber != None:
							if self.tagCategory == "implicit":
								tagSet=self.ASN1_MAP[self.asn1Type].tagSet.tagImplicitly(
									tag.Tag(self.tagClass, self.tagFormat, self.tagNumber))
							else:
								tagSet=self.ASN1_MAP[self.asn1Type].tagSet.tagExplicitly(
									tag.Tag(self.tagClass, self.tagFormat, self.tagNumber))
							
							asn1Obj = self.ASN1_MAP[self.asn1Type](value, tagSet = tagSet)
							
						else:
							asn1Obj = self.ASN1_MAP[self.asn1Type](value)
					except:
						#raise SoftException("Error building asn.1 obj")
						print sys.exc_info()
						raise PeachException("Error building asn.1 obj")
				
				else:
					try:
						#asn1Obj = self.ASN1_MAP[self.asn1Type](self.asnTagSet, self.asn1Spec)
						if self.tagNumber != None:
							if self.tagCategory == "implicit":
								tagSet=self.ASN1_MAP[self.asn1Type].tagSet.tagImplicitly(
									tag.Tag(self.tagClass, self.tagFormat, self.tagNumber))
							else:
								tagSet=self.ASN1_MAP[self.asn1Type].tagSet.tagExplicitly(
									tag.Tag(self.tagClass, self.tagFormat, self.tagNumber))
							
							asn1Obj = self.ASN1_MAP[self.asn1Type](tagSet = tagSet)
						
						else:
							asn1Obj = self.ASN1_MAP[self.asn1Type]()
						
					except:
						print sys.exc_info()
						raise PeachException("Error building asn.1 obj")
				
				if len(childAsn1Objs) > 0:
					for i in range(len(childAsn1Objs)):
						asn1Obj.setComponentByPosition(i, childAsn1Objs[i])
				
				if not haveParent:
					# Perform encoding ourselves
					encoder = eval("pyasn1.codec.%s.encoder" % self.encodeType)
					
					try:
						#print asn1Obj
						bin = encoder.encode(asn1Obj)
					except:
						print self.encodeType
						print encoder
						print asn1Obj
						print sys.exc_info()
						raise SoftException("Error encoding asn.1 obj")
					
					#print asn1Obj
					
					return bin
					
				# Otherwise allow parent to perform encoding
				return asn1Obj
			
			except:
				print sys.exc_info()
				print "Warning, ASN.1 Failed to emmit, this is OK after first iteration."
				return ""
			
			return None
		
		def getRawValue(self, sout = None, parent = None):
			return self.getInternalValue(sout, parent)
	
except:
	pass

class XmlElement(DataElement):
	'''
	An XML Element
	'''
	
	def __init__(self, name, parent):
		DataElement.__init__(self, name, parent)
		self.elementType = 'xmlelement'
		self.currentValue = None
		self.generatedValue = None
		self.insideRelation = False
		self.elementName = None
		self.xmlNamespace = None
	
	def asCType(self):
		# TODO: Should support Ctype, return a string or something...
		raise Exception("This DataElement (XmlElement) does not support asCType()!")
	
	def toXmlDomLight(self, parent, dict):
		'''
		Convert to an XML DOM object tree for use in xpath queries.
		Does not include values (Default or otherwise)
		'''
		
		owner = parent.ownerDocument
		if owner == None:
			owner = parent
		
		#if hasattr(self, 'ref') and self.ref != None:
		#	node = owner.createElementNS(None, self.ref)
		#else:
		node = owner.createElementNS(None, self.name)
		
		node.setAttributeNS(None, "elementType", self.elementType)
		node.setAttributeNS(None, "name", self.name)
		node.setAttributeNS(None, "elementName", self.elementName)
		
		if hasattr(self, 'ref') and self.ref != None:
			self._setXmlAttribute(node, "ref", self.ref)
		
		self._setXmlAttribute(node, "fullName", self.getFullname())
		
		dict[node] = self
		dict[self] = node
		
		parent.appendChild(node)
		
		return node

	def getInternalValue(self, sout = None, parent = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		# 0. If using a stream store our location
		if sout != None:
			pos = sout.storePosition(self.getFullDataName())
		
		# 1. Override with currentValue
		
		if self.currentValue != None:
			value = str(self.currentValue)
			if sout != None:
				sout.write(value, self.getFullDataName())
		
			return value
		
		if parent == None:
			haveParent = False
			parent = getDOMImplementation().createDocument(EMPTY_NAMESPACE, None, None)
			doc = parent
		else:
			haveParent = True
			doc = parent.ownerDocument
		
		node = doc.createElementNS(self.xmlNamespace, self.elementName)
		parent.appendChild(node)
		
		for c in self:
			if isinstance(c, XmlAttribute):
				c.getInternalValue(None, node)
			
			elif isinstance(c, XmlElement):
				c.getInternalValue(None, node)
				
			elif c.isDataElement:
				node.appendChild(doc.createTextNode(c.getValue().decode('latin-1').encode('utf8')))
				#node.appendChild(doc.createTextNode(c.getValue()))
		
		if not haveParent:
			
			try:
				encoding = "utf8"
				unistr = doc.toxml().replace(u'<?xml version="1.0" ?>\n', u'')
				return unistr.encode(encoding, 'xmlcharrefreplace')
				#return unistr
			except:
				return u""
		
		return None
	
	def getRawValue(self, sout = None, parent = None):
		return self.getInternalValue(sout, parent)

class XmlAttribute(DataElement):
	'''
	An XML Element
	'''
	
	def __init__(self, name, parent):
		DataElement.__init__(self, name, parent)
		self.elementType = 'xmlattribute'
		self.currentValue = None
		self.generatedValue = None
		self.insideRelation = False
		self.attributeName = None
		self.xmlNamespace = None
	
	def asCType(self):
		raise Exception("This DataElement (XmlAttribute) does not support asCType()!")
	
	def getInternalValue(self, sout, parent):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		
		if parent == None:
			return u""
		
		value = ""
		for c in self:
			if c.isDataElement:
				value = c.getValue()
				break
		
		parent.setAttributeNS(self.xmlNamespace, self.attributeName, value.decode('latin-1').encode('utf8'))
		
		return None
	
	def getRawValue(self, sout = None, parent = None):
		return self.getInternalValue(sout, parent)


class String(DataElement):
	'''
	A string field
	'''
	
	EncodeAs = {
		'char':'iso-8859-1',
		'wchar':'utf-16le',
		'utf8':'utf-8',
		'utf-8':'utf-8',
		'utf-16le' : 'utf-16le',
		'utf-16be' : 'utf-16be'
		}
	
	#: Default value for valueType
	defaultValueType = 'string'
	#: Default value for lengthTYpe
	defaultLengthType = 'string'
	#: Default value for padCharacter
	defaultPadCharacter = '\0'
	#: Default value for type
	defaultType = 'char'
	#: Default value for nullTerminated
	defaultNullTerminated = False
	
	def __init__(self, name = None, parent = None):
		DataElement.__init__(self, name, parent)
		self.elementType = 'string'
		self.valueType = String.defaultValueType
		self.defaultValue = None
		self.isStatic = False
		self.lengthType = String.defaultLengthType
		self.lengthCalc = None
		self.length = None
		self.minOccurs = 1
		self.maxOccurs = 1
		self.generatedOccurs = 1
		self.currentValue = None
		self.insideRelation = False
		self.analyzer = None
		
		#: Value to pad string with, defaults to NULL '\0'
		self.padCharacter = String.defaultPadCharacter
		#: Type of string, currently only char and wchar are supported.
		self.type = String.defaultType
		#: Is string null terminated, defaults to false
		self.nullTerminated = String.defaultNullTerminated
		#: DEPRICATED, Use hint instead
		self.tokens = None
	
	def clone(self, obj = None):
		
		if obj == None:
			obj = String(self.name, self.parent)
		
		DataElement.clone(self, obj)
		
		obj.valueType = self.valueType
		obj.length = self.length
		obj.lengthType = self.lengthType
		obj.lengthCalc = self.lengthCalc
		obj.insideRelation = self.insideRelation
		obj.analyzer = self.analyzer
		obj.padCharacter = self.padCharacter
		obj.type = self.type
		obj.nullTerminated = self.nullTerminated
		
		return obj
	
	def asCType(self):
		
		if self.type == 'wchar':
			return ctypes.c_wchar_p(self.getInternalValue())
		else:
			return ctypes.c_char_p(self.getInternalValue().encode(self.EncodeAs[self.type]))
		
	def getLength(self, inRaw = True):
		'''
		Get the length of this element.
		'''
		
		if not inRaw and (self.currentValue != None or self.isStatic):
			return len(self.getValue())
		
		if self.lengthType == 'calc':
			self.length = self.calcLength()
		
			if self.length != None and self.length < 0:
				self.length = None
		
		return self.length
		
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		
		# 0. Override value?
		if self.currentValue != None:
			
			# Make sure we null terminate if needed
			if self.nullTerminated:
				if self.currentValue[-1] != 0:
					self.currentValue = self.currentValue + "\0"
			
			if sout != None:
				sout.write(self.currentValue, self.getFullDataName())
			
			return self.currentValue
			
		# 1. Init value
		value = ""
		
		# 3. default value?
		if self.defaultValue != None:
			value = self.defaultValue
		
		# 4. Relations
		
		value = self.getRelationValue(value)
		if not type(value) in [str, unicode]:
			value = str(value)
		
		# 5. fixup
		
		if self.fixup != None:
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
		
		if sout != None:
			sout.write(value, self.getFullDataName())
		
		return value
		
	def getRawValue(self, sout = None):
		
		# finalValue overrides everything!
		if self.finalValue != None:
			value = self.finalValue
		
		else:
			
			# 0. Override value?
			if self.currentValue != None:
				value = self.currentValue
				
			else:
				# 1. Init value
				value = self.getInternalValue()
				
				if len(value) < self.length:
					value += self.padCharacter * (self.length - len(value))
				else:
					value = value[:self.length]
			
			# 7. Null terminated strings
			# Lets try null terminating even the mutated value.  Might as well!
			if self.nullTerminated and (len(value) == 0 or value[-1] != '\0'):
				value += '\0'
			
			# Encode, but only when needed or we get errorzZzz
			if type(value) != str and self.type == 'char':
				value = value.encode(self.EncodeAs['char'])
			
			elif self.type != 'char':
				if type(value) == str:
					value = value.decode(self.EncodeAs['char'])
				
				value = value.encode(self.EncodeAs[self.type])
		
		
		# Even for final values we must return binary strings
		# this will "encode" them as such
		if type(value) != str:
			value = value.encode(self.EncodeAs['char'])
		
		# Output
		
		if sout != None:
			sout.write(value, self.getFullDataName())
			
		#if type(value) != str:
		#	print "[%s]" % value
		#	raise Exception("Whoa, string not str!!")
		
		return value


def ToXmlCommonDataElements(element, node):
	element._setAttribute(node, 'minOccurs', str(element.minOccurs))
	element._setAttribute(node, 'maxOccurs', str(element.maxOccurs))
	element._setAttribute(node, 'generatedOccurs', str(element.generatedOccurs))
	
	# Generators
	for child in element.extraGenerators:
		if element._xmlHadChild(child):
			child.toXml(node)
	
	# Relations
	for child in element.relations:
		if element._xmlHadChild(child):
			child.toXml(node)
	
	# Transformer
	if element.transformer != None:
		if element._xmlHadChild(child):
			child.toXml(node)
	

class Flags(DataElement):
	'''
	Set of flags
	'''
	
	#: Default value for endian
	defaultEndian = 'little'
	
	def __init__(self, name, parent):
		DataElement.__init__(self, name, parent)
		self.elementType = 'flags'
		self.length = None	# called size
		self.endian = Flags.defaultEndian
		self.rightToLeft = False
		self.padding = False

	def clone(self, obj = None):
		
		if obj == None:
			obj = Flags(self.name, self.parent)
		
		DataElement.clone(self, obj)
		
		obj.endian = self.endian
		obj.length = self.length
		
		for c in self:
			obj.append( c.clone() )
		
		return obj
	
	def asCType(self):
		
		value = int(self.getInternalValue())
		ret = None
		
		evalString = "ctypes.c_uint%d(value)" % (self.size)
		ret = eval(evalString)
		
		return ret

	def getSize(self):
		'''
		Return the length of this data element.  Try and
		be fast about it!
		'''
		
		if self.transformer != None or self.fixup != None:
			return len(self.getValue())
		
		return self.length/8
	
	def binaryFormatter(self, num, bits):
		'''
		Convert number to binary string
		'''
		
		ret = ""
		for i in range(bits-1, -1, -1):
			ret += str((num >> i) & 1)
		
		assert len(ret) == bits
		return ret
	
	def flipBitsByByte(self, num, size):
		
		ret = 0
		for n in self.splitIntoBytes(num, size):
			ret = ret << 8
			ret += n
		
		return ret
		
	def splitIntoBytes(self, num, size):
		
		ret = []
		for i in range(size/8):
			ret.append( num & 0xFF )
			num = num >> 8
		
		return ret
		
	def flipBits(self, num, size):
		'''
		Reverse the bits
		'''
		
		ret = 0x00 << size
		for i in range(size):
			b = 0x01 & (num >> i)
			ret += b << (size - i) - 1
		
		print "flipBits: pre %s post %s" % (self.binaryFormatter(num,size),
											self.binaryFormatter(ret,size))
		
		return ret
	
	def isInvalidated(self):
		'''
		Check if we need to reproduce this value.
		
		If we have a relation always True.
		Otherwise False.
		'''
		
		if len(self.relations) > 0:
			return True
		
		# Check children
		for c in self:
			if c.isDataElement:
				if c.isInvalidated():
					return True
		
		# Return false
		return False
	
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Flags we are always a binary string.
		'''
		# 1. Init our value
		
		ret = 0
		
		# 3. Build our flags up
		
		flags = []
		for n in self:
			if n.elementType == 'flag':
				flags.append(n)
		
		if self.padding:
			#print self.endian, self.rightToLeft, self.padding
			bits = BitBuffer("\0" * (self.length/8), not self.rightToLeft)
				
		else:
			bits = BitBuffer("\0" * (self.length/8), self.endian == 'big')
		
		for flag in flags:
			#print "%s: %d:, %d, %d" % (flag.name, flag.position, int(flag.getInternalValue()), flag.length)
			bits.seek(flag.position)
			bits.writebits(int(flag.getInternalValue()), flag.length)
		
		if self.padding and ( (self.endian == 'little' and not self.rightToLeft) or \
			(self.endian == 'big' and self.rightToLeft) ):
			
			fmt = '>'
			fmt2 = '<'
			
			if self.length == 8:
				fmt += 'B'
				fmt2 += 'B'
			elif self.length == 16:
				fmt += 'H'
				fmt2 += 'H'
			elif self.length == 32:
				fmt += 'I'
				fmt2 += 'I'
			elif self.length == 64:
				fmt += 'Q'
				fmt2 += 'Q'
			
			ret = struct.unpack(fmt, bits.getvalue())[0]
			ret = struct.pack(fmt2, ret)
		
		else:
			ret = bits.getvalue()
			
		# 4. do we fixup?
		
		if self.fixup != None:
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
		
		# 5. Do we have an override?
		
		if self.currentValue != None:
			ret = self.currentValue
		
		# 7. Return value
		
		if sout != None:
			sout.write(ret, self.getFullDataName())
		
		return ret
		
	def getRawValue(self, sout = None):
		
		ret = self.getInternalValue()
		
		# 7. Return value
		
		if sout != None:
			sout.write(ret, self.getFullDataName())
		
		return ret


class Flag(DataElement):
	'''
	A flag in a flag set
	'''
	def __init__(self, name, parent):
		DataElement.__init__(self, name, parent)
		self.elementType = 'flag'
		self.defaultValue = None
		self.position = None
		self.length = None	# called size
		self.signed = False
	
	def getSize(self):
		return self.length
	def setSize(self, size):
		self.length = size
	size = property(fget=getSize, fset=setSize)
	
	def getMinValue(self):
		'''
		Get the minimum value this number can have.
		'''
		
		if not self.signed:
			return 0
		
		min = 0 - (pow(2, self.length)-1)
		return min
	
	def getMaxValue(self):
		'''
		Get the maximum value for this number.
		'''
		max = pow(2, self.length)-1
		if self.signed:
			return max/2
		
		return max
	
	def clone(self, obj = None):
		
		if obj == None:
			obj = Flag(self.name, self.parent)
		
		DataElement.clone(self, obj)
		
		obj.position = self.position
		obj.length = self.length
		
		return obj
	
	def getInternalValue(self):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		# 1. Init our value
		
		value = 0
		
		# 2. Default value?
		
		if self.defaultValue != None:
			value = self.defaultValue
		
		# 3. Relations
		
		#print self.name + ": Pre-relation:", value
		value = self.getRelationValue(value)
		#print self.name + ": Post-relation:", value
		
		# 4. Fixup
		
		if self.fixup != None:
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
		
		# 5. Do we have an override?
		
		if self.currentValue != None:
			value = self.currentValue
		
		# 6. Return value
		try:
			value = int(value)
		except:
			try:
				value = ord(value)
			except:
				value = 0
		
		return value
		
	def getRawValue(self, sout = None):
		# We shouldn't ever be here since flag
		# should always be hidden behind Flags
		# but sometimes things get re-arranged.
		return str(self.getInternalValue())
		

class Seek(ElementWithChildren):
	'''
	Change the current position in the data stream.
	'''
	
	def __init__(self, name, parent):
		ElementWithChildren.__init__(self, name, parent)
		
		self.elementType = "seek"
		
		#: Python expression to calculate new position
		self.expression = None
		#: Integer position
		self.position = None
		#: Position change is relative to current position
		self.relative = None
		
		# EMulate some of the DataElement stuff
		self.array = None
		self.minOccurs = 1
		self.maxOccurs = 1
		self.currentValue = None
		self.defaultValue = None
	
	def clone(self, obj = None):
		
		if obj == None:
			obj = Seek(self.name, self.parent)
		
		obj.expression = self.expression
		obj.position = self.position
		obj.relative = self.relative
		
		return obj
	
	def HasWhenRelation(self):
		return False
	
	def _getExpressionPosition(self, currentPosition, dataLength, data):
		environment = {
			'self' : self,
			'pos' : currentPosition,
			'dataLength' : dataLength
			}
		
		#DataElement._fixRealParent(self, self)
		try:
			pos = -1
			pos = evalEvent(self.expression, environment, self)
			
		finally:
			#DataElement._unFixRealParent(self)
			pass
		
		return pos
	
	def _getPosition(self):
		return self.position
	
	def getPosition(self, currentPosition, dataLength, data):
		if self.expression != None:
			return self._getExpressionPosition(currentPosition, dataLength, data)
		
		if self.relative != None:
			return currentPosition + self.relative
		
		return self._getPosition();
	
	def _fixRealParent(self, node):
		'''
		Sometimes when we recurse to crack a
		block we remove the parent from the block
		and save it to .realParent.
		
		Since many scripts want to look up we will
		unsave the parent for a bit.
		'''
		
		# 1. Find root
		
		root = node
		while root.parent != None:
			root = root.parent
		
		# 2. Check if has a realParent
		
		if hasattr(root, 'realParent'):
			#print "_fixRealParent(): Found fake root: ", root.name
			root.parent = root.realParent
		
		# done!
	
	def _unFixRealParent(self, node):
		'''
		Clear the parent if we have it saved.
		'''
		
		# 1. Look for fake root
		
		root = node
		while not hasattr(root, 'realParent') and root.parent != None:
			root = root.parent
		
		# 2. Remove parent link
		#print "_unFixRealParent(): Found fake root: ", root.name
		root.parent = None


class Blob(DataElement):
	'''
	A flag in a flag set
	'''
	
	#: Default value for valueType
	defaultValueType = 'string'
	#: Default value for lengthType
	defaultLengthType = 'string'
	
	def __init__(self, name, parent):
		DataElement.__init__(self, name, parent)
		self.elementType = 'blob'
		self.valueType = Blob.defaultValueType
		self.lengthType = Blob.defaultLengthType
		self.length = None
		self.lengthCalc = None
	
	def clone(self, obj = None):
		
		if obj == None:
			blob = Blob(self.name, self.parent)
		else:
			blob = obj
		
		DataElement.clone(self, blob)
		blob.elementType = self.elementType
		blob.valueType = self.valueType
		blob.lengthType = self.lengthType
		blob.length = self.length
		blob.lengthCalc = self.lengthCalc
		
		return blob
	
	def asCType(self):
		
		value = self.getValue()
		ret = (ctypes.c_ubyte * len(value))()
		
		for i in xrange(len(value)):
			ret[i] = ord(value[i])
		
		# Are we a pointer?
		if self.isPointer:
			if self.pointerDepth != None:
				for i in range(int(self.pointerDepth)):
					ret = ctypes.pointer(ret)
			else:
				ret = ctypes.pointer(ret)
				
		return ret
	
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		return self.getRawValue(sout)
	
	def getSize(self):
		'''
		Return the length of this data element.  Try and
		be fast about it!
		'''
		
		l = self.getLength()
		if l != None:
			return l
		
		return len(self.getValue())
		
	def getLength(self):
		'''
		Get the length of this element.
		'''
		
		if self.lengthType == 'calc':
			try:
				self.length = self.calcLength()
				
				if self.length != None and self.length < 0:
					# SANITY!
					print "Length Calc is off, setting to None", self.length
					self.length = None
			
			except:
				# This can fail while doing
				# mutations.
				print "Warning: Calc failed.  Okay to ignore after first iteration."
				pass
		
		elif self.isStatic:
			return len(self.getValue())
		
		return self.length
		
	def getRawValue(self, sout = None):
		
		targetLength = None
		
		if self.lengthType == 'calc':
			try:
				targetLength = self.calcLength()
			except:
				# Calc may not run correctly yet!
				pass
		
		elif self.length != None:
			targetLength = self.length
		
		# 1. init
		value = ""
		
		if self.currentValue != None:
			value = self.currentValue
		
		else:
			
			# 2. default value?
			if self.defaultValue != None:
				value = self.defaultValue
			
			# 3. Fixup
			if self.fixup != None:
				self.fixup.fixup.context = self
				ret = self.fixup.fixup.dofixup()
				if ret != None:
					value = ret
		
			# Make correct size
			if targetLength != None:
				while len(value) < targetLength:
					value = value + "\x00"
		
		# 5. If we have sout
		if sout != None:
			sout.write(value, self.getFullDataName())
		
		return value
	

###################################################################################
###################################################################################

class Relation(Element):
	'''
	Specifies relations between data
	
	- size-of
	- (when a flag indicates something exists)
	- Zero or more
	- 1 or more
	'''
	
	## For debugging
	#def getParent(self):
	#	return self._parent
	#def setParent(self, value):
	#	self._parent = value
	#	#if hasattr(self, "of") and self.of == "Tables":
	#	#	print self,"Relation.setParent()",value
	#	#	traceback.print_stack()
	#parent = property(fget=getParent, fset=setParent)
	
	def __init__(self, name, parent):
		Element.__init__(self, name, parent)
		self.elementType = 'relation'
		
		#: Type of relation (size, count, when)
		self.type = None
		
		#: Reference to target
		self.of = None
		
		#: Reference to matching of relation
		self.From = None
		
		#: Relative relation
		self.relative = False
		#: Relative to this element (string)
		self.relativeTo = None
		
		#:Only for output?
		self.isOutputOnly = False
		
		#: Parent of this object
		#self.parent = parent
		#: Expression to apply to relation when getting value
		self.expressionGet = None
		#: Expression to apply to relation when setting value
		self.expressionSet = None
	
	def clone(self, obj = None):
		
		if obj == None:
			obj = Relation(self.name, self.parent)
		
		obj.type = self.type
		obj.of = self.of
		obj.From = self.From
		obj.relative = self.relative
		obj.relativeTo = self.relativeTo
		obj.expressionGet = self.expressionGet
		obj.expressionSet = self.expressionSet
		
		return obj
	
	def getFullnameInDataModel(self):
		'''
		This will get fully qualified name of this element starting with the
		root node of the data model.
		'''
		
		name = self.name
		node = self
		
		while node.parent != None and node.parent.isDataElement:
			node = node.parent
			name = "%s.%s" % (node.name, name)
		
		return name
		
	def getValue(self, default = False):
		'''
		For a size-of relation get the size
		of the referenced value.  Apply expression
		to the value if needed.
		
		@type	default: Boolean
		@param	default: Should we try for .defaultValue first? (defaults False)
		'''
		
		if self.From != None:
			raise Exception("Only 'of' relations should have getValue method called.")
		
		environment = None
		value = 0
		
		if self.type == 'size':
			
			if default:
				try:
					value = int(self.parent.defaultValue)
				except:
					value = int(self.parent.getInternalValue())
			
			else:
				value = int(self.parent.getInternalValue())
			
			environment = {
				'self' : self.parent,
				'length' : value,
				'size' : value,
				}
		
		elif self.type == 'count':
			if default:
				try:
					value = int(self.parent.defaultValue)
				except:
					value = int(self.parent.getInternalValue())
			else:
				value = int(self.parent.getInternalValue())
			
			environment = {
				'self' : self.parent,
				'count' : value,
				}
		
		elif self.type == 'offset':
			if default:
				try:
					value = int(self.parent.defaultValue)
				except:
					value = int(self.parent.getInternalValue())
			else:
				value = int(self.parent.getInternalValue())
			
			# Handle Relative Relation
			if self.relative:
				
				# Are we relative to another element?
				if self.relativeTo == None:
					value = value + self.parent.possiblePos
					
				else:
					obj = self.parent.find(self.relativeTo)
					try:
						value = value + obj.possiblePos
					except:
						print "obj:", obj
						print "obj.fullname:", obj.getFullname()
						raise
			
			environment = {
				'self' : self.parent,
				'offset' : value,
				}
		else:
			raise Exception("Should not be here!")
		
		if self.expressionGet != None:
			try:
				self.parent._fixRealParent(self.parent)
				return evalEvent(self.expressionGet, environment, self)
			
			finally:
				self.parent._unFixRealParent(self.parent)
		
		return value

	def setValue(self, value):
		'''
		For a size-of relation get the size
		of the referenced value.  Apply expression
		to the value if needed.
		'''
		
		if self.From != None:
			raise Exception("Only 'of' relations should have setValue method called.")
		
		environment = None
		value = int(value)
		
		if self.type == 'size':
			environment = {
				'of' : self.getOfElement(),
				'self' : self.parent,
				'length' : value,
				'size' : int(value),
				}
		
		elif self.type == 'count':
			environment = {
				'of' : self.getOfElement(),
				'self' : self.parent,
				'count' : int(value),
				}
			
		elif self.type == 'offset':
			
			# Handle Relative Relation
			if self.relative:
				
				# Are we relative to another element?
				if self.relativeTo == None:
					value = value - self.parent.possiblePos
				else:
					obj = self.parent.find(self.relativeTo)
					value = value - obj.possiblePos
			
			environment = {
				'of' : self.getOfElement(),
				'self' : self.parent,
				'offset' : int(value),
				}
		
		else:
			raise Exception("Should not be here!")
		
		if self.expressionSet != None:
			try:
				self.parent._fixRealParent(self.parent)
				ret = evalEvent(self.expressionSet, environment, self)
				return ret
			
			finally:
				self.parent._unFixRealParent(self.parent)
		
		return int(value)

	
	def getOfElement(self):
		'''
		Resolve of reference.  We want todo this at
		runtime in case we are copied around.
		'''
		
		if self.of == None:
			return None
		
		#print self
		#print self.of
		obj = self.parent.findDataElementByName(self.of)
		if obj == None:
			# Could element have become an array?
			obj = self.parent.findArrayByName(self.of)
		
		if obj == None:
			print self.parent.name, self.parent
			print "Parent:",self.parent.parent
			print "DataRoot:", self.parent.getRootOfDataMap()
			print "DataRoot.parent:", self.parent.getRootOfDataMap().parent
			print "Fullname:", self.getFullDataName()
			print "Couldn't locate [%s]" % self.of, self.type
			DomPrint(0, self.parent.getRootOfDataMap())
			raise Exception("Couldn't locate [%s]" % self.of)
		
		return obj
	
	def getFromElement(self):
		'''
		Resolve of reference.  We want todo this at
		runtime in case we are copied around.
		'''
		
		if self.From == None:
			return None
		
		return self.parent.findDataElementByName(self.From)


class Data(ElementWithChildren):
	'''
	Default data container.  Children are Field objects.
	
	When used in multi-file mode, fileName will always
	contain an actual real file.  It's upto the mutator
	strategy to use the other files.
	'''
	def __init__(self, name):
		ElementWithChildren.__init__(self, name, None)
		self.elementType = 'data'
		
		#: Name of file containing data to load
		self.fileName = None
		#: Expression that returns data to load
		self.expression = None
		#: Does this data element point to multiple files
		self.multipleFiles = False
		#: A unix style glob path
		self.fileGlob = None
		#: Folder of files to use
		self.folderName = None
	
	def gotoFirstFile(self):
		if not self.multipleFiles:
			raise PeachException("Error, Data.gotoRandomFile called with self.multipleFiels == False!")
		
		if self.folderName != None:
			self.fileName = self.folderName
			self.files = os.listdir(self.folderName)
			for i in range(len(self.files)):
				self.files[i] = os.path.join(self.folderName, self.files[i])
			
		elif self.fileGlob != None:
			self.files = glob.glob(self.fileGlob)
		
		self.fileName = self.files[0]
		self.files = self.files[1:]
	
	def gotoNextFile(self):
		self.fileName = self.files[0]
		self.files = self.files[1:]
		
	def gotoRandomFile(self):
		'''
		Goto random file.
		'''
		
		if not self.multipleFiles:
			raise PeachException("Error, Data.gotoRandomFile called with self.multipleFiels == False!")
		
		if self.folderName != None:
			self.fileName = self.folderName
			files = os.listdir(self.folderName)
			
			while os.path.isdir(self.fileName):
				self.fileName = random.choice(files)
				self.fileName = os.path.join(self.folderName, self.fileName)
		
		elif self.fileGlob != None:
			files = glob.glob(self.fileGlob)
			self.fileName = random.choice(files)
			while os.path.isdir(self.fileName):
				self.fileName = random.choice(files)


class Field(ElementWithChildren):
	'''
	Default bit of data.
	'''
	def __init__(self, name, value, parent):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'field'
		
		#: Value to set on data element
		self.value = value
		#: Indicates type of value. ['string', 'literal', 'hex'] supported.
		self.valueType = None
		#: Indicates an array expantion
		self.array = None


class Logger(ElementWithChildren):
	'''
	A logger used to log peach events.
	'''
	def __init__(self, parent):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'logger'


def NamespaceToXml(self, parent):
	node = parent.rootNode.createElementNS(None, 'Include')
	parent.appendChild(node)
	
	self._setAttribute(node, 'ns', self.nsName)
	self._setAttribute(node, 'src', self.nsSrc)
	
	return node

class Namespace(Element):
	def __init__(self):
		Element.__init__(self, None, None)
		self.elementType = 'namespace'
		self.nsName = None
		self.nsSrc = None
		#self.toXml = new.instancemethod(PeachModule.Engine.dom.NamespaceToXml, self, self.__class__)

	def toXml(self, parent):
		node = parent.rootNode.createElementNS(None, 'Include')
		parent.appendChild(node)
		
		self._setAttribute(node, 'ns', self.nsName)
		self._setAttribute(node, 'src', self.nsSrc)
		
		return node

class PythonPath(Element):
	def __init__(self):
		Element.__init__(self, None, None)
		self.elementType = 'pythonpath'


class Publisher(ElementWithChildren):
	def __init__(self):
		ElementWithChildren.__init__(self, None, None)
		self.elementType = 'publisher'
		self.classStr = None
		self.publisher = None


# ###################################################################
# ## StateMachine Objects

class StateMachine(Mutatable):
	def __init__(self, name, parent):
		Mutatable.__init__(self, name, parent)
		self.elementType = 'statemachine'
		self.initialState = None
		self.onEnter = None
		self.onExit = None

	def findStateByName(self, stateName):
		for child in self:
			if child.elementType == 'state' and child.name == stateName:
				return child
			
		return None
	
	def getRoute(self):
		paths = [child for child in self if child.elementType == 'path']
		return paths


class State(Mutatable):
	def __init__(self, name, parent):
		Mutatable.__init__(self, name, parent)
		self.elementType = 'state'
		self.onEnter = None
		self.onExit = None

	def getChoice(self):
		for child in self:
			if child.elementType == 'stateChoice':
				return child
		
		return None

class StateChoice(ElementWithChildren):
	def __init__(self, parent):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'stateChoice'
		
	def findActionByRef(self, ref):
		for child in self:
			if child.elementType == 'stateChoiceAction' and child.ref == ref:
				return child
			
		return None
		
class StateChoiceAction(Element):
	def __init__(self, ref, type, parent):
		Element.__init__(self, None, parent)
		self.elementType = 'stateChoiceAction'
		self.ref = ref
		self.type = type
		
class Path(Element):
	def __init__(self, ref, parent):
		Element.__init__(self, None, parent)
		self.elementType = 'path'
		self.ref = ref
		self.stop = False

class Strategy(ElementWithChildren):
	def __init__(self, classStr, parent):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'strategy'
		self.params = {}
		self.classStr = classStr

class Action(Mutatable):
	def __init__(self, name, parent):
		Mutatable.__init__(self, name, parent)
		self.elementType = 'action'
		self.type = None
		self.ref = None
		self.when = None
		self.onStart = None
		self.onComplete = None
		self.data = None
		self.template = None
		self.setXpath = None
		self.valueXpath = None
		self.valueLiteral = None
		self.value = None
		self.method = None
		self.property = None
		self.publisher = None;

class ActionParam(ElementWithChildren):
	def __init__(self, name, parent):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'actionparam'
		self.type = 'in'
		self.template = None
		self.data = None
		self.value = None

class ActionResult(ElementWithChildren):
	def __init__(self, name, parent):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'actionresult'
		self.template = None
		self.value = None
		
class Mutators(ElementWithChildren):
	def __init__(self, name, parent):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'mutators'

class Mutator(ElementWithChildren):
	def __init__(self, name, parent):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'mutator'
		self.mutator = None
		
class Hint(ElementWithChildren):
	'''
	Hints can be a child of DataElements.  They provide hints
	to mutators about the data element.  Hints can be things
	like finer grained type information like "type=xml" or
	possibly hints about related data values "related=Foo".
	
	Hints are optional bits of meta data.
	'''
	def __init__(self, name, parent):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'hint'
		self.value = None
		
	def clone(self, obj = None):
		
		if obj == None:
			obj = Hint(self.name, self.parent)
		
		obj.elementType = self.elementType
		obj.value = self.value
		
		return obj
	
class Custom(DataElement):
	
	def __init__(self, name, parent):
		DataElement.__init__(self, name, parent)
		self.elementType = 'custom'
	
	def handleParsing(self, node):
		'''
		Handle any custom parsing of the XML such as
		attributes.
		'''
		
		raise Exception("handleParsing not implemented")
	
	def handleIncomingSize(self, node, data, pos, parent):
		'''
		Return initial read size for this type.
		'''
		
		# Always at least a single byte
		#return (2,1)
		raise Exception("handleIncomingSize not implemented")
	
	def handleIncoming(self, cntx, data, pos, parent, doingMinMax = False):
		'''
		Handle data cracking.
		'''
		
		#value = str(i)
		#eval("self.%s(value)" % cntx.method)
		
		#return (2, pos)
		
		raise Exception("handleIncoming not implemented")
	
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		
		#value = None
		#
		## Override value?
		#if self.currentValue != None:
		#	value = self.currentValue
		#
		#else:
		#	# Default value
		#	value = self.defaultValue
		#	
		#	# Relation
		#	value = str(self.getRelationValue(value))
		#	
		#	# Fixup
		#	if self.fixup != None:
		#		self.fixup.fixup.context = self
		#		ret = self.fixup.fixup.dofixup()
		#		if ret != None:
		#			value = ret
		#
		## Apply mbint pack
		#
		#### CUSTOM CODE HERE
		#
		## Write to buffer
		#if sout != None:
		#	sout.write(value, self.getFullDataName())
		#
		## Return value
		#return ret;
		raise Exception("getInternalValue not implemented")
	
	def getLength(self):
		'''
		Get the length of this element.
		'''
		
		return len(self.getValue())
	
	def getRawValue(self, sout = None):
		return self.getInternalValue(sout)
		

# ###################################################################

import cPeach

def DomPrint(indent, node):
	
	tabs = '  ' * indent
	
	if hasattr(node, 'parent') and node.parent != None:
		p = "parent"
	else:
		p = "!! no parent !!"
	
	print tabs + node.elementType + ": " + node.name + ": " + p
	
	if node.hasChildren:
		for child in node._children:
			DomPrint(indent+1, child)

# ###########################################################################

# end
