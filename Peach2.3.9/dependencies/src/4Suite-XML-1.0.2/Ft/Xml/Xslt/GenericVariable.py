########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/GenericVariable.py,v 1.25 2005/04/06 23:05:47 jkloth Exp $
"""
Base implementation of XSLT variable assigning elements

Copyright 2002 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import warnings
from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.Xslt import XsltElement, XsltException, Error, XSL_NAMESPACE
from Ft.Xml.Xslt import ContentInfo, AttributeInfo
from Ft.Xml.XPath import FT_EXT_NAMESPACE

# for variable binding
from Ft.Xml.Xslt.StylesheetTree import XsltNode

class GenericVariableElement(XsltElement):

    category = None
    content = ContentInfo.Template
    legalAttrs = {
        'name' : AttributeInfo.QName(required=1),
        'select' : AttributeInfo.Expression(),
        'f:node-set' : AttributeInfo.YesNoAvt(default='no'),
        }

    doesSetup = True

    def setup(self):
        # Check for deprecated f:node-set
        if (FT_EXT_NAMESPACE, 'node-set') in self.attributes:
            warnings.warn("You are using the deprecated f:node-set attribute"
                          " on xsl:variable or xsl:param.  Please switch to"
                          " using exslt:node-set", DeprecationWarning, 2)

        # check for a bad binding
        if self._select and self.children:
            raise XsltException(Error.VAR_WITH_CONTENT_AND_SELECT, self._name)

        # See the bottom of this file for these helper "nodes"
        binding_save = self.parent.children[0]
        if not isinstance(binding_save, PushVariablesNode):
            # varBindings not yet saved for this level in the stylesheet tree
            parent = self.parent
            binding_save = PushVariablesNode(parent.root, parent.baseUri)
            parent.insertChild(0, binding_save)
            parent.root.primeInstructions.append(binding_save)
        return

    def instantiate(self, context, processor):
        # NOTE: all we want to do is change the varBindings
        context.processorNss = self.namespaces
        context.currentInstruction = self

        if self._select:
            result = self._select.evaluate(context)
        elif self.children:
            #This used to be a try with the popResult() in the finally.
            #But this would cause masking of underlying exceptions triggered
            #in variable bodies. See
            #http://lists.fourthought.com/pipermail/4suite-dev/2003-March/001236.html
            processor.pushResultTree(self.baseUri)
            for child in self.children:
                child.instantiate(context, processor)
            result = processor.popResult()
            # Why is the check for childNodes necessary?  This will always
            # be an RTF.
            if self.attributes.get((FT_EXT_NAMESPACE, 'node-set')) == 'yes' \
                   and hasattr(result, 'childNodes'):
                result = [result]
        else:
            result = u""
        context.varBindings[self._name] = result

        return

# pseudo-nodes for save/restore of variable bindings
class PushVariablesNode(XsltNode):

    def __init__(self, root, baseUri):
        self.root = root
        self.baseUri = baseUri
        self.savedVariables = []
        self.popNode = PopVariablesNode(self.savedVariables)
        self._is_primed = False
        return

    def prime(self, processor, context):
        if not self._is_primed:
            self.parent.children.append(self.popNode)
            self._is_primed = True
        return

    def instantiate(self, context, processor):
        self.savedVariables.append(context.varBindings)
        context.varBindings = context.varBindings.copy()
        return

    def isPseudoNode(self):
        return True


class PopVariablesNode(XsltNode):

    def __init__(self, savedVariables):
        self.savedVariables = savedVariables
        return

    def instantiate(self, context, processor):
        context.varBindings = self.savedVariables.pop()
        return

    def isPseudoNode(self):
        return True
