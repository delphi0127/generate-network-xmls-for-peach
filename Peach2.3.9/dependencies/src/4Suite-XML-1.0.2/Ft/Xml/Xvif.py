########################################################################
# $Source: /var/local/cvsroot/4Suite/Ft/Xml/Xvif.py,v $ $Revision: 1.8 $ $Date: 2006/01/16 03:59:42 $
"""
XVIF integration for 4Suite.  Includes basic RELAX NG support

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

#See http://www.advogato.org/proj/xvif/

#Basic RELAX NG support

from xml.dom import Node

from Ft.Xml import InputSource, Sax
from Ft.Xml.Domlette import NonvalidatingReader, SaxWalker
from Ft.Xml.ThirdParty.Xvif import rng


class RelaxNgValidator:
    """
    A class providing RELAX NG support
    """
    def __init__(self, isrc_or_domlette):
        if isinstance(isrc_or_domlette, InputSource.InputSource):
            parser = Sax.CreateParser()
            self._schema = rng.RngParser()
            parser.setContentHandler(self._schema)
            parser.parse(isrc_or_domlette)
        elif isinstance(isrc_or_domlette, Node):
            parser = SaxWalker(isrc_or_domlette)
            self._schema = rng.RngParser()
            parser.setContentHandler(self._schema)
            parser.parse()
        else:
            raise TypeError('Expected InputSource or Domlette Document, got %s' % isrc_or_domlette)

    def isValid(self, isrc):
        reader = NonvalidatingReader
        doc = reader.parse(isrc)
        return self.isValidNode(doc.firstChild)

    def isValidNode(self, node):
        deriv = self.validateNode(node)
        isvalid = deriv.nullable()
        #isvalid = isinstance(deriv, rng.Empty)
        return isvalid

    def validate(self, isrc):
        reader = NonvalidatingReader
        doc = reader.parse(isrc)
        return self.validateNode(doc.firstChild)

    def validateNode(self, node):
        if node.nodeType == Node.DOCUMENT_NODE:
            node = node.firstChild
        #s = copy.deepcopy(schema.grammar)
        return self._schema.grammar.deriv(node)


class RngInvalid(Exception):
    def __init__(self, rngResult):
        # By defining __str__, args will be available.  Otherwise
        # the __init__ of Exception sets it to the passed in arguments.
        self.message = rngResult.msg
        Exception.__init__(self, self.message)


##class XvifProcessor:
##    """
##    EXPERIMENTAL
##    A class providing XVIF processing support
##    """
##    def __init__(self, isrc):
##        parser = Sax.CreateParser()
##        self._schema = rng.RngParser()
##        parser.setContentHandler(self._schema)
##        parser.parse(isrc)

##    def process(self, isrc):
##        reader = NonvalidatingReader
##        doc = reader.parse(isrc)
##        return self.execute(doc)

##    def execute(self, doc):
##        reader = NonvalidatingReader
##        doc = reader.parse(isrc)
##        #s = copy.deepcopy(schema.grammar)
##        deriv = self._schema.grammar.deriv(doc.firstChild)
##        #isvalid = deriv.isnullable()
##        isvalid = isinstance(deriv, rng.Empty)
##        return isvalid


