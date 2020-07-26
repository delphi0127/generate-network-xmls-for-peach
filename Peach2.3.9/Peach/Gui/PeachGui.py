'''
PeachBuilder GUI

@author: Michael Eddington
@version: $Id: PeachGui.py 2156 2010-08-01 23:36:31Z meddingt $
'''

#
# Copyright (c) 2007-2008 Michael Eddington
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

# $Id: PeachGui.py 2156 2010-08-01 23:36:31Z meddingt $

# SPEED ME UP SCOTTY!
#import psyco
#psyco.full()

try:

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
    import wx.propgrid as wxpg
    import re
    import PeachValidator

    from Peach.Engine import parser, engine
    
    from help import *
    
    class PeachGui(gui.PeachMainFrame):
        
        NodeDefaults = {
            'Number' : {
                'size' : '8'
                }
            }
        
        def __init__(self):
            self.title = "Peach Builder - %s"
            gui.PeachMainFrame.__init__(self, None, -1, "")
            self.root = self.peachMainTree.AddRoot("Peach")
            
            #self.peachMainTree.ExpandAll()
            self.SetSize(wx.Size(800, 600))
            
            self.Bind(wx.EVT_TREE_ITEM_MENU, self.OnTreeItemMenu, self.peachMainTree)
            self.Bind(wxpg.EVT_PG_CHANGED, self.OnPropertyGridChanged, self.peachMainPropertyGrid)
            
            # Create Tree image list
            self.treeImages = wx.ImageList(16,16)
            self.treeImages.NodeBlock   = self.treeImages.Add(wx.Bitmap("icons\\node-block.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeChoice  = self.treeImages.Add(wx.Bitmap("icons\\node-choice.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeFlags   = self.treeImages.Add(wx.Bitmap("icons\\node-flags.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeNumber  = self.treeImages.Add(wx.Bitmap("icons\\node-number.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeString  = self.treeImages.Add(wx.Bitmap("icons\\node-string.png", wx.BITMAP_TYPE_ANY))
            #self.treeImages.NodeSequence= self.treeImages.Add(wx.Bitmap("icons\\node-sequence.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeUnknown = self.treeImages.Add(wx.Bitmap("icons\\node-unknown.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeBlob    = self.treeImages.Add(wx.Bitmap("icons\\node-blob.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeAgent   = self.treeImages.Add(wx.Bitmap("icons\\node-agent.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeTest    = self.treeImages.Add(wx.Bitmap("icons\\node-test.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeRun     = self.treeImages.Add(wx.Bitmap("icons\\node-run.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeNs      = self.treeImages.Add(wx.Bitmap("icons\\node-namespace.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeData    = self.treeImages.Add(wx.Bitmap("icons\\node-data.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodePeach   = self.treeImages.Add(wx.Bitmap("icons\\node-peach.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeTemplate= self.treeImages.Add(wx.Bitmap("icons\\node-template.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeGenerator= self.treeImages.Add(wx.Bitmap("icons\\node-generator.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeTransformer= self.treeImages.Add(wx.Bitmap("icons\\node-transform.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeRelation= self.treeImages.Add(wx.Bitmap("icons\\node-relation.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodePublisher= self.treeImages.Add(wx.Bitmap("icons\\node-publisher.gif", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeMonitor = self.treeImages.Add(wx.Bitmap("icons\\node-monitor.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeLogger  = self.treeImages.Add(wx.Bitmap("icons\\node-logger.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodePythonPath = self.treeImages.Add(wx.Bitmap("icons\\node-pythonpath.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeImport  = self.treeImages.Add(wx.Bitmap("icons\\node-import.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeStateModel= self.treeImages.Add(wx.Bitmap("icons\\node-statemachine.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeState   = self.treeImages.Add(wx.Bitmap("icons\\node-state.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeAction  = self.treeImages.Add(wx.Bitmap("icons\\node-action.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeMutator = self.treeImages.Add(wx.Bitmap("icons\\node-mutator.png", wx.BITMAP_TYPE_ANY))
            self.treeImages.NodeMutators= self.treeImages.Add(wx.Bitmap("icons\\node-mutators.png", wx.BITMAP_TYPE_ANY))
            
            self.ImageLookup = {'Block':self.treeImages.NodeBlock,
                                'Choice':self.treeImages.NodeChoice,
                                'Flags':self.treeImages.NodeFlags,
                                'Flag':self.treeImages.NodeFlags,
                                'Number':self.treeImages.NodeNumber,
                                'String':self.treeImages.NodeString,
                                #'Sequence':self.treeImages.NodeSequence,
                                'Blob':self.treeImages.NodeBlob,
                                'Agent':self.treeImages.NodeAgent,
                                'Test':self.treeImages.NodeTest,
                                'Run':self.treeImages.NodeRun,
                                'Include':self.treeImages.NodeNs,
                                'Data':self.treeImages.NodeData,
                                'Field':self.treeImages.NodeUnknown,
                                'Param':self.treeImages.NodeUnknown,
                                'Peach':self.treeImages.NodePeach,
                                'DataModel':self.treeImages.NodeTemplate,
                                'Block':self.treeImages.NodeTemplate,
                                'Generator':self.treeImages.NodeGenerator,
                                'Transformer':self.treeImages.NodeTransformer,
                                'Relation':self.treeImages.NodeRelation,
                                'Publisher':self.treeImages.NodePublisher,
                                'Monitor':self.treeImages.NodeMonitor,
                                'Logger':self.treeImages.NodeLogger,
                                'PythonPath':self.treeImages.NodePythonPath,
                                'Import':self.treeImages.NodeImport,
                                'StateModel':self.treeImages.NodeStateModel,
                                'State':self.treeImages.NodeState,
                                'Action':self.treeImages.NodeAction,
                                'Mutators':self.treeImages.NodeMutators,
                                'Mutator':self.treeImages.NodeMutator,
                                }
            
            self.peachMainTree.SetImageList(self.treeImages)
            
            self.peachMainTree.SetItemImage(self.root, self.treeImages.NodePeach)
            
            self.copy = None
            self.cut = None
            
            # Context menu
            self.MENU_ADD = wx.NewId()
            self.MENU_ADD_REF = wx.NewId()
            self.MENU_REMOVE = wx.NewId()
            self.MENU_SAVE = wx.NewId()
            self.MENU_OPEN = wx.NewId()
            self.MENU_TEST = wx.NewId()
            self.MENU_COPY = wx.NewId()
            self.MENU_CUT = wx.NewId()
            self.MENU_PASTE = wx.NewId()
            self.MENU_UP = wx.NewId()
            self.MENU_DOWN = wx.NewId()
            
            wx.EVT_MENU(self, self.MENU_ADD, self.OnAddElement)
            wx.EVT_MENU(self, self.MENU_REMOVE, self.OnRemoveElement)
            wx.EVT_MENU(self, self.MENU_SAVE, self.OnToolbarSave)
            wx.EVT_MENU(self, self.MENU_OPEN, self.OnToolbarOpen)
            wx.EVT_MENU(self, self.MENU_TEST, self.OnToolbarTest)
            wx.EVT_MENU(self, self.MENU_COPY, self.OnToolbarCopy)
            wx.EVT_MENU(self, self.MENU_CUT, self.OnToolbarCut)
            wx.EVT_MENU(self, self.MENU_PASTE, self.OnToolbarPast)
            wx.EVT_MENU(self, self.MENU_UP, self.OnToolbarUp)
            wx.EVT_MENU(self, self.MENU_DOWN, self.OnToolbarDown)
            
            # Accelerator keys
            keys = [
                wx.AcceleratorEntry(wx.ACCEL_NORMAL,  wx.WXK_INSERT,  self.MENU_ADD),
                wx.AcceleratorEntry(wx.ACCEL_CTRL,    ord('I'),       self.MENU_ADD),
                wx.AcceleratorEntry(wx.ACCEL_CTRL,    ord('N'),       self.MENU_ADD),
                wx.AcceleratorEntry(wx.ACCEL_NORMAL,  wx.WXK_DELETE,  self.MENU_REMOVE),
                wx.AcceleratorEntry(wx.ACCEL_CTRL,    ord('D'),       self.MENU_REMOVE),
                wx.AcceleratorEntry(wx.ACCEL_CTRL,    ord('S'),       self.MENU_SAVE),
                wx.AcceleratorEntry(wx.ACCEL_CTRL,    ord('O'),       self.MENU_OPEN),
                wx.AcceleratorEntry(wx.ACCEL_CTRL,    ord('T'),       self.MENU_TEST),
                wx.AcceleratorEntry(wx.ACCEL_CTRL,    ord('C'),       self.MENU_COPY),
                wx.AcceleratorEntry(wx.ACCEL_CTRL,    ord('X'),       self.MENU_CUT),
                wx.AcceleratorEntry(wx.ACCEL_CTRL,    ord('V'),       self.MENU_PASTE),
                wx.AcceleratorEntry(wx.ACCEL_CTRL,    wx.WXK_UP,      self.MENU_UP),
                wx.AcceleratorEntry(wx.ACCEL_CTRL,    wx.WXK_DOWN,    self.MENU_DOWN),
                ]
            
            self.SetAcceleratorTable( wx.AcceleratorTable(keys) )
            
            # Adjust size of tree
            width, height = self.GetSizeTuple()
            self.peachMainSplitter.SetSashPosition(width * 0.3, True)
            
            #self._LoadFile("HelloWorld.xml")
            self.OnToolbarNew(None)
            self.peachMainTree.SelectItem(self.root, True)
            self.peachMainTree.Expand(self.root)
        
        def _ClearState(self):
            self.peachMainTree.DeleteChildren(self.root)
            self.fileName = None
            self.template = None
            self.SetTitle(self.title % "")
        
        def _LoadFile(self, fileName):
            # Change the cursor
            waitCursor = wx.StockCursor(wx.CURSOR_WAIT)
            self.SetCursor(waitCursor)
            
            try:
                self._ClearState()
                
                self.mainDoc = Ft.Xml.Domlette.NonvalidatingReader.parseUri("file:"+fileName)
                self.doc = self.mainDoc.firstChild
                self.fileName = fileName
                self.SetTitle(self.title % fileName)
                
                self.StripComments(self.doc)
                self.StripText(self.doc)
                
                self.peachMainTree.Freeze()
                
                self.peachMainTree.SetPyData(self.peachMainTree.GetRootItem(), self.doc)
                
                for child in self.doc.childNodes:
                    self.AddChildrenToTree(self.root, child)
                
                self.peachMainTree.Thaw()
            except:
                # should we show error?
                #raise
                print "Caught exception in _LoadFile()!"
                raise
            
            self.SetCursor(wx.NullCursor)
            
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
        
        def _AddDefaults(self, node):
            '''
            Uses NodeDefaults to set default attributes required
            by a node type.  An example would be size for Number.
            '''
            
            if self.NodeDefaults.has_key(node.nodeName):
                for attr in self.NodeDefaults[node.nodeName].keys():
                    if not node.hasAttributeNS(None, attr):
                        node.setAttributeNS(None, attr, self.NodeDefaults[node.nodeName][attr])
        
        def OnToolbarNew(self, event): # wxGlade: PeachMainFrame.<event_handler>
            self._LoadFile("template.xml")
            self.fileName = None
            self.SetTitle(self.title % "New")
    
        def AddChildrenToTree(self, parentId, node):
            '''
            Add a node to the tree.  Adds the children of this node as well!
            
            NOTE: This only builds the tree and links the tree item to the
            node object.
            '''
            
            name = self._GetNodeName(node)
                
            id = self.peachMainTree.AppendItem(parentId, name)
            self.peachMainTree.SetPyData(id, node)
            
            try:
                self.peachMainTree.SetItemImage(id, self.ImageLookup[node.nodeName])
                
            except:
                raise Exception("Unknown nodeName: '%s'" % node.nodeName)
            
            for child in node.childNodes:
                self.AddChildrenToTree(id, child)
            
            return id
        
        def OnToolbarOpen(self, event): # wxGlade: PeachMainFrame.<event_handler>
            dlg = wx.FileDialog(self, 'Choose a Peach XML file to open', '.', '', '*.xml', wx.OPEN)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            
            fileName = dlg.GetPath()
            dlg.Destroy()
            self._LoadFile(fileName)
        
        def OnToolbarSave(self, event): # wxGlade: PeachMainFrame.<event_handler>
            if self.fileName == None or len(self.fileName) == 0:
                self.OnToolbarSaveAs(event)
            
            waitCursor = wx.StockCursor(wx.CURSOR_WAIT)
            self.SetCursor(waitCursor)
            
            try:
                fout = open(self.fileName, "wb+")
                PrettyPrint(self.mainDoc, stream=fout)
                fout.close()
                
            except Exception, e:
                self.SetCursor(wx.NullCursor)
                wx.MessageDialog(self, "Error saving file: %s" % str(e), "Error")
            
            self.SetCursor(wx.NullCursor)
    
        def OnToolbarSaveAs(self, event): # wxGlade: PeachMainFrame.<event_handler>
            dlg = wx.FileDialog(self, 'Save Peach XML As...', '.', '', '*.xml', wx.SAVE)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            
            dlg.Destroy()
            
            try:
                f = open(dlg.GetPath(), 'r')
                f.close()
                
                if wx.MessageDialog(self, "File currently exists, overwrite?", "Overwrite").ShowModal() != wx.ID_OK:
                    return
            except:
                pass
            
            self.fileName = dlg.GetPath()
            self.SetTitle(self.title % self.fileName)
            waitCursor = wx.StockCursor(wx.CURSOR_WAIT)
            self.SetCursor(waitCursor)
            
            try:
                fout = open(self.fileName, "wb+")
                PrettyPrint(self.mainDoc, stream=fout)
                fout.close()
                
            except:
                self.SetCursor(wx.NullCursor)
                raise
                #wx.MessageDialog(self, "Error saving file: %s" % str(e), "Error")
            
            self.SetCursor(wx.NullCursor)
    
        def OnToolbarNewNode(self, event): # wxGlade: PeachMainFrame.<event_handler>
            self.OnAddElement(event)
            
        def OnToolbarCopy(self, event): # wxGlade: PeachMainFrame.<event_handler>
            itemId = self.peachMainTree.GetSelection()
            
            if itemId == self.root:
                return
            
            self.copy = self.peachMainTree.GetPyData(itemId)
            self.cut = None
    
        def OnToolbarCut(self, event): # wxGlade: PeachMainFrame.<event_handler>
            itemId = self.peachMainTree.GetSelection()
            if itemId == self.root:
                return
            
            node = self.peachMainTree.GetPyData(itemId)
            
            self.peachMainTree.Delete(itemId)
            node.parentNode.removeChild(node)
            
            self.copy = None
            self.cut = node
        
        def OnToolbarPast(self, event): # wxGlade: PeachMainFrame.<event_handler>
            itemId = self.peachMainTree.GetSelection()
            parentNode = self.peachMainTree.GetPyData(itemId)
            
            if self.copy != None:
                node = self.copy.cloneNode(True)
                
            elif self.cut != None:
                node = self.cut
                self.cut = None
            
            else:
                pass
            
            #type = self._GetTopLevelType(node)
            imgId = self.treeImages.NodeUnknown
            
            try:
                imgId = self.ImageLookup[node.nodeName]
            except:
                pass
            
            name = self._GetNodeName(node)
            
            self.peachMainTree.Freeze()
            
            self._AddDefaults(node)
            parentNode.appendChild(node)
            id = self.AddChildrenToTree(itemId, node)
            
            self.peachMainTree.Thaw()
            self.peachMainTree.EnsureVisible(id)
            self.peachMainTree.SelectItem(id)
            #self.peachMainTree.EditLabel(id)
            
        def OnToolbarTest(self, event): # wxGlade: PeachMainFrame.<event_handler>
            self.OnToolbarSave(event)
            
            #dialog = _PeachTestDialog(self)
            #dialog.FileName = self.fileName
            #dialog.ShowModal()
            
            peachMain = PeachValidator.PeachValidatorGui()
            peachMain.textPeachXmlFilename.SetValue(self.fileName)
            peachMain.Show()
    
        def OnTreeEndDrag(self, event): # wxGlade: PeachMainFrame.<event_handler>
            print "Event handler `OnTreeEndDrag' not implemented!"
            event.Skip()
    
        def OnTreeDeleteItem(self, event): # wxGlade: PeachMainFrame.<event_handler>
            pass
            
        def OnRemoveElement(self, event):
            itemId = self.peachMainTree.GetSelection()
            
            if itemId == self.root:
                return
            
            node = self.peachMainTree.GetPyData(itemId)
            node.parentNode.removeChild(node)
            
            self.peachMainTree.Freeze()
            self.peachMainTree.Delete(itemId)
            self.peachMainTree.Thaw()
            
        def OnToolbarRemoveNode(self, event): # wxGlade: PeachMainFrame.<event_handler>
            self.OnRemoveElement(event)
    
        def OnToolbarUp(self, event): # wxGlade: PeachMainFrame.<event_handler>
            itemId = self.peachMainTree.GetSelection()
            if itemId == self.root:
                return
            
            parentId = self.peachMainTree.GetItemParent(itemId)
            
            node = self.peachMainTree.GetPyData(itemId)
            
            if node.previousSibling == None:
                # already the first!
                return
            
            try:
                imgId = self.ImageLookup[node.nodeName]
            except:
                imgId = self.treeImages.NodeUnknown
            
            self.peachMainTree.Freeze()
            
            sibling = node.previousSibling
            siblingId = self.peachMainTree.GetPrevSibling(itemId)
            preSiblingId = self.peachMainTree.GetPrevSibling(siblingId)
            
            parentNode = node.parentNode
            parentNode.removeChild(node)
            parentNode.insertBefore(node, sibling)
            
            self.peachMainTree.Delete(itemId)
            
            if siblingId.IsOk() and preSiblingId.IsOk():
                newItemId = self.peachMainTree.InsertItem(parentId, preSiblingId, self._GetNodeName(node), imgId)
            else:
                newItemId = self.peachMainTree.InsertItemBefore(parentId, 0, self._GetNodeName(node), imgId)
                
            self.peachMainTree.SetPyData(newItemId, node)
            
            for child in node.childNodes:
                self.AddChildrenToTree(newItemId, child)
            
            self.peachMainTree.Thaw()
            self.peachMainTree.EnsureVisible(newItemId)
            self.peachMainTree.SelectItem(newItemId)
        
        def OnToolbarDown(self, event): # wxGlade: PeachMainFrame.<event_handler>
            itemId = self.peachMainTree.GetSelection()
            if itemId == self.root or not itemId.IsOk():
                return
            
            parentId = self.peachMainTree.GetItemParent(itemId)
            
            node = self.peachMainTree.GetPyData(itemId)
            
            if node.nextSibling == None:
                # already the last
                return
            
            try:
                imgId = self.ImageLookup[node.nodeName]
            except:
                imgId = self.treeImages.NodeUnknown
            
            self.peachMainTree.Freeze()
            
            sibling = node.nextSibling
            siblingNext = sibling.nextSibling
            siblingId = self.peachMainTree.GetNextSibling(itemId)
            
            parentNode = node.parentNode
            parentNode.removeChild(node)
            
            if siblingNext != None:
                parentNode.insertBefore(node, siblingNext)
            else:
                parentNode.appendChild(node)
                
            self.peachMainTree.Delete(itemId)
            
            if siblingId.IsOk():
                newItemId = self.peachMainTree.InsertItem(parentId, siblingId, self._GetNodeName(node), imgId)
            else:
                newItemId = self.peachMainTree.AppendItem(parentId, self._GetNodeName(node), imgId)
            
            self.peachMainTree.SetPyData(newItemId, node)
            
            for child in node.childNodes:
                self.AddChildrenToTree(newItemId, child)
            
            self.peachMainTree.Thaw()
            self.peachMainTree.EnsureVisible(newItemId)
            self.peachMainTree.SelectItem(newItemId)
        
        def _GetNodeName(self, node):
            '''
            Inspect the node and figure out what we should call it.
            '''
            if node.hasAttributeNS(None, 'name'):
                return node.getAttributeNS(None, 'name')
            
            if node.hasAttributeNS(None, 'ref'):
                return node.getAttributeNS(None, 'ref')
            
            if node.hasAttributeNS(None, 'class'):
                return node.getAttributeNS(None, 'class')
            
            if node.hasAttributeNS(None, 'ns'):
                return node.getAttributeNS(None, 'ns')
            
            if node.hasAttributeNS(None, 'of'):
                return node.getAttributeNS(None, 'of')
            
            if node.hasAttributeNS(None, 'from'):
                return node.getAttributeNS(None, 'from')
            
            if node.hasAttributeNS(None, 'path'):
                return node.getAttributeNS(None, 'path')
            
            if node.hasAttributeNS(None, 'import'):
                return node.getAttributeNS(None, 'import')
            
            return ""
        
        def _SetNodeName(self, node, name):
            '''
            Inspect the node and figure out where the name goes :)
            '''
            
            if node.hasAttributeNS(None, 'name'):
                node.setAttributeNS(None, 'name', name)
                return
            
            type = self._GetTopLevelType(node)
            
            if name.startswith('ref:'):
                name = name[4:]
            
            if type == 'Test' and (node.nodeName == 'StateModel' or node.nodeName == 'Agent' or node.nodeName == 'Agent-Param'):
                node.setAttributeNS(None, 'ref', name)
                return
            
            if type == 'Run' and (node.nodeName == 'Test'):
                node.setAttributeNS(None, 'ref', name)
                return
            
            if node.nodeName == 'Monitor' or node.nodeName == 'Publisher' or node.nodeName == 'Generator' \
               or node.nodeName == 'Transformer' or node.nodeName == 'Logger':
                
                node.setAttributeNS(None, 'class', name)
                return
            
            if node.nodeName == 'Include':
                node.setAttributeNS(None, 'ns', name)
                return
            
            if node.nodeName == 'PythonPath':
                node.setAttributeNS(None, 'path', name)
                return
            
            if node.nodeName == 'Import':
                node.setAttributeNS(None, 'import', name)
                return
            
            if node.nodeName == 'Relation':
                if node.hasAttributeNS(None, 'of'):
                    node.setAttributeNS(None, 'of', name)
                
                elif node.hasAttributeNS(None, 'from'):
                    node.setAttributeNS(None, 'from', name)
                
                else:
                    node.setAttributeNS(None, 'of', name)
            
            node.setAttributeNS(None, 'name', name)
        
        def _GetTopLevelType(self, node):
            '''
            Walk to top level parent and figure out what type we are.
            '''
            
            # F*ing hack, but whatever
            parentNode1 = node
            parentNode2 = node
            parentNode3 = node
            while parentNode1.parentNode != None:
                parentNode3 = parentNode2
                parentNode2 = parentNode1
                parentNode1 = parentNode1.parentNode
            
            return parentNode3.nodeName
        
        def _MapStrToEnum(self, value, strArray, numArray):
            
            if value == None or len(value) == 0:
                return numArray[0]
            
            value = str(value)
            for index in range(len(strArray)):
                if strArray[index] == value:
                    break
            
            return numArray[index]
        
        def _MapNumToEnum(self, num, strArray, numArray):
            
            index = 0
            for n in numArray:
                if n == num:
                    break
                
                index += 1
            
            return strArray[index]
        
        def _CreateStringProperty(self, name, str):
            if str != None:
                return wxpg.StringProperty(name, value=str)
            
            return wxpg.StringProperty(name)
        
        def _CreateIntProperty(self, name, num, default):
            if num != None and len(str(num)) != 0:
                return wxpg.IntProperty(name, value=int(num))
            
            return wxpg.IntProperty(name, value=int(default))
        
        def _StrToBool(self, b, default):
            if b.lower() == 'true':
                return True
            elif b.lower() == 'false':
                return False
            
            return default
        
        ValueTypesKey = ['string', 'hex', 'literal' ]
        ValueTypesVal = [0, 1, 2]
        StringTypeKey = ['char', 'wchar']
        StringTypeVal = [0, 1]
        IntSizeKey = ['', '8', '16', '32', '64']
        IntSizeVal = [0, 8, 16, 32, 64]
        EndianKey = ['little', 'big', 'network']
        EndianVal = [1, 2, 2]
        RelationKey = ['', 'size', 'count', 'offset', 'when']
        RelationVal = [0, 1, 2, 3, 4]
        
        def _CreateEditEnum(self, node, attrib):
            
            nums = range(len(EnumDropDowns[node.nodeName][attrib]))
            
            return wxpg.EditEnumProperty(attrib, attrib,
                EnumDropDowns[node.nodeName][attrib],
                nums,
                node.getAttributeNS(None, attrib))
           
        def _SetPropertiesHelpText(self, key):
            '''
            Generates help text for object properties
            '''

            helpText = ""

            if HelpPropertyItems.has_key(key):
                helpText = "Properties:\r\n"

                for property in HelpPropertyItems[key]:
                    helpText += ("\r\n" + property + ": " + HelpPropertyItems[key][property] + "\r\n")
                
            self.textPropHelp.ChangeValue(helpText)

        def _PopulatePropertyGrid(self, node):
            '''
            Populate the PropertyGrid based on node.
            '''
            
            self.peachMainPropertyGrid.Clear()
            
            if node == None:
                return
            
            # 1st, get top level type (template, tests, data, runs)
            type = self._GetTopLevelType(node)
            self.peachMainPropertyGrid.Freeze()

            if type == 'Peach':
                self.peachMainPropertyGrid.AppendCategory("Peach")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("version", node.getAttributeNS(None, 'version')))
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("author", node.getAttributeNS(None, 'author')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("description", node.getAttributeNS(None, 'description')) )
            
            elif type != 'Action' and type != 'Action-Param' and type != 'Action-Result' and node.nodeName == 'DataModel' or node.nodeName == 'Block':
                if node.nodeName == 'DataModel':
                    self.peachMainPropertyGrid.AppendCategory("DataModel")
                else:
                    self.peachMainPropertyGrid.AppendCategory("Block")
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("ref", node.getAttributeNS(None, 'ref')) )
                
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("minOccurs", node.getAttributeNS(None, 'minOccurs'), 1) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("maxOccurs", node.getAttributeNS(None, 'maxOccurs'), 1) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("generatedOccurs", node.getAttributeNS(None, 'generatedOccurs'), 1) )
                
            elif node.nodeName == 'DataModel':
                self.peachMainPropertyGrid.AppendCategory("DataModel")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("ref", node.getAttributeNS(None, 'ref')) )
            
            elif node.nodeName == 'Choice':
                self.peachMainPropertyGrid.AppendCategory("Choice")
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("Name", node.getAttributeNS(None, 'name')) )
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("ref", node.getAttributeNS(None, 'ref')) )
               
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("minOccurs", node.getAttributeNS(None, 'minOccurs'), 1) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("maxOccurs", node.getAttributeNS(None, 'maxOccurs'), 1) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("generatedOccurs", node.getAttributeNS(None, 'generatedOccurs'), 1) )
            
            elif node.nodeName == 'String':
                self.peachMainPropertyGrid.AppendCategory("String")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("ref", node.getAttributeNS(None, 'ref')) )
                
                self.peachMainPropertyGrid.Append( wxpg.EnumProperty("valueType", "valueType",
                    self.ValueTypesKey, self.ValueTypesVal,
                    self._MapStrToEnum(node.getAttributeNS(None, 'valueType'), self.ValueTypesKey, self.ValueTypesVal)) )
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("value", str(node.getAttributeNS(None, 'value'))) )
                
                self.peachMainPropertyGrid.Append( wxpg.EnumProperty("type", "Type",
                    self.StringTypeKey, self.StringTypeVal, self._MapStrToEnum(node.getAttributeNS(None, 'type'), self.StringTypeKey, self.StringTypeVal)) )
                self.peachMainPropertyGrid.Append( wxpg.BoolProperty("isStatic", value=self._StrToBool(node.getAttributeNS(None, 'isStatic'), False)) )
                self.peachMainPropertyGrid.Append( wxpg.BoolProperty("nullTerminated", value=self._StrToBool(node.getAttributeNS(None, 'nullTerminated'), False)) )
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("length", str(node.getAttributeNS(None, 'length'))) )
               
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("minOccurs", node.getAttributeNS(None, 'minOccurs'), 1) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("maxOccurs", node.getAttributeNS(None, 'maxOccurs'), 1) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("generatedOccurs", node.getAttributeNS(None, 'generatedOccurs'), 1) )
            
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("tokens", str(node.getAttributeNS(None, 'tokens'))) )

            elif node.nodeName == 'Number':
                self.peachMainPropertyGrid.AppendCategory("Number")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("ref", node.getAttributeNS(None, 'ref')) )
                
                self.peachMainPropertyGrid.Append( wxpg.EnumProperty("valueType", "valueType",
                    self.ValueTypesKey, self.ValueTypesVal,
                    self._MapStrToEnum(node.getAttributeNS(None, 'valueType'), self.ValueTypesKey, self.ValueTypesVal)) )
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("value", str(node.getAttributeNS(None, 'value'))) )
                
                self.peachMainPropertyGrid.Append( wxpg.EnumProperty("size", "size",
                    self.IntSizeKey, self.IntSizeVal, self._MapStrToEnum(node.getAttributeNS(None, 'size'), self.IntSizeKey, self.IntSizeVal)) )
                
                self.peachMainPropertyGrid.Append( wxpg.EnumProperty("endian", "endian",
                    self.EndianKey, self.EndianVal, self._MapStrToEnum(node.getAttributeNS(None, 'endian'), self.EndianKey, self.EndianVal)) )
                
                self.peachMainPropertyGrid.Append( wxpg.BoolProperty("signed", value=self._StrToBool(node.getAttributeNS(None, 'signed'), False)) )
                
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("minOccurs", node.getAttributeNS(None, 'minOccurs'), 1) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("maxOccurs", node.getAttributeNS(None, 'maxOccurs'), 1) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("generatedOccurs", node.getAttributeNS(None, 'generatedOccurs'), 1) )

           
            elif node.nodeName == 'Flags':
                self.peachMainPropertyGrid.AppendCategory("Flags")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("ref", node.getAttributeNS(None, 'ref')) )
                
                self.peachMainPropertyGrid.Append( wxpg.EnumProperty("size", "size",
                    self.IntSizeKey, self.IntSizeVal, self._MapStrToEnum(node.getAttributeNS(None, 'size'), self.IntSizeKey, self.IntSizeVal)) )
                
                self.peachMainPropertyGrid.Append( wxpg.EnumProperty("endian", "endian",
                    self.EndianKey, self.EndianVal, self._MapStrToEnum(node.getAttributeNS(None, 'endian'), self.EndianKey, self.EndianVal)) )
                
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("minOccurs", node.getAttributeNS(None, 'minOccurs'), 1) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("maxOccurs", node.getAttributeNS(None, 'maxOccurs'), 1) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("generatedOccurs", node.getAttributeNS(None, 'generatedOccurs'), 1) )
           
            elif node.nodeName == 'Flag':
                self.peachMainPropertyGrid.AppendCategory("Flag")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("position", node.getAttributeNS(None, 'position'), 0) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("size", node.getAttributeNS(None, 'size'), 0) )
                
                self.peachMainPropertyGrid.Append( wxpg.EnumProperty("valueType", "valueType",
                    self.ValueTypesKey, self.ValueTypesVal,
                    self._MapStrToEnum(node.getAttributeNS(None, 'valueType'), self.ValueTypesKey, self.ValueTypesVal)) )
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("value", str(node.getAttributeNS(None, 'value'))) )                          

            elif node.nodeName == 'Blob':
                self.peachMainPropertyGrid.AppendCategory("Blob")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                
                self.peachMainPropertyGrid.Append( wxpg.EnumProperty("valueType", "valueType",
                    self.ValueTypesKey, self.ValueTypesVal,
                    self._MapStrToEnum(node.getAttributeNS(None, 'valueType'), self.ValueTypesKey, self.ValueTypesVal)) )
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("value", str(node.getAttributeNS(None, 'value'))) )
                
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("minOccurs", node.getAttributeNS(None, 'minOccurs'), 1) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("maxOccurs", node.getAttributeNS(None, 'maxOccurs'), 1) )
                self.peachMainPropertyGrid.Append( self._CreateIntProperty("generatedOccurs", node.getAttributeNS(None, 'generatedOccurs'), 1) )
            
            ## SUB-TEMPLATE
            
            elif node.nodeName == 'Generator':
                self.peachMainPropertyGrid.AppendCategory("Generator")
                self.peachMainPropertyGrid.Append( self._CreateEditEnum(node, "class") )
                #self.peachMainPropertyGrid.Append( self._CreateStringProperty("class", node.getAttributeNS(None, 'class')) )         
            
            elif node.nodeName == 'Transformer':
                self.peachMainPropertyGrid.AppendCategory("Transformer")
                self.peachMainPropertyGrid.Append( self._CreateEditEnum(node, "class") )
            
            elif node.nodeName == 'Relation':
                self.peachMainPropertyGrid.AppendCategory("Relation")
                self.peachMainPropertyGrid.Append( wxpg.EnumProperty("type", "type",
                    self.RelationKey, self.RelationVal,
                    self._MapStrToEnum(node.getAttributeNS(None, 'type'), self.RelationKey, self.RelationVal)) )
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("of", node.getAttributeNS(None, 'of')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("from", node.getAttributeNS(None, 'from')) )
            
            ## Mutators
            
            elif node.nodeName == 'Mutators':
                self.peachMainPropertyGrid.AppendCategory("Mutators")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
            
            elif node.nodeName == 'Mutator':
                self.peachMainPropertyGrid.AppendCategory("Mutator")
                #self.peachMainPropertyGrid.Append( self._CreateEditEnum(node, "class") )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("class", node.getAttributeNS(None, 'class')) )
            
            ## Agent
            
            elif type != 'Test' and node.nodeName == 'Agent':
                self.peachMainPropertyGrid.AppendCategory("Agent")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("location", node.getAttributeNS(None, 'location')) )
                
            elif node.nodeName == 'Agent':
                self.peachMainPropertyGrid.AppendCategory("Agent")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("ref", node.getAttributeNS(None, 'ref')) )
                
            elif node.nodeName == 'Monitor':
                self.peachMainPropertyGrid.AppendCategory("Monitor")
                self.peachMainPropertyGrid.Append( self._CreateEditEnum(node, "class") )
            
            ## DATA
            
            elif node.nodeName == 'Data':
                self.peachMainPropertyGrid.AppendCategory("Data")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("ref", node.getAttributeNS(None, 'ref')) )
            
            elif node.nodeName == 'Field':
                self.peachMainPropertyGrid.AppendCategory("Field")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                self.peachMainPropertyGrid.Append( wxpg.EnumProperty("valueType", "valueType",
                    self.ValueTypesKey, self.ValueTypesVal,
                    self._MapStrToEnum(node.getAttributeNS(None, 'valueType'), self.ValueTypesKey, self.ValueTypesVal)) )
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("value", str(node.getAttributeNS(None, 'value'))) )
            
            ## NAMESPACE
            
            elif type == 'Include':
                self.peachMainPropertyGrid.AppendCategory("Include")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("ns", node.getAttributeNS(None, 'ns')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("src", node.getAttributeNS(None, 'src')) )
            
            elif type == 'PythonPath':
                self.peachMainPropertyGrid.AppendCategory("Python Path")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("path", node.getAttributeNS(None, 'path')) )
                
            elif type == 'Import':
                self.peachMainPropertyGrid.AppendCategory("Import Python Module")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("from", node.getAttributeNS(None, 'from')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("import", node.getAttributeNS(None, 'import')) )
            
            ## StateMachine
            
            elif type != 'Test' and node.nodeName == 'StateModel':
                self.peachMainPropertyGrid.AppendCategory("State Model")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("initial", node.getAttributeNS(None, 'initial')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("onEnter", node.getAttributeNS(None, 'onEnter')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("onExit", node.getAttributeNS(None, 'onExit')) )
            
            elif node.nodeName == 'StateModel':
                self.peachMainPropertyGrid.AppendCategory("State Model")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("ref", node.getAttributeNS(None, 'ref')) )
            
            elif node.nodeName == 'State':
                self.peachMainPropertyGrid.AppendCategory("State")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("onEnter", node.getAttributeNS(None, 'onEnter')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("onExit", node.getAttributeNS(None, 'onExit')) )
            
            elif node.nodeName == 'Action':
                self.peachMainPropertyGrid.AppendCategory("Action")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                self.peachMainPropertyGrid.Append( self._CreateEditEnum(node, "type") )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("when", node.getAttributeNS(None, 'when')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("ref", node.getAttributeNS(None, 'ref')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("method", node.getAttributeNS(None, 'method')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("onStart", node.getAttributeNS(None, 'onStart')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("onComplete", node.getAttributeNS(None, 'onComplete')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("setXpath", node.getAttributeNS(None, 'setXpath')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("valueXpath", node.getAttributeNS(None, 'valueXpath')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("value", node.getAttributeNS(None, 'value')) )
            
            elif node.nodeName == 'Action-Param':
                self.peachMainPropertyGrid.AppendCategory("Action Parameter")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                self.peachMainPropertyGrid.Append( self._CreateEditEnum(node, "type") )
            
            elif node.nodeName == 'Action-Result':
                self.peachMainPropertyGrid.AppendCategory("Action Result")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
            
            ## TEST
            
            elif type != 'Run' and node.nodeName == 'Test':
                self.peachMainPropertyGrid.AppendCategory("Test")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("description", node.getAttributeNS(None, 'description')) )
            
            elif node.nodeName == 'Test':
                self.peachMainPropertyGrid.AppendCategory("Test")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("ref", node.getAttributeNS(None, 'ref')) )
            
            elif node.nodeName == 'Publisher':
                self.peachMainPropertyGrid.AppendCategory("Publisher")
                self.peachMainPropertyGrid.Append( self._CreateEditEnum(node, "class") )
                #self.peachMainPropertyGrid.Append( self._CreateStringProperty("class", node.getAttributeNS(None, 'class')) )
            
            elif node.nodeName == 'Param':
                self.peachMainPropertyGrid.AppendCategory("Param")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
                self.peachMainPropertyGrid.Append( wxpg.EnumProperty("valueType", "valueType",
                    self.ValueTypesKey, self.ValueTypesVal,
                    self._MapStrToEnum(node.getAttributeNS(None, 'valueType'), self.ValueTypesKey, self.ValueTypesVal)) )
                
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("value", str(node.getAttributeNS(None, 'value'))) )
            
            ## RUN
            elif node.nodeName == 'Run':
                self.peachMainPropertyGrid.AppendCategory("Run")
                self.peachMainPropertyGrid.Append( self._CreateStringProperty("name", node.getAttributeNS(None, 'name')) )
            
            elif node.nodeName == 'Logger':
                self.peachMainPropertyGrid.AppendCategory("Logger")
                self.peachMainPropertyGrid.Append( self._CreateEditEnum(node, "class") )
            
            else:
                print "_PopulatePropertyGrid(): Unknown node:", node.nodeName

            self._SetPropertiesHelpText(node.nodeName)
            self.peachMainPropertyGrid.Thaw()
            
        def OnTreeSelectionChanged(self, event): # wxGlade: PeachMainFrame.<event_handler>
            itemId = event.GetItem()
            node = self.peachMainTree.GetPyData(itemId)
            self._PopulatePropertyGrid(node)
    
        def OnTreeSelectionChanging(self, event): # wxGlade: PeachMainFrame.<event_handler>
            #print "Event handler `OnTreeSelectionChanging' not implemented!"
            event.Skip()
    
        def OnTreeItemActivated(self, event): # wxGlade: PeachMainFrame.<event_handler>
            if not self.peachMainTree.IsExpanded(event.GetItem()):
                self.peachMainTree.Expand(event.GetItem())
            else:
                self.peachMainTree.Collapse(event.GetItem())
    
        def OnTreeEndLabelEdit(self, event): # wxGlade: PeachMainFrame.<event_handler>
            '''
            Same rules as for displaying label.
            '''
            
            itemId = event.GetItem()
            node = self.peachMainTree.GetPyData(itemId)
            text = event.GetLabel()
            
            if node == None:
                print "OnTreeEndLabelEdit(): node was None"
                return
            
            self._SetNodeName(node, text)
            self._PopulatePropertyGrid(node)
        
        def OnPropertyGridChanged(self, event):
            
            ### TODO: Properly handle enum!!
            
            node = self.peachMainTree.GetPyData(self.peachMainTree.GetSelection())
            if node == None:
                # Shouldn't ever get here!
                return
            
            name = event.GetPropertyLabel()
            value = event.GetPropertyValue()
            
            if name == 'valueType':
                value = self._MapNumToEnum(value, self.ValueTypesKey, self.ValueTypesVal)
            
            elif name == 'endian':
                value = self._MapNumToEnum(value, self.EndianKey, self.EndianVal)
            
            elif name == 'size':
                value = self._MapNumToEnum(value, self.IntSizeKey, self.IntSizeVal)
            
            elif name == 'type' and node.nodeName == 'String':
                value = self._MapNumToEnum(value, self.StringTypeKey, self.StringTypeVal)
            
            elif name == 'type' and node.nodeName == 'Relation':
                value = self._MapNumToEnum(value, self.RelationKey, self.RelationVal)
            
            node.setAttributeNS(None, name, str(value))
            
            self.peachMainTree.Freeze()
            
            n = node.getAttributeNS(None, 'name')
            if name == 'name':
                self.peachMainTree.SetItemText(self.peachMainTree.GetSelection(), value)
                
            elif not node.hasAttributeNS(None, 'name') and name == 'ref':
                self.peachMainTree.SetItemText(self.peachMainTree.GetSelection(), value)
            
            elif not node.hasAttributeNS(None, 'name') and name == 'class':
                self.peachMainTree.SetItemText(self.peachMainTree.GetSelection(), value)
                node.setAttributeNS(None, 'class', value)
            
            elif node.nodeName == 'Include':
                self.peachMainTree.SetItemText(self.peachMainTree.GetSelection(), value)
                node.setAttributeNS(None, 'ns', value)
            
            self.peachMainTree.Thaw()
        
        def OnTreeItemMenu(self, event):
            
            itemId = event.GetItem()
            self.peachMainTree.SelectItem(itemId)
            
            menu = wx.Menu()
            
            menu.Append(self.MENU_ADD, "Add\tInsert")
            
            if itemId != self.root:
                menu.Append(self.MENU_REMOVE, "Remove\tDelete")
            
            menu.AppendSeparator()
            
            menu.Append(self.MENU_COPY, "Copy\tCtrl-Y")
            menu.Append(self.MENU_CUT, "Cut\tCtrl-X")
            menu.Append(self.MENU_PASTE, "Paste\tCtrl-V")
            
            if itemId == self.peachMainTree.GetRootItem():
                menu.AppendSeparator()
                menu.Append(self.MENU_TEST, "Test\tCtrl-T")
            
            self.currentItem = event.GetItem()
            self.PopupMenu(menu, event.GetPoint())
        
        def OnAddElement(self, event):
            
            dialog = None
            nodeType = ''
            
            itemId = self.peachMainTree.GetSelection()
            node = self.peachMainTree.GetPyData(itemId)
            if node != None:
                nodeType = node.nodeName
                
            type = self._GetTopLevelType(node)
            
            # Check if we should display dialog and what goes in it
            if type != 'Test' and (nodeType == 'Block' or nodeType == 'DataModel' or nodeType == 'Sequence' or nodeType == 'Choice'):
                dialog = MyAddDialog(self)
                dialog.textAddHelp.Clear()
                dialog.AddDialogListBox.Clear()
                dialog.AddDialogListBox.InsertItems([
                    'Blob',
                    'Block',
                    'Choice',
                    'Flags',
                    'Number',
                    'Sequence',
                    'String',
                    'Transformer',
                    ], 0)
                dialog.Update()
            
            elif nodeType == 'Peach':
                dialog = MyAddDialog(self)
                dialog.AddDialogListBox.Clear()
                dialog.AddDialogListBox.InsertItems([
                    'Agent',
                    'Data',
                    'Import',
                    'Include',
                    'PythonPath',
                    'Run',
                    'StateModel',
                    'DataModel',
                    'Test',
                    ], 0)
            
            elif nodeType == 'Run':
                dialog = MyAddDialog(self)
                dialog.AddDialogListBox.Clear()
                dialog.AddDialogListBox.InsertItems([
                    'Test',
                    'Logger',
                    ], 0)
            
            elif type != 'Test' and nodeType == 'Agent':
                dialog = SkipDialog('Monitor')
                
            elif type != 'Test' and nodeType == 'Data':
                dialog = SkipDialog('Field')
            
            elif type != 'Run' and nodeType == 'Test':
                dialog = MyAddDialog(self)
                dialog.AddDialogListBox.Clear()
                dialog.AddDialogListBox.InsertItems([
                    'Agent',
                    'Data',
                    'Publisher',
                    'StateModel',
                    ], 0)
            
            elif nodeType == 'Logger':
                dialog = SkipDialog('Param')
                
            elif nodeType == 'String' or nodeType == 'Number' or nodeType == 'Blob':
                dialog = MyAddDialog(self)
                dialog.AddDialogListBox.Clear()
                dialog.AddDialogListBox.InsertItems([
                    'Generator',
                    'Relation',
                    'Transformer',
                    ], 0)
            
            elif nodeType == 'Flags':
                dialog = MyAddDialog(self)
                dialog.AddDialogListBox.Clear()
                dialog.AddDialogListBox.InsertItems([
                    'Flag',
                    'Generator',
                    'Relation',
                    'Transformer',
                    ], 0)
            
            elif nodeType == 'Relation' or nodeType == 'Generator' \
                    or nodeType == 'Transformer' or nodeType == 'Publisher' \
                    or nodeType == 'Monitor':
                
                dialog = SkipDialog('Param')
            
            elif nodeType == 'StateModel':
                dialog = SkipDialog('State')
            
            elif nodeType == 'State':
                dialog = SkipDialog('Action')
            
            elif nodeType == 'Action':
                dialog = MyAddDialog(self)
                dialog.AddDialogListBox.Clear()
                dialog.AddDialogListBox.InsertItems([
                    'Action-Param',
                    'Action-Result',
                    'Data',
                    'DataModel',
                    ], 0)
            
            elif nodeType == 'Action-Param':
                dialog = MyAddDialog(self)
                dialog.AddDialogListBox.Clear()
                dialog.AddDialogListBox.InsertItems([
                    'Data',
                    'DataModel',
                    ], 0)
            
            elif nodeType == 'Action-Result':
                dialog = SkipDialog('DataModel')
            
            else:
                print "OnAddElement: Unknown nodeType: ", nodeType
                return
            
            if dialog.ShowModal() == wx.ID_OK:
                item = dialog.AddDialogListBox.GetSelection()
                item = dialog.AddDialogListBox.GetString(item)
                
                treeItemId = self.peachMainTree.GetSelection()
                
                self._AddElement(treeItemId, item)
                
            else:
                #print "CANCEL"
                pass
            
            dialog.Destroy()
        
        def OnAddReference(self, event):
            print "OnAddReference"
            
        
        def _AddElement(self, treeItemId, item):
            
            parentNode = self.peachMainTree.GetPyData(treeItemId)
            
            imgId = self.treeImages.NodeUnknown
            node = parentNode.ownerDocument.createElementNS(None, item)
            self._AddDefaults(node)
            parentNode.appendChild(node)
            
            try:
                imgId = self.ImageLookup[item]
            except:
                pass
            
            self.peachMainTree.Freeze()
            id = self.peachMainTree.AppendItem(treeItemId, "")
            self.peachMainTree.SetItemImage(id, imgId)
            self.peachMainTree.SetPyData(id, node)
            self.peachMainTree.Thaw()
            self.peachMainTree.EnsureVisible(id)
            self.peachMainTree.SelectItem(id)
            self.peachMainTree.EditLabel(id)
        
        def OnToolbarAbout(self, event): # wxGlade: PeachMainFrame.<event_handler>
            gui.AboutDialog(self).ShowModal()
    
    from traceback import format_tb
    
    class _PeachTestDialog(gui.PeachTestDialog):
        
        def OnParse(self, event): # wxGlade: PeachTestDialog.<event_handler>
            try:
                self.p = parser.ParseTemplate()
                self.peach = self.p.parse("file:"+self.FileName)
                self.textOutput.SetValue("No errors on parse!")
            except:
                out = "*** Errors detected during parse ***\n\n"
                value = sys.exc_info()[1]
                traceback = sys.exc_info()[2]
                
                out += str(value) + "\n\n"
                for t in format_tb(traceback):
                    out += t + "\n"
                out += str(value)
                
                self.textOutput.SetValue(out)
        
        def OnCount(self, event): # wxGlade: PeachTestDialog.<event_handler>
            try:
                #if not self.p:
                #    self.p = parser.ParseTemplate()
                #    self.peach = p.parse("file:"+self.FileName)
                
                e = engine.Engine()
                totalCount = e.Count("file:"+self.FileName)
                self.textOutput.SetValue("\nGrand total of %d test variations" % totalCount)
            
            except:
                out = "*** Errors detected during counting ***\n\n"
                value = sys.exc_info()[1]
                traceback = sys.exc_info()[2]
                
                out += str(value) + "\n\n"
                for t in format_tb(traceback):
                    out += t + "\n"
                out += str(value)
                
                self.textOutput.SetValue(out)
        
        def OnGenerate(self, event): # wxGlade: PeachTestDialog.<event_handler>
            try:
                if not hasattr(self,'p'):
                    self.p = parser.ParseTemplate()
                    self.peach = self.p.parse("file:"+self.FileName)
                
                if not hasattr(self,'build'):
                    runName = 'DefaultRun'
                    if hasattr(self.peach.runs, runName):
                        run = getattr(self.peach.runs, runName)
                    else:
                        self.textOutput.SetValue("Can't find run [%s]" % runName)
                        return
                
                    test = run.tests[0]
                    templateName = test.template.name
                    if test.data != None:
                        dataName = test.data.name
                    else:
                        dataName = None
                
                    self.build = engine.BuildPeach(self.peach)
                    (self.group, self.gen, self.template) = self.build.getDefaultPeachByName(templateName, dataName)
                
                self.textOutput.SetValue(repr(self.gen.getValue()))
                self.group.next()
                
            except:
                out = "*** Errors detected during parse ***\n\n"
                value = sys.exc_info()[1]
                traceback = sys.exc_info()[2]
                
                out += str(value) + "\n\n"
                for t in format_tb(traceback):
                    out += t + "\n"
                out += str(value)
                
                self.textOutput.SetValue(out)
    
    
    class MyAddDialog(gui.AddDialog):
        def __init__(self, parent):
            gui.AddDialog.__init__(self, parent)
            self.textAddHelp.Clear()
            size = wx.Size(300, 350)
            self.SetSize(size)
        
        def OnListBox(self, event):
            index = self.AddDialogListBox.GetSelection()
            item = self.AddDialogListBox.GetString(index)
            
            self.textAddHelp.Clear()
            if HelpTreeNodes.has_key(item):
                self.textAddHelp.ChangeValue(HelpTreeNodes[item])
    
    
    class _SkipDialogHelper:
        def __init__(self, item):
            self.item = item
            
        def GetSelection(self):
            pass
        def GetString(self, item):
            return self.item
    
    class SkipDialog:
        def __init__(self, item):
            self.item = item
            self.AddDialogListBox = _SkipDialogHelper(item)
        
        def ShowModal(self):
            return wx.ID_OK
        
        def Destroy(self):
            pass
    
    def RunPeachEditor():
        app = wx.PySimpleApp(0)
        wx.InitAllImageHandlers()
        peachMain = PeachGui()
        app.SetTopWindow(peachMain)
        peachMain.Show()
        app.MainLoop()

except:
    def RunPeachEdit():
        pass
    raise
    #pass

if __name__ == "__main__":
    RunPeachEditor()
    
# end
