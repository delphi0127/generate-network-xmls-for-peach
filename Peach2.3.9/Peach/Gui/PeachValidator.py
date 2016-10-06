'''
PeachValidator GUI

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

# SPEED ME UP SCOTTY!
#import psyco
#psyco.full()

import sys, os
sys.path.append("../..")
sys.path.append(os.getcwd() + "\\..\\..\\")

try:
	import Ft.Xml.Domlette
	from Ft.Xml.Domlette import *
	from Ft.Xml.Catalog import GetDefaultCatalog
	from Ft.Xml.InputSource import InputSourceFactory
	from Ft.Lib.Resolvers import SchemeRegistryResolver
	from Ft.Lib import Uri

except:
	print "\nError loading 4Suite XML library.  This library"
	print "can be installed from the dependencies folder or"
	print "downloaded from http://4suite.org/.\n\n"
	raise

import gui
import wx
#import wx.propgrid as wxpg
import re, pickle

from Peach.publisher import PublisherBuffer
from Peach.Engine import parser, engine, incoming, dom
from Peach.Engine.dom import *
from Peach.Analyzers import *
import Peach

class PeachValidatorGui(gui.PeachValidation):
	
	def __init__(self):
		self.title = "Peach Validation - %s"
		gui.PeachValidation.__init__(self, None, -1, "")
		
		self._lastXmlFile = ""
		self._lastBinFile = ""
		self._lastPath = "/"
		
		self.LoadState()
		
		# Set values
		self.textFilename.SetValue(self._lastBinFile)
		self.textPeachXmlFilename.SetValue(self._lastXmlFile)
		
		self.mutateObj = None
		
		wx.EVT_CLOSE(self, self.OnClose)
		
		# Disable controls that shouldn't be used yet
		
		self.buttonGenerate.Disable()
		self.comboMutator.Disable()
		self.textFilename.Disable()
		self.buttonBrowse.Disable()
		self.buttonLoad.Disable()
		
		# Create Tree image list
		self.treeImages = wx.ImageList(16,16)
		self.treeImages.NodeTemplate= self.treeImages.Add(wx.Bitmap(os.path.join("icons", "node-template.png"), wx.BITMAP_TYPE_ANY))
		self.treeImages.NodeBlock   = self.treeImages.Add(wx.Bitmap(os.path.join("icons", "node-block.png"), wx.BITMAP_TYPE_ANY))
		self.treeImages.NodeChoice  = self.treeImages.Add(wx.Bitmap(os.path.join("icons", "node-choice.png"), wx.BITMAP_TYPE_ANY))
		self.treeImages.NodeFlags   = self.treeImages.Add(wx.Bitmap(os.path.join("icons", "node-flags.png"), wx.BITMAP_TYPE_ANY))
		self.treeImages.NodeNumber  = self.treeImages.Add(wx.Bitmap(os.path.join("icons", "node-number.png"), wx.BITMAP_TYPE_ANY))
		self.treeImages.NodeString  = self.treeImages.Add(wx.Bitmap(os.path.join("icons", "node-string.png"), wx.BITMAP_TYPE_ANY))
		self.treeImages.NodeUnknown = self.treeImages.Add(wx.Bitmap(os.path.join("icons", "node-unknown.png"), wx.BITMAP_TYPE_ANY))
		self.treeImages.NodeBlob    = self.treeImages.Add(wx.Bitmap(os.path.join("icons", "node-blob.png"), wx.BITMAP_TYPE_ANY))
		self.treeImages.NodeError   = self.treeImages.Add(wx.Bitmap(os.path.join("icons", "node-error.png"), wx.BITMAP_TYPE_ANY))
		
		self.ImageLookup = {'block':self.treeImages.NodeBlock,
							'choice':self.treeImages.NodeChoice,
							'flags':self.treeImages.NodeFlags,
							'flag':self.treeImages.NodeFlags,
							'number':self.treeImages.NodeNumber,
							'string':self.treeImages.NodeString,
							'blob':self.treeImages.NodeBlob,
							'template':self.treeImages.NodeTemplate,
							'custom':self.treeImages.NodeUnknown,
							}
		
		self.root = self.treeDataTree.AddRoot("Peach")
		self.treeDataTree.SetImageList(self.treeImages)
		self.treeDataTree.SetItemImage(self.root, self.treeImages.NodeTemplate)
		
		# Adjust size of tree
		self.SetSize(wx.Size(600, 600))
		width, height = self.GetSizeTuple()
		self.splitterTopBottom.SetSashPosition(height * 0.25, True)
		self.splitterRightLeft.SetSashPosition(width * 0.35, True)
		
		self.treeDataTree.SelectItem(self.root, True)
		self.treeDataTree.Expand(self.root)
	
	def OnClose(self, event):
		try:
			self.SaveState()
		except:
			pass
		
		self.Destroy()
	
	def SaveState(self):
		'''
		Save out our state
		'''
		
		state = [self._lastXmlFile, self._lastBinFile, self._lastPath]
		
		p = Peach.Gui.__path__[0]
		if hasattr(sys,"frozen") and sys.frozen == "windows_exe":
			p = os.path.dirname(os.path.abspath(sys.executable))
		
		fd = open(os.path.join(p, "peachvalidator.state"), "wb+")
		fd.write(pickle.dumps(state))
		fd.close()
	
	def LoadState(self):
		'''
		Load our state if it exists
		'''
		
		try:
			p = Peach.Gui.__path__[0]
			if hasattr(sys,"frozen") and sys.frozen == "windows_exe":
				p = os.path.dirname(os.path.abspath(sys.executable))
			
			fd = open(os.path.join(p, "peachvalidator.state"), "rb")
			state = pickle.loads(fd.read())
			fd.close()
			
			self._lastXmlFile = state[0]
			self._lastBinFile = state[1]
			self._lastPath = state[2]
		except:
			pass
		
	
	def OnButtonBrowse(self, event):
		#print "Event handler `OnButtonBrowse' not implemented!"
		event.Skip()
		
		dlg = wx.FileDialog(self, 'Choose a file to open', self._lastPath, self._lastBinFile, '*.*', wx.OPEN)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return
		
		fileName = dlg.GetPath()
		self._lastBinFile = fileName
		self._lastPath = fileName[:fileName.rfind(os.path.pathsep)]
		dlg.Destroy()
		self.textFilename.SetValue(fileName)

	def OnButtonPeachXmlLoad(self, event): # wxGlade: PeachValidation.<event_handler>
		event.Skip()
		
		self.treeDataTree.DeleteChildren(self.root)
		self.treeDataTree.SetItemImage(self.root, self.treeImages.NodeTemplate)
		
		# Lets add the path of this file to our python path :)
		sys.path.append(os.path.dirname(self.textPeachXmlFilename.GetValue()))
		
		try:
			self.p = parser.ParseTemplate()
			self.p.dontCrack = True
			self.peach = self.p.parse("file:"+ self.textPeachXmlFilename.GetValue())
			
		except Exception, e:
			wx.MessageBox('Failed to load XML file.  Recommend you run "peach.py -t pitfile.xml" to verify it parses correctly.', 'Error')
			print e
		
		# Locate all templates and toss into combo
		self.comboDataModel.Clear()
		self.mutators = {}
		for n in self.peach:
			if n.elementType == 'template':
				self.comboDataModel.Append(n.name)
				self.comboDataModel.SetValue(n.name)
			
			elif n.elementType == 'test':
				for m in n.mutators:
					if m.name not in self.mutators.keys():
						self.mutators[m.name] = m
		
		# Populate Mutator drop-down
		
		self.comboMutator.Clear()
		for m in self.mutators.keys():
			self.comboMutator.Append(m)
			self.comboMutator.SetValue(m)
		
		# Enable controls that shouldn't be used yet
		
		self.buttonGenerate.Disable()
		self.comboMutator.Disable()
		self.textFilename.Enable()
		self.buttonBrowse.Enable()
		self.buttonLoad.Enable()
		
		# Display default model
		self.OnComboDataModel(None)
	
	def OnComboDataModel(self, event):
		# wxGlade: PeachValidation.<event_handler>
		#print "Event handler `OnComboDataModel' not implemented!"
		#event.Skip()
		
		# Locate a template to use
		self.template = None
		for n in self.peach:
			if n.elementType == 'template' and n.name == self.comboDataModel.GetValue():
				self.template = n
				break
		
		# Show our current tree
		self.treeDataTree.DeleteChildren(self.root)
		self.treeDataTree.SetItemImage(self.root, self.treeImages.NodeTemplate)
		self.BuildTree(self.template)
	
	def OnButtonLoad(self, event):
		event.Skip()
		
		if len(self.textFilename.GetValue()) < 1:
			return
		
		self.treeDataTree.DeleteChildren(self.root)
		self.treeDataTree.SetItemImage(self.root, self.treeImages.NodeTemplate)
		
		# Now open'er up!
		fd = open(self.textFilename.GetValue(), "rb")
		data = fd.read()
		fd.close()
		
		self.hexView.SetData(data)
		
		# Locate a template to use
		self.template = None
		for n in self.peach:
			if n.elementType == 'template' and n.name == self.comboDataModel.GetValue():
				self.template = n
				break
		
		if self.template == None:
			raise Exception("Couldn't locate template, suck!")
		
		try:
			cracker = incoming.DataCracker(self.peach)
			cracker.haveAllData = True
			self.template = self.template.copy(self.template.parent)
			cracker.optmizeModelForCracking(self.template, True)
			(rating, pos) = cracker.crackData(self.template, PublisherBuffer(None,data))
			if pos < len(data)-1:
				# not everything was parsed!
				self.treeDataTree.SetItemImage(self.root, self.treeImages.NodeError)
				
				# TODO: Display error dialog
			
			# Pass 6 -- Analyzers
			
			# Simce analyzers can modify the DOM we need to make our list
			# of objects we will look at first!
			
			print "Looking for analyzers to run"
			
			objs = []
			
			for child in self.template.getElementsByType(Blob):
				if child.analyzer != None and child not in objs:
					objs.append(child)
			for child in self.template.getElementsByType(String):
				if child.analyzer != None and child not in objs:
					objs.append(child)
			
			for child in objs:
				try:
					analyzer = eval("%s()" % child.analyzer)
				except:
					analyzer = eval("PeachXml_"+"%s()" % child.analyzer)
				
				analyzer.asDataElement(child, {}, child.getInternalValue())
			
		except:
			raise
			self.treeDataTree.SetItemImage(self.root, self.treeImages.NodeError)
		
		# Build tree
		self.BuildTree(self.template)
		
		self.buttonGenerate.Enable()
		self.comboMutator.Enable()
	
	def BuildTree(self, template):
		self.treeDataTree.Freeze()
		
		self.treeDataTree.SetPyData(self.root, template)
		for child in template:
			self.AddNodeToTree(self.root, child)
		
		self.treeDataTree.Thaw()
		self.treeDataTree.Expand(self.root)
		self.treeDataTree.SelectItem(self.root, True)
	
	def OnTreeSelChanged(self, event):
		event.Skip()
		
		# Look at our junk and output some cool stuff
		# to the text box.
		itemId = event.GetItem()
		node = self.treeDataTree.GetPyData(itemId)
		
		if node == None:
			return
		
		value = "%s is a %s element type\n" % (node.name, node.elementType)
		value += "="*(len(value)-1)
		value += "\n\n"
		
		if hasattr(node, 'pos') and hasattr(node, 'rating') and node.pos != None:
			value += "DataElement.pos = %d\n" % node.pos
			value += "DataElement.rating = %d\n" % node.rating
		
		else:
			value += "Warning: We did not reach, or crack this element!!\n\n"
		
		if node.elementType == 'string':
			if node.length != None:
				value += "String.length: %d\n" % node.length
			else:
				value += "String.length: Unknown\n"
			
			value += "String.nullTerminated: %s\n" % str(node.nullTerminated)
			value += "String.type: %s\n" % node.type
			value += "String.padCharacter: %s\n" % repr(node.padCharacter)
			
			if node.defaultValue != None:
				if len(node.defaultValue) > 100:
					value += "String.defaultValue: %s\n" % repr(node.defaultValue[:100])
				else:
					value += "String.defaultValue: %s\n" % repr(node.defaultValue)
			else:
				value += "String.defaultValue: None\n"
			value += "\n"
		
		elif node.elementType == 'number':
			value += "Number.size: %d\n" % node.size
			value += "Number.endian: %s\n" % node.endian
			value += "Number.signed: %s\n" % str(node.signed)
			
			if node.defaultValue != None:
				value += "Number.defaultValue: %d\n" % int(node.defaultValue)
			else:
				value += "Number.defaultValue: None\n"
			value += "\n"
		
		elif node.elementType == 'flags':
			value += "Flags.size: %d\n" % node.length
			value += "Flags.endian: %s\n" % node.endian
			value += "\n"
		
		elif node.elementType == 'flag':
			value += "Flag.size: %d\n" % node.length
			value += "Flag.position: %d\n" % node.position
			
			if node.defaultValue != None:
				value += "Flag.defaultValue: %d\n" % int(node.defaultValue)
			else:
				value += "Flag.defaultValue: None\n"
			value += "\n"
		
		elif node.elementType == 'block':
			pass
		
		elif node.elementType == 'blob':
			if node.length != None:
				value += "Blob.length: %d\n" % node.length
			else:
				value += "Blob.length: Unknown\n"
			
			if node.defaultValue != None:
				if len(node.defaultValue) > 100:
					value += "Blob.defaultValue: %s\n" % repr(node.defaultValue[:100])
				else:
					value += "Blob.defaultValue: %s\n" % repr(node.defaultValue)
			else:
				value += "Blob.defaultValue: None\n"
			value += "\n"
		
		nodeInternal = None
		nodeValue = None
		
		try:
			#if node.currentValue != None:
			#	nodeInternal = node.getInternalValue()
			#	nodeValue = node.getValue()
			#else:
			#	nodeInternal = node.getInternalValue()
			#	nodeValue = node.getValue()
			nodeValue = str(node.getValue())
			nodeInternal = node.getInternalValue()
			if type(nodeInternal) not in [str, unicode]:
				nodeInternal = str(node.getInternalValue())
		
		except:
			#raise
			pass
		
		if nodeInternal != None:
			if len(nodeInternal) > 100:
				value += "Internal value: (%d bytes)\n%s\n\n\n" % (len(nodeInternal), repr(nodeInternal[:100]))
			else:
				value += "Internal value: (%d bytes)\n%s\n\n\n" % (len(nodeInternal), repr(nodeInternal))
		else:
			value += "Internal value: None\n\n"
		
		if nodeValue != None:
			if len(nodeValue) > 100:
				value += "Output value: (%d bytes)\n%s\n\n\n" % (len(nodeValue), repr(nodeValue[:100]))
			else:
				value += "Output value: (%d bytes)\n%s\n\n\n" % (len(nodeValue), repr(nodeValue))
			
			length = len(nodeValue)
			if length >= 100:
				length = 50
				spaces = '3'
			elif length >= 10:
				spaces = '2'
			else:
				spaces = ''
			
			for i in range(length):
				value += ("[%" + spaces + "d]: %s: %s\n") % (i, hex(ord(nodeValue[i])), repr(nodeValue[i]))
			
			if length < len(nodeValue):
				value += ".\n.\n.\n"
				
				for i in range(len(nodeValue)-10, len(nodeValue)):
					value += ("[%" + spaces + "d]: %s: %s\n") % (i, hex(ord(nodeValue[i])), repr(nodeValue[i]))
		else:
			value += "Output value: None\n\n"
		
		self.textOutput.SetValue(value)
		
		# Update hex view
		if node.pos != None:
			self.hexView.SetDataSelection(node.pos, node.pos+len(nodeValue)-1)
		else:
			self.hexView.SetDataSelection(-1, -1)
		
	
	def AddNodeToTree(self, parentId, node):
		'''
		Add a node to the tree.  Adds the children of this node as well!
		
		NOTE: This only builds the tree and links the tree item to the
		node object.
		'''
		
		if not isinstance(node, DataElement):
			return
		
		id = self.treeDataTree.AppendItem(parentId, node.name)
		self.treeDataTree.SetPyData(id, node)
		
		try:
			self.treeDataTree.SetItemImage(id, self.ImageLookup[node.elementType])
			
		except:
			raise Exception("Unknown element type: '%s'" % node.elementType)
		
		try:
			value = node.getValue()
		
		except:
			self.treeDataTree.SetItemImage(id, self.treeImages.NodeError)
			
		if not hasattr(node, 'pos') or not hasattr(node, 'rating'):
			self.treeDataTree.SetItemImage(id, self.treeImages.NodeError)
		
		for child in node._children:
			self.AddNodeToTree(id, child)
		
		return id

	def OnButtonPeachFileBrowse(self, event): # wxGlade: PeachValidation.<event_handler>
		#print "Event handler `OnButtonPeachFileBrowse' not implemented!"
		event.Skip()
		
		dlg = wx.FileDialog(self, 'Choose a Peach XML file to open', self._lastPath, self._lastXmlFile, '*.xml', wx.OPEN)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return
		
		fileName = dlg.GetPath()
		self._lastXmlFile = fileName
		self._lastPath = fileName[:fileName.rfind(os.path.pathsep)]
		
		dlg.Destroy()
		self.textPeachXmlFilename.SetValue(fileName)

	def OnButtonGenerate(self, event): # wxGlade: PeachValidation.<event_handler>
		#print "Event handler `OnButtonGenerate' not implemented!"
		event.Skip()
		
		if self.mutateObj == None:
			self.mutateObj = dom.Action('Mutation', None)
			self.mutateObj.origionalTemplate = self.template
		
		# Mutate
		
		self.mutateObj.template = self.mutateObj.origionalTemplate.copy(self.mutateObj)
		self.mutators[self.comboMutator.GetValue()].mutator.getActionValue(self.mutateObj)
		try:
			self.mutators[self.comboMutator.GetValue()].mutator.next()
			
			# Build tree
			self.treeDataTree.DeleteChildren(self.root)
			self.treeDataTree.SetItemImage(self.root, self.treeImages.NodeTemplate)
			self.BuildTree(self.mutateObj.template)
		except:
			wx.MessageBox('Mutator Completed', 'Info')

def RunPeachValidator():
	app = wx.PySimpleApp(0)
	wx.InitAllImageHandlers()
	peachMain = PeachValidatorGui()
	app.SetTopWindow(peachMain)
	peachMain.Show()
	app.MainLoop()

if __name__ == "__main__":
    RunPeachValidator()

# end
