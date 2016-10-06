########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/_4xslt.py,v 1.50.2.1 2006/10/16 21:52:39 jkloth Exp $
"""
Implementation of '4xslt' command
(functions defined here are used by the Ft.Lib.CommandLine framework)

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import re, os, sys, traceback, cPickle, time
from cStringIO import StringIO

from Ft import GetConfigVars
from Ft.Lib import UriException, CloseStream
from Ft.Lib.CommandLine import CommandLineApp, Options, Arguments
from Ft.Lib.CommandLine.CommandLineUtil import SourceArgToInputSource
from Ft.Lib.Uri import OsPathToUri, Absolutize
from Ft.Xml.InputSource import InputSourceFactory, DefaultFactory
from Ft.Xml.XPath import RuntimeException, CompiletimeException
from Ft.Xml.Xslt import Processor, XsltException
from Ft.Xml import SplitQName

g_paramBindingPattern = re.compile(r"([\d\D_\.\-]*:?[\d\D_\.\-]+)=(.*)")
g_prefixBindingPattern = re.compile(r"([\d\D_\.\-]+)=(.+)")

from Ft import MAX_PYTHON_RECURSION_DEPTH
sys.setrecursionlimit(MAX_PYTHON_RECURSION_DEPTH)


class XsltCommandLineApp(CommandLineApp.CommandLineApp):

    from Ft.__config__ import \
        NAME as project_name, VERSION as project_version, URL as project_url

    name = '4xslt'
    summary = ('command-line tool for performing XSLT transformations on XML'
               'documents')
    description = """4XSLT command-line application"""

    options = [
        Options.Option(
            'v', 'validate',
            'Validate the input file as it is being parsed'),
        Options.Option(
            'i', 'ignore',
            'Ignore <?xml-stylesheet ...?> instructions'),
        Options.Option(
            None, 'media=MEDIA',
            'Set media to honor in xml-stylesheet PIs'),
        Options.Option(
            'D', 'define=NAME=VALUE',
            'Bind a top-level parameter'),
        Options.Option(
            'P', 'prefix=PREFIX=NSURI',
            'Assign a namespace to a prefix used in a top-level parameter'),
        Options.Option(
            'I', 'alt-sty-path=PATH',
            "Same as --alt-sty-uri but uses OS path"),
        Options.Option(
            None, 'alt-sty-uri=URI',
            "Define an add'l base URI for imports and includes"),
        Options.Option(
            'o', 'outfile=FILE',
            'Direct transformation output to FILE (file will be overwritten'
            ' if it exists)'),
        Options.Option(
            'e', 'stacktrace-on-error',
            'Display a stack trace when an error occurs'),
        Options.Option(
            None, 'noxinclude',
            'Do not expand XIncludes in source document and stylesheet'),
        Options.Option(
            None, 'trace',
            'Send execution trace output to stderr or file set by'
            ' --trace-file'),
        Options.Option(
            None, 'trace-file=FILE',
           'Trace file for execution trace output when using --trace'),
        Options.ExclusiveOptions([
            Options.Option(
                None, 'reflex',
               'Reflexive transform (use the stylesheet as the source'
               ' document).'),
            Options.Option(
                None, 'compile',
               'Compile an instant stylesheet. The result is written to'
               ' stdout, unless -o is used.'),
            Options.Option(
                None, 'instant',
               'The stylesheet is "instant" (compiled). Only one stylesheet'
               ' can be specified with this option.'),
            Options.Option(
                None, 'chain',
               'Chain the stylesheets (result of transforming with the first'
               ' is the source document for transforming with the second, and'
               ' so on). Without this option, each extra stylesheet is'
               ' imported by the preceding one.'),
            ]),
        Options.Option(
            None, 'time',
            'Display the elapsed transformation time on stderr'),
        Options.Option(
            None, 'msg-prefix=STRING',
            'Prepend string to xsl:message output'),
        Options.Option(
            None, 'msg-suffix=STRING',
            'Append string to xsl:message output'),
        Options.Option(
            None, 'no-messages',
            'Suppress xsl:message output and warnings'),
        ]

    arguments = [
        Arguments.RequiredArgument(
            'source-uri',
            'The URI of the XML document to transform, or "-" to indicate'
            ' standard input. If using --reflex, it is also the stylesheet.'
            ' If using --compile, it is the stylesheet to compile.'),
        Arguments.ZeroOrMoreArgument(
            'stylesheet-uri',
            'The URI(s) of the stylesheet(s) to apply.'),
        ]

    def validate_options(self, options):
        if options.has_key('trace'):
            outputfile = options.get('outfile')
            tracefile = options.get('trace-file')
            msg = ''
            if not outputfile and not tracefile:
                msg = 'When using --trace, you must specify an output' \
                      ' file for the trace info (--trace-file) and/or' \
                      ' for the transformation result (-o or --outfile).'
            else:
                outputfile_abspath = outputfile and os.path.abspath(outputfile) or None
                tracefile_abspath = tracefile and os.path.abspath(tracefile) or None
                if outputfile_abspath == tracefile_abspath:
                    msg = 'The trace and result output destinations must differ.'
                for path in (outputfile, outputfile_abspath):
                    if not path:
                        pass # we already handled the one case that matters
                    elif path.endswith(os.sep):
                        msg = 'The output file %s would be a directory.' % path
                    elif os.path.isdir(path):
                        msg = 'The output file %s is a directory.' % path
                for path in (tracefile, tracefile_abspath):
                    if not path:
                        pass # we already handled the one case that matters
                    elif path.endswith(os.sep):
                        msg = 'The trace file %s would be a directory.' % path
                    elif os.path.isdir(path):
                        msg = 'The trace file %s is a directory.' % path
            if msg:
                raise SystemExit('%s\n See "%s -h" for usage info.' % (msg, sys.argv[0]))

        return CommandLineApp.CommandLineApp.validate_options(self, options)

    def run(self, options, arguments):
        # 1st arg ('source-uri') will be the source doc normally, or the
        # source doc & stylesheet in the case of --reflex, or the
        # 1st stylesheet in the case of --compile. It is never OK to have
        # zero args. For --reflex, there must be only one arg. For
        # --instant, there must be exactly two. For --chain, three or more.
        msg = ''
        argslen = len(arguments)
        if argslen != 2 and options.has_key('instant'):
            msg = 'When using --instant, exactly 1 source doc URI and 1 stylesheet URI are required.'
        elif argslen < 3 and options.has_key('chain'):
            msg = 'When using --chain, 1 source doc URI and at least 2 stylesheet URIs are required.'
        elif argslen > 1:
            if options.has_key('reflex'):
                msg = 'When using --reflex, only 1 source/stylesheet URI may be given.'
            elif arguments.values().count('-') > 1:
                msg = 'Standard input may be used for only 1 source document or stylesheet.'
        if msg:
            raise SystemExit('%s\n See "%s -h" for usage info.' % (msg, sys.argv[0]))
        return Run(options, arguments)


def StySourceArgToInputSource(arg, factory, *v_args, **kw_args):
    """
    A wrapper for SourceArgToInputSource().

    If an InputSource cannot be created from the source argument,
    then the argument is resolved against alternative stylesheet base
    URIs (if any) until an InputSource is successfully created or the
    list of URIs is exhausted.
    """
    isrc = None
    stylesheetAltUris = None
    if kw_args.has_key('stylesheetAltUris'):
        stylesheetAltUris = kw_args['stylesheetAltUris']
        del kw_args['stylesheetAltUris']
    try:
        isrc = SourceArgToInputSource(arg, factory, *v_args, **kw_args)
    except (OSError, UriException), error:
        if stylesheetAltUris:
            for alt_uri in stylesheetAltUris:
                try:
                    new_uri = factory.resolver.normalize(arg, alt_uri)
                    isrc = factory.fromUri(new_uri)
                    break
                except (OSError, UriException):
                    pass
        if not isrc:
            raise error

    return isrc


def ReportFatalException(e, stacktrace_on_error=False):
    """
    Formats various exceptions; raises SystemExit, never returns.
    """
    if isinstance(e, XsltException) or \
        isinstance(e, RuntimeException) or \
        isinstance(e, CompiletimeException):
        if stacktrace_on_error:
            traceback.print_exc(1000, sys.stderr)
        raise SystemExit(''.join([c.encode(sys.getdefaultencoding(), 'ignore')
                                  or "&#%d;" % ord(c) for c in e.message]))
    else:
        if stacktrace_on_error:
            traceback.print_exc(1000, sys.stderr)
            msg = ''
        else:
            exceptiontype = str(sys.exc_type)
            if exceptiontype.startswith('exceptions.'):
                exceptiontype = exceptiontype[11:]
            msg = 'An unexpected error occurred while processing.\n' + \
                  'The error was: %s: %s\n' % (exceptiontype, str(e)) + \
                  'Use the -e (--stacktrace-on-error) option for a full stack trace.'
        if msg:
            raise SystemExit(''.join([c.encode(sys.getdefaultencoding(), 'ignore')
                                      or "&#%d;" % ord(c) for c in msg]))
        else:
            sys.exit()


def Run(options, args):

    stacktrace_on_error = options.has_key('stacktrace-on-error')

    # -- Set up output streams (will die if files unwritable) ----------
    # (assumes output destinations have been checked for uniqueness)

    if options.has_key('compile'):
        output_flags = "wb"
    else:
        output_flags = "w"

    out_file = options.has_key('outfile') \
               and open(options['outfile'], output_flags) or sys.stdout

    trace_file = None
    if options.has_key('trace'):
        trace_file_name= options.get('trace-file')
        if trace_file_name:
            trace_file_name = os.path.abspath(trace_file_name)

        out_file_name = options.get('outfile')
        if out_file_name:
            out_file_name = os.path.abspath(out_file_name)

        trace_file = options.has_key('trace-file') \
                     and open(options['trace-file'], 'w') or sys.stderr

    # -- Set up XSLT processor (without stylesheets) -------------------

    # gather alt base URIs for xsl:include/import resolution
    #
    # An ordered list of absolute URIs is derived from these sources:
    #  1. command-line option(s) alt-sty-uri=../../foo.xml
    #  2. command-line option(s) alt-sty-path=C:\foo.xml
    #  3. environment variable XSLTINCLUDE=\a\b\foo.xml
    alt_sty_uris = options.get('alt-sty-uri', [])
    if type(alt_sty_uris) != list:
        alt_sty_uris = [alt_sty_uris]

    alt_sty_paths = options.get('alt-sty-path', [])
    if type(alt_sty_paths) != list:
        alt_sty_paths = [alt_sty_paths]

    more_sty_uris = [OsPathToUri(path, attemptAbsolute=1) for path in alt_sty_paths]
    alt_sty_uris.extend(more_sty_uris)

    if os.environ.has_key('XSLTINCLUDE'):
        more_sty_uris = [
            OsPathToUri(path, attemptAbsolute=1)
            for path in os.environ["XSLTINCLUDE"].split(os.pathsep)
            ]
        alt_sty_uris.extend(more_sty_uris)

    del more_sty_uris

    # tracing requires special setup.
    if options.has_key('trace'):
        from Ft.Xml.Xslt import ExtendedProcessingElements, StylesheetHandler
        processor = ExtendedProcessingElements.ExtendedProcessor(stylesheetAltUris=alt_sty_uris)
        processor._4xslt_trace = True
        processor._4xslt_traceStream = trace_file
        StylesheetHandler._ELEMENT_MAPPING = ExtendedProcessingElements.GetMappings()
    else:
        processor = Processor.Processor(stylesheetAltUris=alt_sty_uris)

    # media prefs affect xsl:stylesheet PI selection
    processor.mediaPref = options.get('media', None)

    # register extension modules
    moduleList = os.environ.get("EXTMODULES")
    if moduleList:
        processor.registerExtensionModules(moduleList.split(":"))

    # set up the source document reader
    from Ft.Xml import Domlette
    validate_flag = options.has_key('validate')
    if validate_flag:
        reader = Domlette.ValidatingReader
    else:
        reader = Domlette.NonvalidatingReader
    processor.setDocumentReader(reader)

    #Customize message behavior
    if options.has_key('no-messages'):
        processor.messageControl(1)
    else:
        processor.messageControl(0)
        if options.has_key('msg-prefix'):
            prefix = options['msg-prefix']
            prefix = prefix.replace('\\n', '\n')
            prefix = prefix.replace('\\r', '\r')
            prefix = prefix.replace('\\t', '\t')
            processor.msgPrefix = prefix
        if options.has_key('msg-suffix'):
            suffix = options['msg-suffix']
            suffix = suffix.replace('\\n', '\n')
            suffix = suffix.replace('\\r', '\r')
            suffix = suffix.replace('\\t', '\t')
            processor.msgSuffix = suffix

    # -- Handle compile operation --------------------------------------

    if options.has_key('compile'):
        xinclude = not options.has_key('noxinclude')
        all_source_args = [args['source-uri']] + args['stylesheet-uri']
        try:
            sty_isrcs = map(lambda arg: StySourceArgToInputSource(arg,
                            DefaultFactory, processIncludes=xinclude,
                            stylesheetAltUris=alt_sty_uris),
                            all_source_args)
            for isrc in sty_isrcs:
                processor.appendStylesheet(isrc)
                CloseStream(isrc, quiet=True)

            # use better pickle format in Python 2.3 and up
            if hasattr(cPickle, 'HIGHEST_PROTOCOL'):
                cPickle.dump(processor.stylesheet.root, out_file, cPickle.HIGHEST_PROTOCOL)
            else:
                cPickle.dump(processor.stylesheet.root, out_file, 1)

        except Exception, e:
            ReportFatalException(e, stacktrace_on_error)

        CloseStream(out_file, quiet=True)

        if out_file is sys.stdout:
            dest = 'standard output'
        elif hasattr(out_file, 'name'):
            dest = out_file.name
        elif options.has_key('outfile'):
            dest = options['outfile']
        else:
            dest = 'unknown destination(!)'
        sys.stderr.write('Compiled stylesheet written to %s.\n' % dest)
        sys.stderr.flush()
        return

    # -- Prepare for any transform -------------------------------------

    # source document will be an InputSource
    source_isrc = None

    # list of InputSources for stylesheets (only if chaining)
    sty_chain = None

    # -- Prepare for reflexive transform -------------------------------

    if options.has_key('reflex'):
        xinclude = not options.has_key('noxinclude')
        source_arg = args['source-uri']
        try:
            isrc = StySourceArgToInputSource(source_arg, DefaultFactory,
                                             processIncludes=xinclude,
                                             stylesheetAltUris=alt_sty_uris)

            # We could parse the doc and use processor.appendStylesheetNode(),
            # but if there are XSLT errors, the line & column # won't show up
            # in the error message. So we will cache the doc in a reusable
            # stream in memory.
            stream = StringIO(isrc.read())
            CloseStream(isrc, quiet=True)
            stream.reset()
            source_isrc = isrc.clone(stream)
            del isrc
            processor.appendStylesheet(source_isrc)
            source_isrc.reset()
        except Exception, e:
            ReportFatalException(e, stacktrace_on_error)

    # -- Prepare for regular transform ---------------------------------

    else:
        xinclude = not options.has_key('noxinclude')
        instant = options.has_key('instant')
        source_arg = args['source-uri']
        if instant:
            sty_arg = args['stylesheet-uri'][0]
            try:
                sty_isrc = StySourceArgToInputSource(sty_arg, DefaultFactory,
                                                     processIncludes=xinclude,
                                                     stylesheetAltUris=alt_sty_uris)
                sty_obj = cPickle.load(sty_isrc)

                CloseStream(sty_isrc, quiet=True)
                processor.appendStylesheetInstance(sty_obj, refUri=sty_isrc.uri)
                source_isrc = SourceArgToInputSource(source_arg, DefaultFactory,
                                                     processIncludes=xinclude)
            except cPickle.UnpicklingError:
                ReportFatalException(ValueError(
                    '%s does not appear to be a compiled stylesheet object.' % sty_arg),
                    stacktrace_on_error)
            except Exception, e:
                ReportFatalException(e, stacktrace_on_error)

        else:
            sty_args = args['stylesheet-uri']
            chain = options.has_key('chain')
            try:
                sty_isrcs = map(lambda arg: StySourceArgToInputSource(arg,
                                DefaultFactory, processIncludes=xinclude,
                                stylesheetAltUris=alt_sty_uris),
                                sty_args)

                if chain and len(sty_isrcs) > 1:
                    sty_chain = sty_isrcs
                else:
                    for isrc in sty_isrcs:
                        processor.appendStylesheet(isrc)
                        CloseStream(isrc, quiet=True)

                source_isrc = SourceArgToInputSource(source_arg, DefaultFactory,
                                                     processIncludes=xinclude)

            except Exception, e:
                ReportFatalException(e, stacktrace_on_error)

    # -- Gather transformation-time options ----------------------------

    # top-level params
    nsmappings = {}
    prefixes = options.get('prefix', [])
    if not isinstance(prefixes, list):
        prefixes = [prefixes]
    for p in prefixes:
        match = g_prefixBindingPattern.match(p)
        if match is None:
            raise TypeError('Error in -P/--prefix arguments')
        nsmappings[match.group(1)] = match.group(2)

    defs = options.get('define', [])
    if not isinstance(defs, list):
        defs = [defs]
    top_level_params = {}
    for d in defs:
        match = g_paramBindingPattern.match(d)
        if match is None:
            raise TypeError('Error in -D/--define arguments')
        name = match.group(1)
        prefix, local = SplitQName(name)
        if prefix in nsmappings:
            name = (nsmappings[prefix], local)
        top_level_params[name] = match.group(2)

    # misc runtime flags
    ignore_pis = options.has_key('ignore')
    checktime = options.has_key('time')

    # -- Do the transformation -----------------------------------------

    try:

        if source_isrc is None:
            raise TypeError('No source document to transform!')

        if sty_chain:
            resultstream = StringIO()
            if checktime:
                start = time.time()
            i = 0
            for sty_isrc in sty_chain[:-1]:
                i += 1
                # FIXME:
                # use RtfWriter to make each result be a Domlette document,
                # for speed, and so that the input to each chained stylesheet
                # is the previous transformation's result tree (not the
                # previous transformation's serialized result tree)
                processor.appendStylesheet(sty_isrc)
                CloseStream(sty_isrc, quiet=True)
                processor.run(source_isrc, ignore_pis,
                              topLevelParams=top_level_params,
                              outputStream=resultstream)
                processor.reset()
                resultstream.reset()
                sourcestream = resultstream
                new_uri = Absolutize('chained-transformation-result-%d' % i,
                                     source_isrc.uri)
                source_isrc = source_isrc.clone(sourcestream, new_uri)
                resultstream = StringIO()

            processor.appendStylesheet(sty_chain[-1])
            processor.run(source_isrc, ignore_pis,
                          topLevelParams=top_level_params,
                          outputStream=out_file)
            if checktime:
                end = time.time()

            CloseStream(source_isrc, quiet=True)

        else:
            if checktime:
                start = time.time()
            processor.run(source_isrc, ignore_pis,
                          topLevelParams=top_level_params,
                          outputStream=out_file)
            if checktime:
                end = time.time()

            CloseStream(source_isrc, quiet=True)

    except Exception, e:
        ReportFatalException(e, stacktrace_on_error)

    # -- Handle post-transformation tasks ------------------------------

    try:
        if out_file.isatty():
            out_file.flush()
            sys.stderr.write('\n')
        else:
            out_file.close()
    except (IOError, ValueError):
        pass

    if checktime:
        sys.stderr.write("Transformation time: %dms\n" % (1000 * (end - start)))

    return
