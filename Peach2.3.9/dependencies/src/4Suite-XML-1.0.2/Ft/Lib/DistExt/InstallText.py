import os
from distutils import util
from distutils.core import Command, DEBUG

from Ft.Lib.DistExt import Structures

class InstallText(Command):

    command_name = "install_text"

    description = "install plain text documentation"

    user_options = [
        ('install-dir=', 'd', "directory to install documentation to"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ]

    boolean_options = ['force']

    def initialize_options(self):
        self.install_dir = None
        self.force = None
        return

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_docs', 'install_dir'),
                                   ('force', 'force'))

        self.files = [ f for f in self.distribution.doc_files
                       if isinstance(f, Structures.File) ]
        if self.distribution.license_file:
            self.files.append(Structures.File(self.distribution.license_file))
        return

    def run(self):
        for file in self.files:
            source = util.convert_path(file.source)
            destdir = util.convert_path(file.outdir)
            destdir = os.path.join(self.install_dir, destdir)
            self.mkpath(destdir)
            self.copy_file(source, destdir)
        return

    # -- Reporting methods ---------------------------------------------

    def get_source_files(self):
        sources = []
        for file in self.files:
            sources.append(util.convert_path(file.source))
        return sources

    def get_inputs(self):
        inputs = []
        for file in self.files:
            inputs.append(util.convert_path(file.source))
        return inputs

    def get_outputs(self):
        outputs = []
        for file in self.files:
            source = util.convert_path(file.source)
            source = os.path.basename(source)
            outdir = util.convert_path(file.outdir)
            outputs.append(os.path.join(self.install_dir, outdir, source))
        return outputs