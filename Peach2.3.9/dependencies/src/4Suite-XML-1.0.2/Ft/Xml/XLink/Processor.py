########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XLink/Processor.py,v 1.5 2005/02/25 05:57:48 mbrown Exp $
"""
XLink processing engine

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Xml.Domlette import NonvalidatingReader
from Ft.Xml.XLink import XLINK_NAMESPACE
from Ft.Xml.XLink import XLinkElements

__all__ = ['Processor']

class Processor:

    def run(self, iSrc):
        """
        Given an InputSource, reads the document, processing XLinks therein.

        Warning: The document will be modified in place.
        """
        document = NonvalidatingReader.parse(iSrc)
        xlinks = document.xpath('/descendant-or-self::*[@xlink:type]',
                                explicitNss={'xlink': XLINK_NAMESPACE})
        for link in xlinks:
            xlink = XLinkElements.Create(link, iSrc)
            xlink.process()
        return document
