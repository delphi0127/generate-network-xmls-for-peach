"""distutils.command.install_egg_info

Implements the Distutils 'install_egg_info' command, for installing
a package's PKG-INFO metadata."""


from distutils.cmd import Command
from distutils import dir_util
import os, sys, re

class InstallEggInfo(Command):
    """Install an .egg-info file for the package"""

    command_name = 'install_egg_info'

    description = "Install package's PKG-INFO metadata as an .egg-info file"
    user_options = [
        ('install-dir=', 'd', "directory to install to"),
    ]

    def initialize_options(self):
        self.install_dir = None

    def finalize_options(self):
        self.set_undefined_options('install_lib',
                                   ('install_dir', 'install_dir'))
        basename = "%s-%s-py%s.egg-info" % (
            to_filename(safe_name(self.distribution.get_name())),
            to_filename(safe_version(self.distribution.get_version())),
            sys.version[:3]
        )
        self.egginfo_filename = os.path.join(self.install_dir, basename)

    def run(self):
        target = self.egginfo_filename
        if os.path.isdir(target) and not os.path.islink(target):
            dir_util.remove_tree(target, dry_run=self.dry_run)

        self.announce("writing '%s'" % target, 2)
        if not self.dry_run:
            f = open(target, 'w')
            try:
                self.distribution.metadata.write_pkg_file(f)
            finally:
                f.close()
        return

    # -- Reporting methods ---------------------------------------------

    def get_source_files(self):
        return []

    def get_outputs(self):
        return [self.egginfo_filename]


# The following routines are taken from setuptools' pkg_resources module and
# can be replaced by importing them from pkg_resources once it is included
# in the stdlib.

def safe_name(name):
    """Convert an arbitrary string to a standard distribution name

    Any runs of non-alphanumeric/. characters are replaced with a single '-'.
    """
    return re.sub('[^A-Za-z0-9.]+', '-', name)


def safe_version(version):
    """Convert an arbitrary string to a standard version string

    Spaces become dots, and all other non-alphanumeric characters become
    dashes, with runs of multiple dashes condensed to a single dash.
    """
    version = version.replace(' ','.')
    return re.sub('[^A-Za-z0-9.]+', '-', version)


def to_filename(name):
    """Convert a project or version name to its filename-escaped form

    Any '-' characters are currently replaced with '_'.
    """
    return name.replace('-','_')
