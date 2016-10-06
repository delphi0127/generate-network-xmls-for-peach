import os
import sys
import re
import copy
from distutils import util
from distutils.command import install
from distutils.core import DEBUG
from distutils.errors import DistutilsOptionError

from Ft.Lib.DistExt import Util

INSTALL_LOCATIONS = {
    'install_lib' : 'Python modules (including C extensions)',
    'install_headers' : 'C/C++ header files',
    'install_scripts' : 'Executable scripts (for PATH environment variable)',
    'install_data' : 'Examples, demos and other miscellaneous data files',
    'install_sysconf': 'Configuration files',
    'install_localstate' : 'Machine-specific variable data space',
    'install_devel' : 'Developer files (regression tests)',
    'install_text' : 'Text documentation',
    'install_l10n' : 'Natural language message catalogs',
    }

# Change the existing "installation schemes" by changing the 'install_data'
# location and adding locations for our additional commands.
INSTALL_SCHEMES = copy.deepcopy(install.INSTALL_SCHEMES)
INSTALL_SCHEMES['unix_prefix'].update({
    'data'       : '$base/share/$dist_name',
    'sysconf'    : '$base/etc/$dist_name',
    'localstate' : '$platbase/var/$dist_name',
    'devel'      : '$platbase/lib/$dist_name',
    'l10n'       : '$base/share/locale',
    'man'        : '$base/man',
    'docs'       : '$base/share/doc/$dist_name',
    })
# The "home" scheme is also updated to include the Python version in the
# 'install_lib' location.
INSTALL_SCHEMES['unix_home'].update({
    'purelib'    : '$base/lib/python$py_version_short',
    'platlib'    : '$base/lib/python$py_version_short',
    'data'       : '$base/share/$dist_name',
    'sysconf'    : '$base/share/etc/$dist_name',
    'localstate' : '$base/share/var/$dist_name',
    'devel'      : '$base/lib/$dist_name',
    'l10n'       : '$base/share/locale',
    'man'        : '$base/share/man',
    'docs'       : '$base/share/doc/$dist_name',
    })
# Update the "other" schemes
for name, scheme in INSTALL_SCHEMES.iteritems():
    if name in ('unix_prefix', 'unix_home'):
        continue
    scheme.update({
        'data'       : '$base/Share/$dist_name',
        'sysconf'    : '$base/Share/Settings/$dist_name',
        'localstate' : '$base/Share/$dist_name',
        'devel'      : '$base/Share/$dist_name',
        'l10n'       : '$base/Share/Locale',
        'man'        : '$base/Share/Help',
        'docs'       : '$base/Share/Doc/$dist_name',
        })
# Add the installation scheme for FHS "local" directories
INSTALL_SCHEMES['unix_local'] = {
    'purelib'    : '/usr/local/lib/python$py_version_short/site-packages',
    'platlib'    : '/usr/local/lib/python$py_version_short/site-packages',
    'headers'    : '/usr/local/include/$dist_name',
    'scripts'    : '/usr/local/bin',
    'data'       : '/usr/local/share/$dist_name',
    'sysconf'    : '/usr/local/etc/$dist_name',
    'localstate' : '/var/local/lib/$dist_name',
    'devel'      : '/usr/local/lib/$dist_name',
    'l10n'       : '/usr/local/share/locale',
    'man'        : '/usr/local/share/man',
    'docs'       : '/usr/local/share/doc/$dist_name',
    }
# Add the installation scheme for FHS "system" directories
INSTALL_SCHEMES['unix_system'] = {
    'purelib'    : '/usr/lib/python$py_version_short/site-packages',
    'platlib'    : '/usr/lib/python$py_version_short/site-packages',
    'headers'    : '/usr/include/$dist_name',
    'scripts'    : '/usr/bin',
    'data'       : '/usr/share/$dist_name',
    'sysconf'    : '/etc/$dist_name',
    'localstate' : '/var/lib/$dist_name',
    'devel'      : '/usr/lib/$dist_name',
    'l10n'       : '/usr/share/locale',
    'man'        : '/usr/share/man',
    'docs'       : '/usr/share/doc/$dist_name',
    }
# The scheme used when no installation scheme options are given. It uses the
# values set by the 'config' command.
INSTALL_SCHEMES['default'] = {
    'base'       : '$exec',
    'platbase'   : '$exec_prefix',
    'purelib'    : '$pythonlibdir',
    'platlib'    : '$pythonlibdir',
    'headers'    : '$includedir',
    'scripts'    : '$bindir',
    'data'       : '$datadir',
    'sysconf'    : '$sysconfdir',
    'localstate' : '$localstatedir',
    'devel'      : '$libdir',
    'l10n'       : '$localedir',
    'man'        : '$mandir',
    'docs'       : '$docdir',
    }
# A special scheme for ZIPs or Python Eggs (or anything using PEP 302
# import hooks); entries that are None indicate that they are unused
INSTALL_SCHEMES['zip'] = {
    'base'       : '',
    'platbase'   : '',
    'purelib'    : '$base',
    'platlib'    : '$base',
    'headers'    : None,
    'scripts'    : None,
    'data'       : '$base/Share',
    'sysconf'    : None,
    'localstate' : None,
    'devel'      : None,
    'l10n'       : '$base/Share/Locale',
    'man'        : None,
    'docs'       : None,
    }

SCHEME_KEYS = install.SCHEME_KEYS + (
    'sysconf', 'localstate', 'devel', 'l10n', 'man', 'docs')

def GetBundleScheme():
    scheme = INSTALL_SCHEMES['zip'].copy()
    scheme['base'] = scheme['platbase'] = os.sep
    for key in SCHEME_KEYS:
        value = scheme[key]
        if value:
            value = util.subst_vars(value, scheme)
            value = util.convert_path(value)
            pathname = os.sep.join([ path for path in value.split(os.sep)
                                     if path not in ('', '.') ])
            if value.startswith(os.sep):
                pathname = os.sep + pathname
            scheme[key] = pathname
    scheme['lib'] = scheme['purelib']
    return scheme

class Install(install.install):

    command_name = 'install'

    user_options = install.install.user_options + [
        ('with-docs', None, 'enable documentation install'),
        ('without-docs', None, 'disable documentation install'),
        ]

    # PKG-INFO is created for source distributions, so allow "developer"
    # friendly features to be enabled/disabled.
    index = -1 - int(os.path.exists('PKG-INFO'))
    user_options[index] = (user_options[index][0],
                           user_options[index][1],
                           user_options[index][2] + ' [default]')

    # inject the scheme selection options at an appropriate place
    index = 0
    while user_options[index][0] != 'exec-prefix=':
        index += 1
    if os.name == 'posix':
        user_options[index+1:index+1] = [
            ('local', None,
             '(Unix only) Use FHS /usr/local installation scheme [default]'),
            ('system', None,
             '(Unix only) Use FHS /usr system installation scheme'),
            ]
    else:
        del user_options[index]

    # inject the "install-XXX" options at an appropriate place
    index = len(user_options)
    while not user_options[index-1][0].startswith('install-'):
        index -= 1
    user_options[index:index] = [
        ('install-sysconf=', None,
         'installation directory for read-only host-specific data'),
        ('install-localstate=', None,
         'installation directory for modifiable host-specific data'),
        ('install-devel=', None,
         'installation directory for development files (regression tests)'),
        ('install-l10n=', None,
         'installation directory for message catalogs'),
        #('install-man=', None,
        # 'installation directory for Unix man pages'),
        ('install-docs=', None,
         'installation directory for documentation files'),
        #('install-info=', None,
        # 'installation directory for GNU info pages'),
        ]

    boolean_options = install.install.boolean_options + ['with-docs']
    if os.name == 'posix':
        boolean_options += ['local', 'system']

    negative_opt = install.install.negative_opt.copy()
    negative_opt['without-docs'] = 'with-docs'

    def initialize_options(self):
        install.install.initialize_options(self)
        self.local = None
        self.system = None
        self.install_sysconf = None
        self.install_localstate = None
        self.install_devel = None
        self.install_l10n = None
        self.install_man = None
        self.install_docs = None
        self.install_info = None
        self.with_docs = None

        # options not selectable from the command-line
        self.scheme = None
        self.no_report = None
        return

    def finalize_options(self):
        if self.scheme is None and (self.install_base is not None or
                                    self.install_platbase is not None):
            if ((self.install_lib is None and
                 self.install_purelib is None and
                 self.install_platlib is None) or
                self.install_headers is None or
                self.install_scripts is None or
                self.install_data is None):
                raise DistutilsOptionError, \
                      ("install-base or install-platbase supplied, but "
                      "installation scheme is incomplete")
            self.scheme = "custom"

        if self.with_docs is None:
            self.with_docs = self.distribution.source_package

        install.install.finalize_options(self)
        return

    if sys.version < '2.3':
        def dump_dirs(self, msg):
            if not DEBUG:
                return
            from distutils.fancy_getopt import longopt_xlate
            print msg + ":"
            for opt in self.user_options:
                opt_name = opt[0]
                if opt_name[-1] == "=":
                    opt_name = opt_name[0:-1]
                if opt_name in self.negative_opt:
                    opt_name = self.negative_opt[opt_name]
                    val = not getattr(self, opt_name.translate(longopt_xlate))
                else:
                    opt_name = opt_name.translate(longopt_xlate)
                    val = getattr(self, opt_name)
                print "  %s: %s" % (opt_name, val)


    def finalize_unix(self):
        # Only one of local, system, home, prefix/exec-prefix may be given
        # The easiest determine this is to just count the Nones
        if ((self.local is not None) + (self.system is not None) +
            (self.home is not None) +
            (self.prefix is not None or self.exec_prefix is not None)) > 1:
            raise DistutilsOptionError("only one of --local, --system, --home"
                                       " or --prefix/exec-prefix allowed")

        if self.scheme is not None:
            return
        elif self.local:
            self.install_base = self.install_platbase = '/usr/local'
            self.select_scheme('unix_local')
        elif self.system:
            self.install_base = self.install_platbase = '/usr'
            self.select_scheme('unix_system')
        elif self.home is not None or self.prefix is not None:
            install.install.finalize_unix(self)
        else:
            # use the directories defined by the 'config' command
            self.select_scheme('default')
        return

    def finalize_other(self):
        if self.scheme is not None:
            return
        elif self.home is not None or self.prefix is not None:
            install.install.finalize_other(self)
        else:
            # use the directories defined by the 'config' command
            self.select_scheme('default')
        return

    def get_scheme(self, name):
        return INSTALL_SCHEMES[name]

    def get_scheme_keys(self):
        return SCHEME_KEYS

    def select_scheme(self, name):
        scheme = self.get_scheme(name)
        for key in self.get_scheme_keys():
            attrname = 'install_' + key
            if getattr(self, attrname) is None:
                setattr(self, attrname, scheme[key])
        self.scheme = name
        return

    def expand_basedirs(self):
        dist = self.distribution.main_distribution
        if dist is not None:
            self.config_vars['dist_name'] = dist.get_name()
            self.config_vars['dist_version'] = dist.get_version()
            self.config_vars['dist_fullname'] = dist.get_fullname()
        config = self.get_finalized_command('config')
        self.config_vars.update(config.config_vars)
        return install.install.expand_basedirs(self)

    def expand_dirs(self):
        install.install.expand_dirs(self)
        self._expand_attrs(['install_sysconf',
                            'install_localstate',
                            'install_devel',
                            'install_l10n',
                            #'install_man',
                            'install_docs',
                            #'install_info',
                            ])

    def convert_paths(self, *names):
        extras = [ key for key in self.get_scheme_keys()
                   if key not in names ]
        names = [ name for name in list(names) + extras
                  if getattr(self, 'install_' + name) is not None ]
        return install.install.convert_paths(self, *names)

    def change_roots(self, *names):
        extras = [ key for key in self.get_scheme_keys()
                   if key not in names ]
        names = [ name for name in list(names) + extras
                  if getattr(self, 'install_' + name) is not None ]
        return install.install.change_roots(self, *names)

    def run(self):
        # Disable the standard warning so we can display it as part of the
        # installation report.
        warn_dir = self.warn_dir
        self.warn_dir = False

        install.install.run(self)

        # Restore the previous value
        self.warn_dir = warn_dir

        report = self.get_installation_report()
        if report:
            # level 3 is WARN, Distutils default level is 2 (INFO) so this
            # will still be displayed if '--quiet' is given.
            self.announce(report, 3)
        return

    def get_installation_report(self):
        lines = []

        # Only display the installation locations if installed from a source
        # distribution (aka "user mode").
        if self.distribution.source_package and not self.no_report:
            package = '%s version %s' % (self.distribution.get_name(),
                                         self.distribution.get_version())
            lines.extend(['-'*72,
                          '%s has been successfully installed!' % package,
                          ''])

            for cmd_name in self.get_sub_commands():
                try:
                    header = INSTALL_LOCATIONS[cmd_name]
                except KeyError:
                    # Unknown install command, skip it
                    continue

                cmd = self.distribution.get_command_obj(cmd_name)
                try:
                    install_dir = getattr(cmd, 'install_dir')
                except AttributeError:
                    install_dir = getattr(self, cmd_name)

                # Strip off trailing separator
                if install_dir.endswith(os.sep):
                    install_dir = install_dir[:-len(os.sep)]

                # Only output location if something is installed there
                if cmd.get_outputs():
                    lines.extend([header,
                                  ' '*4 + install_dir,
                                  ''])
        # Check if the Python library code is installed to a directory that
        # is on Python's search path.
        lib_dir = Util.NormalizePath(self.install_lib)
        sys_path = map(Util.NormalizePath, sys.path)
        if self.warn_dir and (lib_dir not in sys_path):
            lines.append("WARNING: The installation directory %r must be on"
                         " Python's search path (sys.path) --"
                         " This can be done by adding it to PYTHONPATH or by"
                         " modifying sys.path in your code." % self.install_lib)

        return '\n'.join(lines)

    # -- Reporting methods ---------------------------------------------

    def get_source_files(self):
        files = []
        for cmd_name in self.get_sub_commands():
            cmd = self.get_finalized_command(cmd_name)
            files.extend(cmd.get_source_files())
        return files

    # -- Predicates for sub-command list -------------------------------

    def has_sysconf(self):
        return self.distribution.has_sysconf()

    def has_localstate(self):
        return self.distribution.has_localstate()

    def has_text(self):
        return self.distribution.has_text()

    def has_docs(self):
        return self.with_docs and self.distribution.has_docs()

    def has_devel(self):
        return self.distribution.has_devel()

    def has_l10n(self):
        return self.distribution.has_l10n()

    def has_config(self):
        return self.distribution.config_module is not None

    # a list of commands this command might have to run to do its work.
    sub_commands = install.install.sub_commands + [
        ('install_sysconf', has_sysconf),
        ('install_localstate', has_localstate),
        ('install_devel', has_devel),
        #('install_man', has_scripts),
        ('install_text', has_text),
        #('install_info', has_docs),
        ('install_l10n', has_l10n),
        ('install_config', has_config),
        ]

    # Ensure that .egg-info files are provided for by the tool-chain.
    # (new in 2.5 or setuptools)
    if 'install_egg_info' not in dict(sub_commands):
        sub_commands.append(('install_egg_info', None))
