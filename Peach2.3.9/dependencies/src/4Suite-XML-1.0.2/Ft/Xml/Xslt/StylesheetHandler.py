########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/StylesheetHandler.py,v 1.61 2005/09/14 21:38:45 jkloth Exp $
"""
Stylesheet tree generator

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Lib import Truncate, UriException
from Ft.Xml import XML_NAMESPACE, EMPTY_NAMESPACE, Domlette
from Ft.Xml.Lib.XmlString import IsXmlSpace
from Ft.Xml.Xslt import XSL_NAMESPACE, MessageSource
from Ft.Xml.Xslt import XsltException, XsltParserException, Error
from Ft.Xml.Xslt import CategoryTypes, BuiltInExtElements
from Ft.Xml.Xslt import Exslt

from LiteralElement import LiteralElement
from UndefinedElements import UndefinedXsltElement, UndefinedExtensionElement

import StylesheetTree, ContentInfo, AttributeInfo

# Table for load-on-demand of the XSLT elements
_ELEMENT_MAPPING = {
    'apply-templates' : 'ApplyTemplatesElement.ApplyTemplatesElement',
    'apply-imports' : 'ApplyImportsElement.ApplyImportsElement',
    'attribute' : 'AttributeElement.AttributeElement',
    'attribute-set' : 'AttributeSetElement.AttributeSetElement',
    'call-template' : 'CallTemplateElement.CallTemplateElement',
    'choose' : 'ChooseElement.ChooseElement',
    'when' : 'ChooseElement.WhenElement',
    'otherwise' : 'ChooseElement.OtherwiseElement',
    'copy' : 'CopyElement.CopyElement',
    'copy-of' : 'CopyOfElement.CopyOfElement',
    'comment' : 'CommentElement.CommentElement',
    'element' : 'ElementElement.ElementElement',
    'for-each' : 'ForEachElement.ForEachElement',
    'if' : 'IfElement.IfElement',
    'message' : 'MessageElement.MessageElement',
    'number' : 'NumberElement.NumberElement',
    'param' : 'ParamElement.ParamElement',
    'processing-instruction' : 'ProcessingInstructionElement.ProcessingInstructionElement',
    'sort' : 'SortElement.SortElement',
    'stylesheet' : 'Stylesheet.StylesheetElement',
    'transform' : 'Stylesheet.StylesheetElement',
    'template' : 'TemplateElement.TemplateElement',
    'text' : 'TextElement.TextElement',
    'variable' : 'VariableElement.VariableElement',
    'value-of' : 'ValueOfElement.ValueOfElement',
    'with-param' : 'WithParamElement.WithParamElement',
    'import' : 'OtherXslElement.ImportElement',
    'include' : 'OtherXslElement.IncludeElement',
    'decimal-format' : 'OtherXslElement.DecimalFormatElement',
    'key' : 'OtherXslElement.KeyElement',
    'namespace-alias' : 'OtherXslElement.NamespaceAliasElement',
    'output' : 'OtherXslElement.OutputElement',
    'fallback' : 'OtherXslElement.FallbackElement',
    'preserve-space' : 'WhitespaceElements.PreserveSpaceElement',
    'strip-space' : 'WhitespaceElements.StripSpaceElement',
    }

# The XSL attributes allowed on literal elements
_RESULT_ELEMENT_XSL_ATTRS = {
    'exclude-result-prefixes' : AttributeInfo.Prefixes(),
    'extension-element-prefixes' : AttributeInfo.Prefixes(),
    'use-attribute-sets' : AttributeInfo.QNames(),
    'version' : AttributeInfo.Number(),
    }
_RESULT_ELEMENT_ATTR_INFO = AttributeInfo.AnyAvt()

_ELEMENT_CLASSES = {}
_LEGAL_ATTRS = {}

class ParseState:
    """
    Stores the current state of the parser.

    Constructor arguments/instance variables:
      validation - validation state for the current containing node.

      localVariables - set of in-scope variable bindings to determine
                       variable shadowing.

      forwardsCompatible - flag indicating whether or not forwards-compatible
                           processing is enabled.

      currentNamespaces - set of in-scope namespaces for the current node.

      extensionNamespaces - set of namespaces defining extension elements

      outputNamespaces - set of in-scope namespaces for literal result elements
    """
    
    def __init__(self, node, validation, localVariables, forwardsCompatible,
                 currentNamespaces, extensionNamespaces, outputNamespaces):
        self.node = node
        self.validation = validation
        self.localVariables = localVariables
        self.forwardsCompatible = forwardsCompatible
        self.currentNamespaces = currentNamespaces
        self.extensionNamespaces = extensionNamespaces
        self.outputNamespaces = outputNamespaces
        return


class StylesheetHandler:
    """
    Handles SAX events coming from the stylesheet parser,
    in order to build the stylesheet tree.
    """

    def __init__(self, importIndex=0, globalVars=None, extElements=None,
                 visitedStyUris=None, altBaseUris=None, ownerDocument=None):
        self._import_index = importIndex
        if globalVars is None:
            # We need to make sure that the same dictionary is used
            # through the entire processing (even if empty)
            self._global_vars = {}
        else:
            self._global_vars = globalVars
        if extElements is None:
            self._extElements = d = {}
            d.update(Exslt.ExtElements)
            d.update(BuiltInExtElements.ExtElements)
        else:
            self._extElements = extElements

        self._visited_stylesheet_uris = visitedStyUris or {}
        self._alt_base_uris = altBaseUris or []
        self._ownerDoc = ownerDocument
        return

    def reset(self):
        self._global_vars = {}
        self._import_index = 0
        self._visited_stylesheet_uris = {}
        self._ownerDoc = None
        return

    def clone(self):
        return self.__class__(self._import_index, self._global_vars,
                              self._extElements, self._visited_stylesheet_uris,
                              self._alt_base_uris, self._ownerDoc)

    def getResult(self):
        return self._ownerDoc

    def addExtensionElementMapping(self, elementMapping):
        """
        Add a mapping of extension element names to classes to the
        existing mapping of extension elements.

        This should only be used for standalone uses of this class.  The
        only known standalone use for this class is for creating compiled
        stylesheets.  The benefits of compiled stylesheets are now so minor
        that this use case may also disappear and then so will this function.
        You have been warned.
        """
        self._extElements = self._extElements.copy()
        self._extElements.update(elementMapping)
        return

    # -- ContentHandler interface --------------------------------------

    def setDocumentLocator(self, locator):
        self._locator = locator
        return

    def startDocument(self):
        """
        ownerDoc is supplied when processing an XSLT import or include.
        """
        # Our root is always a document
        # We use a document for this because of error checking and
        # because we explicitly pass ownerDocument to the nodes as
        # they are created
        document_uri = self._locator.getSystemId()
        root = StylesheetTree.XsltRoot(document_uri)

        if not self._ownerDoc:
            self._ownerDoc = root

        # the stylesheet element instance
        self._stylesheet = None

        self._state_stack = [
            ParseState(node=root,
                       validation=root.validator.getValidation(),
                       localVariables={},
                       forwardsCompatible=False,
                       currentNamespaces={'xml' : XML_NAMESPACE, None : None},
                       extensionNamespaces={},
                       outputNamespaces={})
            ]

        # for recursive include checks for xsl:include/xsl:import
        self._visited_stylesheet_uris[document_uri] = True

        # namespaces added for the next element
        self._new_namespaces = {}
        return

    def endDocument(self):
        self._import_index += 1
        self._locator = None
        return

    def startPrefixMapping(self, prefix, uri):
        self._new_namespaces[prefix] = uri
        return

    def startElementNS(self, expandedName, qualifiedName, attribs):
        state = ParseState(**self._state_stack[-1].__dict__)

        # ----------------------------------------------------------
        # update in-scope namespaces
        if self._new_namespaces:
            d = state.currentNamespaces = state.currentNamespaces.copy()
            d.update(self._new_namespaces)

            d = state.outputNamespaces = state.outputNamespaces.copy()
            for prefix, uri in self._new_namespaces.items():
                if uri not in (XML_NAMESPACE, XSL_NAMESPACE):
                    d[prefix] = uri

            # reset for next element
            self._new_namespaces = {}
        
        # ----------------------------------------------------------
        # get the class defining this element
        namespace, local = expandedName
        xsl_class = ext_class = None
        category = CategoryTypes.RESULT_ELEMENT
        if namespace == XSL_NAMESPACE:
            try:
                xsl_class = _ELEMENT_CLASSES[local]
            except KeyError:
                # We need to try to import (and cache) it
                try:
                    module = _ELEMENT_MAPPING[local]
                except KeyError:
                    if not state.forwardsCompatible:
                        raise XsltParserException(Error.XSLT_ILLEGAL_ELEMENT,
                                                  self._locator, local)
                    xsl_class = UndefinedXsltElement
                else:
                    parts = module.split('.')
                    path = '.'.join(['Ft.Xml.Xslt'] + parts[:-1])
                    module = __import__(path, {}, {}, parts[-1:])
                    try:
                        xsl_class = module.__dict__[parts[-1]]
                    except KeyError:
                        raise ImportError('.'.join(parts))
                _ELEMENT_CLASSES[local] = xsl_class
                _LEGAL_ATTRS[xsl_class] = xsl_class.legalAttrs.items()
                xsl_class.validator = ContentInfo.Validator(xsl_class.content)
            category = xsl_class.category
        elif namespace in state.extensionNamespaces:
            try:
                ext_class = self._extElements[(namespace, local)]
            except KeyError:
                ext_class = UndefinedExtensionElement
            else:
                if ext_class not in _LEGAL_ATTRS:
                    ext_class.validator = \
                        ContentInfo.Validator(ext_class.content)
                    legal_attrs = ext_class.legalAttrs
                    if legal_attrs is not None:
                        _LEGAL_ATTRS[ext_class] = legal_attrs.items()

        # ----------------------------------------------------------
        # verify that this element can be declared here
        validation_else = ContentInfo.ELSE
        if category is not None:
            next = state.validation.get(category)
            if next is None and validation_else in state.validation:
                next = state.validation[validation_else].get(category)
        else:
            next = None
        if next is None:
            next = state.validation.get(expandedName)
            if next is None and validation_else in state.validation:
                next = state.validation[ContentInfo.ELSE].get(expandedName)
        if next is None:
            #self._debug_validation(expandedName)
            parent = state.node
            if parent is self._stylesheet:
                if (XSL_NAMESPACE, 'import') == expandedName:
                    raise XsltParserException(Error.ILLEGAL_IMPORT,
                                              self._locator)
            elif parent.expandedName == (XSL_NAMESPACE, 'choose'):
                if (XSL_NAMESPACE, 'otherwise') == expandedName:
                    raise XsltParserException(Error.ILLEGAL_CHOOSE_CHILD,
                                              self._locator)
            # ignore whatever elements are defined within an undefined
            # element as an exception will occur when/if this element
            # is actually instantiated
            if not isinstance(parent, UndefinedExtensionElement):
                raise XsltParserException(Error.ILLEGAL_ELEMENT_CHILD,
                                          self._locator, qualifiedName,
                                          parent.nodeName)
        else:
            # save this state for next go round
            self._state_stack[-1].validation = next

        # ----------------------------------------------------------
        # create the instance defining this element
        klass = (xsl_class or ext_class or LiteralElement)
        instance = klass(self._ownerDoc, namespace, local,
                         self._locator.getSystemId())
        instance.lineNumber = self._locator.getLineNumber()
        instance.columnNumber = self._locator.getColumnNumber()
        instance.importIndex = self._import_index
        instance.namespaces = state.currentNamespaces
        instance.nodeName = qualifiedName
        
        # -- XSLT element --------------------------------------
        if xsl_class:
            # Handle attributes in the null-namespace
            inst_dict = instance.__dict__
            for attr_name, attr_info in _LEGAL_ATTRS[xsl_class]:
                attr_expanded = (None, attr_name)
                if attr_expanded in attribs:
                    value = attribs[attr_expanded]
                    del attribs[attr_expanded]
                elif attr_info.required:
                    raise XsltParserException(
                        Error.MISSING_REQUIRED_ATTRIBUTE,
                        self._locator, qualifiedName, attr_name)
                else:
                    value = None
                try:
                    value = attr_info.prepare(instance, value)
                except XsltException, e:
                    raise self._mutate_exception(e)

                if local in ('stylesheet', 'transform'):
                    self._stylesheet = instance
                    self._handle_standard_attr(state, instance, attr_name,
                                               value)
                else:
                    if '-' in attr_name:
                        attr_name = attr_name.replace('-', '_')
                    inst_dict['_' + attr_name] = value

            if attribs:
                # Process attributes with a namespace-uri and check for
                # any illegal attributes in the null-namespace
                for expanded in attribs:
                    attr_ns, attr_name = expanded
                    if attr_ns is None:
                        if not state.forwardsCompatible:
                            raise XsltParserException(
                                Error.ILLEGAL_NULL_NAMESPACE_ATTR,
                                self._locator, attr_name, qualifiedName)
                    else:
                        instance.attributes[expanded] = attribs[expanded]

            # XSLT Spec 2.6 - Combining Stylesheets
            if local in ('import', 'include'):
                self._combine_stylesheet(instance._href, (local == 'import'))

        # -- extension element ---------------------------------
        elif ext_class:
            validate_attributes = (ext_class in _LEGAL_ATTRS)
            if validate_attributes:
                # Handle attributes in the null-namespace
                inst_dict = instance.__dict__
                for attr_name, attr_info in _LEGAL_ATTRS[ext_class]:
                    attr_expanded = (None, attr_name)
                    if attr_expanded in attribs:
                        value = attribs[attr_expanded]
                        del attribs[attr_expanded]
                    elif attr_info.required:
                        raise XsltParserException(
                            Error.MISSING_REQUIRED_ATTRIBUTE,
                            self._locator, qualifiedName, attr_name)
                    else:
                        value = None
                    try:
                        value = attr_info.prepare(instance, value)
                    except XsltException, e:
                        raise self._mutate_exception(e)
                    if '-' in attr_name:
                        attr_name = attr_name.replace('-', '_')
                    inst_dict['_' + attr_name] = value

            # Process attributes with a namespace-uri and check for
            # any illegal attributes in the null-namespace
            if attribs:
                for expanded in attribs:
                    attr_ns, attr_name = expanded
                    value = attribs[expanded]
                    if validate_attributes and attr_ns is None:
                        raise XsltParserException(
                            Error.ILLEGAL_NULL_NAMESPACE_ATTR, self._locator,
                            attr_name, qualifiedName)
                    elif attr_ns == XSL_NAMESPACE:
                        self._handle_result_element_attr(state, instance,
                                                         qualifiedName,
                                                         attr_name, value)
                    else:
                        instance.attributes[expanded] = value

        # -- literal result element ----------------------------
        else:
            output_attrs = []
            for expanded in attribs:
                attr_ns, attr_local = expanded
                value = attribs[expanded]
                if attr_ns == XSL_NAMESPACE:
                    self._handle_result_element_attr(state, instance,
                                                     qualifiedName,
                                                     attr_local, value)
                else:
                    instance.attributes[expanded] = value
                    # prepare attributes for literal output
                    value = _RESULT_ELEMENT_ATTR_INFO.prepare(instance, value)
                    attr_qname = attribs.getQNameByName(expanded)
                    output_attrs.append((attr_qname, attr_ns, value))

            # save information for literal output
            instance._output_namespace = namespace
            instance._output_nss = state.outputNamespaces
            instance._output_attrs = output_attrs

            # Check for top-level result-element in null namespace
            parent = state.node
            if parent is self._stylesheet and \
                   not namespace and not state.forwardsCompatible:
                raise XsltParserException(Error.ILLEGAL_ELEMENT_CHILD,
                                          self._locator, qualifiedName,
                                          parent.nodeName)

        # ----------------------------------------------------------
        # update depth information
        state.node = instance
        state.validation = instance.validator.getValidation()
        self._state_stack.append(state)

        if instance.doesPrime:
            self._ownerDoc.primeInstructions.append(instance)
        if instance.doesIdle:
            self._ownerDoc.idleInstructions.append(instance)
        return

    def endElementNS(self, expandedName, qualifiedName):
        state = self._state_stack.pop()
        element = state.node
        if len(self._state_stack) == 1 and isinstance(element, LiteralElement):
            # a literal result element as stylesheet
            try:
                version = element._version
            except AttributeError:
                raise XsltParserException(Error.LITERAL_RESULT_MISSING_VERSION,
                                          self._locator)

            # FIXME: use the prefix from the document for the XSL namespace
            stylesheet = (XSL_NAMESPACE, u'stylesheet')
            self.startElementNS(stylesheet, u'xsl:stylesheet',
                                {(None, u'version') : version})

            template = (XSL_NAMESPACE, u'template')
            self.startElementNS(template, u'xsl:template',
                                {(None, u'match') :  u'/'})

            # make this element the template's content
            self._state_stack[-1].node.appendChild(element)

            self.endElementNS(template, u'xsl:template')
            self.endElementNS(stylesheet, u'xsl:stylesheet')
        else:
            self._state_stack[-1].node.appendChild(element)

            if expandedName in ((XSL_NAMESPACE, u'variable'),
                                (XSL_NAMESPACE, u'param')):
                name = element._name
                # one for the root and one for the stylesheet or
                # a literal result element as stylesheet
                if len(self._state_stack) > 2 or \
                   isinstance(self._state_stack[-1].node, LiteralElement):
                    # local variables
                    # it is safe to ignore import precedence here
                    local_vars = self._state_stack[-1].localVariables
                    if name in local_vars:
                        raise XsltParserException(Error.ILLEGAL_SHADOWING,
                                                  self._locator, name)
                    # Copy on use
                    if local_vars is self._state_stack[-2].localVariables:
                        local_vars = local_vars.copy()
                        self._state_stack[-1].localVariables = local_vars
                    local_vars[name] = True
                else:
                    # global variables
                    existing = self._global_vars.get(name, -1)
                    if self._import_index > existing:
                        self._global_vars[name] = self._import_index
                    elif self._import_index == existing:
                        raise XsltParserException(Error.DUPLICATE_TOP_LEVEL_VAR,
                                                  self._locator, name)
        return

    def characters(self, data):
        state = self._state_stack[-1]
        # verify that the current element can have text children
        validation = state.validation
        token = ContentInfo.TEXT_NODE
        next = validation.get(token)
        if next is None and ContentInfo.ELSE in validation:
            next = validation[ContentInfo.ELSE].get(token)
        if next is None:
            # If the parent can have element children, but not text nodes,
            # ignore pure whitespace nodes. This clarification is from
            # XSLT 2.0 [3.4] Whitespace Stripping.
            # e.g. xsl:stylesheet, xsl:apply-templates, xsl:choose
            if not (ContentInfo.EMPTY not in validation and IsXmlSpace(data)):
                raise XsltParserException(Error.ILLEGAL_TEXT_CHILD_PARSE,
                                          self._locator,
                                          repr(Truncate(data, 10)),
                                          state.node.nodeName)
            #self._debug_validation(expandedName)
        else:
            # update validation
            state.validation = next

            node = StylesheetTree.XsltText(self._ownerDoc,
                                           self._locator.getSystemId(),
                                           data)
            state.node.appendChild(node)
        return

    # -- utility functions ---------------------------------------------
    
    def _combine_stylesheet(self, href, is_import):
        hint = is_import and 'STYLESHEET IMPORT' or 'STYLESHEET INCLUDE'
        try:
            new_source = self._input_source.resolve(href, hint=hint)
        except (OSError, UriException):
            for uri in self._alt_base_uris:
                try:
                    new_href = self._input_source.getUriResolver().normalize(href, uri)
                    #Do we need to figure out a way to pass the hint here?
                    new_source = self._input_source.factory.fromUri(new_href)
                    break
                except (OSError, UriException):
                    pass
            else:
                raise XsltParserException(Error.INCLUDE_NOT_FOUND,
                                          self._locator, href,
                                          self._locator.getSystemId())

        # XSLT Spec 2.6.1, Detect circular references in stylesheets
        # Note, it is NOT an error to include/import the same stylesheet
        # multiple times, rather that it may lead to duplicate definitions
        # which are handled regardless (variables, params, templates, ...)
        if new_source.uri in self._visited_stylesheet_uris:
            raise XsltParserException(Error.CIRCULAR_INCLUDE,
                                      self._locator, new_source.uri)
        else:
            self._visited_stylesheet_uris[new_source.uri] = True

        # Create a new reader to handle the inclusion
        include = self.clone().fromSrc(new_source)

        # Make sure we detect circular imports/includes, but not other duplicates
        del self._visited_stylesheet_uris[new_source.uri]

        # The stylesheet containing the import will always be one higher
        # than the imported stylesheet.
        #
        # For example:
        #  stylesheet A imports stylesheets B and C in that order,
        #  stylesheet B imports stylesheet D,
        #  stylesheet C imports stylesheet E.
        # The resulting import precedences are:
        #  A=4, C=3, E=2, B=1, D=0

        # Always update the precedence from the included stylesheet
        # because it may have contained imports thus increasing its
        # import precedence.
        import_index = include.importIndex + is_import
        self._stylesheet.importIndex = self._import_index = import_index

        # merge the top-level elements
        self._stylesheet.children.extend(include.children)
        for child in include.children:
            child.parent = self._stylesheet
        return


    def _handle_standard_attr(self, state, instance, name, value):
        if name == 'extension-element-prefixes':
            # a whitespace separated list of prefixes
            ext = state.extensionNamespaces = state.extensionNamespaces.copy()
            out = state.outputNamespaces = state.outputNamespaces.copy()
            for prefix in value:
                # add the namespace URI to the set of extension namespaces
                try:
                    uri = instance.namespaces[prefix]
                except KeyError:
                    raise XsltParserException(Error.UNDEFINED_PREFIX,
                                              self._locator,
                                              prefix or '#default')
                ext[uri] = True

                # remove all matching namespace URIs
                for output_prefix, output_uri in out.items():
                    if output_uri == uri:
                        del out[output_prefix]
        elif name == 'exclude-result-prefixes':
            # a whitespace separated list of prefixes
            out = state.outputNamespaces = state.outputNamespaces.copy()
            for prefix in value:
                try:
                    uri = instance.namespaces[prefix]
                except KeyError:
                    raise XsltParserException(Error.UNDEFINED_PREFIX,
                                              self._locator,
                                              prefix or '#default')
                # remove all matching namespace URIs 
                for output_prefix, output_uri in out.items():
                    if output_uri == uri:
                        del out[output_prefix]
        elif name == 'version':
            # XSLT Spec 2.5 - Forwards-Compatible Processing
            state.forwardsCompatible = (value != 1.0)
            instance._version = value
        else:
            if '-' in name:
                name = name.replace('-', '_')
            instance.__dict__['_' + name] = value
        return

    def _handle_result_element_attr(self, state, instance, elementName,
                                    attributeName, value):
        try:
            attr_info = _RESULT_ELEMENT_XSL_ATTRS[attributeName]
        except KeyError:
            raise XsltParserException(Error.ILLEGAL_XSL_NAMESPACE_ATTR,
                                      self._locator, attributeName,
                                      elementName)
        value = attr_info.prepare(instance, value)
        self._handle_standard_attr(state, instance, attributeName, value)
        return

    def _mutate_exception(self, exception):
        msg = MessageSource.POSITION_INFO % (self._locator.getSystemId(),
                                             self._locator.getLineNumber(),
                                             self._locator.getColumnNumber(),
                                             exception.message)
        exception.message = msg
        return exception


    # -- debugging routines --------------------------------------------
    
    def _debug_validation(self, token=None, next=None):
        from pprint import pprint
        state = self._state_stack[-1]
        parent = state.node
        print '='*60
        print 'parent =',parent
        print 'parent class =',parent.__class__
        print 'content expression =', parent.validator
        print 'initial validation'
        pprint(parent.validator.getValidation())
        print 'current validation'
        pprint(state.validation)
        if token:
            print 'token', token
        if next:
            print 'next validation'
            pprint(next)
        print '='*60
        return

