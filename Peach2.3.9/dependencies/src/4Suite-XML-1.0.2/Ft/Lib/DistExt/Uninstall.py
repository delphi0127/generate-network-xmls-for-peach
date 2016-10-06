import os, sys, string, shutil, glob, tempfile
from distutils import filelist, util
from distutils.core import Command
from distutils.dep_util import newer
from types import *


class Uninstall(Command):

    description = "uninstall the package"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass
        
    def run(self):

        # Execute build
        self.announce('determining installation files')
        orig_dry_run = self.distribution.dry_run
        orig_verbose = self.distribution.verbose
        self.distribution.dry_run = 0
        self.distribution.verbose = 0
        self.run_command('build')

        # Execute install in dry-run mode
        self.distribution.dry_run = 1
        self.run_command('install')
        self.distribution.dry_run = orig_dry_run
        self.distribution.verbose = orig_verbose
        build = self.get_finalized_command('build')
        install = self.get_finalized_command('install')

        # Directories that should not be removed
        # install_headers is skipped because is uses $dist_name
        root_dirs = [install.install_purelib,
                     install.install_platlib,
                     install.install_scripts,
                     install.install_data,
                     ]

        # Remove all installed files
        self.announce("removing files")
        dirs = {}
        filenames = install.get_outputs()
        for filename in filenames:
            if not os.path.isabs(filename):
                raise DistutilsError,\
                      'filename "%s" from .get_output() not absolute' % \
                      filename

            if os.path.isfile(filename):
                self.announce("removing '%s'" % filename)
                if not self.dry_run:
                    try:
                        os.remove(filename)
                    except OSError, details:
                        self.warn("Could not remove file: %s" % details)
                    dir = os.path.split(filename)[0]
                    if not dirs.has_key(dir):
                        dirs[dir] = 1
                    if os.path.splitext(filename)[1] == '.py':
                        # Try and remove the .pyc if not already in the list
                        if filename+'c' not in filenames:
                            try:
                                os.remove(filename + 'c')
                            except OSError:
                                pass

                        # Try and remove the .pyo if not already in the list
                        if filename+'o' not in filenames:
                            try:
                                os.remove(filename + 'o')
                            except OSError:
                                pass

            elif os.path.isdir(filename):
                if not dirs.has_key(dir):
                    dirs[filename] = 1

            else:
                self.announce("skipping removal of '%s' (not found)" %
                              filename)

        # Remove the installation directories
        self.announce("removing directories")
        dirs = dirs.keys()
        dirs.sort(); dirs.reverse() # sort descending
        for dir in dirs:
            if dir in root_dirs:
                # A base directory that shouldn't be removed
                continue
            self.announce("removing directory '%s'" % dir)
            if not self.dry_run:
                if os.listdir(dir):
                    self.warn("skipping removal of '%s' (not empty)" % dir)
                else:
                    try:
                        os.rmdir(dir)
                    except OSError, details:
                        self.warn("could not remove directory: %s" % details)
        return
