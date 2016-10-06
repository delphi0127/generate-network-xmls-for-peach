import os
import re
import sys
from distutils import util, sysconfig
from distutils.command import build_ext
from distutils.dep_util import newer_group, newer
from distutils.version import StrictVersion

from Ft.Lib import ImportUtil
from Ft.Lib.DistExt import Util

# Constants for symbol stripping
STRIP_NONE = 0
STRIP_VERSIONING = 1
STRIP_EXPORTS_FILE = 2
STRIP_EXPORTS_ARGLIST = 3
STRIP_EXPORTS_POST_LINK = 4

BISONGEN_MINIMUM_VERSION = StrictVersion('0.8.0')

try:
    enumerate
except NameError:
    enumerate = lambda sequence: zip(range(len(sequence)), sequence)

class BuildExt(build_ext.build_ext):

    command_name = 'build_ext'

    def initialize_options(self):
        build_ext.build_ext.initialize_options(self)

        # How to format C symbol name to exported symbol name
        self.export_symbol_format = '%s'

        self.symbol_stripping = STRIP_NONE
        self.strip_command = None
        return

    def finalize_options(self):
        build_ext.build_ext.finalize_options(self)

        # Verify that extensions are built with the proper flags.
        # For Windows, Py_DEBUG is enabled whenever debugging information
        # is included. For other platforms, it must be explicited defined.
        if sys.platform == 'win32':
            py_debug = self.debug
        else:
            # 'getobjects()' is only available in debug builds.
            py_debug = hasattr(sys, 'getobjects')
        if py_debug and not Util.GetConfigVars('Py_DEBUG')[0]:
            macros = [('Py_DEBUG', None)]
            if not self.define:
                self.define = macros
            else:
                self.define.extend(macros)

        # If built as shared, remove the library dir if the shared library
        # is not installed there (which Python does not do by default).
        # This fixes the errors building on openSUSE 10.2 w/Python 2.5.
        if (sys.platform.startswith('linux') and
            sysconfig.get_config_var('Py_ENABLE_SHARED')):
            libpl, ldlibrary = sysconfig.get_config_vars('LIBPL', 'LDLIBRARY')
            if libpl in self.library_dirs:
                if not os.path.exists(os.path.join(libpl, ldlibrary)):
                    self.library_dirs.remove(libpl)

        # OpenBSD and NetBSD dlsyms have a leading underscore if the object
        # format is not ELF.  (from src/Python/dynload_shlib.c).
        if (sys.platform.startswith('openbsd')
            or sys.platform.startswith('netbsd')):
            # Capture predefined preprocessor macros (from src/configure)
            cc = sysconfig.get_config_var('CC')
            defines = os.popen(cc + ' -dM -E - </dev/null').read()
            # Check for ELF object format
            if defines.find('__ELF__') == -1:
                self.export_symbol_format = '_%s'

        # By limiting exported symbols, we don't need to worry about symbol
        # conflicts between the shared modules or Python itself.
        if os.name == 'nt' or sys.platform.startswith('cygwin'):
            # The compiler default is to limit exported symbols
            self.symbol_stripping = STRIP_NONE

        elif (sys.platform.startswith('linux')
              or sys.platform.startswith('freebsd')
              or sys.platform.startswith('openbsd')
              or sys.platform.startswith('netbsd')):
            # This assumes the the GNU linker is being used.
            # As of Dec 2005, the SourceForge Compile Farm servers use GNU ld
            # for OpenBSD and NetBSD.
            self.symbol_stripping = STRIP_VERSIONING
            self.strip_command = '-Wl,--version-script,%s'

        elif sys.platform.startswith('sunos'):
            self.symbol_stripping = STRIP_VERSIONING
            self.strip_command = '-Wl,-M,%s'

        elif sys.platform.startswith('darwin'):
            # Mac OS X/Darwin
            ld = sysconfig.get_config_var('LDSHARED')
            output = os.popen(ld + ' -Wl,-exported_symbols_list').read()
            if re.search('unknown flag: -exported_symbols_list', output):
                # Older OSX (10.1 or 10.2 with DevTools prior to Dec 2002)
                # Use external program (nmedit) to limit exported symbols
                self.symbol_stripping = STRIP_EXPORTS_POST_LINK
                self.strip_command = 'nmedit -s %(exports)s -p %(extension)s'
            else:
                self.symbol_stripping = STRIP_EXPORTS_FILE
                self.strip_command = '-Wl,-exported_symbols_list,%s'
                self.export_symbol_format = '_%s'

        elif sys.platform.startswith('hp-ux'):
            # HP-UX linker lists exported symbols one at a time in the
            # argument list.
            self.symbol_stripping = STRIP_EXPORTS_ARGLIST
            self.strip_command = '-Wl,+e,%s'

        elif os.name == 'posix':
            # From online manual pages, most UNIX support limiting exported
            # symbols with the same option.
            self.symbol_stripping = STRIP_EXPORTS_FILE
            self.strip_command = '-Wl,-exports_file,%s'
        return

    def check_extensions_list(self, extensions):
        build_ext.build_ext.check_extensions_list(self, extensions)

        # Add the included files for each source file
        for ext in extensions:
            if not isinstance(ext.sources, (tuple, list)):
                raise DistutilsSetupError(
                    "in 'ext_modules' option (extension '%s'), "
                    "'sources' must be present and must be "
                    "a list of source filenames" % ext.name)
            if not hasattr(ext, 'depends'):
                ext.depends = []
            if not hasattr(ext, 'includes'):
                ext.includes = {}
                for source in ext.sources:
                    includes = Util.FindIncludes(util.convert_path(source),
                                                 ext.include_dirs)
                    ext.includes[source] = includes
        return

    def get_source_files(self):
        self.check_extensions_list(self.extensions)

        filenames = []
        for extension in self.extensions:
            for source in self.prepare_sources(extension):
                filenames.append(source)
                filenames.extend(extension.includes[source])
        return filenames

    def build_extension(self, ext):
        # First, scan the sources for SWIG definition files (.i), run
        # SWIG on 'em to create .c files, and modify the sources list
        # accordingly.
        sources = self.prepare_sources(ext)

        fullname = self.get_ext_fullname(ext.name)
        ext_filename = os.path.join(self.build_lib,
                                    self.get_ext_filename(fullname))

        # Changes to the command indicate that compilation options may have
        # changed so rebuild/link everything
        command_mtime = ImportUtil.GetLastModified(__name__)
        try:
            force = command_mtime > os.stat(ext_filename).st_mtime
        except OSError:
            force = True
        force = self.force or force

        depends = sources + ext.depends
        for includes in ext.includes.values():
            depends.extend(includes)
        if not (force or newer_group(depends, ext_filename, 'newer')):
            self.announce("skipping '%s' extension (up-to-date)" % ext.name)
            return

        self.announce("building '%s' extension" % ext.name, 2)

        # Next, compile the source code to object files.
        extra_args = ext.extra_compile_args or []

        macros = ext.define_macros[:]
        for undef in ext.undef_macros:
            macros.append((undef,))

        # Get the resulting object filenames as we are compiling the sources
        # one at a time to reduce compile time for large source lists.
        objects = self.compiler.object_filenames(sources,
                                                 sysconfig.python_build,
                                                 self.build_temp)

        self.compiler.force = force
        if sys.version >= '2.3':
            # Python 2.3 added dependency checking to the compiler, use that
            for object, source in zip(objects, sources):
                depends = ext.depends + ext.includes[source]
                self.compiler.compile([source],
                                      output_dir=self.build_temp,
                                      macros=macros,
                                      include_dirs=ext.include_dirs,
                                      debug=self.debug,
                                      extra_postargs=extra_args,
                                      depends=depends)
        else:
            if not force:
                # Determine those sources that require rebuilding
                new_sources = []
                for object, source in zip(objects, sources):
                    depends = [source]
                    depends.extend(ext.includes[source])
                    if (newer_group(depends, object, 'newer')
                        or command_mtime > os.stat(object).st_mtime):
                        new_sources.append(source)
                sources = new_sources

            # Forcably build those sources listed in 'sources'
            self.compiler.force = True
            for source in sources:
                output_dir = os.path.join(self.build_temp,
                                          os.path.dirname(source))
                self.compiler.compile([source],
                                      output_dir=output_dir,
                                      macros=macros,
                                      include_dirs=ext.include_dirs,
                                      debug=self.debug,
                                      extra_postargs=extra_args)

        # Now link the object files together into a "shared object" --
        # of course, first we have to figure out all the other things
        # that go into the mix.
        if ext.extra_objects:
            objects.extend(ext.extra_objects)

        # Setup "symbol stripping"
        if self.symbol_stripping == STRIP_VERSIONING:
            # Strip symbols via a versioning script
            f, mapfile = self._mkstemp(ext, '.map')
            f.write('{ global: ')
            for sym in self.get_export_symbols(ext):
                f.write(sym + '; ')
            f.write('local: *; };')
            f.close()
            link_preargs = [self.strip_command % mapfile]

        elif self.symbol_stripping == STRIP_EXPORTS_FILE:
            # Strip symbols via an exports file
            f, expfile = self._mkstemp(ext, '.exp')
            for sym in self.get_export_symbols(ext):
                f.write(sym + '\n')
            f.close()
            link_preargs = [self.strip_command % expfile]

        elif self.symbol_stripping == STRIP_EXPORTS_ARGLIST:
            # Strip symbols via multiple arguments
            symbols = self.get_export_symbols(ext)
            link_preargs = [ self.strip_command % sym for sym in symbols ]

        else:
            # No linker support for limiting exported symbols
            link_preargs = []

        # Detect target language, if not provided
        kwords = {}
        if sys.version >= '2.3':
            lang = ext.language or self.compiler.detect_language(ext.sources)
            kwords['target_lang'] = lang

        self.compiler.link_shared_object(
            objects, ext_filename,
            libraries=self.get_libraries(ext),
            library_dirs=ext.library_dirs,
            runtime_library_dirs=ext.runtime_library_dirs,
            extra_preargs=link_preargs,
            extra_postargs=ext.extra_link_args,
            export_symbols=self.get_export_symbols(ext),
            debug=self.debug,
            build_temp=self.build_temp,
            **kwords)

        if self.symbol_stripping == STRIP_EXPORTS_POST_LINK:
            # Create the exports file
            f, expfile = self._mkstemp(ext, '.exp')
            for sym in self.get_export_symbols(ext):
                f.write(sym + '\n')
            f.close()

            subst = {'exports' : expfile, 'extension' : filename}
            self.spawn([ x % subst for x in self.strip_command.split(' ') ])

        # Reset the force flag on the compilier
        self.compiler.force = self.force
        return

    def prepare_sources(self, extension):
        """Walk the list of source files in 'sources', looking for SWIG
        interface (.i) files.  Run SWIG on all that are found, and
        return a modified 'sources' list with SWIG source files replaced
        by the generated C (or C++) files.
        """
        sources = []
        bgen_sources = []
        bgen_outputs = []
        for source in extension.sources:
            if source.endswith('.bgen'):
                name, includes = self._parse_bgen(source)
                if name is None:
                    name = extension.name.split('.')[-1][:-1]
                extension.includes[source] = includes
                # replace the BisonGen file with the generated C file
                bgen_output = os.path.dirname(source)
                bgen_output = os.path.join(bgen_output, name + '.c')
                # see if the C file needs to be regenerated
                if newer_group([source] + includes, bgen_output):
                    bgen_sources.append(source)
                bgen_outputs.append(bgen_output)
                sources.append(bgen_output)
            else:
                sources.append(source)
        if bgen_sources:
            try:
                from BisonGen import __version__, Processor, OptionParser
            except ImportError:
                # use the pre-generated sources
                for source in bgen_sources:
                    self.warn("not compiling %s (BisonGen not found)" % source)
            else:
                if StrictVersion(__version__) < BISONGEN_MINIMUM_VERSION:
                    raise DistutilsExecError("requires BisonGen %s, found %s"
                                             % (BISONGEN_MINIMUM_VERSION,
                                                __version__))
                # Convert verbosity to logging threshold
                threshold = 3 - self.verbose
                processor = Processor.Processor(threshold)
                options = OptionParser.Values()
                options.language = 'c'
                for source in bgen_sources:
                    options.outputDirectory = os.path.dirname(source)
                    processor.run(source, options)

        # Update the extension's include mapping for the generated file.
        for output in bgen_outputs:
            includes = extension.includes.get(output, [])
            includes = FindIncludes(output, extension.include_dirs, includes)
            extension.includes[output] = includes

        if sys.version < '2.4':
            return self.swig_sources(sources)
        return self.swig_sources(sources, extension)

    def _parse_bgen(self, filename):
        name = None
        includes = []
        basedir = os.path.dirname(filename)
        for event, node in Util.IterXml(filename):
            if name is None and event == 'START_ELEMENT':
                if node.tagName == 'options':
                    name = node.getAttribute('name')
            elif event == 'PROCESSING_INSTRUCTION':
                if node.target == 'include':
                    match = re.match(r'(["]?)(.+)(\1)', node.nodeValue)
                    if match:
                        include = util.convert_path(match.group(2))
                        include = os.path.join(basedir, include)
                        include = os.path.normpath(include)
                        includes.append(include)
                        includes.extend(self._parse_bgen(include)[1])
        return (name, includes)

    def _mkstemp(self, extension, suffix):
        path_parts = extension.name.split('.')
        basename = os.path.join(self.build_temp, *path_parts)
        # extensions in debug_mode are named 'module_d.pyd' under windows
        if os.name == 'nt' and self.debug:
            basename += '_d'
        filename = basename + suffix
        self.mkpath(os.path.dirname(filename))
        return (open(filename, 'w'), filename)

    def get_export_symbols(self, extension):
        symbols = build_ext.build_ext.get_export_symbols(self, extension)
        return [ self.export_symbol_format % symbol for symbol in symbols ]
