import os, glob
from types import ListType
from distutils.command import bdist_rpm
from distutils.core import DEBUG
from distutils.file_util import write_file
from distutils.spawn import find_executable

# Python 2.3+ feature
try:
    enumerate
except NameError:
    enumerate = lambda it: zip(xrange(len(it)), it)

class BDistRpm(bdist_rpm.bdist_rpm):

    command_name = 'bdist_rpm'

    # insert the 'patch_files' options in the appropriate place in the
    # option map (to keep --help sane-looking)
    user_options = [ opt[0] for opt in bdist_rpm.bdist_rpm.user_options ]
    index = user_options.index('doc-files=')
    user_options = bdist_rpm.bdist_rpm.user_options[:]
    user_options.insert(index, ('patch-files=', None,
                                'list of patches (space or comma-separated)'))
    del index

    def initialize_options(self):
        bdist_rpm.bdist_rpm.initialize_options(self)
        self.patch_files = []
        self.keep_temp = None
        return

    def finalize_options(self):
        self.set_undefined_options('bdist', ('keep_temp', 'keep_temp'))
        bdist_rpm.bdist_rpm.finalize_options(self)
        return

    def finalize_package_data(self):
        bdist_rpm.bdist_rpm.finalize_package_data(self)
        self.ensure_string_list('patch_files')
        return

    def run (self):

        if DEBUG:
            print "before _get_package_data():"
            print "vendor =", self.vendor
            print "packager =", self.packager
            print "doc_files =", self.doc_files
            print "changelog =", self.changelog

        # make directories
        if self.spec_only:
            spec_dir = self.dist_dir
            self.mkpath(spec_dir)
        else:
            rpm_dir = {}
            for d in ('SOURCES', 'SPECS', 'BUILD', 'RPMS', 'SRPMS'):
                rpm_dir[d] = os.path.join(self.rpm_base, d)
                self.mkpath(rpm_dir[d])
            spec_dir = rpm_dir['SPECS']

        # Spec file goes into 'dist_dir' if '--spec-only specified',
        # build/rpm.<plat> otherwise.
        spec_path = os.path.join(spec_dir,
                                 "%s.spec" % self.distribution.get_name())
        self.execute(write_file,
                     (spec_path,
                      self._make_spec_file()),
                     "writing '%s'" % spec_path)

        if self.spec_only: # stop if requested
            return

        # Make a source distribution and copy to SOURCES directory with
        # optional icon.
        sdist = self.reinitialize_command('sdist')
        if self.use_bzip2:
            sdist.formats = ['bztar']
        else:
            sdist.formats = ['gztar']
        self.run_command('sdist')

        source = sdist.get_archive_files()[0]
        source_dir = rpm_dir['SOURCES']
        self.copy_file(source, source_dir)

        # Add any user-defined patches
        for patch in self.patch_files:
            self.copy_file(patch, source_dir)

        if self.icon:
            if os.path.exists(self.icon):
                self.copy_file(self.icon, source_dir)
            else:
                raise DistutilsFileError, \
                      "icon file '%s' does not exist" % self.icon


        # build package
        self.announce("building RPMs")

        if find_executable('rpmbuild'):
            rpm_cmd = ['rpmbuild']
        else:
            rpm_cmd = ['rpm']

        if self.source_only: # what kind of RPMs?
            rpm_cmd.append('-bs')
        elif self.binary_only:
            rpm_cmd.append('-bb')
        else:
            rpm_cmd.append('-ba')

        if self.rpm3_mode:
            rpm_cmd.extend(['--define',
                            '_topdir %s/%s' % (os.getcwd(), self.rpm_base),
                            ])

        if not self.keep_temp:
            rpm_cmd.append('--clean')

        rpm_cmd.append(spec_path)
        self.spawn(rpm_cmd)

        # XXX this is a nasty hack -- we really should have a proper way to
        # find out the names of the RPM files created.
        if not self.dry_run:
            if not self.binary_only:
                srpms = glob.glob(os.path.join(rpm_dir['SRPMS'], "*.rpm"))
                for srpm in srpms:
                    self.move_file(srpm, self.dist_dir)

            if not self.source_only:
                rpms = glob.glob(os.path.join(rpm_dir['RPMS'], "*/*.rpm"))
                for rpm in rpms:
                    self.move_file(rpm, self.dist_dir)
        return

    def _make_spec_file(self):
        """Generate the text of an RPM spec file and return it as a
        list of strings (one per line).
        """
        # definitions and headers
        pyver = "python -c 'import sys;print sys.version[:3]'"
        spec_file = [
            '%{expand: %%define pyver %(' + pyver + ')}',
            '%define pylib %{_libdir}/python%{pyver}/site-packages',
            '',
            '%define name ' + self.distribution.get_name(),
            '%define version ' + self.distribution.get_version(),
            '%define release ' + self.release,
            '',
            'Summary: ' + self.distribution.get_description(),
            ]

        # put locale summaries into spec file
        # XXX not supported for now (hard to put a dictionary
        # in a config file -- arg!)
        #for locale in self.summaries.keys():
        #    spec_file.append('Summary(%s): %s' % (locale,
        #                                          self.summaries[locale]))

        spec_file.extend([
            'Name: %{name}',
            'Version: %{version}',
            'Release: %{release}',])

        # XXX yuck! this filename is available from the "sdist" command,
        # but only after it has run: and we create the spec file before
        # running "sdist", in case of --spec-only.
        if self.use_bzip2:
            spec_file.append('Source0: %{name}-%{version}.tar.bz2')
        else:
            spec_file.append('Source0: %{name}-%{version}.tar.gz')

        for patch_info in enumerate(self.patch_files):
            spec_file.append('Patch%d: %s' % patch_info)

        spec_file.extend([
            'License: ' + self.distribution.get_license(),
            'Group: ' + self.group,
            'BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot',
            'Prefix: %{_prefix}',
            ])

        # noarch if no extension modules
        if not self.distribution.has_ext_modules():
            spec_file.append('BuildArchitectures: noarch')

        for field in ('Vendor',
                      'Packager',
                      'Provides',
                      'Requires',
                      'Conflicts',
                      'Obsoletes',
                      ):
            val = getattr(self, field.lower())
            if type(val) is ListType:
                spec_file.append('%s: %s' % (field, ''.join(val)))
            elif val is not None:
                spec_file.append('%s: %s' % (field, val))


        if self.distribution.get_url() != 'UNKNOWN':
            spec_file.append('Url: ' + self.distribution.get_url())

        if self.distribution_name:
            spec_file.append('Distribution: ' + self.distribution_name)

        if self.build_requires:
            spec_file.append('BuildRequires: ' +
                             ''.join(self.build_requires))

        if self.icon:
            spec_file.append('Icon: ' + os.path.basename(self.icon))

        spec_file.extend([
            '',
            '%description',
            self.distribution.get_long_description()
            ])

        # Add the sub-package information
        distributions = []
        for pkg in self.distribution.sub_packages:
            dist = self.distribution.get_package_distribution(pkg)
            spec_file.extend([
                '',
                '%package ' + dist.get_name(),
                'Summary: ' + dist.get_description(),
                'Group: ' + self.group,
                ])

            for dep in dist.dependencies:
                spec_file.append(
                    'Requires: %%{name}-%s = %%{version}-%%{release}' % dep)

            spec_file.extend([
                '',
                '%description ' + dist.get_name(),
                dist.get_long_description(),
                ])

            # Save it for later use in the %files section
            distributions.append(dist)

        # Add the docs sub-package
        if self.distribution.has_docs():
            spec_file.extend([
                '',
                '%package Docs',
                'Summary: Documentation for %{name}',
                'Group: ' + self.group,
                '',
                '%description Docs',
                ('The %{name}-Docs package contains documentation on the '
                 '%{name} libraries.  The documentation is provided in ASCII '
                 'text files and in HTML files.'),
                ])

        # Add the tests sub-package
        if self.distribution.has_devel():
            spec_file.extend([
                '',
                '%package Tests',
                'Summary: The test suite for %{name}',
                'Group: ' + self.group,
                ])

            for pkg in self.distribution.sub_packages:
                spec_file.append(
                    'Requires: %%{name}-%s = %%{version}-%%{release}' % pkg)

            spec_file.extend([
                '',
                '%description Tests',
                ('This package includes various tests for %{name}, including '
                 'regression tests and benchmarks.'),
                ])

        # rpm scripts

        # %prep
        spec_file.extend([
            '',
            '%prep',
            '%setup',
            ])

        # %build
        if self.use_rpm_opt_flags:
            python = 'env CFLAGS="$RPM_OPT_FLAGS" ' + self.python
        else:
            python = self.python

        spec_file.extend([
            '',
            '%build',
            python + (' setup.py config \\\n'
                      '\t--prefix=%{_prefix} \\\n'
                      '\t--exec-prefix=%{_exec_prefix} \\\n'
                      '\t--pythonlibdir=%{pylib} \\\n'
                      '\t--bindir=%{_bindir} \\\n'
                      '\t--datadir=%{_datadir}/%{name} \\\n'
                      '\t--sysconfdir=%{_sysconfdir} \\\n'
                      '\t--localstatedir=%{_localstatedir}/%{name} \\\n'
                      '\t--libdir=%{_libdir}/%{name} \\\n'
                      '\t--docdir=%{_docdir}'),
             '%s setup.py build' % python,
            ])

        # %install
        spec_file.extend([
            '',
            '%install',
            '%s setup.py install --root=$RPM_BUILD_ROOT' % self.python,
            ])

        # %clean
        spec_file.extend([
            '',
            '%clean',
            'rm -rf $RPM_BUILD_ROOT',
            ])

        # %pre
        # %post
        # %preun
        # %postun
        # %verifyscript

        # %files
        def finalize_install_for_rpm(cmd):
            install = cmd.reinitialize_command('install')
            install.install_lib = '%{pylib}'
            install.install_scripts = '%{_bindir}'
            install.install_data = '%{_datadir}/%{name}'
            install.install_sysconf = '%{_sysconfdir}'
            install.install_localstate = '%{_localstatedir}/%{name}'
            install.install_docs = '%{_docdir}'
            install.install_devel = '%{_libdir}/%{name}'
            install.with_docs = 1
            install.ensure_finalized()
            return

        for dist in distributions:
            spec_file.extend([
                '',
                '%%files %s' % dist.get_name(),
                '%defattr(-,root,root)',
                ])

            finalize_install_for_rpm(dist)

            install_sysconf = dist.get_command_obj('install_sysconf')
            install_sysconf.ensure_finalized()
            for fname in install_sysconf.get_outputs():
                spec_file.append('%config ' + fname)

            for command in ('install_lib',
                            'install_scripts',
                            'install_data',
                            'install_localstate'):
                cmd_obj = dist.get_command_obj(command)
                cmd_obj.ensure_finalized()
                for fname in cmd_obj.get_outputs():
                    spec_file.append(fname)

        finalize_install_for_rpm(self)

        if self.distribution.has_docs():
            spec_file.extend([
                '',
                '%files Docs',
                '%defattr(-,root,root)',
                ])
            install_docs = self.get_finalized_command('install_docs')
            for fname in install_docs.get_outputs():
                spec_file.append(fname)

        if self.distribution.has_devel():
            spec_file.extend([
                '',
                '%files Tests',
                '%defattr(-,root,root)',
                ])
            install_devel = self.get_finalized_command('install_devel')
            for fname in install_devel.get_outputs():
                spec_file.append(fname)

        return spec_file
