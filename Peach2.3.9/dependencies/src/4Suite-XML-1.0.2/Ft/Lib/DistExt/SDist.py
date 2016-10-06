import os
from distutils import dir_util, filelist, util
from distutils.command import sdist

class SDist(sdist.sdist):
    """
    Extended 'sdist' command that uses 'manifest_templates' from the
    distribution options instead of manifest files.
    """
    command_name = 'sdist'

    description = "create a source distribution (tarball, zip file, etc.)"

    user_options = [
        ('use-defaults', None,
         "include the default file set in the manifest "
         "[default; disable with --no-defaults]"),
        ('no-defaults', None,
         "don't include the default file set"),
        ('prune', None,
         "specifically exclude files/directories that should not be "
         "distributed (build tree, RCS/CVS dirs, etc.) "
         "[default; disable with --no-prune]"),
        ('no-prune', None,
         "don't automatically exclude anything"),
        ('formats=', None,
         "formats for source distribution (comma-separated list)"),
        ('keep-temp', 'k',
         "keep the distribution tree around after creating " +
         "archive file(s)"),
        ('dist-dir=', 'd',
         "directory to put the source distribution archive(s) in "
         "[default: dist]"),
        ]

    # sdist.sdist defines this, so we must undefine it
    negative_opt = {}

    def get_file_list(self):
        """
        Figure out the list of files to include in the source
        distribution, and put it in 'self.filelist'.
        """
        self.filelist.set_allfiles(self.distribution.get_allfiles())

        # Add default file set to 'files'
        if self.use_defaults:
            self.add_defaults()

        # Process manifest template lines
        if not self.distribution.manifest_templates:
            self.announce("using default file list only", 1)
        else:
            for line in self.distribution.manifest_templates:
                try:
                    self.filelist.process_template_line(line)
                except DistutilsTemplateError, msg:
                    self.warn(str(msg))

        # Prune away any directories that don't belong in the source
        # distribution
        if self.prune:
            self.prune_file_list(self.filelist)

        # File list now complete -- sort it so that higher-level files
        # come first
        self.filelist.sort()

        # Remove duplicates from the file list
        self.filelist.remove_duplicates()
        return

    def add_defaults(self):
        """Add all the default files to self.filelist:
          - setup.py
          - README or README.txt (in all directories)
          - all pure Python modules mentioned in setup script
          - all C sources listed as part of extensions or C libraries
            in the setup script (doesn't catch C headers!)
        """
        self.filelist.include_pattern('README*')
        self.filelist.include_pattern('COPYRIGHT')

        # Add the files from the distribution
        self.filelist.extend(self.distribution.get_source_files())
        return

    def prune_file_list(self, filelist):
        """Prune off branches that might slip into the file list as created
        by 'read_template()', but really don't belong there:
          * the build tree (typically "build")
          * the release tree itself (only an issue if we ran "sdist"
            previously with --keep-temp, or it aborted)
          * any RCS or CVS directories
        """
        config = self.get_finalized_command('config')
        filelist.exclude_pattern(config.cache_filename, anchor=1)

        build = self.get_finalized_command('build')
        filelist.exclude_pattern(None, prefix=build.build_base)

        filelist.exclude_pattern(None, prefix=self.dist_dir)

        # Trim the source code tree
        base_dir = self.distribution.get_fullname()
        filelist.exclude_pattern(None, prefix=base_dir)

        # Trim the documentation tree
        base_dir = '%s-docs-%s' % (self.distribution.get_name(),
                                   self.distribution.get_version())
        filelist.exclude_pattern(None, prefix=base_dir)

        return filelist

    def make_distribution(self):
        # Ensure that all files in the source tree are included in the
        # would be distribution
        if not self.check_distribution():
            return

        # Create the source code distribution
        sdist.sdist.make_distribution(self)

        # Create the documentation distribution
        base_dir = '%s-docs-%s' % (self.distribution.get_name(),
                                   self.distribution.get_version())
        base_name = os.path.join(self.dist_dir, base_dir)

        # Make the documentation tree
        install = self.reinitialize_command('install')
        install.install_docs = base_dir
        install.ensure_finalized()
        for command_name in ('install_text'):
            command = self.reinitialize_command(command_name)
            command.ensure_finalized()
            command.run()

        # Add a PKG-INFO entry to allow for uploading to PyPI.
        self.distribution.metadata.write_pkg_info(base_dir)

        # Archive the documentation tree
        for fmt in self.formats:
            file = self.make_archive(base_name, fmt, base_dir=base_dir)
            self.archive_files.append(file)
            if hasattr(self.distribution, 'dist_files'):
                # Save it for the "upload" command as well.
                self.distribution.dist_files.append(('sdist', '', file))

        if not self.keep_temp:
            dir_util.remove_tree(base_dir, dry_run=self.dry_run)
        return

    def check_distribution(self):
        # Start out with all files included
        allfiles = filelist.FileList()
        allfiles.set_allfiles([])
        allfiles.extend(self.distribution.get_allfiles())

        # Prune the same files as the distribution filelist
        self.prune_file_list(allfiles)

        # Exclude files included by other sub-packages
        validate_distributions = [self.distribution]
        if self.distribution.main_distribution:
            main_distribution = self.distribution.main_distribution
            validate_distributions.append(main_distribution)
            for name in main_distribution.package_options:
                dist = main_distribution.get_package_distribution(name)
                if dist is not self.distribution:
                    # Remove the other sub-package source files
                    for filename in dist.get_source_files():
                        filename = util.convert_path(filename)
                        allfiles.exclude_pattern(filename)
                    validate_distributions.append(dist)

        # Process the ignorable files for all available distributions
        for distribution in validate_distributions:
            for line in distribution.validate_templates:
                try:
                    allfiles.process_template_line(line)
                except DistutilsTemplateError, msg:
                    self.warn('in %s: %s' % (dist.package_file, msg))

        # File list now complete -- sort it so that higher-level files
        # come first
        allfiles.sort()

        # Remove duplicates from the file list
        allfiles.remove_duplicates()

        # Ensure file paths are formatted the same
        # This removes any dot-slashes and converts all slashes to
        # OS-specific separators.
        dist_files = map(os.path.normpath, self.filelist.files)
        src_files = map(os.path.normpath, allfiles.files)

        valid = 1
        for file in src_files:
            if file not in dist_files:
                self.warn('missing from source distribution: %s' % file)
                valid = 0

        if not valid:
            self.warn('Not all source files in distribution')
            prompt = raw_input('Do you want to continue? (yes/no)')
            valid = prompt.lower() in ['y', 'yes']
        return valid
