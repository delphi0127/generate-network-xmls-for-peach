from distutils.core import Command

class Generate(Command):

    command_name = 'generate'

    description = "generate additional files needed to install"

    user_options = [
        ('force', 'f',
         'forcibly generate everything (ignore file timestamps)'),
        ]

    boolean_options = ['force']

    def initialize_options(self):
        self.force = 0

    def finalize_options(self):
        return

    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)
        return

    def get_source_files(self):
        files = []
        for cmd_name in self.get_sub_commands():
            cmd = self.get_finalized_command(cmd_name)
            files.extend(cmd.get_source_files())
        return files

    def get_outputs(self):
        outputs = []
        for cmd_name in self.get_sub_commands():
            cmd = self.get_finalized_command(cmd_name)
            outputs.extend(cmd.get_outputs())
        return outputs

    # -- Predicates for sub-command list -------------------------------

    def has_bgen(self):
        return self.distribution.has_bgen()

    def has_l10n(self):
        return self.distribution.has_l10n()

    sub_commands = [('generate_bgen', has_bgen),
                    ('generate_l10n', has_l10n),
                    ]
