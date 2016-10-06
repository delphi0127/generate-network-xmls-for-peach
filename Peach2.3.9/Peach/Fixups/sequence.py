
#
# Copyright (c) 2008 Eddington and Frantz
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
#   Blake Frantz (blakefrantz@gmail.com)

# $Id$

from Peach.fixup import Fixup

import random

class SequenceIncrementFixup(Fixup):
    '''
    Allows a field to emit a sequential value without adding additional test cases.
    This is useful for sequence numbers common in network protocols.
    '''
    
    num = 1;

    def __init__(self):
               
        Fixup.__init__(self)        
            
    def fixup(self):
                       
        SequenceIncrementFixup.num += 1
        
        return SequenceIncrementFixup.num

class SequenceRandomFixup(Fixup):
    '''
    Allows a field to emit a random value without adding additional test cases.
    This is useful for sequence numbers common in network protocols.
    '''

    def __init__(self):
               
        random.seed() 
        Fixup.__init__(self)        
            
    def fixup(self):
        
        return random.randint(0, (1 << self.context.size) - 1)
    
# end
