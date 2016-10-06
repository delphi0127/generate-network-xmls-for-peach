import os
from distutils.core import Command

class InstallL10n(Command):

    command_name = 'install_l10n'

    description = "install binary message catalogs"

    user_options = [
        ('force', 'f', "force installation (overwrite existing files)"),
        ('skip-build', None, "skip the build steps"),
        ]

    boolean_options = ['force', 'skip-build']

    def initialize_options(self):
        self.install_dir = None
        self.force = None
        self.skip_build = None
        return

    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('install_l10n', 'install_dir'),
                                   ('force', 'force'),
                                   ('skip_build', 'skip_build'),
                                   )
        return

    def run (self):
        if not self.distribution.l10n:
            # Nothing to do
            return
        
        if not self.skip_build:
            self.run_command('build_l10n')

        for src, dst in self.get_inputs_outputs():
            # Create the destination directory if needed
            self.mkpath(os.path.dirname(dst))

            # Copy the file
            self.copy_file(src, dst)
        return

    # -- utility functions ---------------------------------------------

    def get_inputs_outputs(self):
        build_cmd = self.get_finalized_command('build_l10n')
        build_dir = build_cmd.build_dir
        build_files = build_cmd.get_outputs()
        
        prefix_len = len(build_dir) + len(os.sep)
        paired = []
        for source in build_files:
            # Trim off the build directory
            outfile = os.path.join(self.install_dir, source[prefix_len:])
            paired.append((source, outfile))
        return paired
        
    # -- external interfaces -------------------------------------------

    def get_inputs(self):
        return [ src for (src, dst) in self.get_inputs_outputs() ]

    def get_outputs(self):
        return [ dst for (src, dst) in self.get_inputs_outputs() ]
