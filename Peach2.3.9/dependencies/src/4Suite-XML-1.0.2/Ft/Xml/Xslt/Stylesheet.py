########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/Stylesheet.py,v 1.53 2006/07/30 16:45:47 uogbuji Exp $
"""
xsl:stylesheet / xsl:transform implementation;
various stylesheet internals

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import sys
from xml.dom import Node, XMLNS_NAMESPACE

from Ft.Lib import Set
from Ft.Xml import XPath
from Ft.Xml.XPath import Conversions
from Ft.Xml.Xslt import XSL_NAMESPACE, XsltElement, XsltException, Error
from Ft.Xml.Xslt import CategoryTypes, ContentInfo, AttributeInfo
from Ft.Xml.Xslt import XsltContext, PatternList
from Ft.Xml.Xslt import OutputParameters, MessageSource
from Ft.Xml.Xslt.LiteralElement import LiteralElement

__all__ = ['MatchTree', 'StylesheetElement']

def MatchTree(patterns, context):
    """
    Returns all nodes, from context on down, that match the patterns
    """
    state = context.copy()

    # Save these before any changes are made to the context
    children = context.node.childNodes
    attributes = context.node.xpathAttributes or None

    matched = patterns.xsltKeyPrep(context, context.node)

    pos = 1
    size = len(children)
    for node in children:
        context.node, context.position, context.size = node, pos, size
        map(lambda x, y: x.extend(y), matched, MatchTree(patterns, context))
        pos += 1

    if attributes:
        size = len(attributes)
        pos = 1
        for node in attributes:
            context.node, context.position, context.size = node, pos, size
            map(lambda x, y: x.extend(y),
                matched, patterns.xsltKeyPrep(context, node))
            pos += 1

    context.set(state)
    return matched


class StylesheetElement(XsltElement):
    category = None
    content = ContentInfo.Seq(
        ContentInfo.Rep(ContentInfo.QName(XSL_NAMESPACE, 'xsl:import')),
        ContentInfo.TopLevelElements)
    legalAttrs = {
        'id' : AttributeInfo.Id(),
        'extension-element-prefixes' : AttributeInfo.Prefixes(),
        'exclude-result-prefixes' : AttributeInfo.Prefixes(),
        'version' : AttributeInfo.Number(required=1),
        }

    # We don't want ourselves included in these lists since we do the walking
    doesSetup = doesPrime = doesIdle = 0

    def __init__(self, root, namespaceUri, localName, baseUri):
        XsltElement.__init__(self, root, namespaceUri, localName, baseUri)
        self.reset1()
        return

    def reset1(self):
        self.matchTemplates = {}
        self.namedTemplates = {}
        self.globalVars = {}
        self.initialFunctions = {}
        return

    def reset2(self):
        self.outputParams = OutputParameters.OutputParameters()
        self.spaceRules = []
        self.namespaceAliases = {}
        self.decimalFormats = {}
        return

    def setup(self):
        """
        Called only once, at the first initialization
        """
        self.reset2()

        # By sharing the same list, no special processing is needed later
        space_rules = []
        global_vars = []

        # no need for multiple filters to get these
        top_level_elements = {
            'namespace-alias' : [],
            'decimal-format' : [],
            'strip-space' : space_rules,
            'preserve-space' : space_rules,
            'output' : [],
            'template' : [],
            'key' : [],
            'variable' : global_vars,
            'param' : global_vars,
            }

        # this merges the XSLT children into the above dictionary
        # any elements whose name is not in the dictionary are thrown away
        reduce(lambda ignored, child, toplevel=top_level_elements:
               child.expandedName[0] == XSL_NAMESPACE and
               toplevel.get(child.expandedName[1], []).append(child),
               self.children, 'ignored')

        # process elements which do not depend on other parts of the stylesheet
        self._setupNamespaceAliases(top_level_elements['namespace-alias'])
        self._setupDecimalFormats(top_level_elements['decimal-format'])
        self._setupWhitespaceRules(space_rules)
        self._setupOutput(top_level_elements['output'])
        self._setupTemplates(top_level_elements['template'])
        self._setupKeys(top_level_elements['key'])

        # process those which could require other parts of the stylesheet
        if self.namespaceAliases:
            self._setupLiteralElements(self)

        self._setupTopLevelVarParams(global_vars)
        return

    def _setupNamespaceAliases(self, aliases):
        merged = {}
        for alias in aliases:
            stylesheet_ns = alias.namespaces[alias._stylesheet_prefix]
            if stylesheet_ns in merged:
                existing = merged[stylesheet_ns].importIndex
                if existing < alias.importIndex:
                    merged[stylesheet_ns] = alias
                elif existing == alias.importIndex:
                    raise XsltException(Error.DUPLICATE_NAMESPACE_ALIAS,
                                        alias._stylesheet_prefix)
            else:
                merged[stylesheet_ns] = alias

        for stylesheet_ns, alias in merged.items():
            namespace = alias.namespaces[alias._result_prefix]
            prefix = alias._result_prefix
            self.namespaceAliases[stylesheet_ns] = (namespace, prefix)
        return

    def _setupDecimalFormats(self, decimal_formats):
        for df in decimal_formats:
            name, format = df.getFormatInfo()
            existing = self.decimalFormats.get(name)
            if existing and existing != format:
                # conflicting formats
                if name:
                    # name is (namespace-uri, local-name)
                    if name[0]:
                        name = df.namespaces[name[0]] + ':' + name[1]
                    else:
                        name = name[1]
                else:
                    name = '#default'
                raise XsltException(Error.DUPLICATE_DECIMAL_FORMAT, name)
            self.decimalFormats[name] = format

        if None not in self.decimalFormats:
            # no default format specified
            self.decimalFormats[None] = ('.', ',', 'Infinity', '-', 'NaN', '%',
                                         unichr(0x2030), '0', '#', ';')
        return

    def _setupWhitespaceRules(self, space_rules):
        # These values only affect the source document(s)
        # Sort in increasing import precedence, so the last one added
        # will have the highest import precedence
        space_rules.sort(lambda a, b: cmp(a.importIndex, b.importIndex))
        merged = {}
        for rule in space_rules:
            strip, elements = rule.getWhitespaceInfo()
            for eName in elements:
                merged[eName] = strip

        # these are sorted by priority where '*' is lowest followed by
        # 'prefix:*', then remaining tests
        star = None
        prefix_star = []
        for (namespace, local), strip in merged.items():
            rule = (namespace, local, strip)
            if local == '*':
                if namespace:
                    prefix_star.append(rule)
                else:
                    star = rule
            else:
                self.spaceRules.append(rule)
        self.spaceRules.extend(prefix_star)
        star and self.spaceRules.append(star)
        return

    def _setupOutput(self, outputs):
        outputs.sort(lambda a, b: cmp(a.importIndex, b.importIndex))
        for output in outputs:
            self.outputParams.parse(output)
        return

    def _setupTemplates(self, templates):
        named_tpls = self.namedTemplates
        match_tpls = self.matchTemplates

        shortcuts = []
        for template, position in zip(templates, xrange(len(templates))):
            # A 'shortcut' is (sort_key, template_info)
            (shorts, name) = template.getTemplateInfo(position)
            if name:
                # for call-templates
                existing = named_tpls.get(name)
                if existing:
                    if existing.importIndex == template.importIndex:
                        raise XsltException(Error.DUPLICATE_NAMED_TEMPLATE, name)
                    elif existing.importIndex > template.importIndex:
                        pass
                    else:
                        # The new template has a higher import precedence
                        # so replace what was already there.
                        named_tpls[name] = template
                else:
                    # The first occurrence of a template with this name.
                    named_tpls[name] = template

            shortcuts.extend(shorts)

        # Sort using the sort key, where it is:
        #   (<import precedence>, <template priority>, <stylesheet position>)
        shortcuts.sort()
        # We want the highest numbers first
        shortcuts.reverse()

        # Make the lookup tables. A lookup table is first keyed by mode,
        # then keyed by node type, then, if an element, keyed by expanded name
        for sort_key, template_info in shortcuts:
            mode, pattern_info, (node_type, expanded_name) = template_info

            # Save the sort key for use in matching
            pattern_info = (sort_key, pattern_info)

            mode_table = match_tpls.get(mode)
            if not mode_table:
                mode_table = match_tpls[mode] = {}

            type_table = mode_table.get(node_type)
            if not type_table:
                if node_type == Node.ELEMENT_NODE:
                    # Elements are further keyed by expanded name
                    type_list = [pattern_info]
                    mode_table[node_type] = {expanded_name : type_list}
                else:
                    mode_table[node_type] = [pattern_info]
            elif node_type == Node.ELEMENT_NODE:
                # Elements are further keyed by expanded name
                type_list = type_table.get(expanded_name)
                if not type_list:
                    type_table[expanded_name] = [pattern_info]
                else:
                    type_list.append(pattern_info)
            else:
                # Every other node type gets lumped into a single list
                # for that node type
                type_table.append(pattern_info)

        #self._printMatchTemplates()
        return

    #def _printMatchTemplates(self):
    #    print "=" * 50
    #    print "matchTemplates:"
    #    templates = {}
    #    for mode in self.matchTemplates.keys():
    #        print "-" * 50
    #        print "mode:",mode
    #        for nodetype in self.matchTemplates[mode].keys():
    #            print "  node type:",nodetype
    #            for patterninfo in self.matchTemplates[mode][nodetype]:
    #                pat, axistype, template = patterninfo
    #                print "    template matching pattern  %r  for axis type %s" % (pat, axistype)
    #                templates[template] = 1
    #
    #    print
    #    for template in templates.keys():
    #        template._printTemplateInfo()
    #
    #    return

    def _setupKeys(self, keys):
        # Group the keys by name
        self._keys = {}
        for key in keys:
            name, info = key.getKeyInfo()
            if name not in self._keys:
                self._keys[name] = [info]
            else:
                self._keys[name].append(info)
        return

    def _setupLiteralElements(self, node):
        if isinstance(node, LiteralElement):
            node.fixupAliases(self.namespaceAliases)
        for child in (node.children or []):
            self._setupLiteralElements(child)
        return

    def _setupTopLevelVarParams(self, global_vars):
        self._topVariables = index, ordered = {}, []
        for vp in global_vars:
            existing = index.get(vp._name)
            if vp.importIndex > (existing and existing.importIndex or -1):
                # current variable has a higher import precedence
                index[vp._name] = vp
                ordered.append(vp)
        return

    ############################# Prime Routines #############################

    def primeStylesheet(self, contextNode, processor, topLevelParams, docUri):
        doc = contextNode.rootNode
        #self.newSource(doc, processor)

        context = XsltContext.XsltContext(doc, 1, 1,
                                          processorNss=self.namespaces,
                                          stylesheet=self,
                                          processor=processor,
                                          extFunctionMap=processor.extFunctions
                                          )

        baseUri = docUri or getattr(context.node, 'refUri', None)
        context.addDocument(doc, baseUri)

        #Run prime for all instructions that declared they used it
        #NOTE: Must prime instructions *before* setting up variables and
        #parameters because vars and params might rely on context updates
        #while priming (e.g. if an EXSLT func:function is declared and used
        #in a variable defn)
        for instruction in self.root.primeInstructions:
            instruction.prime(processor, context)

        self.initialFunctions.update(context.functions)

        overridden_params = {}
        for split_name, value in topLevelParams.items():
            if not isinstance(split_name, tuple):
                try:
                    split_name = self.expandQName(split_name)
                except KeyError:
                    continue
            overridden_params[split_name] = value

        for vnode in self._topVariables[1]:
            self._computeGlobalVar(vnode._name, context, [], [],
                                   overridden_params, processor)
            self.globalVars.update(context.varBindings)

        return


    def _computeGlobalVar(self, vname, context, processed, deferred,
                          overriddenParams, processor):
        vnode = self._topVariables[0][vname]

        if vnode in deferred:
            raise XsltException(Error.CIRCULAR_VAR, vname[0], vname[1])
        if vnode in processed:
            return
        # Is it an <xsl:param>?
        # expandedName is a tuple (namespace-uri, local-name)
        if vnode.expandedName[1][0] == 'p':
            if vname in overriddenParams:
                context.varBindings[vname] = overriddenParams[vname]
            else:
                finished = 0
                while not finished:
                    orig_depth = len(processor.writers)
                    try:
                        vnode.instantiate(context, processor)
                        finished = 1
                    except XPath.RuntimeException, e:
                        if e.errorCode == XPath.RuntimeException.UNDEFINED_VARIABLE:
                            #Remove any aborted and possibly unbalanced
                            #outut handlers on the stack
                            depth = len(processor.writers)
                            for i in xrange(depth - orig_depth):
                                processor.writers.pop()
                            #Defer the current and try evaluating the
                            #one that turned up undefined
                            deferred.append(vnode)
                            self._computeGlobalVar((e.params[0], e.params[1]),
                                                   context, processed, deferred,
                                                   overriddenParams,
                                                   processor)
                            deferred.remove(vnode)
                        else:
                            raise
                #Set up so that later stylesheets will get overridden by
                #parameter values set in higher-priority stylesheets
                overriddenParams[vname] = context.varBindings[vname]
        else:
            finished = 0
            while not finished:
                orig_depth = len(processor.writers)
                try:
                    vnode.instantiate(context, processor)
                    finished = 1
                except XPath.RuntimeException, e:
                    if e.errorCode == XPath.RuntimeException.UNDEFINED_VARIABLE:
                        #Remove any aborted and possibly unbalanced
                        #output handlers on the stack
                        depth = len(processor.writers)
                        for i in xrange(depth - orig_depth):
                            processor.writers.pop()
                        #Defer the current and try evaluating the
                        #one that turned up undefined
                        deferred.append(vnode)
                        self._computeGlobalVar((e.params[0], e.params[1]),
                                               context, processed, deferred,
                                               overriddenParams,
                                               processor)
                        deferred.remove(vnode)
                    else:
                        raise
        processed.append(vnode)
        return

    def updateKey(self, doc, keyName, processor):
        """
        Update a particular key for a new document
        """
        from pprint import pprint
        if doc not in processor.keys:
            processor.keys[doc] = {}
        if keyName not in processor.keys[doc]:
            key_values = processor.keys[doc][keyName] = {}
        else:
            key_values = processor.keys[doc][keyName]
        try:
            keys = self._keys[keyName]
        except KeyError:
            return

        # Find the matching nodes using all matching xsl:key elements
        updates = {}
        for key in keys:
            match_pattern, use_expr, namespaces = key
            context = XsltContext.XsltContext(
                doc, 1, 1, processorNss=namespaces, processor=processor,
                extFunctionMap=self.initialFunctions)
            patterns = PatternList([match_pattern], namespaces)
            matched = MatchTree(patterns, context)[0]
            for node in matched:
                state = context.copy()
                context.node = node
                key_value_list = use_expr.evaluate(context)
                if not isinstance(key_value_list, list):
                    key_value_list = [key_value_list]
                for key_value in key_value_list:
                    key_value = Conversions.StringValue(key_value)
                    if key_value not in updates:
                        updates[key_value] = [node]
                    else:
                        updates[key_value].append(node)
                context.set(state)

        # Put the updated results in document order with duplicates removed
        for key_value in updates:
            if key_value in key_values:
                nodes = Set.Union(key_values[key_value], updates[key_value])
            else:
                nodes = Set.Unique(updates[key_value])
            key_values[key_value] = nodes
        return

    def updateAllKeys(self, context, processor):
        """
        Update all the keys for all documents in the context
        Only used as an override for the default lazy key eval
        """
        for keyName in self._keys:
            for doc in context.documents.values():
                self.updateKey(doc, keyName, processor)
        return

    ############################# Exit Routines #############################

    def idle(self, contextNode, processor, baseUri=None):
        # run idle for all instructions that declared they used it
        for instruction in self.root.idleInstructions:
            instruction.idle(processor)
        return

    def reset(self):
        """
        Called whenever the processor is reset, i.e. after each run
        Also called whenever multiple stylesheets are appended to
        a processor, because the new top-level elements from the
        new stylesheet need to be processed into the main one
        """
        self.reset1()
        self.reset2()
        return

    ############################ Runtime Routines ############################

    def getNamedTemplates(self):
        return self.namedTemplates.copy()

    def getGlobalVariables(self):
        return self.globalVars.copy()

    def getInitialFunctions(self):
        return self.initialFunctions.copy()

    def applyTemplates(self, context, processor, params=None, maxImport=None):
        # Set the current node for this template application
        save_current = context.currentNode
        node = context.currentNode = context.node
        context.stylesheet = self
        #print
        #print "#" * 60
        #print "finding template for node", repr(context.node)

        mode_table = self.matchTemplates.get(context.mode)
        if not mode_table:
            # No patterns defined in this mode
            return 0

        patterns = []
        node_type = node.nodeType
        if node_type == Node.ELEMENT_NODE:
            table = mode_table.get(node_type)
            if table:
                key = (node.namespaceURI, node.localName)
                # First use those template which could match this expanded name
                patterns.extend(table.get(key, []))
                # Then add those that are wildcard tests ('*' and 'prefix:*')
                patterns.extend(table.get(None, []))
        else:
            patterns.extend(mode_table.get(node_type, []))

        # For any node type add those patterns that don't have a distinct type:
        #   node(), id() and key() patterns
        patterns.extend(mode_table.get(None, []))

        # Early exit for no matches
        if not patterns:
            return 0

        # If this is called from apply-imports, remove those patterns
        # with a higher import precedence than what was specified.
        if maxImport is not None:
            patterns = filter(lambda x, m=maxImport: x[0][0] < m, patterns)

        # Since the patterns may come from different tables, resort them
        patterns.sort()
        patterns.reverse() # highest numbers first

        if 1: # recovery_method == Recovery.SILENT
            # (default until recovery behaviour is selectable)
            # Just use the first matching pattern since they are
            # already sorted in descending order.
            for sort_key, (pattern, axis_type, template) in patterns:
                context.processorNss = template.namespaces
                if pattern.match(context, context.node, axis_type):
                    # let Python collect this list to reduce memory usage
                    del patterns
                    # Make sure the template starts with a clean slate
                    current_variables = context.varBindings
                    context.varBindings = self.globalVars
                    try:
                        template.instantiate(context, processor, params)
                    finally:
                        context.currentNode = save_current
                        context.varBindings = current_variables
                    return 1
        else: # recovery_method in (Recovery.WARNING, Recovery.NONE)
            # Find all templates that match the context node

            # Use the import index, priority and position from the last
            # possible matching pattern as starting points.
            highest_import, highest_priority, last_position = patterns[-1][0]
            matches = []
            for sort_key, (pattern, axis_type, template) in patterns:
                import_index, priority, position = sort_key

                if import_index < highest_import or \
                   (import_index == highest_import
                    and priority < highest_priority):
                    # Passed the point of possible conflicts, we can stop
                    break

                context.processorNss = template.namespaces
                if pattern.match(context, context.node, axis_type):
                    matches.append((template, pattern))

            if len(matches) > 1:
                # Report the template conflicts
                locations = []
                for template, pattern in matches:
                    locations.append((template.baseUri, template.lineNumber,
                                      template.columnNumber, repr(pattern)))

                # Sort them based on position
                locations.sort()

                locations = [
                        MessageSource.TEMPLATE_CONFLICT_LOCATION % location
                        for location in locations
                        ]
                exception = XsltException(Error.MULTIPLE_MATCH_TEMPLATES,
                                          context.node, '\n'.join(locations))

                if 1: # recovery_method == Recovery.WARNING
                    processor.warning(str(exception))
                else:
                    raise exception

            if matches:
                template = matches[0][0]
                # let Python collect these list to reduce memory usage
                del patterns
                del matches

                # Since the patterns were sorted to start with, use the first
                context.processorNss = template.namespaces
                template.instantiate(context, processor, params)
                context.currentNode = save_current
                return 1

        # Nothing matched
        return 0

    def __getstate__(self):
        self.root.sourceNodes = {}
        self._input_source = None
        return self.__dict__

#def PrintStylesheetTree(node, stream=None, indentLevel=0, showImportIndex=0,
#                        lastUri=None):
#    """
#    Function to print the nodes in the stylesheet tree, to aid in debugging.
#    """
#    stream = stream or sys.stdout
#    if lastUri != node.baseUri:
#        stream.write(indentLevel * '  ')
#        stream.write('====%s====\n' % node.baseUri)
#        lastUri = node.baseUri
#    stream.write(indentLevel * '  ' + str(node))
#    if showImportIndex:
#        stream.write(' [' + str(node.importIndex) + ']')
#    stream.write('\n')
#    stream.flush()
#    show_ii = isinstance(node, XsltElement) and \
#        node.expandedName in [(XSL_NAMESPACE, 'stylesheet'),
#                              (XSL_NAMESPACE, 'transform')]
#    for child in node.children:
#        PrintStylesheetTree(child, stream, indentLevel+1, show_ii, lastUri)
#    return
