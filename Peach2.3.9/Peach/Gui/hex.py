'''
HexView Control v0.1

@author: Michael Eddington
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

import wx

class HexView(wx.ScrolledWindow):
    '''
    A Hex view control for wx.  This control will display data in a
    scrolled (virtically) panel in the "standard" hex display format.
    This control displays 16 characters per line.  Even with larger files
    the speed of this control is quick.  The control does need all of the
    data to display and does not currently support a stream style interface.
    '''
    
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent)
        
        self.data = ""
        self.hexPosSize = len("%x" % len(self.data))
        self.hexPosDisplay = "%%%dx:" % self.hexPosSize
        self.cols = 8
        self.div = 4
        self.fontHight = 14
        
        # Determin how large our window needs to be
        height = ((len(self.data)/self.cols) * self.fontHight) + (self.fontHight*4)
        self.SetVirtualSize(((self.cols + 6 + 4 + (self.cols*2))*self.fontHight, height))
        self.SetScrollRate(0,self.fontHight)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.selStartPos = -1
        self.selEndPos = -1
        
        self.paintCount = 0
        
    def SetDataSelection(self, start, end):
        
        if start == -1 and end == -1:
            self.selEndPos = self.selStartPos = -1
            return
        
        if start < 0 or start > len(self.data):
            raise Exception("Invalid start position")
        if end < start or end > len(self.data):
            raise Exception("Invalid end position [%d] through [%d] out of [%d]" % (start, end, len(self.data)))
        
        self.selStartPos = start
        self.selEndPos = end
        self.Refresh()
    
    def SetData(self, data):
        self.data = data
        self.hexPosSize = len("%x" % len(self.data))
        self.hexPosDisplay = "%%%dx:" % self.hexPosSize
        
        # Determin how large our window needs to be
        height = ((len(self.data)/self.cols) * self.fontHight) + (self.fontHight*4)
        self.SetVirtualSize(((self.cols + 6 + 4 + (self.cols*2))*self.fontHight, height))
        self.SetScrollRate(0,self.fontHight)
        self.Refresh()
        
    def OnPaint(self, event):
        '''
        Handle displaying the hex 'n stuff
        '''
        
        # Required to create PaintDC or WIndows will
        # continue calling our OnPaint handler!
        pdc = wx.PaintDC(self)
        
        # The DC we actually use
        dc = wx.ClientDC(self)
        self.DoPrepareDC(dc)
        
        dc.Clear()
        
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        dc.SetFont(font)
        
        cols = self.cols
        div = self.div
        pos = 0
        colPos = 0
        fontHight = self.fontHight
        rowPos = 0
        row = []
        charPos = 0
        charWidth = dc.GetCharWidth()
        
        startPos = 0
        viewStartHeight = self.GetViewStart()[1] * self.GetScrollPixelsPerUnit()[1]
        if viewStartHeight > fontHight:
            startPos = int(viewStartHeight / fontHight) * cols
            if startPos > len(self.data):
                startPos = len(self.data)
        
        rowPos = viewStartHeight
        
        endPos = len(self.data)
        viewEndHeight = self.GetClientSize()[1]
        if endPos > viewEndHeight / fontHight:
            endPos = startPos + ((int(viewEndHeight/fontHight) + 2) * cols)
            if endPos > len(self.data):
                endPos = len(self.data)
        
        s = ""
        for pos in xrange(startPos, endPos):
            
            if colPos >= cols:
                s += "  "
                for r in row:
                    if ord(r) < 32 or ord(r) > 126:
                        s += "."
                    else:
                        s += r
                row = []
                
                font.SetWeight(wx.NORMAL)
                dc.SetFont(font)
                dc.DrawText(s, charPos, rowPos )
                s = ""
                rowPos += fontHight
                colPos = 0
            
            if colPos == 0:
                s = self.hexPosDisplay % pos
                dc.DrawText(s, 0, rowPos)
                charPos = dc.GetTextExtent(s)[0]
                s = ""
                
            if pos >= self.selStartPos and pos <= self.selEndPos:
                dc.DrawText(s, charPos, rowPos)
                charPos += dc.GetTextExtent(s)[0]
                s = ""
                
            if colPos % div == 0:
                s += "  "
            
            c = hex(ord(self.data[pos]))[2:]
            if len(c) < 2:
                s += "0" + c + " "
            else:
                s += c + " "
            
            if pos >= self.selStartPos and pos <= self.selEndPos:
                font.SetWeight(wx.BOLD)
                dc.SetFont(font)
                dc.SetTextForeground(wx.RED)
                dc.DrawText(s, charPos, rowPos)
                dc.SetTextForeground(wx.BLACK)
                charPos += dc.GetTextExtent(s)[0]
                s = ""
                
            elif font.GetWeight() != wx.NORMAL:
                font.SetWeight(wx.NORMAL)
                dc.SetFont(font)
            
            row.append(self.data[pos])
            
            colPos += 1

        if colPos < cols:
            
            s += "   " * (cols - colPos) + ("  " * int( (cols-colPos)/4)) + "  "
            
            #s += "  "
            for r in row:
                if ord(r) < 32 or ord(r) > 126:
                    s += "."
                else:
                    s += r
            row = []
            
            font.SetWeight(wx.NORMAL)
            dc.SetFont(font)
            dc.DrawText(s, charPos, rowPos )
            s = ""
            rowPos += fontHight
            colPos = 0

# end
