########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/DistExt/InstallConfig.py,v 1.1 2006/08/12 15:56:24 jkloth Exp $
"""
distutils command for installing the configuration file.

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""
import os
from distutils.core import Command
from distutils.util import convert_path, subst_vars

from Ft.Lib.DistExt import Install

METADATA_KEYS = ('name', 'version', 'fullname', 'url')

CONFIG_KEYS = ('resourcebundle', 'pythonlibdir', 'bindir', 'datadir',
               'sysconfdir', 'localstatedir', 'libdir', 'localedir')

CONFIG_MAPPING = {
    'pythonlibdir'  : 'lib',
    'bindir'        : 'scripts',
    'datadir'       : 'data',
    'sysconfdir'    : 'sysconf',
    'localstatedir' : 'localstate',
    'libdir'        : 'devel',
    'localedir'     : 'l10n',
    }

CONFIG_STUB = """# Configuration variables
%(metadata)s

import sys
if getattr(sys, 'frozen', False):
    # "bundled" installation locations (e.g., py2exe, cx_Freeze)
    %(bundle_config)s
else:
    # standard distutils installation directories
    %(install_config)s
del sys
"""

class InstallConfig(Command):

    command_name = 'install_config'

    description = "install configuration file"

    user_options = [
        ('install-dir=', 'd', "directory to install to"),
        ]

    def initialize_options(self):
        self.install_dir = None
        return

    def finalize_options(self):
        self.set_undefined_options('install_lib',
                                   ('install_dir', 'install_dir'))
        if self.distribution.config_module:
            parts = self.distribution.config_module.split('.')
            basename = os.path.join(*parts) + '.py'
            self.config_filename = os.path.join(self.install_dir, basename)
        else:
            self.config_filename = None
        return

    def run(self):
        if not self.config_filename:
            return

        install = self.get_finalized_command('install')
        prefix_len = len(install.root or '')
        install_config = dict(install.config_vars)
        install_config['resourcebundle'] = install.scheme == 'zip'
        config_vars = CONFIG_MAPPING.values()
        for var in config_vars:
            command = 'install_' + var
            install_dir = self.get_finalized_command(command).install_dir
            if install_dir and prefix_len:
                install_dir = install_dir[prefix_len:]
            install_config[var] = install_dir

        self.announce('writing %s' % self.config_filename, 2)
        if not self.dry_run:
            f = open(self.config_filename, 'w')
            try:
                self.write_config_module(f, install_config)
            finally:
                f.close()
        return

    def write_config_module(self, file, install_config):
        """
        Write the configuration variables to a file object.
        """
        maxlen = max(map(len, METADATA_KEYS))
        lines = []
        for name in METADATA_KEYS:
            value = getattr(self.distribution, 'get_' + name)()
            lines.append('%-*s = %r' % (maxlen, name.upper(), value))
        metadata = '\n'.join(lines)

        maxlen = max(map(len, CONFIG_KEYS))
        lines = []
        for name in CONFIG_KEYS:
            value = install_config[CONFIG_MAPPING.get(name, name)]
            lines.append('%-*s = %r' % (maxlen, name.upper(), value))
        install_config = '\n    '.join(lines)

        lines = []
        bundle_config = Install.GetBundleScheme()
        bundle_config['resourcebundle'] = True
        for name in CONFIG_KEYS:
            value = bundle_config[CONFIG_MAPPING.get(name, name)]
            lines.append('%-*s = %r' % (maxlen, name.upper(), value))
        bundle_config = '\n    '.join(lines)

        file.write(CONFIG_STUB % {'metadata' : metadata,
                                  'bundle_config' : bundle_config,
                                  'install_config' : install_config,
                                  })
        return

    # -- Reporting methods ---------------------------------------------

    def get_source_files(self):
        return []

    def get_outputs(self):
        if self.config_filename:
            outputs = [self.config_filename]
        else:
            outputs = []
        return outputs
