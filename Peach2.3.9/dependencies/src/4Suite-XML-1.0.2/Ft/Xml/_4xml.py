########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/_4xml.py,v 1.27.2.1 2006/10/16 21:52:38 jkloth Exp $
"""
Implementation of '4xml' command
(functions defined here are used by the Ft.Lib.CommandLine framework)

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os, sys

from Ft.Lib import CloseStream
from Ft.Lib.CommandLine import CommandLineApp, Options, Arguments
from Ft.Lib.CommandLine.CommandLineUtil import SourceArgToInputSource
from Ft.Xml import InputSource

class XmlCommandLineApp(CommandLineApp.CommandLineApp):

    from Ft.__config__ import \
        NAME as project_name, VERSION as project_version, URL as project_url

    name = '4xml'
    summary = 'command-line tool for working with XML documents'
    description = """4XML command-line application"""

    options = [
        Options.Option(
            'v', 'validate',
            'DTD validate the input file as it is being parsed'),
        Options.Option(
            'e', 'encoding=ENC',
            'The encoding to use for output'),
        Options.Option(
            None, 'input-encoding=ENC',
            'The encoding to assume for input'),
        Options.Option(
            'o', 'outfile=FILE',
            'Direct output to FILE (file will be overwritten if it exists)'),
        Options.Option(
            'p', 'pretty',
            'Pretty-print the result'),
        Options.Option(
            'n', 'noserialize',
            "Do not serialize; just parse"),
        Options.Option(
            None, 'html',
            'Use HTML mode when pretty-printing (emit XHTML as HTML)'),
        Options.Option(
            None, 'noxinclude',
            'Do not expand XIncludes'),
        Options.Option(
            None, 'rng=FILE',
            'Apply RELAX NG from the given file (technically RNG with XVIF'
            ' features)'),
        ]

    arguments = [
        Arguments.RequiredArgument(
            'source-uri',
            'The URI of the XML document to parse, or "-" to indicate standard'
            ' input.'),
        ]

    def validate_arguments(self, args):
        if not args:
            raise SystemExit('A source URI argument is required.' \
                             ' See "%s -h" for usage info.' % sys.argv[0])
        return CommandLineApp.CommandLineApp.validate_arguments(self, args)

    def run(self, options, arguments):
        return Run(options, arguments)


def Run(options, args):

    xinclude = not options.has_key('noxinclude')
    noserialize = options.has_key('noserialize')
    out_file = options.has_key('outfile') and open(options['outfile'], 'w') or sys.stdout
    validate_flag = options.has_key('validate')
    pretty = options.has_key('pretty')
    as_html = options.has_key('html')
    encoding = options.get('encoding', 'utf-8')
    input_encoding = options.get('input-encoding', None)
    rng_sourceUri = options.get('rng')
    sourceUri = args['source-uri']

    try:
        source_isrc = SourceArgToInputSource(sourceUri,
            InputSource.DefaultFactory,
            processIncludes=xinclude, encoding=input_encoding)
        rng_isrc = None
        if rng_sourceUri:
            rng_isrc = SourceArgToInputSource(rng_sourceUri,
                InputSource.DefaultFactory,
                processIncludes=xinclude, encoding=input_encoding)
    except Exception, e:
        sys.stderr.write(str(e)+'\n')
        sys.stderr.flush()
        return

    if rng_isrc is not None:
        try:
            from Ft.Xml.Xvif import RelaxNgValidator, RngInvalid
        except ImportError:
            raise SystemExit("Missing RELAX-NG support library.  It is "
                             "available in the Ft.Xml.ThirdParty package.")

    from Ft.Xml import Domlette
    if validate_flag:
        reader = Domlette.ValidatingReader
    else:
        reader = Domlette.NonvalidatingReader

    try:
        doc = reader.parse(source_isrc)
        CloseStream(source_isrc, quiet=True)

        if rng_isrc is not None:
            validator = RelaxNgValidator(rng_isrc)
            CloseStream(rng_isrc, quiet=True)
            result = validator.validateNode(doc)
            if not result.nullable():
                raise RngInvalid(result)

        if not noserialize:
            from Ft.Xml.Domlette import Print, PrettyPrint
            if pretty:
                PrettyPrint(doc, out_file, encoding, as_html)
            else:
                Print(doc, out_file, encoding, as_html)

    except Exception, e:
        import traceback
        traceback.print_exc(1000, sys.stderr)
        raise

    try:
        if out_file.isatty():
            out_file.flush()
            sys.stderr.write('\n')
        else:
            out_file.close()
    except (IOError, ValueError):
        pass

    return
