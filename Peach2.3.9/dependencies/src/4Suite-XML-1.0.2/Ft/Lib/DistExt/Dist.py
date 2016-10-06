import sys, os, warnings, email
from types import ClassType, ListType
from distutils import command, filelist, version
from distutils.cmd import Command
from distutils.core import Distribution, gen_usage, DEBUG
from distutils.errors import *
from distutils.fancy_getopt import FancyGetopt, wrap_text
try:
    from distutils import log
except ImportError:
    # Python 2.2; create an instance that has the module interface but acts
    # like the announce() methods in 2.2.
    class Log:
        verbose = 1
        def log(self, level, msg):
            if self.verbose >= level:
                print msg
                sys.stdout.flush()
        def set_verbosity(self, verbose):
            self.verbose = verbose
    log = Log()
else:
    if sys.version < '2.5':
        def _log(self, level, msg, args):
            if level >= self.threshold:
                if args:
                    msg %= args
                print msg
                sys.stdout.flush()
            return
        log.Log._log = _log
        del _log

from Ft.Lib import Terminfo
from Ft.Lib.DistExt import Version

# Our new Distribution class
class Dist(Distribution):
    """
    An enhanced version of core Distutils' Distribution class.

    Currently supported features, for *all* Python (2.2+) versions:
    (from Python 2.3+)
    download_url, classifiers - PEP 314 metadata fields

    (from Python 2.5+)
    install_egg_info command - for setuptools
    requires, provides, obsoletes - PEP 314 metadata fields

    (only available in 4Suite)
    requires_python - [PEP 345] a list of version restrictions for Python
    requires_external - [PEP 345] a list of external requirements
    command_mapping - maps command names to a module/class name that differs
                      from the actual command name
    """
    # 'command_mapping' maps command names to the module/class names
    command_mapping = {
        'config' : 'Config',

        'build' : 'Build',
        'build_py' : 'BuildPy',
        'build_ext' : 'BuildExt',
        'build_clib' : None,
        'build_scripts' : 'BuildScripts',
        'build_l10n' : 'BuildL10n',                     # only in 4Suite

        'clean' : None,

        'install' : 'Install',
        'install_lib' : 'InstallLib',
        'install_headers' : None,
        'install_scripts' : 'InstallScripts',
        'install_data' : 'InstallData',
        'install_egg_info' : 'InstallEggInfo',          # new in 2.5+
        'install_sysconf' : 'InstallSysconf',           # only in 4Suite
        'install_localstate' : 'InstallLocalState',     # only in 4Suite
        'install_devel' : 'InstallDevel',               # only in 4Suite
        #'install_man' : 'InstallMan',                   # only in 4Suite
        'install_text' : 'InstallText',                 # only in 4Suite
        #'install_info' : 'InstallInfo',                 # only in 4Suite
        'install_l10n' : 'InstallL10n',                 # only in 4Suite
        'install_config' : 'InstallConfig',             # only in 4Suite

        'sdist' : 'SDist',

        'register' : None,                              # new in 2.3+

        'bdist' : 'BDist',
        'bdist_dumb' : None,
        'bdist_rpm' : 'BDistRpm',
        'bdist_inno' : 'BDistInno',                     # only in 4Suite
        'bdist_msi' : None,                             # new in 2.5+
        'bdist_egg' : 'BDistEgg',

        'upload' : None,                                # new in 2.5+

        'generate' : 'Generate',                        # only in 4Suite
        'generate_bgen' : 'GenerateBisonGen',           # only in 4Suite
        'generate_l10n' : 'GenerateL10n',               # only in 4Suite

        }

    command_aliases = {
        'bdist_wininst' : 'bdist_inno',
        }

    standard_commands = ['config', 'build', 'clean', 'install', 'sdist',
                         'register', 'bdist', 'upload', 'generate']
    if sys.version < '2.5':
        standard_commands.remove('upload')
    if sys.version < '2.3':
        standard_commands.remove('register')

    # 'toplevel_options' desribes the command-line options that may be
    # supplied to the setup script prior to any actual command.
    toplevel_options = []

    # PKG-INFO is created for source distributions, so allow "developer"
    # friendly features to be enabled/disabled (i.e., install_docs)
    source_package = os.path.exists('PKG-INFO')
    if not source_package:
        toplevel_options.extend([
            ('source-package', 's',
             'run as if from a source dist (developer testing)'),
            ])

    def __init__(self, attrs):
        # Add our placeholders for arguments from setup()
        self.l10n = []
        self.doc_files = []
        self.bgen_files = []
        self.sysconf_files = []
        self.localstate_files = []
        self.devel_files = []

        # The module where configuration variables are written.
        # Used by the 'install_config' command.
        self.config_module = None

        # File in source tree that represents the software copyright.
        # Currently, only used by the 'bdist_inno' command.
        self.license_file = None

        # 'package' is the name of the subpackage.
        self.package = None

        # File in source tree that contains the setup attributes for the
        # subpackage.
        self.package_file = None
        self.main_distribution = None

        # Used for gathering and validating the files included in a source
        # distribution. Used by the 'sdist' command.
        self.manifest_templates = []
        self.validate_templates = []

        # Add support for build_py's 'package_data'. New in Python 2.4+
        self.package_data = {}

        # 'namespace_packages' is a list of package names whose contents are
        # split across multiple distributions.
        self.namespace_packages = None
        Distribution.__init__(self, attrs)
        return

    def get_allfiles(self):
        if self._allfiles is None:
            # If a "main" distribution exists, use its files to prevent
            # unnecessary additional searches.
            if self.main_distribution:
                self._allfiles = self.main_distribution.get_allfiles()
            else:
                source_list = filelist.FileList()
                source_list.extend(filelist.findall())
                # Remove files that don't really belong in the file list.
                # Note the leading slash (\) before os.sep substitutions. It is
                # needed to prevent regex-escaping when os.sep is '\' (Windows).
                exclude_patterns = (
                    # revision control (CVS client) files
                    r'\%s?CVS(\.sandboxinfo)?\%s' % (os.sep, os.sep),
                    r'\.cvsignore$',
                    r'\.#[^\%s]+$' % os.sep,
                    # (X)Emacs temporary files
                    r'\.?#[^\%s]+#$' % os.sep,
                    # common editor backup files
                    r'[^\%s]+~$' % os.sep,
                    # python bytecode files
                    r'\.py[co]$',
                    )
                for pattern in exclude_patterns:
                    source_list.exclude_pattern(pattern, is_regex=True)
                self._allfiles = source_list.files
        return self._allfiles

    def get_source_files(self):
        source_list = filelist.FileList()
        source_list.set_allfiles(self.get_allfiles())

        # Add the files used to create the Distribution
        source_list.append(self.script_name)
        if os.path.exists('setup.cfg'):
            source_list.append('setup.cfg')
        if self.package_file:
            source_list.append(self.package_file)

        # Get the source files from the command groupds
        for cmd_name in ('generate', 'build', 'install'):
            cmd = self.get_command_obj(cmd_name)
            cmd.ensure_finalized()
            source_list.extend(cmd.get_source_files())
        # 'license_file' is used by bdist_inno
        if self.license_file:
            source_list.append(self.license_file)

        # Add the files not included by the commands
        for line in self.manifest_templates:
            try:
                source_list.process_template_line(line)
            except DistutilsTemplateError, msg:
                self.warn(str(msg))

        # File list now complete -- sort it so that higher-level files
        # come first
        source_list.sort()

        # Remove duplicates from the file list
        source_list.remove_duplicates()

        return source_list.files

    # -- Config file finding/parsing methods ---------------------------

    if sys.version < '2.4':
        def parse_config_files(self, filenames=None):
            Distribution.parse_config_files(self, filenames)
            if 'global' in self.command_options:
                global_options = self.command_options['global']
                boolean_options = {'verbose':1, 'dry_run':1}
                boolean_options.update(self.negative_opt)
                for opt in global_options:
                    if opt not in boolean_options:
                        setattr(self, opt, global_options[opt][1])
            return
    # -- Command-line parsing methods ----------------------------------

    if sys.version < '2.4':
        def parse_command_line(self):
            """Parse the setup script's command line, taken from the
            'script_args' instance attribute (which defaults to 'sys.argv[1:]'
            -- see 'setup()' in core.py).  This list is first processed for
            "global options" -- options that set attributes of the Distribution
            instance.  Then, it is alternately scanned for Distutils commands
            and options for that command.  Each new command terminates the
            options for the previous command.  The allowed options for a
            command are determined by the 'user_options' attribute of the
            command class -- thus, we have to be able to load command classes
            in order to parse the command line.  Any error in that 'options'
            attribute raises DistutilsGetoptError; any error on the
            command-line raises DistutilsArgError.  If no Distutils commands
            were found on the command line, raises DistutilsArgError.  Return
            true if command-line was successfully parsed and we should carry
            on with executing commands; false if no errors but we shouldn't
            execute commands (currently, this only happens if user asks for
            help).
            """
            #
            # We now have enough information to show the Macintosh dialog
            # that allows the user to interactively specify the "command line".
            #
            toplevel_options = self._get_toplevel_options()
            if sys.platform == 'mac':
                import EasyDialogs
                cmdlist = self.get_command_list()
                self.script_args = EasyDialogs.GetArgv(
                    toplevel_options + self.display_options, cmdlist)

            # We have to parse the command line a bit at a time -- global
            # options, then the first command, then its options, and so on --
            # because each command will be handled by a different class, and
            # the options that are valid for a particular class aren't known
            # until we have loaded the command class, which doesn't happen
            # until we know what the command is.

            self.commands = []
            parser = FancyGetopt(toplevel_options + self.display_options)
            parser.set_negative_aliases(self.negative_opt)
            parser.set_aliases({'licence': 'license'})
            args = parser.getopt(args=self.script_args, object=self)
            option_order = parser.get_option_order()
            log.set_verbosity(self.verbose)

            # for display options we return immediately
            if self.handle_display_options(option_order):
                return

            while args:
                args = self._parse_command_opts(parser, args)
                if args is None:            # user asked for help (and got it)
                    return

            # Handle the cases of --help as a "global" option, ie.
            # "setup.py --help" and "setup.py --help command ...".  For the
            # former, we show global options (--verbose, --dry-run, etc.)
            # and display-only options (--name, --version, etc.); for the
            # latter, we omit the display-only options and show help for
            # each command listed on the command line.
            if self.help:
                self._show_help(parser,
                                display_options=len(self.commands) == 0,
                                commands=self.commands)
                return

            # Oops, no commands found -- an end-user error
            if not self.commands:
                raise DistutilsArgError, "no commands supplied"

            # All is well: return true
            return 1

    def _get_toplevel_options(self):
        """Return the non-display options recognized at the top level.

        This includes options that are recognized *only* at the top
        level as well as options recognized for commands.
        """
        if sys.version < '2.4':
            toplevel_options = self.global_options
        else:
            toplevel_options = Distribution._get_toplevel_options(self)
        return toplevel_options + self.toplevel_options

    def finalize_options(self):
        if sys.version < '2.5':
            # Run the setter functions for the metadata fields that have them.
            # Only those fields that have a supplied value (not None) will
            # be considered.
            for name, value in vars(self.metadata).items():
                if value is not None:
                    try:
                        setter = getattr(self.metadata, 'set_' + name)
                    except AttributeError:
                        pass
                    else:
                        setter(value)

        requires_python = self.get_requires_python()
        if requires_python:
            requires_python = 'Python (%s)' % ', '.join(requires_python)
            requires_python = Version.VersionPredicate(requires_python)
            python_version = version.StrictVersion()
            python_version.version = sys.version_info[:3]
            python_version.prerelease = sys.version_info[3:]
            if not requires_python.satisfied_by(python_version):
                raise DistutilsSetupError(
                    "%s requires %s" % (self.metadata.name, requires_python))

        # Initialize the containter type data variables before dealing
        # with the information from the package defintions.
        if self.packages is None:
            self.packages = []
        if self.package_dir is None:
            self.package_dir = {}
        if self.py_modules is None:
            self.py_modules = []
        if self.libraries is None:
            self.libraries = []
        if self.headers is None:
            self.headers = []
        if self.ext_modules is None:
            self.ext_modules = []
        if self.include_dirs is None:
            self.include_dirs = []
        if self.scripts is None:
            self.scripts = []
        if self.data_files is None:
            self.data_files = []
        if self.package_file is None:
            self.package_file = self.script_name
        if self.namespace_packages is None:
            self.namespace_packages = []

        # Per PEP 314, only use License and Platform if they can't be
        # handled by an appropriate classifier. Or, in our case, aren't
        # being handled by a classifier entry.
        has_platform = has_license = False
        for classifier in self.get_classifiers():
            category = classifier.split('::', 1)[0]
            category = category.strip().title()
            if category == 'Operating System':
                has_platform = True
            elif category == 'License':
                has_license = True

        if self.metadata.license and has_license:
            raise DistutilsSetupError("license keyword conflicts with"
                                      " classifiers list")

        if self.metadata.platforms and has_platform:
            raise DistutilsSetupError("platforms keyword conflicts with"
                                      " classifiers list")

        # Finalize "private" variables; those that are not part of the
        # setup arguments.
        self._allfiles = None

        Distribution.finalize_options(self)

    def print_commands(self):
        """
        Overridden to add the commands defined by 'command_mapping' to the
        list of "standard commands".
        """
        std_commands = []
        is_std = {}
        for command in self.standard_commands:
            std_commands.append(command)
            is_std[command] = True
            klass = self.get_command_class(command)
            for command, method in klass.sub_commands:
                std_commands.append(command)
                is_std[command] = True

        extra_commands = []
        for command in self.cmdclass:
            if command not in is_std:
                extra_commands.append(command)

        max_length = max(map(len, (std_commands + extra_commands)))

        self.print_command_list(std_commands, "Standard commands", max_length)

        if extra_commands:
            print
            self.print_command_list(extra_commands, "Extra commands",
                                    max_length)
        return

    def get_command_list(self):
        """
        Overridden to add the commands defined by 'command_mapping' to the
        list of (command, description) tuples.
        """
        for command in self.command_mapping:
            self.get_command_class(command)
        return Distribution.get_command_list(self)

    def print_option_list(self, options, header, max_length):
        # Generate lines of help text.
        line_width = Terminfo.GetColumns()
        opt_width = max_length + 2 + 2 + 2  # room for indent + dashes + gutter
        text_width = line_width - opt_width
        big_indent = ' ' * opt_width

        print header

        for option in options:
            long, short, help = option[:3]
            if long[-1] == '=':
                long = long[0:-1]

            # Case 1: no short option at all
            if short is None:
                opt_names = long

            # Case 2: we have a short option, so we have to include it
            # just after the long option
            else:
                opt_names = "%s (-%s)" % (long, short)

            text = wrap_text(help, text_width)
            if text:
                print "  --%-*s  %s" % (max_length, opt_names, text[0])
                for line in text[1:]:
                    print big_indent + line
            else:
                print "  --%-*s" % (max_length, opt_names)

        print
        return

    def _show_help (self, parser, global_options=1, display_options=1,
                    commands=[]):
        # Gather the options for the distribution
        options = []
        if global_options:
            if display_options:
                global_options = self._get_toplevel_options()
            else:
                global_options = self.global_options
            options.extend(global_options)

        if display_options:
            display_options = self.display_options
            options.extend(display_options)

        # Gather the options for the requested commands
        commands = []
        for command in self.commands:
            klass = self.get_command_class(command)
            command_name = getattr(klass, 'command_name', klass.__name__)
            command_options = klass.user_options
            if hasattr(klass, 'help_options'):
                command_options = command_options + klass.help_options
            commands.append((command_name, command_options))
            options.extend(command_options)

        # Determine maximum length of option names
        max_length = 0
        for option in options:
            long = option[0]
            short = option[1]
            l = len(long)
            if long[-1] == '=':
                l = l - 1
            if short is not None:
                l = l + 5                   # " (-x)" where short == 'x'
            if l > max_length:
                max_length = l

        # Now print the option tables
        if global_options:
            self.print_option_list(global_options, "Global options:",
                                   max_length)

        if display_options:
            self.print_option_list(display_options,
                                   "Information display options (just display"
                                   " information, ignore any commands):",
                                   max_length)

        for name, options in commands:
            self.print_option_list(options,
                                   "Options for '%s' command:" % name,
                                   max_length)

        print gen_usage(self.script_name)
        return

    # -- Command class/object methods ----------------------------------

    def get_command_class(self, command):
        """
        Extends Distribution.get_command_class() to search 'command_mapping'
        for modules that implement that requested command.
        """
        # Try user defined classes first (and already loaded classes)
        klass = self.cmdclass.get(command)
        if klass:
            return klass

        if command in self.command_aliases:
            command = self.command_aliases[command]

        base_name = self.command_mapping.get(command)
        if base_name is None:
            return Distribution.get_command_class(self, command)

        command_package = 'Ft.Lib.DistExt'
        module_name = command_package + '.' + base_name
        klass_name = base_name
        try:
            module = __import__(module_name, {}, {}, [klass_name])
        except ImportError:
            # If the module exists but is just broken, re-raise the existing
            # exception as this is (most likely) a developer error.
            if sys.exc_info()[-1].tb_next is not None:
                raise
            raise DistutilsModuleError(
                "invalid command '%s' (no module named '%s')" %
                (command, module_name))

        try:
            klass = getattr(module, klass_name)
        except AttributeError:
            raise DistutilsModuleError(
                "invalid command '%s' (no class '%s' in module '%s')" %
                (command, klass_name, module_name))

        # Make sure that the command provides the proper command name
        try:
            if command != klass.command_name:
                raise AttributeError('command_name')
        except AttributeError:
            raise DistutilsClassError(
                "command class %s must define 'command_name' as %r" %
                (klass, command))

        self.cmdclass[command] = klass
        return klass

    # -- Methods that operate on the Distribution ----------------------

    def announce (self, msg, level=1):
        """If the current verbosity level is of greater than or equal to
        'level' print 'msg' to stdout.
        """
        log.log(level, msg)

    # -- Distribution query methods ------------------------------------

    def has_l10n(self):
        # Used for both build and generate
        return len(self.l10n) > 0

    def has_sysconf(self):
        # Used for install
        return len(self.sysconf_files) > 0

    def has_localstate(self):
        # Used for install
        return len(self.localstate_files) > 0

    def has_docs(self):
        # Used for both build and install
        # Both scripts and modules have generated documentation
        return (len(self.doc_files) > 0 or
                self.has_modules() or self.has_scripts())

    def has_text(self):
        return self.license_file is not None or len(self.doc_files) > 0

    def has_devel(self):
        # Used for install
        return len(self.devel_files) > 0

    def has_bgen(self):
        # Used for both sdist and generate
        return self.bgen_files and len(self.bgen_files) > 0

# ----------------------------------------------------------------------
# Upgade distutils core support to 2.5+ features

import re, operator
from distutils import dist
from distutils.util import rfc822_escape

class DistributionMetadata(dist.DistributionMetadata):

    _METHOD_BASENAMES = dist.DistributionMetadata._METHOD_BASENAMES + (
        'requires_python', 'requires_external')

    requires_python = None
    requires_external = None
    copyright = None

    def get_requires_python(self):
        return self.requires_python or []

    def set_requires_python(self, value):
        if not isinstance(value, list):
            value = [ v.strip() for v in value.split(',') ]
        for v in value:
            Version.SplitComparison(v)
        self.requires_python = value

    def get_requires_external(self):
        return self.requires_external or []

    def set_requires_external(self, value):
        for v in value:
            Version.SplitComparison(v)
        self.requires_external = value

    if sys.version < '2.5':
        requires = None
        provides = None
        obsoletes = None

        _METHOD_BASENAMES += ('requires', 'provides', 'obsoletes')

        def get_requires(self):
            return self.requires or []

        def set_requires(self, value):
            for v in value:
                Version.VersionPredicate(v)
            self.requires = value

        def get_provides(self):
            return self.provides or []

        def set_provides(self, value):
            for v in value:
                Version.SplitProvision(v)
            self.provides = value

        def get_obsoletes(self):
            return self.obsoletes or []

        def set_obsoletes(self, value):
            for v in value:
                Version.VersionPredicate(v)
            self.obsoletes = value

        def write_pkg_info(self, base_dir):
            """
            Write the PKG-INFO file into the release tree.
            """
            pkg_info = open(os.path.join(base_dir, 'PKG-INFO'), 'w')
            self.write_pkg_file(pkg_info)
            pkg_info.close()

    if sys.version < '2.3':
        classifiers = None
        download_url = None

        _METHOD_BASENAMES += ('classifiers', 'download_url')

        def get_classifiers(self):
            return self.classifiers or []

        def get_download_url(self):
            return self.download_url or "UNKNOWN"

    # -- PKG-INFO and .egg-info utility methods --------------------

    def from_stream(cls, stream):
        headers = email.message_from_file(stream)
        fields = {}
        for header, value in headers.items():
            # clean up the keys and values, normalise "-" to "_"
            field = header.lower().replace('-', '_')
            value = value.strip()

            # Platform, Classifiers, Requires, Provides, Obsoletes,
            # Requires-External
            if field in fields:
                old = fields[field]
                if isinstance(old, list):
                    old.append(value)
                else:
                    fields[field] = [old, value]
            else:
                fields[field] = value

        # remove fields only needed for the Python Package Index
        for field in ('metadata_version', 'target_version'):
            if field in fields:
                del fields[field]

        # convert comma-separated items into lists
        for field in ('keywords', 'requires_python'):
            if field in fields:
                values = fields[field].split(',')
                values = [ value.strip() for value in values ]
                fields[field] = [ value for value in values if value ]

        # ensure multiple-use fields are lists
        for field in ('platform', 'classifier', 'requires', 'provides',
                     'obsoletes', 'requires_external'):
            if field in fields:
                value = fields[field]
                if not isinstance(value, list):
                    fields[field] = [value]

        # convert PKG-INFO field names to the corresponding metadata names
        for field, attr in (('platform', 'platforms'),
                            ('classifier', 'classifiers'),
                            ('home_page', 'url'),
                            ('summary', 'description'),
                            ):
            if field in fields:
                fields[attr] = fields[field]
                del fields[field]

        self = cls()
        for name, value in fields.items():
            if hasattr(self, 'set_' + name):
                getattr(self, 'set_' + name)(value)
            elif hasattr(self, name):
                setattr(self, name, value)
            else:
                warnings.warn("unknown metadata attribute: %s" % name)
        return self
    from_stream = classmethod(from_stream)

    def from_string(cls, string):
        from cStringIO import StringIO
        return cls.from_stream(StringIO(string))
    from_string = classmethod(from_string)

    def from_filename(cls, filename):
        fp = open(filename)
        try:
            return cls.from_stream(fp)
        finally:
            fp.close()
    from_filename = classmethod(from_filename)

    def write_pkg_file(self, file):
        """
        Write the PKG-INFO format data to a file object.

        Supports metadata version 1.2 (PEP 345), 1.1 (PEP 314) and
        1.0 (PEP 241) in a lowest common denominator fashion.
        """
        # Use lowest possible version for metadata version
        if self.requires_python or self.requires_external:
            # PEP 345 fields
            version = '1.2'
        elif (self.download_url or self.classifiers or
              self.provides or self.requires or self.obsoletes):
            # PEP 314 fields
            version = '1.1'
        else:
            # PEP 241 fields
            version = '1.0'
        file.write('Metadata-Version: %s\n' % version)

        # PEP 241 (http://python.org/dev/peps/pep-0241.html) fields:
        #   Name
        #   Version
        #   Platform (multiple use)     [obsolete]
        #   Summary
        #   Description (optional)
        #   Keywords (comma-separated list, optional)
        #   Home-page (optional)
        #   Author (optional)
        #   Author-email
        #   License                     [obsolete]
        file.write('Name: %s\n' % self.get_name() )
        file.write('Version: %s\n' % self.get_version() )
        file.write('Summary: %s\n' % self.get_description() )
        file.write('Home-page: %s\n' % self.get_url() )
        file.write('Author: %s\n' % self.get_contact() )
        file.write('Author-email: %s\n' % self.get_contact_email() )

        if self.long_description:
            description = rfc822_escape(self.long_description)
            file.write('Description: %s\n' % description)

        if self.keywords:
            keywords = ','.join(self.keywords)
            file.write('Keywords: %s\n' % keywords)

        # Per PEP 314, only use License and Platform if they can't be
        # handled by an appropriate classifier. Or, in our case, aren't
        # being handled by a classifier entry.
        has_platform = has_license = False
        for classifier in self.get_classifiers():
            category = classifier.split('::', 1)[0]
            category = category.strip().title()
            if category == 'Operating System':
                has_platform = True
            elif category == 'License':
                has_license = True

        if self.license:
            if has_license:
                raise DistutilsSetupError("license keyword conflicts with"
                                          " classifiers list")
            file.write('License: %s\n' % self.license)

        if self.platforms:
            if has_platform:
                raise DistutilsSetupError("platforms keyword conflicts with"
                                          " classifiers list")
            for platform in self.platforms:
                file.write('Platform: %s\n' % platform)

        # PEP 314 (http://python.org/dev/peps/pep-0314.html) fields:
        #   Supported-Platform (multiple use) [binary dists only; unused]
        #   Download-URL
        #   Classifier (multiple use)
        #   Requires (multiple use)
        #   Provides (multiple use)
        #   Obsoletes (multiple use)
        if self.download_url:
            file.write('Download-URL: %s\n' % self.get_download_url())
        for value in self.get_classifiers():
            file.write('Classifier: %s\n' % value)
        for value in self.get_requires():
            file.write('Requires: %s\n' % value)
        for value in self.get_provides():
            file.write('Provides: %s\n' % value)
        for value in self.get_obsoletes():
            file.write('Obsoletes: %s\n' % value)

        # PEP 345 (http://python.org/dev/peps/pep-0345.html) fields:
        #   Requires-Python (comma separated list)
        #   Requires-External (multiple use)
        #   Copyright
        if self.requires_python:
            value = ','.join(self.get_requires_python())
            file.write('Requires-Python: %s\n' % value)
        for value in self.get_requires_external():
            file.write('Requires-External: %s\n' % value)
        if self.copyright:
            file.write('Copyright: %s\n' % self.copyright)
        return

# Unfortunately, this is the only way to supply a different metadata class
dist.DistributionMetadata = DistributionMetadata
