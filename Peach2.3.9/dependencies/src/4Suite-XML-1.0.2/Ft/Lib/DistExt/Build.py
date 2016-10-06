import sys, os
from distutils import util, ccompiler
from distutils.command import build

import Util

class Build(build.build):

    command_name = "build"

    description = "build everything needed to install"

    user_options = [
        ('build-base=', 'b', "base directory for build library"),
        ('build-lib=', None, "build directory for all distributions"),
        ('build-scripts=', None, "build directory for scripts"),
        ('build-temp=', 't', "temporary build directory"),
        ('build-l10n=', None, 'build directory for binary message catalogs'),
        ('compiler=', 'c', "specify the compiler type"),
        ('ldflags=', 'l', "specify additional linker options"),
        ('debug', 'g', "compile with debugging information"),
        ('force', 'f', "forcibly build everything (ignore file timestamps)"),
        ('with-docs', None, 'ignored; maintained for compatability'),
        ('without-docs', None, 'ignored; maintained for compatability'),
        ]

    boolean_options = ['debug', 'force', 'with-docs', 'without-docs']

    negative_opt = {'without-docs' : 'with-docs'}

    help_options = [
        ('help-compiler', None,
         "list available compilers", ccompiler.show_compilers),
        ]

    def initialize_options(self):
        self.build_base = 'build'
        self.build_lib = None
        self.build_temp = None
        self.build_scripts = None
        self.build_l10n = None
        self.compiler = None
        self.ldflags = None
        self.debug = None
        self.force = False
        self.with_docs = True
        self.plat_name = None
        return

    def finalize_options(self):
        self.set_undefined_options('config',
                                   ('compiler', 'compiler'),
                                   ('debug', 'debug'),
                                   ('plat_name', 'plat_name'))
        plat_build = '%s.' + self.plat_name + '-' + sys.version[:3]
        plat_build = os.path.join(self.build_base, plat_build)
        if self.debug:
            plat_build += '-debug'

        # platform specific (can contain extension modules)
        if self.build_lib is None:
            self.build_lib = plat_build % 'lib'

        # platform specific (compiler by-products)
        if self.build_temp is None:
            self.build_temp = plat_build % 'temp'

        # platform specific (can have real executables)
        if self.build_scripts is None:
            self.build_scripts = plat_build % 'scripts'

        # all platforms (no compiled objects)
        if self.build_l10n is None:
            self.build_l10n = os.path.join(self.build_base, 'locale')
        return

    def run(self):
        self.run_command('config')
        return build.build.run(self)

    # -- External interfaces -------------------------------------------

    def get_source_files(self):
        """
        Called by 'sdist' command.
        """
        files = []
        for cmd_name, predicate in self.sub_commands:
            cmd = self.get_finalized_command(cmd_name)
            files.extend(cmd.get_source_files())
        return files

    # -- Predicates for sub-command list -------------------------------

    def has_docs(self):
        return self.distribution.has_docs()

    def has_l10n(self):
        return self.distribution.has_l10n()

    # a list of commands this command might have to run to do its work.
    sub_commands = build.build.sub_commands + [
        ('build_l10n', has_l10n),
        ]
