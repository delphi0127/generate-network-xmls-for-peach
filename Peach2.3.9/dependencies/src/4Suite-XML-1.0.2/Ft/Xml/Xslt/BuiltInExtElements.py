########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/BuiltInExtElements.py,v 1.55.4.1 2006/12/17 21:29:25 uogbuji Exp $
"""
Fourthought proprietary XSLT extension elements

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import cStringIO
from xml.dom import Node

from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.XPath import Conversions
from Ft.Xml.XPath import FT_EXT_NAMESPACE
from Ft.Xml.Xslt import XSL_NAMESPACE, XsltElement, XsltException, Error
from Ft.Xml.Xslt import CategoryTypes, ContentInfo, AttributeInfo
from Ft.Xml.Xslt import ApplyTemplatesElement, ApplyImportsElement
from Ft.Xml.Xslt import OutputParameters

RESERVED_NAMESPACE = u'http://xmlns.4suite.org/reserved'

__all__ = ['RESERVED_NAMESPACE',
           'ExtNamespaces', 'ExtElements',
           'AssignElement',
           'ChainToElement',
           'CreateIndexElement',
           'DumpKeysElement',
           'DumpVarsElement',
           'FtApplyImports',
           'FtApplyTemplates',
           'FtOutputElement',
           'MsgControlElement',
           'RawTextOutputElement',
           'ReplaceElement',
           'UriToElementElement',
           'GettextElement',
           'SetupTranslationsElement',
           ]


class FtApplyImports(XsltElement):
    """
    The f:apply-imports element is an extension of the xsl:apply-imports
    element. It differs from xsl:apply-imports in the following way:
    The element accepts xsl:with-param children that designate
    parameters that will be passed to the applied templates.
    """
    category = CategoryTypes.INSTRUCTION
    legalAttrs = {}
    content = ContentInfo.Rep(
        ContentInfo.QName(XSL_NAMESPACE, 'xsl:with-param')
        )

    doesSetup = 1

    def setup(self):
        self._params = []
        for child in self.children:
            if child.expandedName == (XSL_NAMESPACE, 'with-param'):
                self._params.append((child, child._name, child._select))
        return

    def instantiate(self, context, processor):
        if not context.stylesheet:
            raise XsltRuntimeException(
                Error.APPLYIMPORTS_WITH_NULL_CURRENT_TEMPLATE, self)

        context.processorNss = self.namespaces
        context.currentInstruction = self

        with_params = {}
        for (param, name, expr) in self._params:
            context.processorNss = param.namespaces
            context.currentInstruction = param
            with_params[name] = expr.evaluate(context)

        context.stylesheet.applyTemplates(context, processor,
                                          params=with_params,
                                          maxImport=self.importIndex)

        return


class FtApplyTemplates(ApplyTemplatesElement.ApplyTemplatesElement):
    """
    The f:apply-templates element is an extension of the xsl:apply-templates
    element. It differs from xsl:apply-templates in the following way:
    The value of the mode attribute is an attribute value template
    rather than a static string. Thus, the mode can be computed at
    run time.
    """
    legalAttrs = ApplyTemplatesElement.ApplyTemplatesElement.legalAttrs.copy()
    legalAttrs['mode'] = AttributeInfo.QNameAvt(description="The mode to be used for template application.  In this variation the mode is an AVT and thus can be computed at run time.")

    def _instantiate_mode(self, context):
        return self._mode.evaluate(context)


class FtOutputElement(XsltElement):
    """
    f:output is similar to xsl:output, but it allows you to compute the
    output parameters dynamically (as attribute value templates). Unlike
    xsl:output, this element is not expected to be empty; the output
    parameters apply only to the serialization of the element's content.
    """
    content = ContentInfo.Template
    legalAttrs = {
        'method' : AttributeInfo.QNameAvt(),
        'version' : AttributeInfo.NMTokenAvt(),
        'encoding' : AttributeInfo.StringAvt(),
        'omit-xml-declaration' : AttributeInfo.YesNoAvt(),
        'standalone' : AttributeInfo.YesNoAvt(),
        'doctype-public' : AttributeInfo.StringAvt(),
        'doctype-system' : AttributeInfo.StringAvt(),
        'cdata-section-elements' : AttributeInfo.QNamesAvt(),
        'indent' : AttributeInfo.YesNoAvt(),
        'media-type' : AttributeInfo.StringAvt(),
        }

    def __init__(self, *args, **kwds):
        XsltElement.__init__(self, *args, **kwds)
        self._output_parameters = OutputParameters.OutputParameters()
        return

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self

        # this uses attributes directly from self
        self._output_parameters.avtParse(self, context)

        processor.addHandler(self._output_parameters,
                             processor.writer.getStream())
        try:
            for child in self.children:
                child.instantiate(context, processor)
        finally:
            processor.removeHandler()

        return


class AssignElement(XsltElement):
    """The f:assign element works like xsl:variable, but forces both a local
    and a global variable binding, replacing any other in-scope bindings
    having the same expanded-name. Thus, it can be used to circumvent XSLT's
    restriction on variables not being reassignable. However, its use is not
    recommended, for reasons explained below.

    As with xsl:variable, the name of the variable is given in the mandatory
    name attribute, and the new value may be given either by an expression in
    the select attribute, or by instantiating the content of the element.

    If no select attribute is given, then a body-as-ns attribute may be used
    to indicate whether to assign the variable to the contents as a node-set
    (value 'yes') or as a result tree fragment (default, or value 'no').
    In either case, be aware that the node-set or result tree fragment will
    have a root node.

    Note that reassignment of variables is generally never actually needed.
    Before using f:assign, read the XSL FAQ or ask on xsl-list if there is a
    better, more portable way to solve your problem.

    XSLT is designed as a language that is free of side-effects, which is
    why assignment is not allowed and variables have very specific scope.
    When variable assignment is allowed, certain optimizations in the XSLT
    processor become impossible. Also, there are some circumstances in which
    the order of execution may not be quite what you expect, in which case
    f:assign may show anomalous behavior. It does not work predictably when
    called from within a tail-recursive template, for example.

    That said, f:assign can be a convenient way to create a node-set from
    a result tree fragment in XSLT 1.0. The proper way to do this is with
    EXSLT: <xsl:variable name="rtf"><foo/></xsl:variable>
    <xsl:variable name="ns" select="exsl:node-set($rtf)" xmlns:exsl="http://exslt.org/common"/>
    but f:assign can do it in one step:
    <f:assign name="ns" body-as-ns="yes"><foo/></f:assign>"""

    legalAttrs = {
        'name' : AttributeInfo.QName(required=1),
        'select' : AttributeInfo.Expression(),
        'body-as-ns' : AttributeInfo.YesNoAvt(default='no'),
        }

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self
        if self._select:
            result = self._select.evaluate(context)
        else:
            processor.pushResultTree(self.baseUri)
            try:
                for child in self.children:
                    child.instantiate(context, processor)
            finally:
                result = processor.popResult()

            if self._body_as_ns.evaluate(context):
                result = [result]

        context.varBindings[self._name] = result
        context.processor.stylesheet.globalVars[self._name] = result
        return


class DumpKeysElement(XsltElement):
    """
    f:dump-keys reports the XSLT keys that have been defined, and the
    nodes they identify, for the document that owns the context node.
    Keys will only be reported if key() has been evaluated prior to
    the instantiation of this element. The key() evaluation must have
    been performed with a context node that is from the same document
    as the context node for this element.

    This extension element is useful for debugging.

    By default, the key data is exposed as nodes with this structure:

    <zz:KeyDump xmlns:zz="%s">
      <zz:Key name="keyName">
        <zz:MatchSet value="keyUseValue">
          (representation of nodes matched by the key)
        </zz:MatchSet>
        ...
      </zz:Key>
      ...
    </zz:KeyDump>

    The node representation will be a copy of each of the nodes,
    except for attributes. Attribute nodes matched by the key will
    manifest as comment nodes with the content "Attribute: name=value".

    If raw="yes", the keys will be emitted as a stylesheet message
    (as if via xsl:message) and the format will be their Python repr()
    representation.

    If force-update="yes" all keys will be computed on all documents
    that have been loaded into the processor.

    4Suite evaluates keys lazily, which means that you could have
    situations where f:dump-keys returns unexpected empty results
    because the key of interest has not yet been invoked.
    """ % RESERVED_NAMESPACE
    legalAttrs = {
        'raw' : AttributeInfo.YesNoAvt(default='no', description="Present keys in a compact non-XML format"),
        'force-update' : AttributeInfo.YesNoAvt(default='no', description="Force evaluation of all keys on all loaded documents"),
        }

    def instantiate(self, context, processor):
        from Ft.Xml.Xslt.CopyOfElement import CopyNode

        if self._force_update.evaluate(context):
            sheet = context.processor.stylesheet
            sheet.updateAllKeys(context, processor)

        doc = context.node.rootNode
        try:
            xkeys = processor.keys[doc]
        except KeyError:
            xkeys = {}
        if (FT_EXT_NAMESPACE, 'indices') in processor.extensionParams:
            for k, v in processor.extensionParams[(FT_EXT_NAMESPACE, 'indices')].items():
                #Dummy to xsl:key storage format
                xkeys[(None, k)] = v

        if self._raw.evaluate(context):
            processor.xslMessage(repr(xkeys))
        else:
            writer = processor.writer
            writer.startElement(u'zz:KeyDump', RESERVED_NAMESPACE)
            for k, v in xkeys.items():
                writer.startElement(u'zz:Key', RESERVED_NAMESPACE)
                writer.attribute(u'name', k[1], EMPTY_NAMESPACE)
                for kk, vv in v.items():
                    writer.startElement(u'zz:MatchSet', RESERVED_NAMESPACE)
                    writer.attribute(u'value', kk, EMPTY_NAMESPACE)
                    for node in vv:
                        if node.nodeType == Node.ATTRIBUTE_NODE:
                            processor.writer.comment(
                                u"Attribute: %s=%s"%(node.nodeName, node.value))
                        else:
                            CopyNode(processor, node)
                    writer.endElement(u'zz:MatchSet', RESERVED_NAMESPACE)
                writer.endElement(u'zz:Key', RESERVED_NAMESPACE)
            writer.endElement(u'zz:KeyDump', RESERVED_NAMESPACE)
        return


class DumpVarsElement(XsltElement):
    """
    f:dump-vars reports the XPath/XSLT variables and parameters in scope.

    This extension element is useful for debugging.

    By default, the variables are exposed as nodes with this structure:

    <zz:varDump xmlns:zz="%s">
      <zz:var name="variableName">(representation of object)</zz:var>
      ...
    </zz:varDump>

    The representation of the object bound to the variable depends on
    the object type: If the object is not a node-set or result tree
    fragment, the representation will be the object's string-value.
    If the object is a node-set or result tree fragment, the
    representation will be a copy of each of the nodes. Attribute nodes
    in the node-set or result tree fragment will manifest as comment
    nodes with the content "Attribute: name=value".

    If raw="yes", the variables will be emitted as a stylesheet message
    (as if via xsl:message) and the format will be their Python repr()
    representation.
    """ % RESERVED_NAMESPACE
    legalAttrs = {
        'raw' : AttributeInfo.YesNoAvt(default='no', description="Present variables and values in a compact non-XML format"),
        }

    def instantiate(self, context, processor):
        doc = context.node.rootNode
        if self._raw.evaluate(context):
            processor.xslMessage(repr(context.varBindings))
        else:
            from Ft.Xml.XPath.XPathTypes import g_xpathPrimitiveTypes
            from Ft.Xml.Xslt.CopyOfElement import CopyNode
            writer = processor.writer
            writer.startElement(u'zz:VarDump', RESERVED_NAMESPACE)
            for k, v in context.varBindings.items():
                writer.startElement(u'zz:Var', RESERVED_NAMESPACE)
                #FIXME: should try to join back prefix to var name
                writer.attribute(u'name', k[1], EMPTY_NAMESPACE)
                if isinstance(v, list):
                    # NOTE - this must be before the primitive check due to
                    #  the fact that a node-set is a primitive type
                    for node in v:
                        if node.nodeType == Node.ATTRIBUTE_NODE:
                            processor.writer.comment(
                                u"Attribute: %s=%s"%(node.nodeName, node.value))
                        else:
                            CopyNode(processor, node)
                elif type(v) in g_xpathPrimitiveTypes:
                    writer.text(Conversions.StringValue(v))
                elif hasattr(v, 'nodeType'):
                    CopyNode(processor, v)
                writer.endElement(u'zz:Var', RESERVED_NAMESPACE)
            writer.endElement(u'zz:VarDump', RESERVED_NAMESPACE)
        return


class ReplaceElement(XsltElement):
    """
    f:replace performs a search and replace on a string, placing the results
    in the output.  The content is treated as a template.  The string value
    of the output from this template is the replacement string.
    All instances of the string given by the 'substring' attribute
    are replaced with the replacement string.
    """
    legalAttrs = {
        'string' : AttributeInfo.StringExpression(description="The string to be processed.  If not given, the string value of the context node is used."),
        'substring' : AttributeInfo.StringExpression(required=1, description="The sub-string to be replaced."),
        }

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self

        if self._string:
            value = self._string.evaluate(context)
        else:
            value = context.node

        string_ = Conversions.StringValue(value)
        substring = Conversions.StringValue(self._substring.evaluate(context))
        writer = processor.writer
        for chunk in string_.split(substring):
            writer.text(chunk)
            for child in self.children:
                child.instantiate(context, processor)

        return


class MsgControlElement(XsltElement):
    """
    f:msg-control provides, as a side effect, context-sensitive control
    over whether messages (i.e., those produced by xsl:message) and
    warnings are output by the processor.
    """
    legalAttrs = {
        'suppress' : AttributeInfo.YesNoAvt(default='no', description="Disable display of all XSLT messages."),
        }

    def instantiate(self, context, processor):
        processor.messageControl(self._suppress.evaluate(context))
        return


class CreateIndexElement(XsltElement):
    """
    f:create-index allows one to create an arbitrary key at run time using
    any node data.  It is similar to xsl:key, except that it is computed
    on demand at run-time, and uses an XPath selection rather than an XSLT
    match, which gives more flexibility over what is indexed.

    These keys can be accessed using the extension function f:lookup().

    Avoid making a dynamic index have the same name as a proper xsl:key.
    In particular this will confuse tools such as the <f:dump-keys/>
    diagnostic extension.
    """

    legalAttrs = {
        'name' : AttributeInfo.StringAvt(required=1, description='The name of the key to create'),
        'select' : AttributeInfo.Expression(required=1, description='Selects which nodes are to be indexed'),
        'use' : AttributeInfo.Expression(required=1, description='The expression that computes the index key value for each node'),
        }

    def instantiate(self, context, processor):
        selected = self._select.evaluate(context)
        name = self._name.evaluate(context)
        index = {}
        if not isinstance(selected, list):
            return
        state = context.copy()
        size = len(selected)
        pos = 1
        for node in selected:
            context.node, context.position, context.size = node, pos, size
            context.currentNode = node
            key = Conversions.StringValue(self._use.evaluate(context))
            if key not in index:
                index[key] = []
            index[key].append(node)
            pos += 1
        if (FT_EXT_NAMESPACE, 'indices') not in processor.extensionParams:
            processor.extensionParams[(FT_EXT_NAMESPACE, 'indices')] = {}
        processor.extensionParams[(FT_EXT_NAMESPACE, 'indices')][name] = index
        context.set(state)
        return


class RawTextOutputElement(XsltElement):
    """
    Given a foreign XPath object, f:raw-text-output creates a text node
    based on the object, just like xsl:value-of with
    disable-output-escaping="yes". Unlike xsl:value-of, however, this
    element does not use the string-value of the object; it instead
    feeds the object directly to the current output writer. Therefore,
    unless a custom output writer is used, the object must be a Python
    Unicode string.

    The intent is to provide a way to serialize a Unicode string that may
    contain characters that are not permitted in an XPath string object.
    For example, another extension can convert raw binary data to a
    Unicode string, and then this extension can reserialize that string
    through the XSLT output stream, without risk of losing any data due
    to XPath's restrictions on string content.
    """
    legalAttrs = {
        'select' : AttributeInfo.Expression(required=1,
                                            description="An XPath expression that returns a Python Unicode object."),
        }

    def instantiate(self, context, processor):
        processor.writer.text(self._select.evaluate(context), escapeOutput=False)
        return


class ChainToElement(XsltElement):
    """
    f:chain-to tells the processor to apply the output of the current
    stylsheet as the input of another stylesheet, establishing a chain of
    transforms.  The next stylesheet in the chain is specified using an
    AVT, which allows for dynamically constructed chains.

    Children can be xsl:with-param elements, in which case the specified
    values are passed on to the next stylesheet as top-level parameters

    Warning: if the href attribute is blank, it will chain back to this
    same stylesheet and could lead to an infinite loop.
    FIXME: Trap this condition
    """
    legalAttrs = {
        'href' : AttributeInfo.UriReferenceAvt(
            required=1,
            description="The URI of the next stylesheet in the chain"),
        }

    content = ContentInfo.Rep(ContentInfo.QName(XSL_NAMESPACE, 'xsl:with-param'))

    def instantiate(self, context, processor):
        href = self._href.evaluate(context)
        params = {}
        for child in self.children:
            context.processorNss = child.namespaces
            context.currentInstruction = child
            params[child._name] = child._select.evaluate(context)

        base = self.baseUri
        processor.chainTo = processor.inputSourceFactory.resolver.normalize(href, base)
        processor.chainParams = params
        #print "chain to: %s, from base %s and href %s"%(processor.chainTo, base, href)
        return


import ElementElement
class UriToElementElement(ElementElement.ElementElement):
    """
    Extends xsl:element by deriving the constructed element's QName and
    namespace from the supplied URI reference. The URI reference is
    first resolved to absolute form. Then, if the resulting URI begins
    with an in-scope namespace, that namespace will be used as if it had
    been supplied as the 'namespace' attribute to xsl:element, and the
    remainder of the URI will be combined with a prefix from the
    in-scope namespace bindings and used as if supplied as the 'name'
    attribute to xsl:element.

    Otherwise, the supplied default-name and default-namespace will be
    used, effecting the same result as calling xsl:element with these
    values.

    The intent is to allow an RDF resource, as identified by a URI with
    a fragment component, to be easily converted into an element.
    """
    content = ContentInfo.Template
    legalAttrs = {
        'uri' : AttributeInfo.UriReferenceAvt(description='A URI to be used to create the element.  An attempt will be made to split the URI into a head and a tail such that the head matches an in-scope namespace URI.  If matched a qname will be constructed from the prefix of that namespace declaration and the tail of the URI and the namespace from the declaration will be used to complete an output element.', required=1),
        'default-name' : AttributeInfo.RawQNameAvt(description='Used if the given URI cannot be broken down using in-scope namespaces', required=1),
        'default-namespace' : AttributeInfo.UriReferenceAvt(description='Used if the given URI cannot be broken down using in-scope namespaces', isNsName=1),
        'use-attribute-sets' : AttributeInfo.QNames(),
        }

    def instantiate(self, context, processor):
        context.currentInstruction = self

        matched = 0
        uri = self._uri.evaluate(context)
        for (prefix, namespace) in self.namespaces.items():
            if namespace and uri.startswith(namespace):
                local = uri.split(namespace)[1]
                if prefix:
                    qname = prefix + u':' + local
                else:
                    qname = local
                matched = 1
                break

        if matched:
            ElementElement.ElementElement.execute(self, context, processor, qname, namespace)
            return
        else:
            self._name = self._default_name
            self._namespace = self._default_namespace
            return ElementElement.ElementElement.instantiate(self, context, processor)


class SetupTranslationsElement(XsltElement):
    category = CategoryTypes.TOP_LEVEL_ELEMENT
    legalAttrs = {
        'domain' : AttributeInfo.StringAvt(required=1, description='The domain name of the message catalog'),
        'localedir' : AttributeInfo.StringAvt(description='The message catalog path'),
        }
    doesPrime = 1

    #def instantiate(self, context, processor):
    def prime(self, processor, context):
        import gettext
        domain = self._domain.evaluate(context)
        localedir = self._localedir.evaluate(context) or None
        translations = gettext.translation(domain, localedir)
        processor.extensionParams[
            (FT_EXT_NAMESPACE, 'translations')
            ] = translations
        return


class GettextElement(XsltElement):
    content = ContentInfo.Template
    def instantiate(self, context, processor):
        context.setProcessState(self)
        stream = cStringIO.StringIO()
        op = processor.writer._outputParams.clone()
        op.method = (EMPTY_NAMESPACE, 'text')
        #op.omitXmlDeclaration = "yes"
        processor.addHandler(op, stream)
        self.processChildren(context, processor)
        processor.removeHandler()
        text = stream.getvalue()
        translations = processor.extensionParams[(FT_EXT_NAMESPACE, 'translations')]
        text = translations.ugettext(text)
        processor.writer.text(text)
        return


ExtNamespaces = {
    FT_EXT_NAMESPACE : 'f',
    }

ExtElements = {
    (FT_EXT_NAMESPACE, 'apply-imports'): FtApplyImports,
    (FT_EXT_NAMESPACE, 'apply-templates'): FtApplyTemplates,
    (FT_EXT_NAMESPACE, 'output'): FtOutputElement,
    (FT_EXT_NAMESPACE, 'dump-keys'): DumpKeysElement,
    (FT_EXT_NAMESPACE, 'dump-vars'): DumpVarsElement,
    (FT_EXT_NAMESPACE, 'assign'): AssignElement,
    (FT_EXT_NAMESPACE, 'replace'): ReplaceElement,
    (FT_EXT_NAMESPACE, 'message-control'): MsgControlElement,
    (FT_EXT_NAMESPACE, 'create-index'): CreateIndexElement,
    (FT_EXT_NAMESPACE, 'raw-text-output'): RawTextOutputElement,
    (FT_EXT_NAMESPACE, 'chain-to'): ChainToElement,
    (FT_EXT_NAMESPACE, 'uri-to-element'): UriToElementElement,
    (FT_EXT_NAMESPACE, 'gettext'): GettextElement,
    (FT_EXT_NAMESPACE, 'setup-translations'): SetupTranslationsElement,
    }

