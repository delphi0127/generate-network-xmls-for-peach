import inspect, pydoc, types
import XmlFormatter

class ExtensionFormatter(XmlFormatter.XmlFormatter):

    document_type = types.ModuleType

    def document(self, module):
        """
        Produce documentation for a given module object.
        """
        attributes = {'name' : module.__name__}
        self.start_element('ext-module', attributes)

        desc = self.escape(pydoc.getdoc(module))
        self.write_element('description', content=desc)

        namespaces = getattr(module, 'ExtNamespaces', {})
        functions = getattr(module, 'ExtFunctions', {})
        elements = getattr(module, 'ExtElements', {})

        if namespaces:
            self.start_element('namespaces')
            for namespace_uri, prefix in namespaces.items():
                self.doc_namespace(namespace_uri, prefix)
            self.end_element('namespaces')

        if functions:
            self.start_element('functions')
            for (namespace_uri, name), function in functions.items():
                qname = self.make_qname(namespaces, namespace_uri, name)
                self.doc_function(function, namespace_uri, qname)
            self.end_element('functions')

        if elements:
            self.start_element('elements')
            for (namespace_uri, name), element in elements.items():
                qname = self.make_qname(namespaces, namespace_uri, name)
                self.doc_element(element, namespace_uri, qname)
            self.end_element('elements')

        self.end_element('ext-module')
        return

    def make_qname(self, namespaces, namespace_uri, name):
        if namespace_uri:
            prefix = 'extns'  # default (if not given)
            if not namespaces.has_key(namespace_uri):
                # No namespace/prefix mapping
                self.warn("doc_extensions: namespace '%s' used, but no "
                          "prefix defined (defaulting to '%s')" %
                          (namespace_uri, prefix))
            elif not namespaces.get(namespace_uri):
                # A namespace/prefix mapping exists, but prefix is empty
                self.warn("doc_extensions: namespace '%s' used, but empty "
                          "prefix defined " % namespace_uri)
            prefix = namespaces.get(namespace_uri, prefix)
            namespaces[namespace_uri] = prefix
            qname = prefix + ':' + name
        else:
            qname = name
        return qname

    def doc_namespace(self, namespace, prefix):
        """
        Document extension namespaces
        """
        attributes = {'namespace-uri' : namespace,
                      'prefix' : prefix,
                      }
        self.write_element('namespace', attributes)
        return

    def doc_function(self, function, namespace, qname):
        """
        Document extension functions
        """
        from Ft.Xml.XPath.XPathTypes import g_xpathPrimitiveTypes

        attributes = {'namespace-uri' : namespace or '',
                      'name' : qname,
                      }
        self.start_element('function', attributes)

        desc = self.escape(pydoc.getdoc(function))
        self.write_element('description', content=desc)

        result = getattr(function, 'result', None)
        result = g_xpathPrimitiveTypes.get(result, 'unknown')
        self.write_element('result', content=self.escape(result))

        argtypes = getattr(function, 'arguments', ())
        args, varargs, varkw, defaults = inspect.getargspec(function)
        firstdefault = len(args) - len(defaults or ())
        # All extension functions take 'context' as their first argument so
        # start the index at 1 instead of 0.
        # IMPLEMENTATION NOTE: using map(None, ...) instead of zip to not
        # truncate the list if argtypes is shorter than args.
        for i, argtype in map(None, xrange(1, len(args)), argtypes):
            argname = str(args[i])
            attributes = {'name' : argname,
                          'type' : g_xpathPrimitiveTypes.get(argtype, argname),
                          }
            if (i < firstdefault):
                attributes['required'] = 'yes'
            self.write_element('argument', attributes)

        self.end_element('function')
        return

    def doc_element(self, element, namespace, qname):
        """
        Document extension elements
        """
        attributes = {'namespace-uri' : namespace or '',
                      'name' : qname,
                      }
        self.start_element('element', attributes)

        desc = self.escape(pydoc.getdoc(element))
        self.write_element('description', content=desc)

        if element.content:
            content  = self.escape(str(element.content))
            self.write_element('content', content=content)

        attributes = element.legalAttrs or {}
        for name, info in attributes.items():
            attrs = {'name' : name,
                     'content' : str(info),
                     'required' : info.required and 'yes' or 'no',
                     }
            if info.default:
                attrs['default'] = info.default
            self.start_element('attribute', attrs)
            desc = info.description or ''
            self.write_element('description', content=desc)
            self.end_element('attribute')

        self.end_element('element')
        return
