import os, sys, re
import ConfigParser
from distutils.ccompiler import show_compilers
from distutils.core import Command, DEBUG
from distutils.errors import DistutilsOptionError, DistutilsPlatformError
from distutils import util, sysconfig

def get_python_lib(prefix):
    libdir = sysconfig.get_python_lib(prefix=prefix)
    if libdir not in sys.path:
        libdir = sysconfig.get_python_lib()
    return libdir

CONFIG_SCHEMES = {
    'fhs_local' : {
        'pythonlibdir'  : get_python_lib('/usr/local'),
        'includedir'    : '/usr/local/include/$name',
        'bindir'        : '/usr/local/bin',
        'datadir'       : '/usr/local/share/$name',
        'sysconfdir'    : '/usr/local/etc/$name',
        'localstatedir' : '/var/local/lib/$name',
        'libdir'        : '/usr/local/lib/$name',
        'docdir'        : '/usr/local/share/doc/$name',
        'localedir'     : '/usr/local/share/locale',
        'mandir'        : '/usr/local/share/man',
    },
    'fhs_system' : {
        'pythonlibdir'  : get_python_lib('/usr'),
        'includedir'    : '/usr/include/$name',
        'bindir'        : '/usr/bin',
        'datadir'       : '/usr/share/$name',
        'sysconfdir'    : '/etc/$name',
        'localstatedir' : '/var/lib/$name',
        'libdir'        : '/usr/lib/$name',
        'docdir'        : '/usr/share/doc/$name',
        'localedir'     : '/usr/share/locale',
        'mandir'        : '/usr/share/man',
        },
    'posix_autoconf' : {
        'pythonlibdir'  : sysconfig.get_python_lib(),
        'includedir'    : '$prefix/include/$name',
        'bindir'        : '$exec_prefix/bin',
        'datadir'       : '$prefix/share/$name',
        'sysconfdir'    : '$prefix/etc/$name',
        'localstatedir' : '$exec_prefix/var/$name',
        'libdir'        : '$exec_prefix/lib/$name',
        'docdir'        : '$prefix/share/doc/$name',
        'localedir'     : '$datadir/locale',
        'mandir'        : '$prefix/man',
        },
    'posix_home' : {
        'pythonlibdir'  : '$prefix/lib/python$python_version',
        'includedir'    : '$prefix/include/python$python_version/$name',
        'bindir'        : '$prefix/bin',
        'datadir'       : '$prefix/share/$name',
        'sysconfdir'    : '$prefix/share/etc/$name',
        'localstatedir' : '$prefix/share/var/$name',
        'libdir'        : '$prefix/lib/$name',
        'docdir'        : '$prefix/share/doc/$name',
        'localedir'     : '$prefix/share/locale',
        'mandir'        : '$prefix/share/man',
        },
    'nt' : {
        'pythonlibdir'  : '$prefix/Lib/site-packages',
        'includedir'    : '$prefix/Include/$name',
        'bindir'        : '$prefix/Scripts',
        'datadir'       : '$prefix/Share/$name',
        'sysconfdir'    : '$prefix/Share/Settings/$name',
        'localstatedir' : '$prefix/Share/$name',
        'libdir'        : '$prefix/Share/$name',
        'docdir'        : '$prefix/Share/Doc/$name',
        'localedir'     : '$prefix/Share/Locale',
        'mandir'        : '$prefix/Share/Help',
        },
    'other' : {
        'pythonlibdir'  : '$prefix/Lib/site-packages',
        'includedir'    : '$prefix/Include/$name',
        'bindir'        : '$prefix/Scripts',
        'datadir'       : '$prefix/Share/$name',
        'sysconfdir'    : '$prefix/Share/Settings/$name',
        'localstatedir' : '$prefix/Share/$name',
        'libdir'        : '$prefix/Share/$name',
        'docdir'        : '$prefix/Share/Doc/$name',
        'localedir'     : '$prefix/Share/Locale',
        'mandir'        : '$prefix/Share/Help',
        },
    }

CACHE_FILENAME = 'config.cache'

CONFIG_KEYS = ('prefix', 'exec_prefix', 'pythonlibdir', 'includedir',
               'bindir', 'datadir', 'sysconfdir', 'localstatedir', 'libdir',
               'docdir', 'localedir', 'mandir', 'compiler', 'debug')

class Config(Command):

    command_name = 'config'

    description = 'select installation scheme and base directories'

    user_options = [
        # All platforms support the 'prefix' installation scheme.
        ('prefix=', None,
         'Use POSIX autoconf-style or Windows installation scheme with this prefix'),
        ]

    # POSIX systems have additional scheme selectors.
    if os.name == 'posix':
        user_options.extend([
            ('exec-prefix=', None,
             'Prefix for platform-specific files (for use with --prefix)'),
            ('local', None,
             'Use FHS /usr/local installation scheme [default]'),
            ('system', None,
             'Use FHS /usr installation scheme (e.g. for RPM builds)'),
            ])

    user_options.extend([
        # All platforms also support the 'home' installation scheme.
        ('home=', None,
         'Use home directory installation scheme with this prefix'),
        # Fine-tuning of directories
        ('pythonlibdir=', None,
         'Directory for 3rd-party Python libraries (site-packages)'),
        ('includedir=', None,
         'Directory for C header files'),
        ('bindir=', None,
         'Directory for user executables'),
        ('datadir=', None,
         'Directory for read-only platform-independent data'),
        ('sysconfdir=', None,
         'Directory for read-only host-specific data'),
        ('localstatedir=', None,
         'Directory for modifiable host-specific data'),
        ('libdir=',None,
         'Directory for program & package libraries'),
        ('docdir=', None,
         'Directory for documentation files'),
        ('localedir=', None,
         'Directory for message catalogs'),
        ('mandir=', None,
         'Directory for man documentation'),

        # Compilation options
        ('compiler=', 'c',
         "specify the compiler type"),
        ('debug', 'g',
         "compile extensions and libraries with debugging information"),
        ('plat-name=', 'p',
         "target platform for compiling extensions and libraries"
         " (default: %s)" % util.get_platform()),
        ])

    boolean_options = ['local', 'system', 'debug']

    help_options = [
        ('help-compiler', None,
         "list available compilers", show_compilers),
        ]

    def initialize_options(self):
        self.cache_filename = CACHE_FILENAME
        self.scheme = None

        # User selectable Options
        self.local = None
        self.system = None
        self.home = None
        self.prefix = None
        self.exec_prefix = None

        self.pythonlibdir = None
        self.includedir = None
        self.bindir = None
        self.datadir = None
        self.sysconfdir = None
        self.localstatedir = None
        self.libdir = None
        self.docdir = None
        self.localedir = None
        self.mandir = None

        self.compiler = None
        self.debug = None
        self.plat_name = None
        return

    def finalize_options(self):
        if DEBUG: print "Config.finalize_options():"

        if self.debug is None:
            # sys.getobjects() is only defined in a debug build of Python
            self.debug = hasattr(sys, 'getobjects')

        if self.plat_name is None:
            self.plat_name = util.get_platform()

        cache_section = self.plat_name + '-' + sys.version[:3]
        if self.debug:
            cache_section += '-debug'

        if os.name == 'posix':
            self.finalize_posix()
        else:
            self.finalize_other()

        # Read the configuration cache to fill in values not already set.
        parser = ConfigParser.ConfigParser()
        if self.cache_filename and os.path.exists(self.cache_filename):
            if DEBUG: print "  reading", self.cache_filename
            fp = open(self.cache_filename, 'rb')
            parser.readfp(fp)
            fp.close()

        # Use the cached configuration only if the platform specific section
        # already exists in the cache (duh!) and no options have been
        # specified by the user.
        changed = False
        if not (parser.has_section(cache_section) and
                not (self.local or self.system or self.home or
                     filter(self.__dict__.get, CONFIG_KEYS))):
            # Fill in the cache with values from the scheme and options.
            if not parser.has_section(cache_section):
                parser.add_section(cache_section)

            # string values
            for key in ('prefix', 'exec_prefix', 'compiler'):
                value = getattr(self, key) or ''
                parser.set(cache_section, key, value)

            # boolean values
            for key in ('debug',):
                value = str(getattr(self, key))
                parser.set(cache_section, key, value)

            # Set the scheme directories from the options, or the default
            # value if not specified.
            scheme = CONFIG_SCHEMES[self.scheme]
            for key in scheme.keys():
                value = getattr(self, key)
                if value is None:
                    value = scheme[key]
                parser.set(cache_section, key, value)
            changed = True
        elif DEBUG:
            print '  using cached options'

        # string values
        for key in ('prefix', 'exec_prefix', 'compiler'):
            if parser.has_option(cache_section, key):
                value = parser.get(cache_section, key) or None
                setattr(self, key, value)
            else:
                value = getattr(self, key) or ''
                parser.set(cache_section, key, value)
                changed = True

        # boolean values
        for key in ('debug',):
            if parser.has_option(cache_section, key):
                value = eval(parser.get(cache_section, key))
                setattr(self, key, value)
            else:
                value = str(getattr(self, key))
                parser.set(cache_section, key, value)
                changed = True

        # directory scheme
        scheme = CONFIG_SCHEMES[self.scheme]
        for key in scheme.keys():
            if parser.has_option(cache_section, key):
                value = parser.get(cache_section, key) or None
                if value and key == 'docdir' and value.find('$fullname') >= 0:
                    value = value.replace('$fullname', '$name')
                    changed = True
                setattr(self, key, value)
            else:
                value = CONFIG_SCHEMES[self.scheme][key]
                parser.set(cache_section, key, value)
                changed = True

        # Save this configuration for next run
        if self.cache_filename and changed:
            if DEBUG:
                print '  writing', self.cache_filename
                print '    [%s]' % cache_section
                for name in CONFIG_KEYS:
                    value = parser.get(cache_section, name)
                    print '    %s = %s' % (name, value)

            fp = open(self.cache_filename, 'wb')
            parser.write(fp)
            fp.close()

        if self.prefix is None:
            self.prefix = sys.prefix

        self.finalize_config_vars()
        return

    def finalize_posix(self):
        # Only one of local/system/home/[prefix|exec-prefix] may be given
        # The easiest determine this is to just count the Nones
        specified_count = ((self.local is not None) +
                           (self.system is not None) +
                           (self.home is not None) +
                           ((self.prefix or self.exec_prefix) is not None))
        if specified_count > 1:
            raise DistutilsOptionError("only one of --local, --system, --home"
                                       " or --prefix/exec-prefix allowed")

        if self.local or not specified_count:
            self.scheme = 'fhs_local'
        elif self.system:
            self.scheme = 'fhs_system'
        elif self.home:
            self.prefix = self.exec_prefix = os.path.expanduser(self.home)
            self.scheme = 'posix_home'
        else:
            # Either self.prefix or self.exec_prefix is specified
            if self.exec_prefix is None:
                self.exec_prefix = self.prefix
            elif self.prefix is None:
                raise DistutilsOptionError, \
                      "must not supply exec-prefix without prefix"
            self.prefix = os.path.expanduser(self.prefix)
            self.exec_prefix = os.path.expanduser(self.exec_prefix)
            self.scheme = 'posix_autoconf'
        return

    def finalize_other(self):
        if self.local:
            self.warn("'--local' option ignored on this platform")
            self.local = None
        if self.system:
            self.warn("'--system' option ignored on this platform")
            self.system = None
        if self.exec_prefix:
            self.warn("'--exec-prefix' option ignored on this platform")
            self.exec_prefix = None
        if self.home:
            self.warn("'--home' option ignored on this platform")
            self.home = None

        if os.name == 'nt':
            self.scheme = 'nt'
        else:
            self.scheme = 'other'
        return

    def finalize_config_vars(self):
        # Expand configuration variables, tilde, etc.
        main_distribution = self.distribution.main_distribution
        if main_distribution is None:
            main_distribution = self.distribution
        self.config_vars = {
            'name' : main_distribution.get_name(),
            'version' : main_distribution.get_version(),
            'fullname' : main_distribution.get_fullname(),
            'python_version' : sys.version[:3],
            }
        for key in CONFIG_KEYS:
            value = getattr(self, key)
            # Distutils prior to Python 2.3 cannot handle empty strings
            # in the util.* functions.
            if isinstance(value, str) and value:
                if os.name == 'posix':
                    value = os.path.expanduser(value)
                value = util.convert_path(value)
                value = util.subst_vars(value, self.config_vars)
            self.config_vars[key] = value
        return self.config_vars

    def run(self):
        if DEBUG:
            print "Config.run():"
            for name in CONFIG_KEYS:
                print '   ', name, '=', getattr(self, name)
        return
