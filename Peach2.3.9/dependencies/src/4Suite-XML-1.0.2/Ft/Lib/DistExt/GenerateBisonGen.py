import os, re
from distutils import util
from distutils.core import Command
from distutils.errors import DistutilsModuleError
from distutils.version import StrictVersion

MINIMUM_VERSION = StrictVersion('0.8.0b2')

class GenerateBisonGen(Command):

    command_name = 'generate_bgen'

    description = "regenerate BisonGen parsers"

    user_options = [
        ('force', 'f',
         'force rebuild (ignore timestamps)'),
        ]

    boolean_options = ['force']

    def initialize_options(self):
        self.bgen_files = None
        self.force = 0

    def finalize_options(self):
        self.set_undefined_options('generate', ('force', 'force'))
        self.bgen_files = self.distribution.bgen_files

    _include_re = re.compile('<\?include (?P<file>.*(?=\?>))\?>')
    def _find_includes(self, file):
        includes = []
        source = open(file).read()
        base = os.path.dirname(file)

        match = self._include_re.search(source)
        while match:
            filename = util.convert_path(match.group('file'))
            include = os.path.normpath(os.path.join(base, filename))
            includes.append(include)
            includes.extend(self._find_includes(include))
            match = self._include_re.search(source, match.end())
        return includes

    def get_source_files(self):
        sources = []
        for filename in self.bgen_files:
            sources.append(filename)
            includes = self._find_includes(filename)
            for filename in includes:
                if filename not in sources:
                    sources.append(filename)
        return sources

    def get_outputs(self):
        return []

    def run(self):
        if not self.bgen_files:
            return

        try:
            from BisonGen import Main, __version__
        except ImportError, err:
            failure = str(err)
        else:
            if MINIMUM_VERSION > StrictVersion(__version__):
                failure = "found " + __version__
            else:
                failure = None
            
        if failure:
            msg = "%s requires BisonGen %s (%s)" % (self.command_name,
                                                    MINIMUM_VERSION, failure)
            raise DistutilsModuleError(msg)

        outputs = []
        args = ['BisonGen', '--mode=c']
        if self.force:
            args.append('--force')
        if not self.distribution.verbose:
            args.append('--quiet')
        for filename in self.bgen_files:
            outputs.extend(Main.Run(args + [filename]))
        return
