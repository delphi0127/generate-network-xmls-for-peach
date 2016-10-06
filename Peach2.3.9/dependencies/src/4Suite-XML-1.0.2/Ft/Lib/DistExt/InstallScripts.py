import os
from distutils.core import Command

class InstallScripts(Command):

    command_name = 'install_scripts'

    description = "install scripts (Python or otherwise)"

    user_options = [
        ('force', 'f', "force installation (overwrite existing files)"),
        ]

    boolean_options = ['force']

    def initialize_options(self):
        self.force = None
        self.install_dir = None
        self.skip_build = None
        return

    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('install_scripts', 'install_dir'),
                                   ('force', 'force'),
                                   ('skip_build', 'skip_build'),
                                   )
        return

    def run (self):
        if not self.skip_build:
            self.run_command('build_scripts')

        # Create the destination directory if needed
        self.mkpath(self.install_dir)

        # Copy the files created in build_scripts
        for source in self.get_inputs():
            self.copy_file(source, self.install_dir)
        return

    # -- Reporting methods ---------------------------------------------

    def get_source_files(self):
        # The sources are assumed to be reported by 'build_scripts'
        return []

    def get_inputs(self):
        build_scripts = self.get_finalized_command('build_scripts')
        return build_scripts.get_outputs()

    def get_outputs(self):
        outputs = []
        for source in self.get_inputs():
            source = os.path.basename(source)
            outfile = os.path.join(self.install_dir, source)
            outputs.append(outfile)
        return outputs
