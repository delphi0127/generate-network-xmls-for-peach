########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XPath/_4xpath.py,v 1.11.2.1 2006/10/16 21:52:39 jkloth Exp $
"""
Implementation of '4xpath' command
(functions defined here are used by the Ft.Lib.CommandLine framework)

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import re, os, sys, traceback

from Ft.Lib import CloseStream
from Ft.Lib.CommandLine import CommandLineApp, Options, Arguments
from Ft.Lib.CommandLine.CommandLineUtil import SourceArgToInputSource
from Ft.Xml import XPath, InputSource
from Ft.Xml.XPath import Conversions
from Ft.Xml.XPath import XPathTypes as Types
from Ft.Xml.XPath.Util import ExpandQName

g_paramBindingPattern = re.compile(r"([\d\D_\.\-]*:?[\d\D_\.\-]+)=(.*)")
g_nssBindingPattern = re.compile(r"([\d\D_\.\-]*:?[\d\D_\.\-]+)=(.*)")

from Ft import MAX_PYTHON_RECURSION_DEPTH
sys.setrecursionlimit(MAX_PYTHON_RECURSION_DEPTH)


class XPathCommandLineApp(CommandLineApp.CommandLineApp):

    from Ft.__config__ import \
        NAME as project_name, VERSION as project_version, URL as project_url

    name = '4xpath'
    summary = 'command-line tool for performing XPath queries on XML documents'
    description = """4XPath command-line application"""

    options = [
        Options.Option(
            'D', 'define=NAME=VALUE',
            'Bind a top-level parameter'),
        Options.Option(
            'N', 'namespace=PREFIX=NAMESPACE',
            'Define a namespace/prefix binding'),
        Options.Option(
            'e', 'stacktrace-on-error',
            'Display a stack trace when an error occurs'),
        Options.Option(
            None, 'string',
            'Print the string-value of the results'),
        ]

    arguments = [
        Arguments.RequiredArgument(
            'source-uri',
            'The URI of the XML document to parse, or "-" to indicate'
            ' standard input. The document\'s root node will be used as the'
            ' context node.'),
        Arguments.RequiredArgument(
            'expression',
            'The XPath expression to evaluate'),
        ]

    def validate_arguments(self, args):
        if len(args) < 2:
            raise SystemExit('A source URI argument and an expression'
                             ' argument are required. See "%s -h" for usage'
                             ' info.' % sys.argv[0])
        return CommandLineApp.CommandLineApp.validate_arguments(self, args)

    def run(self, options, arguments):
        return Run(options, arguments)


def Run(options,args):

    defs = options.get('define', [])
    if type(defs) != type([]):
        defs = [defs]

    namespaces = options.get('namespace', [])
    if type(namespaces) != type([]):
        namespaces = [namespaces]

    processorNss = {}
    for n in namespaces:
        match = g_nssBindingPattern.match(n)
        processorNss[match.group(1)] = match.group(2)

    top_level_params = {}
    for d in defs:
        match = g_paramBindingPattern.match(d)
        name = ExpandQName(match.group(1),namespaces = processorNss)
        top_level_params[name] = match.group(2)

    stringValue = options.has_key('string')
    stacktrace_on_error = options.has_key('stacktrace-on-error')

    from Ft.Xml import Domlette
    reader = Domlette.NonvalidatingReader

    sourceUri = args['source-uri']
    try:
        source_isrc = SourceArgToInputSource(sourceUri, InputSource.DefaultFactory)
    except Exception, e:
        sys.stderr.write(str(e)+'\n')
        sys.stderr.flush()
        return

    extmodules = os.environ.get("EXTMODULES")
    if extmodules:
        extmodules = extmodules.split(":")
    else:
        extmodules = []

    try:
        compExpr = XPath.Compile(args['expression'])

        dom = reader.parse(source_isrc)
        CloseStream(source_isrc, quiet=True)

        context = XPath.Context.Context(dom,
                                        processorNss = processorNss,
                                        varBindings = top_level_params,
                                        extModuleList = extmodules)

        res = compExpr.evaluate(context)
        if stringValue:
            res = Conversions.StringValue(res)

    except (XPath.RuntimeException, XPath.CompiletimeException), error:
        if stacktrace_on_error:
            traceback.print_exc(1000, sys.stderr)
        raise SystemExit(str(error))
    except Exception, error:
        if stacktrace_on_error:
            traceback.print_exc(1000, sys.stderr)
        raise SystemExit(str(error))


    if Types.g_xpathPrimitiveTypes.has_key(type(res)):
        heading = "Result (XPath %s):" % Types.g_xpathPrimitiveTypes[type(res)]
        if isinstance(res, Types.NodesetType):
            res = res and '\n'.join(map(str, res)) or '<empty node-set>'
    else:
        heading = "Result (unknown type):"
    sys.stderr.write('%s\n%s\n' % (heading, '=' * len(heading)))
    sys.stderr.flush()
    print res
    return
