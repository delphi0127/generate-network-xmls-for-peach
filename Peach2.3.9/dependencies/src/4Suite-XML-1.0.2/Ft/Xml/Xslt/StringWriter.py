########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/StringWriter.py,v 1.4 2005/02/09 08:57:09 mbrown Exp $
"""
A specialized XSLT output writer that only captures text output events

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import NullWriter

class StringWriter(NullWriter.NullWriter):
    def __init__(self, outputParams):
        NullWriter.NullWriter.__init__(self, outputParams)
        self._result = []
        self._ignore_events = 0
        self.had_nontext = False

    def getResult(self):
        return u"".join(self._result)

    def text(self, text, escapeOutput=True):
        if not self._ignore_events:
            self._result.append(text)
        return

    def startElement(self, name, namespace=None, extraNss=None):
        # Ignore non-text creation as per XSLT 1.0 spec
        self._ignore_events += 1
        self.had_nontext = True
        return

    def endElement(self, name, namespace=None):
        # Ignore non-text creation as per XSLT 1.0 spec
        self._ignore_events -= 1
        return

    def comment(self, body):
        self.had_nontext = True
        return

    def processingInstruction(self, target, data):
        self.had_nontext = True
        return

    def attribute(self, name, value, namespace=None):
        self.had_nontext = True
        return
