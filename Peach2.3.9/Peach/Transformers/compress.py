
'''
Some default compression transforms (gzip, compress, etc).

@author: Michael Eddington
@version: $Id: compress.py 2020 2010-04-14 23:13:14Z meddingt $
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

# $Id: compress.py 2020 2010-04-14 23:13:14Z meddingt $

import zlib

try:
	import bz2
except:
	pass

from Peach.transformer import Transformer

class GzipCompress(Transformer):
	'''
	Gzip compression transform.  Also allows for compression level 
	selection (default is 6).
	'''
	
	def __init__(self, level = 6):
		'''
		@type	level: number
		@param	level: level is an integer from 1 to 9 controlling the level
		of compression; 1 is fastest and produces the least compression, 9
		is slowest and produces the most. The default value is 6.
		'''
		Transformer.__init__(self)
		self._level = level
		self._wbits = 15
	
	def realEncode(self, data):
		return zlib.compress(data, self._level)
	
	def realDecode(self, data):
		return zlib.decompress(data, self._wbits)
	

class GzipDecompress(Transformer):
	'''
	Gzip decompression transform.
	'''
	
	def __init__(self, wbits = 15):
		'''
		@type	wbits: number
		@param	wbits: The absolute value of wbits is the base two logarithm
		of the size of the history buffer (the ``window size'') used when
		compressing data. Its absolute value should be between 8 and 15 for
		the most recent versions of the zlib library, larger values resulting
		in better compression at the expense of greater memory usage. The
		default value is 15. When wbits is negative, the standard gzip
		header is suppressed; this is an undocumented feature of the zlib
		library, used for compatibility with unzip's compression file format.
		'''
		Transformer.__init__(self)
		self._wbits = wbits
		self._level = 6
	
	def realEncode(self, data):
		return zlib.decompress(data, self._wbits)

	def realDecode(self, data):
		return zlib.compress(data, self._level)


class Bz2Compress(Transformer):
	'''
	bzip2 compression transform.  Also allows for compression level 
	selection (default is 9).
	'''
	
	def __init__(self, level = 9):
		'''
		@type	level: number
		@param	level: The compresslevel parameter, if given, must be a number
		between 1 and 9; the default is 9.
		'''
		Transformer.__init__(self)
		self._level = level
	
	def realEncode(self, data):
		return bz2.compress(data, self._level)
	
	def realDecode(self, data):
		return bz2.decompress(data)


class Bz2Decompress(Transformer):
	'''
	bzip2 decompression transform.
	'''
	
	def realEncode(self, data):
		return bz2.decompress(data)
	
	def realDecode(self, data):
		return bz2.compress(data, 6)


# end
