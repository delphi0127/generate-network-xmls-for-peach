########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/PlainTextWriter.py,v 1.8 2005/02/09 08:57:09 mbrown Exp $
"""
Plain text writer for XSLT processor output

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import codecs

from Ft.Xml.Xslt import NullWriter


class PlainTextWriter(NullWriter.NullWriter):
    def __init__(self, outputParams, stream):
        NullWriter.NullWriter.__init__(self, outputParams)
        self._outputParams.setDefault('mediaType', 'text/plain')
        # the default is actually system-dependent; we'll use UTF-8
        self._outputParams.setDefault('encoding', 'utf-8')
        self._stream = codecs.lookup(self._outputParams.encoding)[3](stream)
        return

    # the NullWriter already defines the rest of the handlers as no-ops

    def getStream(self):
        return self._stream.stream

    def text(self, text, escapeOutput=True):
        self._stream.write(text)
        return
